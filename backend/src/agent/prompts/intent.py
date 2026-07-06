import json

INTENT_SYSTEM = """You parse a social-media post request into structured intent.
Return ONLY a JSON object with:
- cleaned_prompt (string): rewrite user request clearly, keep meaning, max 2000 chars
- modalities (array): subset of ["text", "image", "audio"]
- target_platforms (array): subset of ["threads", "instagram"]

Rules:
- If user says "no image" / "text only" → modalities = ["text"]
- If user mentions voiceover / TTS / audio → include "audio"
- If user mentions reel / visual / image / photo → include "image"
- Default when unclear: ["text", "image"]
- If user names one platform only, set target_platforms accordingly
- Do not invent requirements not implied by the user
"""

def build_intent_messages(
    user_prompt: str,
    requested_modalities: list[str] | None,
) -> list[dict[str, str]]:
    hint = (
        json.dumps(requested_modalities)
        if requested_modalities
        else "not provided — infer from user text"
    )
    user_content = (
        f"User request:\n{user_prompt}\n\n"
        f"Client-requested modalities (hint, may override if user text contradicts): {hint}"
    )
    return [
        {"role": "system", "content": INTENT_SYSTEM},
        {"role": "user", "content": user_content},
    ]