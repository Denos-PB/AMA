from pydantic import BaseModel, Field

class VideoScriptSchema(BaseModel):
    title: str = Field(description="A catchy 3-word title for the video.")
    script: str = Field(description="The main spoken script (max 50 words).")
    image_prompts: str = Field(description="Detailed prompt for the image generator (9:16 aspect ratio).")
    caption: str = Field(description="caption with 3-5 hashtags that describe the video content or trends.")
    reasoning: str = Field(description="Why you wrote it this way.")

class AudioInputSchema(BaseModel):
    text: str = Field(description="The text to convert to speech. Must be under 200 chars.")
    voice: str = Field(default="en-US-ChristopherNeural", description="The voice ID to use.")

class ImageInputSchema(BaseModel):
    prompt: str = Field(description="The visual description for the image.")