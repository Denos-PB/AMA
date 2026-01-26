from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Any, cast, AsyncGenerator
from contextlib import asynccontextmanager
import os

from src.agent.graph import create_workflow
from src.agent.configuration import Configuration
from src.logging_config import setup_logging, get_logger
from src.agent.utils import validate_required_fields

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
setup_logging(log_level=LOG_LEVEL, verbose=VERBOSE)

logger = get_logger(__name__)

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
    image_path: Optional[str] = None
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
async def generate(request: GenerateRequest = Body(...)):
    request_id = request.request_id or f"req_{hash(request.user_prompt) % 1000000}"
    
    logger.info(f"[{request_id}] Processing request: {request.user_prompt[:50]}...")
    
    try:
        input_state = {
            "request_id": request_id,
            "user_prompt": request.user_prompt,
            "requested_modalities": request.modalities or ["audio", "image"],
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
            image_path=result.get("image_path"),
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