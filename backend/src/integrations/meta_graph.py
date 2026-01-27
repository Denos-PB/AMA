import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass(frozen=True)
class MetaGraphError(Exception):
    message: str
    status_code: Optional[int] = None
    error: Optional[dict] = None

    def __str__(self) -> str:
        suffix = ""
        if self.status_code is not None:
            suffix += f" (status_code={self.status_code})"
        if self.error is not None:
            suffix += f" (error={self.error})"
        return f"{self.message}{suffix}"


def _extract_graph_error(payload: Any) -> Optional[dict]:
    if isinstance(payload, dict) and "error" in payload and isinstance(payload["error"], dict):
        return payload["error"]
    return None


def _request_graph_json(
    *,
    method: str,
    url: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout_seconds: float = 30.0,
) -> Dict[str, Any]:
    try:
        response = requests.request(
            method=method,
            url=url,
            data=data,
            params=params,
            timeout=timeout_seconds,
        )
    except requests.RequestException as e:
        raise MetaGraphError(f"Meta Graph request failed: {e}") from e

    try:
        payload: Any = response.json()
    except ValueError as e:
        raise MetaGraphError(
            "Meta Graph returned a non-JSON response",
            status_code=response.status_code,
        ) from e

    graph_error = _extract_graph_error(payload)
    if response.status_code >= 400 or graph_error is not None:
        raise MetaGraphError(
            "Meta Graph API error",
            status_code=response.status_code,
            error=graph_error if graph_error is not None else payload if isinstance(payload, dict) else {"raw": payload},
        )

    if not isinstance(payload, dict):
        raise MetaGraphError(
            "Meta Graph returned unexpected JSON payload",
            status_code=response.status_code,
            error={"raw": payload},
        )

    return payload


async def ig_create_image_container(
    *,
    graph_version: str,
    ig_user_id: str,
    access_token: str,
    image_url: str,
    caption: str,
    timeout_seconds: float = 30.0,
) -> str:
    url = f"https://graph.facebook.com/{graph_version}/{ig_user_id}/media"
    payload = await asyncio.to_thread(
        _request_graph_json,
        method="POST",
        url=url,
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": access_token,
        },
        timeout_seconds=timeout_seconds,
    )
    container_id = payload.get("id")
    if not isinstance(container_id, str) or not container_id:
        raise MetaGraphError("Instagram container creation did not return id", error=payload)
    return container_id


async def ig_get_container_status(
    *,
    graph_version: str,
    container_id: str,
    access_token: str,
    timeout_seconds: float = 30.0,
) -> Dict[str, Any]:
    url = f"https://graph.facebook.com/{graph_version}/{container_id}"
    return await asyncio.to_thread(
        _request_graph_json,
        method="GET",
        url=url,
        params={
            "fields": "status_code",
            "access_token": access_token,
        },
        timeout_seconds=timeout_seconds,
    )


async def ig_publish_container(
    *,
    graph_version: str,
    ig_user_id: str,
    container_id: str,
    access_token: str,
    timeout_seconds: float = 30.0,
) -> str:
    url = f"https://graph.facebook.com/{graph_version}/{ig_user_id}/media_publish"
    payload = await asyncio.to_thread(
        _request_graph_json,
        method="POST",
        url=url,
        data={
            "creation_id": container_id,
            "access_token": access_token,
        },
        timeout_seconds=timeout_seconds,
    )
    media_id = payload.get("id")
    if not isinstance(media_id, str) or not media_id:
        raise MetaGraphError("Instagram publish did not return id", error=payload)
    return media_id


async def threads_create_container(
    *,
    graph_version: str,
    threads_user_id: str,
    access_token: str,
    media_type: str,
    text: Optional[str],
    image_url: Optional[str],
    timeout_seconds: float = 30.0,
) -> str:
    url = f"https://graph.threads.net/{graph_version}/{threads_user_id}/threads"
    data: Dict[str, Any] = {
        "media_type": media_type,
        "access_token": access_token,
    }
    if text is not None:
        data["text"] = text
    if image_url is not None:
        data["image_url"] = image_url

    payload = await asyncio.to_thread(
        _request_graph_json,
        method="POST",
        url=url,
        data=data,
        timeout_seconds=timeout_seconds,
    )
    container_id = payload.get("id")
    if not isinstance(container_id, str) or not container_id:
        raise MetaGraphError("Threads container creation did not return id", error=payload)
    return container_id


async def threads_get_container_status(
    *,
    graph_version: str,
    container_id: str,
    access_token: str,
    timeout_seconds: float = 30.0,
) -> Dict[str, Any]:
    url = f"https://graph.threads.net/{graph_version}/{container_id}"
    return await asyncio.to_thread(
        _request_graph_json,
        method="GET",
        url=url,
        params={
            "fields": "status,error_message",
            "access_token": access_token,
        },
        timeout_seconds=timeout_seconds,
    )


async def threads_publish_container(
    *,
    graph_version: str,
    threads_user_id: str,
    container_id: str,
    access_token: str,
    timeout_seconds: float = 30.0,
) -> str:
    url = f"https://graph.threads.net/{graph_version}/{threads_user_id}/threads_publish"
    payload = await asyncio.to_thread(
        _request_graph_json,
        method="POST",
        url=url,
        data={
            "creation_id": container_id,
            "access_token": access_token,
        },
        timeout_seconds=timeout_seconds,
    )
    media_id = payload.get("id")
    if not isinstance(media_id, str) or not media_id:
        raise MetaGraphError("Threads publish did not return id", error=payload)
    return media_id

