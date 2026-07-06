import logging
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.fusion import run_fusion
from app.providers import ProviderNotRunning, ModelNotFound, ProviderError
from app.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatChoice,
    FusionRequest,
    FusionResponse,
    HealthResponse,
    ModelInfo,
    ModelsResponse,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Local Fusion Runtime", version="0.1.0")


@app.exception_handler(ProviderNotRunning)
async def provider_not_running_handler(request: Request, exc: ProviderNotRunning):
    return JSONResponse(status_code=503, content={"error": str(exc)})


@app.exception_handler(ModelNotFound)
async def model_not_found_handler(request: Request, exc: ModelNotFound):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(ProviderError)
async def provider_error_handler(request: Request, exc: ProviderError):
    return JSONResponse(status_code=502, content={"error": str(exc)})


@app.get("/", response_model=HealthResponse)
async def health():
    return HealthResponse()


@app.get("/v1/models", response_model=ModelsResponse)
async def list_models():
    models = [
        ModelInfo(id=settings.get_model_for_role("router"), role="router"),
        ModelInfo(id=settings.get_model_for_role("reasoner"), role="reasoner"),
        ModelInfo(id=settings.get_model_for_role("coder"), role="coder"),
        ModelInfo(id=settings.get_model_for_role("general"), role="general"),
        ModelInfo(id=settings.get_model_for_role("critic"), role="critic"),
        ModelInfo(id=settings.get_model_for_role("judge"), role="judge"),
    ]
    return ModelsResponse(
        models=models,
        provider=settings.local_fusion_provider,
    )


@app.post("/v1/fusion", response_model=FusionResponse)
async def fusion_endpoint(req: FusionRequest):
    try:
        result = await run_fusion(
            prompt=req.prompt,
            mode=req.mode,
            return_raw=req.return_raw,
        )
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(req: ChatRequest):
    user_msgs = [m for m in req.messages if m.role == "user"]
    if not user_msgs:
        raise HTTPException(status_code=400, detail="No user message found in messages.")
    latest = user_msgs[-1].content

    try:
        fusion = await run_fusion(prompt=latest, mode="auto", return_raw=False)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return ChatResponse(
        id=f"local-fusion-{uuid.uuid4().hex[:12]}",
        model="local-fusion",
        choices=[
            ChatChoice(
                message=ChatMessage(role="assistant", content=fusion.final_answer),
            )
        ],
    )
