import json
import re
from typing import TypeVar, Type
from pydantic import BaseModel, ValidationError
T = TypeVar("T", bound=BaseModel)

class LLMJsonError(ValueError):
    pass

def extract_json_dict(text: str) -> dict:
    if not text or not isinstance(text, str):
        raise LLMJsonError("Input must be a non-empty string")

    cleaned = text.strip()
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed,dict):
            return parsed
    except json.JSONDecodeError:
        pass

    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if fence_match:
        try:
            parsed = json.loads(fence_match.group(1))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError as e:
            raise LLMJsonError(f"Invalid JSON inside markdown fence: {e}") from e
        
    brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if brace_match:
        try:
            parsed = json.loads(brace_match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError as e:
            raise LLMJsonError(f"Invalid JSON in extracted block: {e}") from e

    raise LLMJsonError("Could not extract JSON object from text")

def parse_and_validate(text: str, model: Type[T]) -> T:
    data = extract_json_dict(text)
    try:
        return model.model_validate(data)
    except ValidationError as e:
        raise LLMJsonError(f"JSON did not match schema {model.__name__}: {e}") from e