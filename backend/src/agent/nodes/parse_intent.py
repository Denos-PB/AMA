from src.agent.state import OverallState
from src.capabilities.intent_parser import parse_intent
from src.core.llm_json import LLMJsonError
from src.integrations.deepseek import DeepSeekError

async def parse_intent_node(state: OverallState) -> dict:
    try:
        parsed = await parse_intent(
            state["user_prompt"],
            state.get("modalities"),
        )
        return {
            "user_prompt": parsed["cleaned_prompt"],
            "modalities": parsed["modalities"],
            "target_platforms": parsed["target_platforms"],
            "status": "running",
            "completed_steps": ["parse_intent"],
        }
    except ValueError as e:
        return {
            "failed_steps": ["parse_intent"],
            "errors": [f"parse_intent: {e}"],
            "status": "failed",
        }
    except (DeepSeekError, LLMJsonError) as e:
        return {
            "failed_steps": ["parse_intent"],
            "errors": [f"parse_intent: {e}"],
            "status": "failed",
        }