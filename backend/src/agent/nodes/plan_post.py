from src.agent.state import OverallState
from src.capabilities.post_planner import plan_post
from src.core.llm_json import LLMJsonError
from src.integrations.deepseek import DeepSeekError


async def plan_post_node(state: OverallState) -> dict:
    try:
        plan = await plan_post(
            state.get("user_prompt", ""),
            state.get("context_block", ""),
        )
        return {"post_plan": plan, "completed_steps": ["plan_post"]}
    except (DeepSeekError, LLMJsonError) as e:
        return {
            "failed_steps": ["plan_post"],
            "errors": [f"plan_post: {e}"],
            "status": "failed",
        }
