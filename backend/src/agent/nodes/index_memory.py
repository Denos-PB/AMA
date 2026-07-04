from src.agent.state import OverallState


async def index_memory_node(state: OverallState) -> dict:
    if state.get("approval_status") != "approved":
        return {
            "errors": ["index_memory: only approved posts are indexed"],
            "failed_steps": ["index_memory"],
        }
    return {
        "status": "completed",
        "completed_steps": ["index_memory"],
    }
