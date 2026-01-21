# backend/src/workers/image_generator.py
import json
import requests
import urllib.parse
from typing import Dict, Any
from pathlib import Path
from google import genai
from google.genai import types
from workers.base import BaseWorker, WorkerResult
from agent.prompts import IMAGE_PROMPT_SYSTEM

class ImageGeneratorWorker(BaseWorker):
    """Worker 3: Generates images using Pollinations.ai."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = genai.Client()
        self.model_id = config.get("writer_model", "gemini-2.0-flash")
        
        self.output_dir = Path(config.get("output_dir", "outputs/images"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "enhanced_prompt" in input_data
    
    async def process(self, input_data: Dict[str, Any]) -> WorkerResult:
        try:
            enhanced_prompt = input_data["enhanced_prompt"]
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=f"Enhanced prompt: {enhanced_prompt}",
                config=types.GenerateContentConfig(
                    system_instruction=IMAGE_PROMPT_SYSTEM,
                    response_mime_type="application/json"
                )
            )
            
            if response.text is None:
                raise ValueError("Model response was empty or blocked by safety filters.")
            
            prompt_data = json.loads(response.text)
            image_prompt = prompt_data.get("image_prompt", enhanced_prompt)
            width = prompt_data.get("width", 1024)
            height = prompt_data.get("height", 576)

            encoded_prompt = urllib.parse.quote(image_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
            image_response = requests.get(url, timeout=60)
            image_response.raise_for_status()
            safe_hash = abs(hash(image_prompt)) % 100000
            output_path = self.output_dir / f"image_{safe_hash}_{width}x{height}.png"
            
            with open(output_path, "wb") as f:
                f.write(image_response.content)
            
            return WorkerResult(
                success=True,
                output={"image_path": str(output_path)},
                metadata={
                    "prompt": image_prompt, 
                    "dimensions": f"{width}x{height}",
                    "model": "pollinations.ai"
                }
            )
        except Exception as e:
            return WorkerResult(
                success=False,
                error=str(e)
            )