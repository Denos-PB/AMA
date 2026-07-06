from langgraph.graph import END
from src.agent.state import OverallState

def route_after_plan(state: OverallState):
    if state.get("status") == "failed":
        return END
    return "generate_text"


def route_after_generate_text(state: OverallState):
    if state.get("status") == "failed":
        return END
    modalities = state.get("modalities", [])
    if "image" in modalities:
        return "generate_image"
    if "audio" in modalities:
        return "generate_audio"
    return "assemble_draft"


def route_after_generate_image(state: OverallState):
    if state.get("status") == "failed":
        return END
    modalities = state.get("modalities", [])
    if "audio" in modalities:
        return "generate_audio"
    return "assemble_draft"

def route_after_parse_intent(state: OverallState):
    if state.get("status") == "failed":
        return END
    return "retrieve_context"