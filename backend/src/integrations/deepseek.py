from __future__ import annotations

import logging
from typing import Any, Literal

import httpx

from src.core.config import get_settings

logger = logging.getLogger(__name__)

DeepSeekErrorKind = Literal["auth", "api", "response", "timeout", "network"]


class DeepSeekError(Exception):
    def __init__(
        self,
        message: str,
        *,
        kind: DeepSeekErrorKind = "api",
        status_code: int | None = None,
    ) -> None:
        self.message = message
        self.kind = kind
        self.status_code = status_code
        super().__init__(message)

    @classmethod
    def auth(cls, message: str) -> DeepSeekError:
        return cls(message, kind="auth", status_code=401)

    @classmethod
    def api(cls, status_code: int, message: str) -> DeepSeekError:
        return cls(message, kind="api", status_code=status_code)

    @classmethod
    def response(cls, message: str) -> DeepSeekError:
        return cls(message, kind="response")

    @classmethod
    def timeout(cls, seconds: float) -> DeepSeekError:
        return cls(f"Request timed out after {seconds}s", kind="timeout")

    @classmethod
    def network(cls, message: str) -> DeepSeekError:
        return cls(message, kind="network")


async def chat_completion(
    messages: list[dict[str, str]],
    *,
    temperature: float | None = None,
    timeout: float | None = None,
    model: str | None = None,
    response_format: dict[str, str] | None = None,
) -> str:
    settings = get_settings()
    if not settings.deepseek_api_key:
        raise DeepSeekError.auth("DEEPSEEK_API_KEY is not set")

    resolved_model = model or settings.deepseek_model
    resolved_timeout = timeout if timeout is not None else settings.deepseek_timeout
    resolved_temperature = (
        temperature if temperature is not None else settings.deepseek_temperature
    )

    payload: dict[str, Any] = {
        "model": resolved_model,
        "messages": messages,
        "temperature": resolved_temperature,
        "stream": False,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(
            base_url=settings.deepseek_base_url,
            timeout=resolved_timeout,
        ) as client:
            response = await client.post(
                "/chat/completions",
                json=payload,
                headers=headers,
            )
    except httpx.TimeoutException:
        raise DeepSeekError.timeout(resolved_timeout)
    except httpx.RequestError as e:
        raise DeepSeekError.network(str(e))

    if response.status_code == 401:
        raise DeepSeekError.auth("Invalid DeepSeek API key")
    if response.status_code >= 400:
        logger.error("DeepSeek error %s: %s", response.status_code, response.text)
        raise DeepSeekError.api(response.status_code, response.text)

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise DeepSeekError.response(f"Unexpected response body: {response.text}")

    if not content:
        raise DeepSeekError.response("Empty content in response")

    return content
