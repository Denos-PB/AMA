import json
from typing import Any, Dict
from google import genai
from google.genai import types
from workers.base import BaseWorker,WorkerResult
from agent.prompts import DESCRIPTION_WRITER_SYSTEM

class DescriptionWriterWorker(BaseWorker):
    """Worker 5: Writes descriptions and hashtags."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = genai.Client()
        self.model = config.get("writer_model", "gemini-2.0-flash")

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "enhanced_prompt" in input_data

    async def process(self, input_data: Dict[str, Any]) -> WorkerResult:
        try:
            enhanced_prompt = input_data["enhanced_prompt"]
            assets = input_data.get("assets", {})

            assets_info = ", ".join([
                f"{k}: {v}" for k,v in assets.items() if v
            ])

            response = self.client.models.generate_content(
                model = self.model,
                contents=f"Content prompt: {enhanced_prompt}\nGenerated assets: {assets_info}",
                config=types.GenerateContentConfig(
                    system_instruction=DESCRIPTION_WRITER_SYSTEM,
                    response_mime_type="application/json"
                )

            )

            if response.text is None:
                raise ValueError("Model response was empty or blocked by safety filters.")

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