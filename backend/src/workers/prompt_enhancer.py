import json
from typing import Any, Dict, Optional
import google.genai as genai
from google.genai import types
from src.workers.base import BaseWorker, WorkerResult
from src.agent.prompts import PROMPT_ENHANCER_SYSTEM
from src.agent.utils import get_logger

logger = get_logger(__name__)

class PromptEnhancerWorker(BaseWorker):

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = genai.Client()
        self.model = config.get("writer_model", "gemini-2.0-flash")

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "user_prompt" in input_data and isinstance(input_data["user_prompt"],str)

    async def process(self, input_data: Dict[str, Any]) -> WorkerResult:
        try:
            user_prompt = input_data["user_prompt"]

            response = self.client.models.generate_content(
                model=self.model,
                contents=f"User request: {user_prompt}",
                config=types.GenerateContentConfig(
                    system_instruction=PROMPT_ENHANCER_SYSTEM,
                    response_mime_type="application/json"
                )
            )

            if response.text is None:
                raise ValueError("Model response was empty or blocked.")

            result = json.loads(response.text)

            return WorkerResult(
                success=True,
                output=result,
                metadata={"model": self.model}
            )
            
        except Exception as e:
            return WorkerResult(
                success=False,
                error=str(e)
            )