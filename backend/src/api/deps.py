from typing import Any

from fastapi import Request
from langgraph.graph.state import CompiledStateGraph

from src.core.config import Settings, get_settings


def get_app_settings() -> Settings:
    return get_settings()


def get_graph(request: Request) -> CompiledStateGraph:
    return request.app.state.graph


def graph_config(thread_id: str) -> dict[str, Any]:
    return {"configurable": {"thread_id": thread_id}}


def resolve_status(values: dict[str, Any], next_nodes: tuple[str, ...]) -> str:
    if next_nodes:
        return "awaiting_review"
    return values.get("status", "pending")
