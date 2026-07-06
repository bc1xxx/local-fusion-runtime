import time
import httpx

from app.config import settings


class OllamaError(Exception):
    pass


class OllamaNotRunning(OllamaError):
    def __str__(self):
        return (
            "Cannot connect to Ollama. Make sure Ollama is installed and running:\n"
            "  ollama serve\n"
            "Or visit https://ollama.com for installation instructions."
        )


class ModelNotFound(OllamaError):
    def __init__(self, model: str):
        self.model = model

    def __str__(self):
        return (
            f"Model '{self.model}' is not available locally.\n"
            f"Pull it with:  ollama pull {self.model}"
        )


async def ollama_chat(
    model: str,
    messages: list[dict],
    client: httpx.AsyncClient | None = None,
    timeout: int | None = None,
) -> str:
    url = f"{settings.ollama_url}/api/chat"
    payload = {"model": model, "messages": messages, "stream": False}
    t = timeout or settings.ollama_timeout
    own_client = client is None

    if own_client:
        client = httpx.AsyncClient(timeout=t)

    try:
        resp = await client.post(url, json=payload)
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        raise OllamaNotRunning() from exc
    finally:
        if own_client and client is not None:
            await client.aclose()

    if resp.status_code == 404:
        raise ModelNotFound(model)
    if resp.status_code != 200:
        raise OllamaError(f"Ollama returned status {resp.status_code}: {resp.text}")

    data = resp.json()
    return data.get("message", {}).get("content", "")


async def call_model(
    model: str,
    system_prompt: str,
    user_prompt: str,
    client: httpx.AsyncClient | None = None,
    timeout: int | None = None,
) -> tuple[str, float]:
    start = time.monotonic()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    content = await ollama_chat(model, messages, client, timeout)
    elapsed = time.monotonic() - start
    return content, elapsed
