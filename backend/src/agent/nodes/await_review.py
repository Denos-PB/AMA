from src.agent.state import OverallState


async def await_review_node(state: OverallState) -> dict:
    return {
        "approval_status": "awaiting_review",
        "status": "awaiting_review",
        "completed_steps": ["await_review"],
    }
