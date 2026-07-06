import asyncio
import logging
import time

import httpx

from app.config import settings
from app.ollama_client import call_model
from app.prompts import CRITIC_SYSTEM, JUDGE_SYSTEM
from app.router import classify
from app.schemas import FusionResponse, WorkerOutput

logger = logging.getLogger(__name__)

MODE_MODELS: dict[str, list[str]] = {
    "general": [settings.general_model],
    "reasoning": [settings.reasoner_model, settings.general_model],
    "code": [settings.coder_model, settings.reasoner_model],
    "writing": [settings.general_model, settings.router_model],
    "all": [
        settings.coder_model,
        settings.reasoner_model,
        settings.general_model,
        settings.router_model,
    ],
}

MODE_WORKER_PROMPTS = {
    "general": ["You are a helpful assistant. Answer clearly and concisely."],
    "reasoning": [
        "You are a reasoning expert. Break down complex problems step by step. Be thorough and logical.",
        "You are a helpful assistant. Answer clearly and concisely.",
    ],
    "code": [
        "You are an expert programmer. Write clean, correct code with brief explanations.",
        "You are a reasoning expert. Break down complex problems step by step.",
    ],
    "writing": [
        "You are a skilled writer. Respond with well-crafted, engaging prose.",
        "You are a helpful assistant. Answer clearly and concisely.",
    ],
    "all": [
        "You are an expert programmer. Write clean, correct code.",
        "You are a reasoning expert. Break down complex problems step by step.",
        "You are a skilled writer. Respond with well-crafted, engaging prose.",
        "You are a helpful assistant. Answer clearly and concisely.",
    ],
}


def _models_for_mode(mode: str) -> list[str]:
    return MODE_MODELS.get(mode, MODE_MODELS["general"])


def _prompts_for_mode(mode: str) -> list[str]:
    return MODE_WORKER_PROMPTS.get(mode, MODE_WORKER_PROMPTS["general"])


async def _run_workers(
    prompt: str,
    mode: str,
    client: httpx.AsyncClient,
) -> list[WorkerOutput]:
    models = _models_for_mode(mode)
    system_prompts = _prompts_for_mode(mode)

    async def _call(model: str, sp: str) -> WorkerOutput | None:
        try:
            content, elapsed = await call_model(model, sp, prompt, client=client)
            return WorkerOutput(model=model, content=content, latency=round(elapsed, 2))
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

    async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
        if mode == "auto":
            mode = await classify(prompt, client)

        worker_results = await _run_workers(prompt, mode, client)

        if not worker_results:
            raise RuntimeError("All model workers failed. Check that models are pulled and Ollama is running.")

        models_used = [w.model for w in worker_results]

        combined = "\n\n---\n\n".join(
            f"[Response from {w.model}]:\n{w.content}" for w in worker_results
        )

        if len(worker_results) > 1:
            critic_content, _ = await call_model(
                settings.critic_model,
                CRITIC_SYSTEM,
                f"User question: {prompt}\n\nResponses to review:\n{combined}",
                client=client,
            )
        else:
            critic_content = "Single response — no cross-comparison needed."

        judge_content, _ = await call_model(
            settings.judge_model,
            JUDGE_SYSTEM,
            f"User question: {prompt}\n\nRaw responses:\n{combined}\n\nCritic analysis:\n{critic_content}",
            client=client,
        )

    latency = round(time.monotonic() - start, 2)

    return FusionResponse(
        final_answer=judge_content,
        selected_mode=mode,
        models_used=models_used,
        latency=latency,
        local_only=True,
        raw_outputs=worker_results if return_raw else None,
    )
