from src.agent.state import OverallState
from src.capabilities.text_writer import generate_text_stub


async def generate_text_node(state: OverallState) -> dict:
    plan = state.get("post_plan", {})
    prompt = state.get("user_prompt", "")
    text = generate_text_stub(plan, prompt)
    return {
        "threads_text": text["threads_text"],
        "caption": text["caption"],
        "hashtags": text["hashtags"],
        "completed_steps": ["generate_text"],
    }
