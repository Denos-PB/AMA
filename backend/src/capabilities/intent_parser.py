def parse_intent(user_prompt: str, modalities: list | None) -> dict:
    return {
        "cleaned_prompt": user_prompt.strip(),
        "modalities": modalities or ["text", "image"],
        "target_platforms": ["threads", "instagram"],
    }
