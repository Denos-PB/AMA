from src.agent.state import OverallState


async def generate_image_node(state: OverallState) -> dict:
    if "image" not in state.get("modalities", []):
        return {}
    return {
        "image_path": None,
        "completed_steps": ["generate_image"],
    }
