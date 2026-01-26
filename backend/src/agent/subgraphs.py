from langgraph.graph import StateGraph, END
from typing import TypedDict, Any
from src.agent.state import (
    PromptEnhancerState,
    AudioState,
    ImageState,
    DescriptionState
)
from src.tools.error_classification import classify_error
from src.workers.prompt_enhancer import PromptEnhancerWorker
from src.workers.audio_generator import AudioGeneratorWorker
from src.workers.image_generator import ImageGeneratorWorker
from src.workers.description_writer import DescriptionWriterWorker
from src.agent.utils import run_worker_with_error_handling, validate_required_fields, get_logger

logger = get_logger(__name__)


def build_prompt_subgraph(config):
    async def _run(state: PromptEnhancerState) -> dict:
        state_dict = dict(state)
        is_valid, error_msg = validate_required_fields(state_dict, ["input_prompt"])
        
        if not is_valid:
            return {"status": "failed", "errors": [error_msg]}

        worker = PromptEnhancerWorker(config.model_dump())
        result = await run_worker_with_error_handling(
            worker=worker,
            input_data={"user_prompt": state.get("input_prompt", "")},
            context="prompt_enhancer",
            error_classifier=classify_error,
            max_retries=config.max_retries
        )

        if result["status"] == "completed":
            return {
                "enhanced_prompt": result["output"].get("enhanced_prompt", ""),
                "main_statement": result["output"].get("main_statement", ""),
                "status": "completed"
            }
        
        return {
            "status": result["status"],
            "errors": [result.get("suggestion", result.get("error", "Unknown error"))]
        }

    g = StateGraph(PromptEnhancerState)
    g.add_node("run", _run)
    g.set_entry_point("run")
    g.add_edge("run", END)
    return g.compile()


def build_audio_subgraph(config):
    async def _run(state: AudioState) -> dict:
        state_dict = dict(state)
        is_valid, error_msg = validate_required_fields(state_dict, ["script"])
        
        if not is_valid:
            return {"status": "failed", "errors": [error_msg]}

        worker = AudioGeneratorWorker(config.model_dump())
        result = await run_worker_with_error_handling(
            worker=worker,
            input_data={
                "enhanced_prompt": state.get("script", ""),
                "main_statement": state.get("main_statement", "")
            },
            context="audio_generator",
            error_classifier=classify_error,
            max_retries=config.max_retries
        )

        if result["status"] == "completed":
            return {
                "audio_path": result["output"].get("audio_path", ""),
                "status": "completed"
            }
        
        return {
            "status": result["status"],
            "errors": [result.get("suggestion", result.get("error", "Unknown error"))]
        }

    g = StateGraph(AudioState)
    g.add_node("run", _run)
    g.set_entry_point("run")
    g.add_edge("run", END)
    return g.compile()


def build_image_subgraph(config):
    async def _run(state: ImageState) -> dict:
        state_dict = dict(state)
        is_valid, error_msg = validate_required_fields(state_dict, ["prompt"])
        
        if not is_valid:
            return {"status": "failed", "errors": [error_msg]}

        worker = ImageGeneratorWorker(config.model_dump())
        result = await run_worker_with_error_handling(
            worker=worker,
            input_data={"enhanced_prompt": state.get("prompt", "")},
            context="image_generator",
            error_classifier=classify_error,
            max_retries=config.max_retries
        )

        if result["status"] == "completed":
            return {
                "image_path": result["output"].get("image_path", ""),
                "status": "completed"
            }
        
        return {
            "status": result["status"],
            "errors": [result.get("suggestion", result.get("error", "Unknown error"))]
        }

    g = StateGraph(ImageState)
    g.add_node("run", _run)
    g.set_entry_point("run")
    g.add_edge("run", END)
    return g.compile()


def build_description_subgraph(config):
    async def _run(state: DescriptionState) -> dict:
        state_dict = dict(state)
        is_valid, error_msg = validate_required_fields(state_dict, ["prompt"])
        
        if not is_valid:
            return {"status": "failed", "errors": [error_msg]}

        worker = DescriptionWriterWorker(config.model_dump())
        result = await run_worker_with_error_handling(
            worker=worker,
            input_data={
                "enhanced_prompt": state.get("prompt", ""),
                "assets": state.get("assets", {})
            },
            context="description_writer",
            error_classifier=classify_error,
            max_retries=config.max_retries
        )

        if result["status"] == "completed":
            return {
                "description": result["output"].get("description", ""),
                "hashtags": result["output"].get("hashtags", []),
                "status": "completed"
            }
        
        return {
            "status": result["status"],
            "errors": [result.get("suggestion", result.get("error", "Unknown error"))]
        }

    g = StateGraph(DescriptionState)
    g.add_node("run", _run)
    g.set_entry_point("run")
    g.add_edge("run", END)
    return g.compile()