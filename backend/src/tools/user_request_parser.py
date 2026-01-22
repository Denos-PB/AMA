from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any
import re

class ParseUserRequestInput(BaseModel):
    user_input: str = Field(description="Raw user request")

class ParseUserRequestOutput(BaseModel):
    prompt: str = Field(description="Cleaned prompt text")
    requested_modalities: List[Literal["audio", "image", "video"]]

def _parse_user_request(user_input: str) -> Dict[str, Any]:
    text = user_input.lower()
    modalities = []

    if any(k in text for k in ["audio", "voice", "speech", "tts"]):
        modalities.append("audio")
    if any(k in text for k in ["image", "photo", "picture", "art"]):
        modalities.append("image")
    if any(k in text for k in ["video", "clip", "animation"]):
        modalities.append("video")

    if not modalities:
        modalities = ["image", "audio"]  # safe default

    cleaned = re.sub(r"\b(audio|voice|speech|tts|image|photo|picture|art|video|clip|animation)\b", "", user_input, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return {"prompt": cleaned or user_input, "requested_modalities": modalities}

parse_user_request = StructuredTool.from_function(
    func=_parse_user_request,
    name="parse_user_request",
    description="Extracts prompt + requested modalities from user input.",
    args_schema=ParseUserRequestInput,
    return_schema=ParseUserRequestOutput,
)