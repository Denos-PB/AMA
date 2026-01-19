import os
import uuid
import asyncio
from langchain_core.tools import tool
import google.generativeai as genai
from schema import VideoScriptSchema, AudioInputSchema, ImageInputSchema

@tool(args_schema=AudioInputSchema)
def generate_audio_tool(text:str, voice:str="en-US-ChristopherNeural") -> str:
    import edge_tts

    if not os.path.exists("assets"):
        os.makedirs("assets")

    filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
    output_path = os.path.join("assets", filename)

    async def _run():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    try:
        asyncio.run(_run())
    except Exception as e:
        print(f"Error generating audio: {e}")

    if not os.path.exists(output_path):
        return "Error: Audio file was not created."
    
    return output_path

@tool(args_schema=ImageInputSchema)
def generate_image_tool(prompt: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")

    genai.configure(api_key=api_key)  # type: ignore
    filename = f"image_{uuid.uuid4().hex[:8]}.jpg"
    output_path = os.path.join("assets", filename)

    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    try:
        model = genai.GenerativeModel("gemini-2.0-image-exp") # type: ignore

        enhanced_prompt = f"Cinematic vertical (9:16 aspect ratio) image. {prompt}"

        response = model.generate_content(
            enhanced_prompt,
            generation_config=genai.GenerationConfig(
                candidate_count=1,
                response_mime_type="image/jpeg",
            )
        )

        if not response.parts or not response.parts[0].inline_data:
            if response.prompt_feedback:
                return f"Error: Blocked by safety filters. Reason: {response.prompt_feedback}"
            return "Error: No image data returned by API."
        
        with open(output_path, "wb") as img_file:
            img_file.write(response.parts[0].inline_data.data)

    except Exception as e:
        return f"Error generating image: {e}"
    
    if os.path.exists(output_path):
        return output_path

    return "Error: File save failed."