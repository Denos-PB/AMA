from typing import Literal
from pydantic import BaseModel, Field

RevisionTarget = Literal["threads for threads_text", "caption", "hashtags", "image", "audio"]
RevisionTarget = Literal["threads_text", "caption", "hashtags", "image", "audio"]

class RevisionPlanOutput(BaseModel):
    targets: list[RevisionTarget] = Field(min_length=1)
    instruction_summary: str = Field(min_length=1, max_length=500)
    regenerate_all: bool = False