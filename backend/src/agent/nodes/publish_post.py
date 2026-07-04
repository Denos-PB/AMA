from src.agent.state import OverallState


async def publish_post_node(state: OverallState) -> dict:
    if state.get("approval_status") != "approved":
        return {
            "errors": ["publish_post: draft is not approved"],
            "failed_steps": ["publish_post"],
            "status": "failed",
        }
    return {
        "status": "publishing",
        "completed_steps": ["publish_post"],
    }
