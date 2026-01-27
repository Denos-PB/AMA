from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Any, cast, AsyncGenerator
from contextlib import asynccontextmanager
import os
from pathlib import Path
from urllib.parse import quote

from src.agent.graph import create_workflow
from src.agent.configuration import Configuration
from src.logging_config import setup_logging, get_logger
from src.agent.utils import validate_required_fields

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
setup_logging(log_level=LOG_LEVEL, verbose=VERBOSE)

logger = get_logger(__name__)

SERVE_GENERATED_ASSETS = os.getenv("SERVE_GENERATED_ASSETS", "false").lower() == "true"

def build_asset_url(
    *,
    file_path: Optional[str],
    request: Request,
    output_root: Path,
) -> Optional[str]:
    if not file_path:
        return None

    try:
        resolved_file_path = Path(file_path).resolve()
        resolved_output_root = output_root.resolve()
        relative_path = resolved_file_path.relative_to(resolved_output_root)
    except Exception:
        return None

    quoted_relative = "/".join(quote(part) for part in relative_path.parts)
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/assets/{quoted_relative}"

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("=" * 50)
    logger.info("AMA Social Media Agent Starting Up")
    logger.info("=" * 50)
    logger.info(f"API running on {os.getenv('API_HOST', '0.0.0.0')}:{os.getenv('API_PORT', '8000')}")
    logger.info(f"Configuration: {config.model_dump_json(indent=2)}")
    
    yield
    
    logger.info("=" * 50)
    logger.info("AMA Social Media Agent Shutting Down")
    logger.info("=" * 50)


app = FastAPI(
    title="AMA - Social Media Content Agent",
    description="Generates enhanced text, audio, images, and descriptions for social media",
    version="1.0.0",
    lifespan=lifespan,
)

CORS_ENABLED = os.getenv("CORS_ENABLED", "true").lower() == "true"
if CORS_ENABLED:
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for origins: {CORS_ORIGINS}")


try:
    config = Configuration()
    logger.info(f"Configuration loaded: Model={config.writer_model}, Audio={config.audio_engine}")
    
    workflow = create_workflow(config)
    logger.info("Workflow created successfully")
except Exception as e:
    logger.error(f"Failed to initialize application: {e}")
    raise

OUTPUT_ROOT = Path(config.output_dir).resolve()
if SERVE_GENERATED_ASSETS:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    app.mount("/assets", StaticFiles(directory=str(OUTPUT_ROOT)), name="assets")
    logger.warning(f"Serving generated assets publicly (dev): /assets -> {OUTPUT_ROOT}")

class GenerateRequest(BaseModel):
    user_prompt: str = Field(
        ...,
        description="The user's content request or idea",
        min_length=10,
        max_length=2000
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Optional request ID for tracking (auto-generated if not provided)"
    )
    modalities: Optional[List[str]] = Field(
        default=None,
        description="Requested output types: ['audio', 'image'] (default: both)"
    )


class WorkerOutput(BaseModel):
    status: str
    output: Optional[dict] = None
    error: Optional[str] = None


class GenerateResponse(BaseModel):
    success: bool
    request_id: str
    status: str
    enhanced_text: Optional[str] = None
    audio_path: Optional[str] = None
    audio_url: Optional[str] = None
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    hashtags: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    message: Optional[str] = None


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AMA Agent",
        "version": "1.0.0"
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(http_request: Request, payload: GenerateRequest = Body(...)):
    request_id = payload.request_id or f"req_{hash(payload.user_prompt) % 1000000}"
    
    logger.info(f"[{request_id}] Processing request: {payload.user_prompt[:50]}...")
    
    try:
        input_state = {
            "request_id": request_id,
            "user_prompt": payload.user_prompt,
            "requested_modalities": payload.modalities or ["audio", "image"],
            "status": "pending"
        }
        
        logger.info(f"[{request_id}] Invoking workflow...")
        result = await workflow.ainvoke(cast(Any, input_state))
        
        if isinstance(result, dict) and "success" in result:
            success = bool(result.get("success"))
        else:
            success = not bool(result.get("errors"))
        
        response = GenerateResponse(
            success=success,
            request_id=request_id,
            status=result.get("status", "unknown"),
            enhanced_text=result.get("enhanced_prompt"),
            audio_path=result.get("audio_path"),
            audio_url=build_asset_url(
                file_path=result.get("audio_path"),
                request=http_request,
                output_root=OUTPUT_ROOT,
            ) if (SERVE_GENERATED_ASSETS and http_request is not None) else None,
            image_path=result.get("image_path"),
            image_url=build_asset_url(
                file_path=result.get("image_path"),
                request=http_request,
                output_root=OUTPUT_ROOT,
            ) if (SERVE_GENERATED_ASSETS and http_request is not None) else None,
            description=result.get("description"),
            hashtags=result.get("hashtags"),
            errors=result.get("errors"),
            message="Content generated successfully" if success else "Content generation completed with errors"
        )
        
        logger.info(f"[{request_id}] Response: status={response.status}, success={response.success}")
        return response
        
    except Exception as e:
        logger.error(f"[{request_id}] Generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Generation failed",
                "message": str(e),
                "request_id": request_id
            }
        )


@app.get("/config")
async def get_config():
    return {
        "writer_model": config.writer_model,
        "audio_engine": config.audio_engine,
        "image_model": config.image_model,
        "video_model": config.video_model,
        "max_retries": config.max_retries,
        "output_dir": config.output_dir
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.detail}")
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code
    }
