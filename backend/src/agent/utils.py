import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


async def run_worker_with_error_handling(
    worker: Any,
    input_data: Dict[str, Any],
    context: str,
    error_classifier: Any,
    max_retries: int = 3
) -> Dict[str, Any]:
    attempt = 0
    last_error = None
    
    while attempt < max_retries:
        try:
            logger.info(f"Worker execution: {context}, attempt {attempt + 1}/{max_retries}")
            result = await worker.process(input_data)
            
            if result.success:
                logger.info(f"Worker successful: {context}")
                return {
                    "status": "completed",
                    "output": result.output,
                    "metadata": result.metadata
                }
            else:
                last_error = result.error
                logger.warning(f"Worker failed: {context}, error: {result.error}")
        
        except Exception as e:
            last_error = str(e)
            logger.error(f"Worker exception: {context}, error: {e}")
        
        attempt += 1
        
        if attempt < max_retries:
            try:
                err_classification = error_classifier.invoke({
                    "error_message": str(last_error),
                    "context": context
                })
                
                if not err_classification.get("is_retryable", False):
                    logger.info(f"Error not retryable for {context}")
                    break
                
                retry_delay = err_classification.get("retry_delay_seconds", 2)
                logger.info(f"Retrying {context} after {retry_delay}s: {err_classification.get('suggestion')}")
                await asyncio.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Error classification failed: {e}")
                break
    
    err_classification = error_classifier.invoke({
        "error_message": str(last_error),
        "context": context
    })
    
    return {
        "status": "failed",
        "error": str(last_error),
        "error_type": err_classification.get("error_type"),
        "suggestion": err_classification.get("suggestion")
    }


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> tuple[bool, Optional[str]]:
    missing_fields = [f for f in required_fields if f not in data or data[f] is None]
    
    if missing_fields:
        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
        logger.error(error_msg)
        return False, error_msg
    
    return True, None


def ensure_directory_exists(path: str) -> bool:
    from pathlib import Path
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def dict_to_string(data: Dict[str, Any], separator: str = ", ") -> str:
    return separator.join([f"{k}: {v}" for k, v in data.items() if v])
