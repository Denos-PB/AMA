from pydantic import BaseModel, Field
from src.agent.schemas.common import AspectRatio, Platform

class PostPlanOutput(BaseModel):
    enhanced_brief: str = Field(min_length=1, max_length=800)
    main_message: str = Field(min_length=1, max_length=200)
    tone: str = "casual"
    aspect_ratio: AspectRatio = "1:1"
    needs_text_on_image: bool = False
    platforms: list[Platform] = Field(default_factory=lambda: ["threads", "instagram"])