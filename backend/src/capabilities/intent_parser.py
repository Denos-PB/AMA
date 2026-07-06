import logging

from src.agent.prompts.intent import build_intent_messages
from src.agent.schemas.intent import ParsedIntentOutput
from src.core.llm_json import LLMJsonError, parse_and_validate
from src.integrations.deepseek import DeepSeekError, chat_completion

logger = logging.getLogger(__name__)


def parse_intent_stub(user_prompt: str, modalities: list | None) -> dict:
    return ParsedIntentOutput(
        cleaned_prompt=user_prompt.strip(),
        modalities=modalities or ["text", "image"],
        target_platforms=["threads", "instagram"],
    ).model_dump()


async def parse_intent_with_llm(user_prompt: str) -> dict:
    messages = build_intent_messages(user_prompt, requested_modalities=None)
    logger.info("parse_intent: calling DeepSeek")

    try:
        raw_text = await chat_completion(
            messages,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        parsed = parse_and_validate(raw_text, ParsedIntentOutput)
    except DeepSeekError:
        raise
    except LLMJsonError as e:
        logger.error("parse_intent: invalid JSON from model: %s", e)
        raise

    return parsed.model_dump()


async def parse_intent(user_prompt: str, modalities: list | None) -> dict:
    cleaned = user_prompt.strip()
    if not cleaned:
        raise ValueError("user_prompt is empty")

    if modalities is not None:
        return parse_intent_stub(cleaned, modalities)

    return await parse_intent_with_llm(cleaned)
