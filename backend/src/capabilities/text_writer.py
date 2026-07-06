import logging
from src.agent.prompts.text import build_text_messages
from src.agent.schemas.text import SocialTextOutput
from src.core.llm_json import LLMJsonError, parse_and_validate
from src.integrations.deepseek import DeepSeekError, chat_completion

logger = logging.getLogger(__name__)

async def generate_text(post_plan: dict, user_prompt: str) -> dict:
    messages = build_text_messages(user_prompt,post_plan)
    logger.info("generate_text: calling DeepSeek")

    try:
        raw_text = await chat_completion(
            messages,
            temperature=0.3,
            response_format={"type":"json_object"}
        )
        output = parse_and_validate(raw_text,SocialTextOutput)
    except DeepSeekError:
        raise
    except LLMJsonError as e:
        logger.error("generate_text: invalid JSON from model: %s", e)
        raise
    return output.model_dump()