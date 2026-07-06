import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.schemas import FusionRequest, ChatRequest
from app.config import settings
from pydantic import ValidationError


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_root_endpoint(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Local Fusion Runtime"
    assert data["version"] == "0.1.0"
    assert data["status"] == "running"
    assert data["local_only"] is True
    assert data["provider"] == "ollama"
    assert "/v1/fusion" in data["endpoints"]


@pytest.mark.asyncio
async def test_models_endpoint(client):
    resp = await client.get("/v1/models")
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "ollama"
    assert "models" in data
    roles = {m["role"] for m in data["models"]}
    assert roles == {"router", "reasoner", "coder", "general", "critic", "judge"}


def test_fusion_request_validates_empty_prompt():
    with pytest.raises(ValidationError):
        FusionRequest(prompt="")


def test_fusion_request_validates_invalid_mode():
    with pytest.raises(ValidationError):
        FusionRequest(prompt="hello", mode="invalid")


def test_fusion_request_valid_defaults():
    req = FusionRequest(prompt="hello")
    assert req.mode == "auto"
    assert req.return_raw is False


def test_fusion_response_includes_provider():
    from app.schemas import FusionResponse
    resp = FusionResponse(
        final_answer="test",
        selected_mode="general",
        models_used=["gemma3:4b"],
        latency=1.0,
    )
    assert resp.provider == "ollama"
    assert resp.local_only is True


def test_chat_request_validates_no_messages():
    with pytest.raises(ValidationError):
        ChatRequest(messages=[])


def test_chat_request_defaults():
    req = ChatRequest(messages=[{"role": "user", "content": "hi"}])
    assert req.model == "local-fusion"
    assert req.temperature == 0.3


def test_config_model_resolution_default():
    assert settings.get_model_for_role("router") == "llama3.2:3b"
    assert settings.get_model_for_role("reasoner") == "phi4-mini"
    assert settings.get_model_for_role("coder") == "qwen3.5:4b"
    assert settings.get_model_for_role("general") == "gemma3:4b"
    assert settings.get_model_for_role("critic") == "phi4-mini"
    assert settings.get_model_for_role("judge") == "qwen3.5:4b"
