from src.agent.state import OverallState
from src.capabilities.context_retriever import retrieve_context
from src.memory.errors import MemoryError

async def retrieve_context_node(state:OverallState) -> dict:
    user_id = state.get("user_id","user_default")
    user_prompt = state.get("user_prompt","")

    try:
        context_block = await retrieve_context(
            user_id=user_id,
            user_prompt=user_prompt
        )
        return {
            "context_block" : context_block,
            "compleated_steps" : ["retrieve_context"]
        }
    except MemoryError as e:
        return {
            "context_block": "",
            "errors" : [f"retrieve_context: {e}"],
            "completed_steps": ["retrieve_context"]
        }