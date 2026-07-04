from src.agent.state import OverallState


async def generate_audio_node(state: OverallState) -> dict:
    if "audio" not in state.get("modalities", []):
        return {}
    return {
        "audio_path": None,
        "completed_steps": ["generate_audio"],
    }
