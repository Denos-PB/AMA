from langgraph.graph import StateGraph, END
from agent.state import (
    PromptEnhancerState,
    AudioState,
    ImageState,
    DescriptionState
)
from tools.error_clasification import classify_error
from workers.prompt_enhancer import PromptEnhancerWorker
from workers.audio_generator import AudioGeneratorWorker
from workers.image_generator import ImageGeneratorWorker
from workers.description_writer import DescriptionWriterWorker


def build_prompt_subgraph(config):
    async def _run(state: PromptEnhancerState):
        user_prompt = state.get("input_prompt")
        if not user_prompt:
            raise ValueError("PromptEnhancerState.input_prompt is required")

        worker = PromptEnhancerWorker(config.model_dump())
        result = await worker.process({"user_prompt": user_prompt})

        if result.success and result.output:
            return {
                "enhanced_prompt": result.output.get("enhanced_prompt"),
                "main_statement": result.output.get("main_statement"),
                "status": "completed"
            }

        err = classify_error.invoke({"error_message": str(result.error), "context": "prompt"})
        return {"status": "failed", "errors": [err["suggestion"]]}

    g = StateGraph(PromptEnhancerState)
    g.add_node("run", _run)
    g.set_entry_point("run")
    g.add_edge("run", END)
    return g.compile()


def build_audio_subgraph(config):
    async def _run(state: AudioState):
        script = state.get("script")
        if not script:
            raise ValueError("AudioState.script is required")

        worker = AudioGeneratorWorker(config.model_dump())
        result = await worker.process({
            "enhanced_prompt": script,
            "main_statement": state.get("main_statement", "")
        })

        if result.success and result.output:
            return {"audio_path": result.output.get("audio_path"), "status": "completed"}

        err = classify_error.invoke({"error_message": str(result.error), "context": "audio"})
        return {"status": "failed", "errors": [err["suggestion"]]}

    g = StateGraph(AudioState)
    g.add_node("run", _run)
    g.set_entry_point("run")
    g.add_edge("run", END)
    return g.compile()


def build_image_subgraph(config):
    async def _run(state: ImageState):
        prompt = state.get("prompt")
        if not prompt:
            raise ValueError("ImageState.prompt is required")

        worker = ImageGeneratorWorker(config.model_dump())
        result = await worker.process({"enhanced_prompt": prompt})

        if result.success and result.output:
            return {"image_path": result.output.get("image_path"), "status": "completed"}

        err = classify_error.invoke({"error_message": str(result.error), "context": "image"})
        return {"status": "failed", "errors": [err["suggestion"]]}

    g = StateGraph(ImageState)
    g.add_node("run", _run)
    g.set_entry_point("run")
    g.add_edge("run", END)
    return g.compile()


def build_description_subgraph(config):
    async def _run(state: DescriptionState):
        prompt = state.get("prompt")
        if not prompt:
            raise ValueError("DescriptionState.prompt is required")

        worker = DescriptionWriterWorker(config.model_dump())
        result = await worker.process({
            "enhanced_prompt": prompt,
            "assets": state.get("assets", {})
        })

        if result.success and result.output:
            return {
                "description": result.output.get("description"),
                "hashtags": result.output.get("hashtags"),
                "status": "completed"
            }

        err = classify_error.invoke({"error_message": str(result.error), "context": "description"})
        return {"status": "failed", "errors": [err["suggestion"]]}

    g = StateGraph(DescriptionState)
    g.add_node("run", _run)
    g.set_entry_point("run")
    g.add_edge("run", END)
    return g.compile()