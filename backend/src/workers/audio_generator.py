import json
import edge_tts
import asyncio
from typing import Dict, Any
from pathlib import Path
from google import genai
from google.genai import types
from src.workers.base import BaseWorker, WorkerResult
from src.agent.prompts import AUDIO_SCRIPT_SYSTEM
from src.agent.utils import get_logger, ensure_directory_exists

logger = get_logger(__name__)

class AudioGeneratorWorker(BaseWorker):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = genai.Client()
        self.model_id = config.get("writer_model", "gemini-2.0-flash")
        
        # Use config.output_dir instead of hardcoded path
        output_base = config.get("output_dir", "outputs")
        self.output_dir = Path(output_base) / "audio"
        ensure_directory_exists(str(self.output_dir))
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "enhanced_prompt" in input_data and "main_statement" in input_data
    
    async def process(self, input_data: Dict[str, Any]) -> WorkerResult:
        try:
            enhanced_prompt = input_data["enhanced_prompt"]
            main_statement = input_data["main_statement"]
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=f"Enhanced prompt: {enhanced_prompt}\nMain statement: {main_statement}",
                config=types.GenerateContentConfig(
                    system_instruction=AUDIO_SCRIPT_SYSTEM,
                    response_mime_type="application/json"
                )
            )
            
            if response.text is None:
                raise ValueError("Model response was empty or blocked by safety filters.")
            
            script_data = json.loads(response.text)
            script = script_data["script"]
            voice = self.config.get("default_voice", "en-US-AriaNeural")
            output_path = self.output_dir / f"audio_{hash(script) % 100000}.mp3"
            
            communicate = edge_tts.Communicate(script, voice)
            await communicate.save(str(output_path))
            
            return WorkerResult(
                success=True,
                output={"audio_path": str(output_path), "script": script},
                metadata={
                    "voice": voice, 
                    "duration_estimate": script_data.get("estimated_duration_seconds"),
                    "model": self.model_id
                }
            )
        except Exception as e:
            return WorkerResult(
                success=False,
                error=str(e)
            )