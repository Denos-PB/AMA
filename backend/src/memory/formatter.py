from __future__ import annotations
from typing import Any

DEFAULT_MAX_CHARS = 2000

def format_memory_hits(hits: list[dict[str,Any]],*,max_chars: int = DEFAULT_MAX_CHARS,)-> str:
    if not hits or max_chars <= 0:
        return ""
    
    parts: list[str] = []
    used = 0

    for hit in hits:
        text = (hit.get("text") or "").strip()
        if not text:
            continue

        memory_type = hit.get("memory_type") or "memory"
        chunk = f"[Memory - {memory_type}]\n{text}\n"

        if used + len(chunk) > max_chars:
            remaining = max_chars - used
            if remaining > 40 and not parts:
                truncated = text [: max(0, remaining - 30)].rstrip()
                if truncated:
                    parts.append(f"Memory - {memory_type}]\n{truncated}…\n")
            break

        parts.append(chunk)
        used += len(chunk)

    return "\n".join(parts).strip()