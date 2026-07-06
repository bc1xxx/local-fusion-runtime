import httpx

from app.providers.base import BaseProvider, ProviderError, ProviderNotRunning, ModelNotFound


class OllamaProvider(BaseProvider):
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 180):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        timeout: int | None = None,
    ) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        t = timeout or self.timeout

        async with httpx.AsyncClient(timeout=t) as client:
            try:
                resp = await client.post(url, json=payload)
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                raise ProviderNotRunning(
                    "Cannot connect to Ollama. Make sure Ollama is installed and running:\n"
                    "  ollama serve\n"
                    "Or visit https://ollama.com for installation instructions."
                ) from exc

            if resp.status_code == 404:
                raise ModelNotFound(model, provider="ollama")
            if resp.status_code != 200:
                raise ProviderError(f"Ollama returned status {resp.status_code}: {resp.text}")

        data = resp.json()
        return data.get("message", {}).get("content", "")
