from src.agent.state import OverallState
from src.capabilities.text_writer import generate_text
from src.core.llm_json import LLMJsonError
from src.integrations.deepseek import DeepSeekError


async def generate_text_node(state: OverallState) -> dict:
    try:
        text = await generate_text(
            state.get("post_plan", {}),
            state.get("user_prompt", ""),
        )
        return {
            "threads_text": text["threads_text"],
            "caption": text["caption"],
            "hashtags": text["hashtags"],
            "completed_steps": ["generate_text"],
        }
    except (DeepSeekError, LLMJsonError) as e:
        return {
            "failed_steps": ["generate_text"],
            "errors": [f"generate_text: {e}"],
            "status": "failed",
        }