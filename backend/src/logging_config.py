import logging
import logging.handlers
from pathlib import Path
from typing import Optional

LOG_DIR = Path("logs")


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    verbose: bool = False
) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, logs only to console
        verbose: If True, logs to both console and file
    """
    if log_file:
        LOG_DIR.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if log_file or verbose:
        file_path = Path(log_file) if log_file else LOG_DIR / "ama_agent.log"
        file_handler = logging.handlers.RotatingFileHandler(
            filename=file_path,
            maxBytes=10_000_000,
            backupCount=5,
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    logging.info(f"Logging configured at level {log_level}")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


__all__ = ["setup_logging", "get_logger", "LOG_DIR"]