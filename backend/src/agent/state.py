from __future__ import annotations

from typing import TypedDict, Optional
import operator
from typing_extensions import Annotated

from langgraph.graph import add_messages


class OverallState(TypedDict):
    messages: Annotated[list,add_messages]
    topic: Optional[str]
    final_script: Optional[str]
    final_image_prompt: Optional[str]
    final_caption: Optional[str]
    final_video_path: Optional[str]
    status: str

class WriterState(TypedDict):
    topic: str
    drafts: Annotated[list[str], operator.add]
    critiques: Annotated[list[str], operator.add]
    word_count: int
    revision_count: str
    current_script: str
    current_image_prompt: str

class VisualState(TypedDict):
    script: str
    image_prompt: str
    generated_image_paths: Annotated[list[str], operator.add]
    generated_audio_paths: Annotated[list[str], operator.add]
    render_errors: Annotated[list[str], operator.add]
    attempt_count: int