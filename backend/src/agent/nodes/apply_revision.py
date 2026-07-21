from src.agent.state import OverallState


async def apply_revision_node(state: OverallState) -> dict:
    return {
        "completed_steps": ["apply_revision"],
    }
