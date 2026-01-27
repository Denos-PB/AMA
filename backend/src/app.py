from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Any, cast, AsyncGenerator
from contextlib import asynccontextmanager
import asyncio
import os
from pathlib import Path
from urllib.parse import quote

from src.agent.graph import create_workflow
from src.agent.configuration import Configuration
from src.logging_config import setup_logging, get_logger
from src.agent.utils import validate_required_fields
from src.integrations.meta_graph import (
    MetaGraphError,
    ig_create_image_container,
    ig_get_container_status,
    ig_publish_container,
    threads_create_container,
    threads_get_container_status,
    threads_publish_container,
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
setup_logging(log_level=LOG_LEVEL, verbose=VERBOSE)

logger = get_logger(__name__)

SERVE_GENERATED_ASSETS = os.getenv("SERVE_GENERATED_ASSETS", "false").lower() == "true"
META_IG_GRAPH_VERSION = os.getenv("META_IG_GRAPH_VERSION", "v24.0")
META_THREADS_GRAPH_VERSION = os.getenv("META_THREADS_GRAPH_VERSION", "v1.0")

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


class PublishInstagramRequest(BaseModel):
    ig_user_id: str = Field(..., min_length=1)
    access_token: str = Field(..., min_length=10)
    image_url: str = Field(..., min_length=10)
    caption: str = Field(default="", max_length=2200)
    wait_timeout_seconds: int = Field(default=90, ge=5, le=300)
    poll_interval_seconds: float = Field(default=2.0, ge=0.5, le=30.0)


class PublishInstagramResponse(BaseModel):
    success: bool
    platform: str
    container_id: Optional[str] = None
    media_id: Optional[str] = None
    status: str
    error: Optional[Any] = None


class PublishThreadsRequest(BaseModel):
    threads_user_id: str = Field(..., min_length=1)
    access_token: str = Field(..., min_length=10)
    text: Optional[str] = Field(default=None, max_length=500)
    image_url: Optional[str] = Field(default=None, min_length=10)
    media_type: Optional[str] = Field(default=None)
    wait_timeout_seconds: int = Field(default=150, ge=10, le=300)
    poll_interval_seconds: float = Field(default=15.0, ge=10.0, le=60.0)


class PublishThreadsResponse(BaseModel):
    success: bool
    platform: str
    container_id: Optional[str] = None
    media_id: Optional[str] = None
    status: str
    error: Optional[Any] = None


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


@app.post("/publish/instagram", response_model=PublishInstagramResponse)
async def publish_instagram(payload: PublishInstagramRequest = Body(...)):
    if not payload.caption.strip():
        caption = ""
    else:
        caption = payload.caption.strip()

    try:
        container_id = await ig_create_image_container(
            graph_version=META_IG_GRAPH_VERSION,
            ig_user_id=payload.ig_user_id,
            access_token=payload.access_token,
            image_url=payload.image_url,
            caption=caption,
        )

        deadline = asyncio.get_running_loop().time() + float(payload.wait_timeout_seconds)
        status_code: Optional[str] = None
        while asyncio.get_running_loop().time() < deadline:
            status_payload = await ig_get_container_status(
                graph_version=META_IG_GRAPH_VERSION,
                container_id=container_id,
                access_token=payload.access_token,
            )
            status_code = status_payload.get("status_code")
            if status_code == "FINISHED":
                break
            if status_code in {"ERROR", "EXPIRED"}:
                return PublishInstagramResponse(
                    success=False,
                    platform="instagram",
                    container_id=container_id,
                    status=str(status_code),
                    error=status_payload,
                )
            await asyncio.sleep(float(payload.poll_interval_seconds))

        if status_code != "FINISHED":
            return PublishInstagramResponse(
                success=False,
                platform="instagram",
                container_id=container_id,
                status="timeout",
                error={"status_code": status_code},
            )

        media_id = await ig_publish_container(
            graph_version=META_IG_GRAPH_VERSION,
            ig_user_id=payload.ig_user_id,
            container_id=container_id,
            access_token=payload.access_token,
        )
        return PublishInstagramResponse(
            success=True,
            platform="instagram",
            container_id=container_id,
            media_id=media_id,
            status="published",
        )
    except MetaGraphError as e:
        return PublishInstagramResponse(
            success=False,
            platform="instagram",
            status="failed",
            error={"message": e.message, "status_code": e.status_code, "error": e.error},
        )
    except Exception as e:
        return PublishInstagramResponse(
            success=False,
            platform="instagram",
            status="failed",
            error={"message": str(e)},
        )


@app.post("/publish/threads", response_model=PublishThreadsResponse)
async def publish_threads(payload: PublishThreadsRequest = Body(...)):
    normalized_media_type: str
    if payload.media_type is not None:
        normalized_media_type = payload.media_type.strip().upper()
    elif payload.image_url:
        normalized_media_type = "IMAGE"
    else:
        normalized_media_type = "TEXT"

    if normalized_media_type not in {"TEXT", "IMAGE"}:
        return PublishThreadsResponse(
            success=False,
            platform="threads",
            status="failed",
            error={"message": "Only TEXT and IMAGE are supported by this endpoint"},
        )

    if normalized_media_type == "TEXT" and not (payload.text and payload.text.strip()):
        return PublishThreadsResponse(
            success=False,
            platform="threads",
            status="failed",
            error={"message": "text is required for media_type=TEXT"},
        )

    if normalized_media_type == "IMAGE" and not (payload.image_url and payload.image_url.strip()):
        return PublishThreadsResponse(
            success=False,
            platform="threads",
            status="failed",
            error={"message": "image_url is required for media_type=IMAGE"},
        )

    try:
        container_id = await threads_create_container(
            graph_version=META_THREADS_GRAPH_VERSION,
            threads_user_id=payload.threads_user_id,
            access_token=payload.access_token,
            media_type=normalized_media_type,
            text=payload.text.strip() if payload.text else None,
            image_url=payload.image_url.strip() if payload.image_url else None,
        )

        deadline = asyncio.get_running_loop().time() + float(payload.wait_timeout_seconds)
        status: Optional[str] = None
        status_payload: Optional[dict] = None
        while asyncio.get_running_loop().time() < deadline:
            status_payload = await threads_get_container_status(
                graph_version=META_THREADS_GRAPH_VERSION,
                container_id=container_id,
                access_token=payload.access_token,
            )
            status = status_payload.get("status")
            if status in {"FINISHED", "PUBLISHED"}:
                break
            if status in {"ERROR", "EXPIRED"}:
                return PublishThreadsResponse(
                    success=False,
                    platform="threads",
                    container_id=container_id,
                    status=str(status),
                    error=status_payload,
                )
            await asyncio.sleep(float(payload.poll_interval_seconds))

        if status not in {"FINISHED", "PUBLISHED"}:
            return PublishThreadsResponse(
                success=False,
                platform="threads",
                container_id=container_id,
                status="timeout",
                error=status_payload or {"status": status},
            )

        media_id = await threads_publish_container(
            graph_version=META_THREADS_GRAPH_VERSION,
            threads_user_id=payload.threads_user_id,
            container_id=container_id,
            access_token=payload.access_token,
        )
        return PublishThreadsResponse(
            success=True,
            platform="threads",
            container_id=container_id,
            media_id=media_id,
            status="published",
        )
    except MetaGraphError as e:
        return PublishThreadsResponse(
            success=False,
            platform="threads",
            status="failed",
            error={"message": e.message, "status_code": e.status_code, "error": e.error},
        )
    except Exception as e:
        return PublishThreadsResponse(
            success=False,
            platform="threads",
            status="failed",
            error={"message": str(e)},
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.detail}")
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code
    }
