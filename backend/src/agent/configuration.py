import os
from typing import Any, Optional
from pydantic import BaseModel, Field

from langchain_core.runnables import RunnableConfig

class Configuration(BaseModel):
    """The configuration for the agent."""

    writer_model: str = Field(
        default="gemini-2.0-flash",
        description = "Model used for prompt enhancement and description writing.",
    )

    audio_engine: str = Field(
        default="edge-tts",
        description="TTS engine."
    )

    image_model: str = Field(
        default="pollinations",
        description="Image generation service."
    )
    video_model: str = Field(
        default="disabled",
        description="Video generation (disabled to save cost)."
    )
    max_retries: int = Field(
        default=3,
        description="Number of retries per worker."
    )
    script_max_words: int = Field(
        default=120,
        description="Limit script length to keep audio/video concise."
    )
    default_voice: str = Field(
        default="neutral-female",
        description="Default TTS voice."
    )
    image_style: str = Field(
        default="cinematic",
        description="Fallback style for images when none provided."
    )
    video_duration_hint: str = Field(
        default="short",
        description="Hint passed to video generator."
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""

        configurable = (
            config['configurable'] if config and "configurable" in config else {}
        )

        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper() , configurable.get(name))
            for name in cls.model_fields.keys()
        }

        values = {k: v for k,v in raw_values.items() if v is not None}

        return cls(**values)