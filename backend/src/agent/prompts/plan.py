PLAN_SYSTEM = """You are a social media content strategist.
Return ONLY a JSON object with these fields:
- enhanced_brief (string, max 800 chars)
- main_message (string, max 200 chars)
- tone (string, e.g. casual, professional)
- aspect_ratio ("1:1" | "4:5" | "9:16")
- needs_text_on_image (boolean)
- platforms (array of "threads" and/or "instagram")
"""

def build_plan_messages(user_prompt: str, context_block: str) -> list[dict[str, str]]:
    user_content = (
        f"User request:\n{user_prompt}\n\n"
        f"Retrieved context:\n{context_block or '(none)'}"
    )
    return [
        {"role": "system", "content": PLAN_SYSTEM},
        {"role": "user", "content": user_content},
    ]