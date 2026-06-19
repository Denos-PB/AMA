from pydantic import BaseModel, Field

class DraftPackage(BaseModel):
    draft_version: int = Field(ge=1)
    threads_text: str | None = None
    caption: str | None = None
    hashtags: list[str] = Field(default_factory=list)
    image_path: str | None = None
    audio_path: str | None = None