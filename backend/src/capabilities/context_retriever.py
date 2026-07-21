from __future__ import annotations
import logging
from src.core.config import get_settings
from src.memory.embedder import embed_texts
from src.memory.errors import MemoryError
from src.memory.formatter import format_memory_hits
from src.memory.store import search_memories

logger = logging.getlogger(__name__)

DEFAULT_TOP_K = 5
MAX_CONTEXT_CHARS = 2000

async def retrieve_context(
        user_id: str,
        user_prompt: str,
        *,
        k:int | None = None,
) -> str:
    settings = get_settings()

    if getattr(settings, "rag_enabled", True) is False:
        return ""
    
    cleaned_prompt = user_prompt.strip()
    if not cleaned_prompt:
        return ""
    
    top_k = k or getattr(settings,"rag_top_k",DEFAULT_TOP_K)

    try:
        vectors = await embed_texts([cleaned_prompt])
        if not vectors or not vectors[0]:
            raise MemoryError("Empty embedding for query")
        
        hits = await search_memories(
            user_id=user_id,
            query_vector=vectors[0],
            k=top_k,
        )
    except MemoryError:
        raise
    except Exception as e:
        logger.exception("retrive_context failed")
        raise MemoryError(str(e)) from e
    
    if not hits:
        logger.info("retrieve_context: no hits for user_id=%s", user_id)
        return ""
    
    context_block = format_memory_hits(hits,max_chars=MAX_CONTEXT_CHARS)
    logger.info(
        "retrieve_context: user_id=%s hits=%d chars=%d",
        user_id,
        len(hits),
        len(context_block),
    )
    return context_block