from typing import Dict, Any
from src.agent.state import (
    OverallState,
    PromptEnhancerState,
    AudioState,
    ImageState,
)
from src.tools.user_request_parser import parse_user_request
from src.agent.utils import get_logger, validate_required_fields

logger = get_logger(__name__)


async def parse_request_node(state: OverallState) -> Dict[str, Any]:
    user_prompt = state.get("user_prompt")
    if not user_prompt:
        raise ValueError("OverallState.user_prompt is required")
    parsed = parse_user_request.invoke({"user_input": user_prompt})
    return {
        "user_prompt": parsed["prompt"],
        "requested_modalities": parsed["requested_modalities"],
        "status": "running"
    }


def make_prompt_subgraph_node(prompt_graph):
    async def _node(state: OverallState) -> Dict[str, Any]:
        user_prompt = state.get("user_prompt")
        if not user_prompt:
            raise ValueError("OverallState.user_prompt is required")
        payload: PromptEnhancerState = {"input_prompt": user_prompt}
        result = await prompt_graph.ainvoke(payload)
        return {
            "enhanced_prompt": result.get("enhanced_prompt"),
            "main_statement": result.get("main_statement")
        }
    return _node


def make_audio_subgraph_node(audio_graph):
    async def _node(state: OverallState) -> Dict[str, Any]:
        if "audio" not in state.get("requested_modalities", []):
            return {}
        enhanced_prompt = state.get("enhanced_prompt")
        if not enhanced_prompt:
            raise ValueError("OverallState.enhanced_prompt is required for audio")
        payload: AudioState = {
            "script": enhanced_prompt,
            "main_statement": state.get("main_statement") or ""
        }
        result = await audio_graph.ainvoke(payload)
        return {"audio_path": result.get("audio_path")}
    return _node


def make_image_subgraph_node(image_graph):
    async def _node(state: OverallState) -> Dict[str, Any]:
        if "image" not in state.get("requested_modalities", []):
            return {}
        enhanced_prompt = state.get("enhanced_prompt")
        if not enhanced_prompt:
            raise ValueError("OverallState.enhanced_prompt is required for image")
        payload: ImageState = {"prompt": enhanced_prompt}
        result = await image_graph.ainvoke(payload)
        return {"image_path": result.get("image_path")}
    return _node


def _description_ready(state: OverallState) -> bool:
    if state.get("description"):
        return False

    requested = set(state.get("requested_modalities", []))

    supported = {"audio", "image"}
    requested = requested.intersection(supported)

    if not requested:
        return False

    required_paths = []
    if "audio" in requested:
        required_paths.append("audio_path")
    if "image" in requested:
        required_paths.append("image_path")

    return all(state.get(k) for k in required_paths)


def make_description_subgraph_node(description_graph):
    async def _node(state: OverallState) -> Dict[str, Any]:
        if not _description_ready(state):
            return {}

        enhanced_prompt = state.get("enhanced_prompt")
        if not enhanced_prompt:
            raise ValueError("OverallState.enhanced_prompt is required for description")

        assets = {
            "audio": state.get("audio_path"),
            "image": state.get("image_path"),
            "video": state.get("video_path"),
        }

        result = await description_graph.ainvoke({
            "prompt": enhanced_prompt,
            "assets": assets
        })

        return {
            "description": result.get("description"),
            "hashtags": result.get("hashtags"),
            "status": "completed"
        }
    return _node