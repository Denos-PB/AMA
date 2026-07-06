import logging

from src.agent.prompts.plan import build_plan_messages
from src.agent.schemas.plan import PostPlanOutput
from src.core.llm_json import LLMJsonError, parse_and_validate
from src.integrations.deepseek import DeepSeekError, chat_completion

logger = logging.getLogger(__name__)


def plan_post_stub(prompt: str, context: str) -> dict:
    return {
        "enhanced_brief": prompt,
        "main_message": prompt[:100],
        "tone": "casual",
        "aspect_ratio": "1:1",
        "needs_text_on_image": False,
        "platforms": ["threads", "instagram"],
    }


async def plan_post(user_prompt: str, context_block: str) -> dict:
    messages = build_plan_messages(user_prompt, context_block)
    logger.info("plan_post: calling DeepSeek")

    try:
        raw_text = await chat_completion(
            messages,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        plan = parse_and_validate(raw_text, PostPlanOutput)
    except DeepSeekError:
        raise
    except LLMJsonError as e:
        logger.error("plan_post: invalid JSON from model: %s", e)
        raise

    return plan.model_dump()
