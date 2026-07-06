import httpx

from app.providers.base import BaseProvider, ProviderError, ProviderNotRunning


class LMStudioProvider(BaseProvider):
    def __init__(self, base_url: str = "http://localhost:1234/v1", timeout: int = 180):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        timeout: int | None = None,
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        t = timeout or self.timeout

        async with httpx.AsyncClient(timeout=t) as client:
            try:
                resp = await client.post(url, json=payload)
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                raise ProviderNotRunning(
                    "LM Studio server is not running.\n"
                    "Open LM Studio, load a model, go to Developer / Local Server,\n"
                    "and start the server."
                ) from exc

            if resp.status_code != 200:
                raise ProviderError(
                    f"LM Studio returned status {resp.status_code}: {resp.text}"
                )

        data = resp.json()
        return data["choices"][0]["message"]["content"]
