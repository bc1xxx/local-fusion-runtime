from app.config import settings
from app.providers.base import BaseProvider, ProviderError, ProviderNotRunning, ModelNotFound
from app.providers.ollama import OllamaProvider
from app.providers.lmstudio import LMStudioProvider


def get_provider() -> BaseProvider:
    provider_name = settings.local_fusion_provider
    timeout = settings.request_timeout

    if provider_name == "ollama":
        return OllamaProvider(base_url=settings.ollama_base_url, timeout=timeout)
    elif provider_name == "lmstudio":
        return LMStudioProvider(base_url=settings.lmstudio_base_url, timeout=timeout)
    else:
        raise ValueError(
            f"Unknown provider '{provider_name}'. "
            f"Set LOCAL_FUSION_PROVIDER to 'ollama' or 'lmstudio'."
        )


__all__ = [
    "BaseProvider",
    "ProviderError",
    "ProviderNotRunning",
    "ModelNotFound",
    "get_provider",
    "OllamaProvider",
    "LMStudioProvider",
]
