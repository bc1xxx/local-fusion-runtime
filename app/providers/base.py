from abc import ABC, abstractmethod
from typing import Any


class ProviderError(Exception):
    pass


class ProviderNotRunning(ProviderError):
    pass


class ModelNotFound(ProviderError):
    def __init__(self, model: str, provider: str = "ollama"):
        self.model = model
        self.provider = provider

    def __str__(self):
        if self.provider == "ollama":
            return f"Model '{self.model}' is not available locally.\nPull it with:  ollama pull {self.model}"
        return f"Model '{self.model}' was not found on the {self.provider} server. Make sure it is loaded."


class BaseProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        timeout: int | None = None,
    ) -> str:
        ...
