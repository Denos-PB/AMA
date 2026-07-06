from langgraph.graph import END
from src.agent.state import OverallState

def route_after_plan(state: OverallState):
    if state.get("status") == "failed":
        return END
    return "generate_text"


def route_after_generate_text(state: OverallState):
    if state.get("status") == "failed":
        return END
    return "generate_image"

def route_after_parse_intent(state: OverallState):
    if state.get("status") == "failed":
        return END
    return "retrieve_context"