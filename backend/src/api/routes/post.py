from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from langgraph.graph.state import CompiledStateGraph

from src.api.deps import get_app_settings, get_graph, graph_config, resolve_status
from src.api.schemas.post import CreatePostRequest, PostResponse
from src.core.config import Settings

router = APIRouter(prefix="/posts", tags=["posts"])


def _state_to_response(
    thread_id: str,
    values: dict,
    next_nodes: tuple[str, ...],
) -> PostResponse:
    return PostResponse(
        thread_id=thread_id,
        status=resolve_status(values, next_nodes),
        threads_text=values.get("threads_text"),
        caption=values.get("caption"),
        hashtags=values.get("hashtags") or [],
        draft_version=values.get("draft_version", 0),
        image_path=values.get("image_path"),
        audio_path=values.get("audio_path"),
        post_plan=values.get("post_plan"),
        modalities=values.get("modalities") or [],
        target_platforms=values.get("target_platforms") or [],
        completed_steps=values.get("completed_steps") or [],
        failed_steps=values.get("failed_steps") or [],
        errors=values.get("errors") or [],
    )


@router.post("", response_model=PostResponse)
async def create_post(
    body: CreatePostRequest,
    graph: CompiledStateGraph = Depends(get_graph),
    settings: Settings = Depends(get_app_settings),
) -> PostResponse:
    thread_id = f"thread_{uuid4()}"
    request_id = str(uuid4())
    config = graph_config(thread_id)

    input_state = {
        "thread_id": thread_id,
        "user_id": body.user_id or settings.default_user_id,
        "request_id": request_id,
        "user_prompt": body.user_prompt,
        "modalities": body.modalities,
        "status": "pending",
        "hashtags": [],
        "draft_version": 0,
        "completed_steps": [],
        "failed_steps": [],
        "errors": [],
    }

    await graph.ainvoke(input_state, config=config)
    snapshot = await graph.aget_state(config)
    if snapshot is None:
        raise HTTPException(status_code=500, detail="Graph state unavailable after invoke")

    return _state_to_response(
        thread_id,
        snapshot.values,
        snapshot.next,
    )


@router.get("/{thread_id}", response_model=PostResponse)
async def get_post(
    thread_id: str,
    graph: CompiledStateGraph = Depends(get_graph),
) -> PostResponse:
    config = graph_config(thread_id)
    snapshot = await graph.aget_state(config)
    if snapshot is None or not snapshot.values:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    return _state_to_response(
        thread_id,
        snapshot.values,
        snapshot.next,
    )
