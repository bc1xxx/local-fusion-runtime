from pydantic import BaseModel, Field
from typing import Literal, Optional


class FusionRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    mode: Literal["auto", "general", "reasoning", "code", "writing", "all"] = "auto"
    return_raw: bool = False


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "local-fusion"
    messages: list[ChatMessage] = Field(..., min_length=1)
    temperature: float = 0.3
    max_tokens: Optional[int] = None


class RouterOutput(BaseModel):
    mode: str
    raw: Optional[str] = None


class WorkerOutput(BaseModel):
    model: str
    content: str
    latency: float


class FusionResponse(BaseModel):
    final_answer: str
    selected_mode: str
    models_used: list[str]
    latency: float
    provider: str = "ollama"
    local_only: bool = True
    raw_outputs: Optional[list[WorkerOutput]] = None


class ChatChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"


class ChatUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    model: str = "local-fusion"
    choices: list[ChatChoice]
    usage: Optional[ChatUsage] = None


class HealthResponse(BaseModel):
    name: str = "Local Fusion Runtime"
    version: str = "0.1.0"
    status: str = "running"
    local_only: bool = True
    provider: str = "ollama"
    endpoints: list[str] = ["/v1/fusion", "/v1/chat/completions", "/v1/models"]


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    role: str
    provider: str = "ollama"


class ModelsResponse(BaseModel):
    provider: str = "ollama"
    models: list[ModelInfo]
