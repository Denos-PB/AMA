from src.agent.state import OverallState
from src.capabilities.post_planner import plan_post_stub


async def plan_post_node(state: OverallState) -> dict:
    plan = plan_post_stub(
        state.get("user_prompt", ""),
        state.get("context_block", ""),
    )
    return {
        "post_plan": plan,
        "completed_steps": ["plan_post"],
    }
