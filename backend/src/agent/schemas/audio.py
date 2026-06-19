from typing import Literal
from pydantic import BaseModel, Field

VoiceSuggestion = Literal["neutral", "energetic", "calm", "dramatic"]

class AudioScriptOutput(BaseModel):
    script: str = Field(min_length=1, max_length=1200)
    estimated_duration_seconds: int = Field(default=45, ge=5, le=120)
    voice_suggestion: VoiceSuggestion = "neutral"