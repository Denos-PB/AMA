from pydantic import BaseModel, Field
from src.agent.schemas.common import Modality, Platform

class ParsedIntentOutput(BaseModel):
    cleaned_prompt: str = Field(min_length=1, max_lenth=2000)
    modalities: list[Modality] = Field(default_factory=lambda:["text", "image"])
    target_platforms: list[Platform] = Field(default_factory=lambda: ["threads", "instagram"])