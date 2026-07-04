def generate_text_stub(plan: dict, prompt: str) -> dict:
    return {
        "threads_text": f"[stub] Threads draft for: {prompt[:80]}",
        "caption": f"[stub] IG caption for: {prompt[:80]}",
        "hashtags": ["#ama", "#ai"],
    }
