from __future__ import annotations

from email import message
from typing import Optional, Literal, TypedDict
from typing_extensions import Annotated
import operator

from langgraph.graph import add_messages

class OverallState(TypedDict, total=False):
    request_id: str
    user_prompt: str
    requested_modalities: list[Literal["audio", "image", "video"]]
    enhanced_prompt: Optional[str]
    main_statement: Optional[str]

    audio_path: Optional[str]
    image_path: Optional[str]
    video_path: Optional[str]
    description: Optional[str]
    hashtags: Optional[list[str]]
    
    messages: Annotated[list, add_messages]
    status: Literal["pending", "running", "partial", "completed", "failed"]
    errors: Annotated[list[str], operator.add]

class PromptEnhancerState(TypedDict, total=False):
    input_prompt: str
    enhanced_prompt: Optional[str]
    main_statement: Optional[str]
    style: Optional[str]
    mood: Optional[str]
    duration_hint: Optional[str]
    status: Literal["pending", "running", "completed", "failed"]
    errors: Annotated[list[str],operator.add]

class AudioState(TypedDict, total=False):
    script: Optional[str]
    main_statement: Optional[str]
    voice: Optional[str]
    audio_path: Optional[str]
    status: Literal["pending", "running", "completed", "failed"]
    errors: Annotated[list[str], operator.add]

class ImageState(TypedDict, total=False):
    prompt: Optional[str]
    style: Optional[str]
    image_path: Optional[str]
    status: Literal["pending","running", "completed", "failed"]
    errors: Annotated[list[str], operator.add]

class VideoState(TypedDict, total=False):
    prompt: Optional[str]
    duration_hint: Optional[str]
    video_path: Optional[str]
    status: Literal["pending", "running", "completed", "failed"]
    errors: Annotated[list[str], operator.add]

class DescriptionState(TypedDict, total=False):
    prompt: Optional[str]
    assets: dict[str, Optional[str]]
    description: Optional[str]
    hashtags: Optional[list[str]]
    status: Literal["pending", "running", "completed", "failed"]
    errors: Annotated[list[str], operator.add]