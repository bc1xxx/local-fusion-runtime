import asyncio
import logging
import time

from app.config import settings
from app.providers import get_provider
from app.prompts import CRITIC_SYSTEM, JUDGE_SYSTEM
from app.router import classify
from app.schemas import FusionResponse, WorkerOutput

logger = logging.getLogger(__name__)


def _resolve_model(role: str) -> str:
    return settings.get_model_for_role(role)


_DEFAULT_GENERAL = "You are a helpful assistant. Answer clearly and concisely."
_DEFAULT_REASONING = "You are a reasoning expert. Break down complex problems step by step. Be thorough and logical."
_DEFAULT_CODE = "You are an expert programmer. Write clean, correct code with brief explanations."
_DEFAULT_WRITING = "You are a skilled writer. Respond with well-crafted, engaging prose."

_FULL_MODELS: dict[str, list[str]] = {
    "general": [_resolve_model("general")],
    "reasoning": [_resolve_model("reasoner"), _resolve_model("general")],
    "code": [_resolve_model("coder"), _resolve_model("reasoner")],
    "writing": [_resolve_model("general"), _resolve_model("router")],
    "all": [
        _resolve_model("coder"),
        _resolve_model("reasoner"),
        _resolve_model("general"),
        _resolve_model("router"),
    ],
}

_FULL_PROMPTS = {
    "general": [_DEFAULT_GENERAL],
    "reasoning": [_DEFAULT_REASONING, _DEFAULT_GENERAL],
    "code": [_DEFAULT_CODE, _DEFAULT_REASONING],
    "writing": [_DEFAULT_WRITING, _DEFAULT_GENERAL],
    "all": [_DEFAULT_CODE, _DEFAULT_REASONING, _DEFAULT_WRITING, _DEFAULT_GENERAL],
}


def _models_for_mode(mode: str) -> list[str]:
    models = _FULL_MODELS.get(mode, _FULL_MODELS["general"])
    if settings.local_fusion_profile == "lite" and mode != "all":
        return models[:1]
    return models


def _prompts_for_mode(mode: str) -> list[str]:
    prompts = _FULL_PROMPTS.get(mode, _FULL_PROMPTS["general"])
    if settings.local_fusion_profile == "lite" and mode != "all":
        return prompts[:1]
    return prompts


async def _run_workers(
    prompt: str,
    mode: str,
    provider: object,
) -> list[WorkerOutput]:
    models = _models_for_mode(mode)
    system_prompts = _prompts_for_mode(mode)

    async def _call(model: str, sp: str) -> WorkerOutput | None:
        try:
            start = time.monotonic()
            content = await provider.chat(
                model,
                [
                    {"role": "system", "content": sp},
                    {"role": "user", "content": prompt},
                ],
            )
            elapsed = round(time.monotonic() - start, 2)
            return WorkerOutput(model=model, content=content, latency=elapsed)
        except Exception as exc:
            logger.error("Worker %s failed: %s", model, exc)
            return None

    tasks = [_call(m, s) for m, s in zip(models, system_prompts)]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


async def run_fusion(
    prompt: str,
    mode: str = "auto",
    return_raw: bool = False,
) -> FusionResponse:
    start = time.monotonic()
    provider = get_provider()

    if mode == "auto":
        mode = await classify(prompt, provider)

    worker_results = await _run_workers(prompt, mode, provider)

    if not worker_results:
        raise RuntimeError(
            "All model workers failed. Check that models are pulled and the provider server is running."
        )

    models_used = [w.model for w in worker_results]

    combined = "\n\n---\n\n".join(
        f"[Response from {w.model}]:\n{w.content}" for w in worker_results
    )

    if len(worker_results) > 1:
        critic_model = _resolve_model("critic")
        critic_content = await provider.chat(
            critic_model,
            [
                {"role": "system", "content": CRITIC_SYSTEM},
                {
                    "role": "user",
                    "content": f"User question: {prompt}\n\nResponses to review:\n{combined}",
                },
            ],
        )
    else:
        critic_content = "Single response — no cross-comparison needed."

    judge_model = settings.judge_model
    if settings.local_fusion_profile == "strong" and settings.judge_model_strong:
        judge_model = settings.judge_model_strong

    judge_content = await provider.chat(
        judge_model,
        [
            {"role": "system", "content": JUDGE_SYSTEM},
            {
                "role": "user",
                "content": f"User question: {prompt}\n\nRaw responses:\n{combined}\n\nCritic analysis:\n{critic_content}",
            },
        ],
    )

    latency = round(time.monotonic() - start, 2)

    return FusionResponse(
        final_answer=judge_content,
        selected_mode=mode,
        models_used=models_used,
        latency=latency,
        provider=settings.local_fusion_provider,
        local_only=True,
        raw_outputs=worker_results if return_raw else None,
    )
