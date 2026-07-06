import logging

from app.config import settings

logger = logging.getLogger(__name__)

VALID_MODES = {"general", "reasoning", "code", "writing"}

ROUTER_SYSTEM = (
    "You are a prompt classifier. Classify the user's prompt into exactly one category:\n"
    "- general: everyday questions, advice, explanations, chit-chat\n"
    "- reasoning: logic puzzles, math, analysis, step-by-step thinking, complex problems\n"
    "- code: programming, debugging, code generation, technical implementation\n"
    "- writing: creative writing, editing, storytelling, content creation, drafting\n\n"
    "Respond with ONLY the single category word. No explanation, no punctuation."
)


async def classify(prompt: str, provider: object) -> str:
    messages = [
        {"role": "system", "content": ROUTER_SYSTEM},
        {"role": "user", "content": prompt},
    ]
    try:
        router_model = settings.get_model_for_role("router")
        raw = await provider.chat(router_model, messages)
        mode = raw.strip().lower().rstrip(".")
        if mode in VALID_MODES:
            return mode
        logger.warning("Router returned invalid mode '%s', falling back to 'general'", raw)
    except Exception as exc:
        logger.warning("Router failed (%s), falling back to 'general'", exc)

    return "general"
