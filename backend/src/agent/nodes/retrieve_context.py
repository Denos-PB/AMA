from src.agent.state import OverallState


async def retrieve_context_node(state: OverallState) -> dict:
    return {
        "context_block": "",
        "completed_steps": ["retrieve_context"],
    }
