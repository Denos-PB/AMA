import os
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig

class Configuration(BaseModel):
    """The configuration for the agent."""

    writer_model: str = Field(
        default="gemini-2.0-flash",
        description = "The name of the language model to use for the agent's query generation.",
    )

    visual_model: str = Field(
        default="gemini-2.0-flash-exp",
        description="The 'Nano-Banana' model used for creating a video content" 
    )

    max_retries: int = Field(
        default=3,
        description="How many retries need to perform"
    )

    script_max_words: int = Field(
        default=100,
        description="Limit script length to keep video short."
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