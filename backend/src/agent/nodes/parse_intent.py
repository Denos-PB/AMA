from src.agent.state import OverallState
from src.capabilities.intent_parser import parse_intent


async def parse_intent_node(state: OverallState) -> dict:
    parsed = parse_intent(state["user_prompt"], state.get("modalities"))
    return {
        "user_prompt": parsed["cleaned_prompt"],
        "modalities": parsed["modalities"],
        "target_platforms": parsed["target_platforms"],
        "status": "running",
        "completed_steps": ["parse_intent"],
    }
