from src.agent.state import OverallState


async def assemble_draft_node(state: OverallState) -> dict:
    return {
        "draft_version": state.get("draft_version", 0) + 1,
        "approval_status": "draft",
        "status": "running",
        "completed_steps": ["assemble_draft"],
    }
