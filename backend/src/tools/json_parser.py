from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Dict, Any
import json
import re

class ExtractJsonInput(BaseModel):
    text: str = Field(description="LLM response text (may contain JSON in markdown or extra text)")

class ExtractJsonOutput(BaseModel):
    parsed_json: Dict[str,Any] = Field(description = "Parsed JSON object")
    extraction_method: str = Field(description="direct | markdown | regex")

def _extract_json_from_text(text: str) -> Dict[str,Any]:
    if not text or not isinstance(text,str):
        raise ValueError("Input must be non-empty string")

    text = text.strip()

    try:
        result = json.loads(text)
        if isinstance(result,dict):
            return {"parsed_json": result, "extraction_method": "direct"}

    except Exception:
        pass

    match = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(match, text, re.DOTALL | re.IGNORECASE)

    if match:
        return {"parsed_json": json.loads(match.group(1)), "extraction_method": "markdown"}

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return {"parsed_json": json.loads(match.group(0)), "extraction_method": "regex"}

    raise ValueError("Could not extract JSON")

extract_json_from_text = StructuredTool.from_function(
    func=_extract_json_from_text,
    name="extract_json_from_text",
    description="Extracts JSON from LLM response (handles markdown and extra text).",
    args_schema=ExtractJsonInput,
    return_schema=ExtractJsonOutput,
)