from typing import Literal

from pydantic import BaseModel, Field

Modality = Literal["text", "image", "audio"]
Status = Literal[
    "pending",
    "running",
    "awaiting_review",
    "publishing",
    "completed",
    "failed",
    "partial",
]


class CreatePostRequest(BaseModel):
    user_prompt: str = Field(min_length=1)
    modalities: list[Modality] | None = None
    user_id: str | None = None


class PostResponse(BaseModel):
    thread_id: str
    status: Status
    threads_text: str | None = None
    caption: str | None = None
    hashtags: list[str] = Field(default_factory=list)
    draft_version: int = 0
    image_path: str | None = None
    audio_path: str | None = None
    completed_steps: list[str] = Field(default_factory=list)
