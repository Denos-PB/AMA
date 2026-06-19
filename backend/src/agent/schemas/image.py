from pydantic import BaseModel, Field

class SocialTextOutput(BaseModel):
    threads_text: str = Field(min_length=1, max_length=500)
    caption: str = Field(min_length=1, max_length=2200)
    hashtags: list[str] = Field(min_length=1, max_length=15)
    call_to_action: str = Field(default="", max_length=100)