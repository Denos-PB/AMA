from langgraph.graph import END, StateGraph

from src.agent.nodes.apply_revision import apply_revision_node
from src.agent.nodes.assemble_draft import assemble_draft_node
from src.agent.nodes.await_review import await_review_node
from src.agent.nodes.generate_audio import generate_audio_node
from src.agent.nodes.generate_image import generate_image_node
from src.agent.nodes.generate_text import generate_text_node
from src.agent.nodes.index_memory import index_memory_node
from src.agent.nodes.parse_intent import parse_intent_node
from src.agent.nodes.plan_post import plan_post_node
from src.agent.nodes.publish_post import publish_post_node
from src.agent.nodes.retrieve_context import retrieve_context_node
from src.agent.routing import route_after_generate_text, route_after_plan
from src.agent.state import OverallState


def build_graph() -> StateGraph:
    g = StateGraph(OverallState)

    g.add_node("parse_intent", parse_intent_node)
    g.add_node("retrieve_context", retrieve_context_node)
    g.add_node("plan_post", plan_post_node)
    g.add_node("generate_text", generate_text_node)
    g.add_node("generate_image", generate_image_node)
    g.add_node("generate_audio", generate_audio_node)
    g.add_node("assemble_draft", assemble_draft_node)
    g.add_node("await_review", await_review_node)
    g.add_node("apply_revision", apply_revision_node)
    g.add_node("publish_post", publish_post_node)
    g.add_node("index_memory", index_memory_node)

    g.set_entry_point("parse_intent")
    g.add_edge("parse_intent", "retrieve_context")
    g.add_edge("retrieve_context", "plan_post")
    g.add_conditional_edges(
        "plan_post",
        route_after_plan,
        {
            "generate_text": "generate_text",
            END: END,
        },
    )
    g.add_conditional_edges(
        "generate_text",
        route_after_generate_text,
        {
            "generate_image": "generate_image",
            END: END,
        },
    )
    g.add_edge("generate_image", "generate_audio")
    g.add_edge("generate_audio", "assemble_draft")
    g.add_edge("assemble_draft", "await_review")
    g.add_edge("await_review", END)

    return g


def compile_graph(checkpointer):
    return build_graph().compile(
        checkpointer=checkpointer,
        interrupt_before=["await_review"],
    )
