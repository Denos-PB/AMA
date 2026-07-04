from __future__ import annotations

import operator
from typing import Annotated, Literal, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

Status = Literal[
    "pending",
    "running",
    "awaiting_review",
    "publishing",
    "completed",
    "failed",
    "partial",
]


class OverallState(TypedDict, total=False):
    thread_id: str
    user_id: str
    request_id: str

    user_prompt: str
    modalities: list[Literal["text", "image", "audio"]]
    target_platforms: list[Literal["threads", "instagram"]]

    context_block: str
    post_plan: dict

    threads_text: Optional[str]
    caption: Optional[str]
    hashtags: list[str]
    image_path: Optional[str]
    audio_path: Optional[str]

    draft_version: int
    approval_status: Literal["draft", "awaiting_review", "approved", "rejected"]

    messages: Annotated[list[BaseMessage], add_messages]

    completed_steps: Annotated[list[str], operator.add]
    failed_steps: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
    status: Status
