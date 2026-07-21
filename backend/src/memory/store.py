from __future__ import annotations
import logging
import uuid
from typing import Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qm
from src.core.config import get_settings
from src.memory.errors import MemoryError

logger = logging.getLogger(__name__)
_client: AsyncQdrantClient | None = None

def _get_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        settings = get_settings()
        url = getattr(settings,"qdrant_url","http://localhost:6333")
        _client = AsyncQdrantClient(url=url)
    return _client

async def ensure_collection() -> None:
    settings = get_settings()
    collection = getattr(settings,"qdrant_collection","ama_memory")
    dim = getattr(settings,"embedding_dimensions",1536)
    client = _get_client()

    try:
        exists = await client.collection_exists(collection)
        if exists:
            return
        
        await client.create_collection(
            collection_name=collection,
            vectors_config = qm.VectorParams(
                size=dim,
                distance=qm.Distance.COSINE,
            ),
        )

        await client.create_payload_index(
            collection_name=collection,
            field_name="user_id",
            field_schema=qm.PayloadSchemaType.KEYWORD
        )
        logger.info("Created Qdrant collection %s (dim=%d)", collection, dim)
    except Exception as e:
        raise MemoryError.store(f"ensure_collection failed: {e}") from e
    
async def upsert_memories(*,user_id: str,items: list[dict[str, Any]],) -> list[str]:
    if not items:
        return []
    
    await ensure_collection()
    settings = get_settings()
    collection = getattr(settings,"qdrant_collection","ama_memory")
    client = _get_client()

    points: list[qm.PointStruct] = []
    ids: list[str]

    for item in items:
        text = (item.get("text") or "").strip()
        vector = item.get("vector")
        if not text or not vector:
            raise MemoryError.store("Each item needs non-empty text and vector")

        point_id = str(item.get("id") or uuid.uuid4())
        ids.append(point_id)

        payload: dict[str,Any] = {
            "user_id":user_id,
            "text": text,
            "memory_type": item.get("memory_type", "approved_post"),
            **(item.get("metadata") or {}),
        }

        points.append(
            qm.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
        )

    try:
        await client.upsert(collection_name=collection, points=points)
    except Exception as e:
        raise MemoryError.store(f"upsert failed: {e}") from e
    
    return ids


async def search_memories(*,user_id:str,query_vector:list[float],k: int=5,) -> list[dict[str,Any]]:
    if not query_vector:
        raise MemoryError.search("query_vector is empty")
    
    await ensure_collection()
    settings = get_settings()
    collection = getattr(settings,"qdrant_collection","ama_memory")
    client = _get_client()

    try:
        result = await client.search(
            collection_name=collection,
            query_vector=query_vector,
            link=k,
            query_filter=qm.Filter(
                must=[
                    qm.FieldCondition(
                        key="user_id",
                        match=qm.MatchValue(value=user_id),
                    )
                ]
            ),
            with_payload=True,
        )
    except Exception as e:
        raise MemoryError.search(f"search failed: {e}") from e

    hits: list[dict[str,Any]] = []
    for point in result:
        payload=point.payload or {}
        text = (payload.get("text") or "").strip()
        if not text:
            continue

        memory_type = payload.get("memory_type","memory")
        metadata = {
            key:value
            for key,value in payload.items()
            if key not in {"user_id","text","memory_type"}
        }

        hits.append(
            {
                "memory_type":memory_type,
                "text":text,
                "score":float(point.score) if point.score is not None else 0.0,
                "metadata":metadata,
            }
        )

    return hits

async def close_store() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None