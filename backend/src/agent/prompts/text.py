import json

TEXT_SYSTEM = """You are a social media copywriter for Threads and Instagram.
Return ONLY a JSON object with these fields:
- threads_text (string, max 500 chars) — short, punchy post for Threads
- caption (string, max 2200 chars) — Instagram caption, can be longer
- hashtags (array of 1-15 strings, each must start with #)
- call_to_action (string, max 100 chars, can be empty)

Rules:
- Match the tone from the plan
- Use the main_message as the core idea
- Do not invent facts not in the user request or plan
- hashtags must be relevant, not spam
"""

def build_text_messages(user_prompt: str, post_plan: dict) -> list[dict[str, str]]:
    plan_json = json.dumps(post_plan, ensure_ascii=False, indent=2)
    user_content = (
        f"User request:\n{user_prompt}\n\n"
        f"Post plan:\n{plan_json}"
    )
    return [
        {"role": "system", "content": TEXT_SYSTEM},
        {"role": "user", "content": user_content},
    ]