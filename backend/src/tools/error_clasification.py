from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any

class ClassifyErrorInput(BaseModel):
    error_message: str = Field(description="Raw error message")
    context: str = Field(default="", description="Where the error happened")

class ClassifyErrorOutput(BaseModel):
    error_type: Literal["network", "api", "validation", "generation", "unknown"]
    is_retryable: bool
    retry_delay_seconds: int
    suggestion: str

def _classify_error(error_message: str, context: str = "") -> Dict[str, Any]:
    msg = error_message.lower()

    if any(k in msg for k in ["timeout", "connection", "network"]):
        return {"error_type": "network", "is_retryable": True, "retry_delay_seconds": 5,
                "suggestion": "Network issue, retry later."}

    if any(k in msg for k in ["429", "rate limit", "quota", "api key", "unauthorized"]):
        return {"error_type": "api", "is_retryable": True, "retry_delay_seconds": 60,
                "suggestion": "API limit or auth issue, wait and retry."}

    if any(k in msg for k in ["invalid", "missing", "required", "validation"]):
        return {"error_type": "validation", "is_retryable": False, "retry_delay_seconds": 0,
                "suggestion": "Fix input before retry."}

    if any(k in msg for k in ["empty response", "blocked", "generation"]):
        return {"error_type": "generation", "is_retryable": True, "retry_delay_seconds": 2,
                "suggestion": "Model generation issue, retry once."}

    return {"error_type": "unknown", "is_retryable": True, "retry_delay_seconds": 3,
            "suggestion": "Unknown error, retry once then stop."}

classify_error = StructuredTool.from_function(
    func=_classify_error,
    name="classify_error",
    description="Classifies errors and returns retry guidance.",
    args_schema=ClassifyErrorInput,
    return_schema=ClassifyErrorOutput,
)