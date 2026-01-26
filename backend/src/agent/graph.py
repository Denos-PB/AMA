from langgraph.graph import StateGraph, END
from src.agent.state import OverallState
from src.agent.configuration import Configuration
from src.agent.subgraphs import (
    build_prompt_subgraph,
    build_audio_subgraph,
    build_image_subgraph,
    build_description_subgraph,
)
from src.agent.nodes import (
    parse_request_node,
    make_prompt_subgraph_node,
    make_audio_subgraph_node,
    make_image_subgraph_node,
    make_description_subgraph_node,
)


def create_workflow(config: Configuration):
    prompt_graph = build_prompt_subgraph(config)
    audio_graph = build_audio_subgraph(config)
    image_graph = build_image_subgraph(config)
    description_graph = build_description_subgraph(config)

    g = StateGraph(OverallState)

    g.add_node("parse_request", parse_request_node)
    g.add_node("prompt_subgraph", make_prompt_subgraph_node(prompt_graph))
    g.add_node("audio_subgraph", make_audio_subgraph_node(audio_graph))
    g.add_node("image_subgraph", make_image_subgraph_node(image_graph))
    g.add_node("description_subgraph", make_description_subgraph_node(description_graph))

    g.set_entry_point("parse_request")

    g.add_edge("parse_request", "prompt_subgraph")
    g.add_edge("prompt_subgraph", "audio_subgraph")
    g.add_edge("prompt_subgraph", "image_subgraph")

    g.add_edge("audio_subgraph", "description_subgraph")
    g.add_edge("image_subgraph", "description_subgraph")

    g.add_edge("description_subgraph", END)

    return g.compile()