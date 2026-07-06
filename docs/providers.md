# Local Backend Providers

Local Fusion Runtime supports local inference through backend providers.

## Supported Providers

| Provider | Local URL | API Style | Status |
|---|---|---|---|
| Ollama | `http://localhost:11434` | Native Ollama `/api/chat` | Supported |
| LM Studio | `http://localhost:1234/v1` | OpenAI-compatible `/chat/completions` | Supported |

## Choosing a Provider

Set the `LOCAL_FUSION_PROVIDER` environment variable:

```bash
export LOCAL_FUSION_PROVIDER=ollama    # default
```

or:

```bash
export LOCAL_FUSION_PROVIDER=lmstudio
```

## Ollama

Ollama is best for simple terminal-based local model management.

- Pull models with `ollama pull <model>`.
- Start the Ollama service before running the server.
- Default endpoint: `http://localhost:11434/api/chat`.
- Model names match the tags used in `ollama pull`.

```bash
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull qwen3.5:4b
ollama pull gemma3:4b

export LOCAL_FUSION_PROVIDER=ollama
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## LM Studio

LM Studio is best for users who prefer a desktop UI for managing local models.

### Setup

1. Download and open [LM Studio](https://lmstudio.ai).
2. Download and load a local model in LM Studio.
3. Go to the **Developer** tab / **Local Server** section.
4. Click **Start Server**.
5. Confirm the server is running at `http://localhost:1234/v1`.

### Model Names

LM Studio model names may differ from Ollama tag names. For example, a model pulled as `phi-4` in Ollama might appear as `phi-4:q4_K_M` or `lmstudio-community/phi-4-GGUF` in LM Studio.

Use the `LMSTUDIO_*_MODEL` environment variables to set LM Studio-specific names:

```bash
export LOCAL_FUSION_PROVIDER=lmstudio
export LMSTUDIO_ROUTER_MODEL="llama-3.2-3b-instruct"
export LMSTUDIO_REASONER_MODEL="phi-4-mini-instruct"
export LMSTUDIO_CODER_MODEL="qwen2.5-coder-7b"
export LMSTUDIO_GENERAL_MODEL="gemma-3-4b-it"
export LMSTUDIO_CRITIC_MODEL="phi-4-mini-instruct"
export LMSTUDIO_JUDGE_MODEL="qwen2.5-coder-7b"
```

If an `LMSTUDIO_*_MODEL` variable is empty or unset, the runtime falls back to the default model name.

### Run

```bash
export LOCAL_FUSION_PROVIDER=lmstudio
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Provider Comparison

| Aspect | Ollama | LM Studio |
|---|---|---|
| Setup | `ollama pull <model>` | Download + load in GUI |
| Server | Background service | Start/stop in Developer tab |
| Model names | Standard tags (`llama3.2:3b`) | Varies by file/GGUF name |
| API format | Native `/api/chat` | OpenAI-compatible |
| Configuration | `OLLAMA_BASE_URL` | `LMSTUDIO_BASE_URL` |
| Override models | Not needed | Use `LMSTUDIO_*_MODEL` |

## Future Providers

Possible future local providers:

- **llama.cpp server** — lightweight C++ inference server
- **vLLM** — high-throughput inference engine
- **Jan** — desktop local model runner
- **KoboldCPP** — focused on storytelling / roleplay
- **Any OpenAI-compatible local server** — generic adapter for local endpoints using the OpenAI API format
