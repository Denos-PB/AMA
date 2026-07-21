from __future__ import annotations
import logging
from typing import Any
import httpx
from src.core.config import get_settings
from src.memory.errors import MemoryError
logger = logging.getLogger(__name__)

async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    
    cleaned = [t.strip() for t in texts]
    if any(not t for t in cleaned):
        raise MemoryError.embed("Cannot embed empty text")
    
    settings = get_settings()
    if not settings.openai_api_key:
        raise MemoryError.config("OPENAI_API_KEY is not set")
    
    payload: dict[str, Any] = {
        "model": getattr(settings, "embedding_model", "text-embedding-3-small"),
        "input": cleaned,
    }

    dims = getattr(settings, "embedding_dimensions", None)
    if dims:
        payload["dimensions"] = dims

    headers = {
        "Authorization" : f"Bearer {settings.openai_api_key}",
        "Content-Type" : "application/json",
    }
    base_url = getattr(settings, "embedding_base_url", "https://api.openai.com/v1")
    timeout = getattr(settings, "embedding_timeout", 30.0)

    try:
        async with httpx.AsyncClient(base_url=base_url,timeout=timeout) as client:
            response = await client.post("/embeddings",json=payload,headers=headers)

    except httpx.TimeoutException:
        raise MemoryError.embed(f"Embedding request timed out after {timeout}s")
    
    except httpx.RequestError as e:
        raise MemoryError.embed(f"Embedding network error: {e}") from e
    
    if response.status_code == 401:
        raise MemoryError.config("Invalid OPENAI_API_KEY")
    
    if response.status_code >= 400:
        logger.error("Embedding API %s: %s", response.status_code, response.text)
        raise MemoryError.embed(f"Embedding API {response.status_code}: {response.text}")


    try:
        data = response.json()
        items = data["data"]
        items = sorted(items, key=lambda x: x["index"])
        vectors = [item["embedding"] for item in items]
    except (KeyError, TypeError, ValueError) as e:
        raise MemoryError.embed(f"Unexpected embedding response: {response.text}") from e
    
    if len(vectors) != len(cleaned):
        raise MemoryError.embed(
            f"Expected {len(cleaned)} vectors, got {len(vectors)}"
        )
    
    return vectors


async def embed_query(text: str) -> list[float]:
    vectors = await embed_texts([text])

    return vectors[0]