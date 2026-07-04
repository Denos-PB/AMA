def plan_post_stub(prompt: str, context: str) -> dict:
    return {
        "enhanced_brief": prompt,
        "main_message": prompt[:100],
        "tone": "casual",
        "needs_text_on_image": False,
        "platforms": ["threads", "instagram"],
    }
