# Local Fusion Runtime

**A fully local compound AI runtime** — route prompts across multiple small Ollama models, run critic and judge passes, and get one synthesized answer. All inference runs on your machine. No cloud, no API keys, no telemetry.

```
┌──────────────────────────┐
│       USER PROMPT        │
└────────────┬─────────────┘
             │
             ▼
┌────────────────────────────────┐
│ ROUTER                         │
│ Llama 3.2 3B Instruct          │
│ Fast task classifier           │
└────────────┬───────────────────┘
             │
  ┌──────────┼─────────────┬─────┘
  ▼          ▼             ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ REASONING MODEL  │ │ CODING MODEL     │ │ GENERAL MODEL    │
│ Phi-4 Mini       │ │ Qwen3 / Qwen3.5  │ │ Gemma 3 4B       │
│ 3.8B             │ │ 4B               │ │ 4B               │
│ Logic, math,     │ │ code, APIs,      │ │ writing, summary,│
│ analysis         │ │ debugging        │ │ broad answers    │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              ▼
┌────────────────────────────────┐
│ RAG / EMBEDDINGS               │
│ nomic-embed-text or bge-m3     │
│ local docs, code, memory       │
└────────────┬───────────────────┘
             ▼
┌────────────────────────────────┐
│ CRITIC                         │
│ Qwen3 4B or Phi-4 Mini        │
│ finds weak logic / bad claims  │
└────────────┬───────────────────┘
             ▼
┌────────────────────────────────┐
│ JUDGE                          │
│ Qwen3.5 4B or Qwen3 8B Q4     │
│ merges final answer            │
└────────────┬───────────────────┘
             ▼
┌────────────────────────────────┐
│ FINAL LOCAL FUSION ANSWER      │
└────────────────────────────────┘
```

## Features

- **100% local** — No data leaves your machine. No cloud APIs. No telemetry.
- **Compound AI pipeline** — Router → Workers → Critic → Judge
- **Async parallel workers** — Calls multiple models simultaneously
- **Smart routing** — Classifies prompts into general, reasoning, code, or writing
- **Quality review** — Critic model checks for errors, contradictions, weak logic
- **Final synthesis** — Judge model merges the best output into one answer
- **OpenAI-compatible endpoint** — Drop-in for tools that expect `/v1/chat/completions`
- **Configurable** — Swap models via environment variables
- **MIT License** — Free to use, modify, and distribute

## Prerequisites

- Python 3.11+
- Either [Ollama](https://ollama.com) or [LM Studio](https://lmstudio.ai) installed

## Install

```bash
git clone https://github.com/your-username/local-fusion-runtime.git
cd local-fusion-runtime
pip install -r requirements.txt
```

## Local Backends

You can run Local Fusion Runtime with either **Ollama** or **LM Studio**. Both backends run entirely on your machine. No cloud calls, no API keys, no telemetry.

Set the provider with the `LOCAL_FUSION_PROVIDER` environment variable:

```bash
export LOCAL_FUSION_PROVIDER=ollama    # default
export LOCAL_FUSION_PROVIDER=lmstudio  # alternative
```

### Ollama Setup

Pull the default models and start Ollama:

```bash
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull qwen3.5:4b
ollama pull gemma3:4b

# Start Ollama if not already running
ollama serve
```

Run with Ollama:

```bash
LOCAL_FUSION_PROVIDER=ollama uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### LM Studio Setup

1. Download and open [LM Studio](https://lmstudio.ai).
2. Download and load local models in LM Studio.
3. Go to **Developer** / **Local Server** and start the server.
4. Confirm the server is running at `http://localhost:1234/v1`.

LM Studio model names may differ from Ollama tags. Use `LMSTUDIO_*_MODEL` env vars if needed (see [docs/providers.md](docs/providers.md)).

Run with LM Studio:

```bash
LOCAL_FUSION_PROVIDER=lmstudio uvicorn app.main:app --host 0.0.0.0 --port 8080
```

See [docs/providers.md](docs/providers.md) for detailed provider setup and model name configuration.

## Hardware Profiles

Choose the profile that matches your hardware.

| Profile | RAM | Best for | Workers | Judge | Est. Score |
|---------|-----|----------|--------|-------|-----------|
| Lite (default) | 16 GB | Writing, summaries, basic code, planning, local Q&A | 1–2 | qwen3.5:4b | 550–700 |
| Strong | 32 GB | Reasoning, code review, RAG, all-mode tests | 2–3 | qwen3:8b | 650–850 |

```bash
export LFR_PROFILE=lite      # 16 GB (default)
export LFR_PROFILE=strong    # 32 GB
```

See [docs/hardware-profiles.md](docs/hardware-profiles.md) for full profiles, ASCII architecture diagrams, pull commands, and score estimates.

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

The server starts at `http://localhost:8080`.

## Usage

### Health check

```bash
curl http://localhost:8080/
```

### List configured models

```bash
curl http://localhost:8080/v1/models
```

### Fusion endpoint (auto mode)

```bash
curl -X POST http://localhost:8080/v1/fusion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "mode": "auto",
    "return_raw": false
  }'
```

### Fusion endpoint (specific mode)

```bash
curl -X POST http://localhost:8080/v1/fusion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a recursive Fibonacci function in Python",
    "mode": "code",
    "return_raw": true
  }'
```

### OpenAI-compatible chat completions

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-fusion",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "temperature": 0.3
  }'
```

## Configuration

All settings can be configured via environment variables or a `.env` file (see `.env.example`).

### Provider

```bash
export LOCAL_FUSION_PROVIDER=ollama    # or lmstudio
export OLLAMA_BASE_URL=http://localhost:11434
export LMSTUDIO_BASE_URL=http://localhost:1234/v1
```

### Models

```bash
export ROUTER_MODEL=llama3.2:3b
export REASONER_MODEL=phi4-mini
export CODER_MODEL=qwen3.5:4b
export GENERAL_MODEL=gemma3:4b
export CRITIC_MODEL=phi4-mini
export JUDGE_MODEL=qwen3.5:4b
```

### LM Studio Model Overrides

Use these if your LM Studio model names differ from the defaults:

```bash
export LMSTUDIO_ROUTER_MODEL=
export LMSTUDIO_REASONER_MODEL=
export LMSTUDIO_CODER_MODEL=
export LMSTUDIO_GENERAL_MODEL=
export LMSTUDIO_CRITIC_MODEL=
export LMSTUDIO_JUDGE_MODEL=
```

### Profile & Timeout

```bash
export LOCAL_FUSION_PROFILE=lite     # or strong
export REQUEST_TIMEOUT_SECONDS=180
```

## Project Structure

```
local-fusion-runtime/
├── app/                    # Application code
│   ├── main.py             # FastAPI server and endpoints
│   ├── config.py           # Configuration with env overrides
│   ├── schemas.py          # Pydantic request/response models
│   ├── ollama_client.py    # Async Ollama API client
│   ├── router.py           # Prompt classifier
│   ├── fusion.py           # Pipeline orchestrator
│   └── prompts.py          # System prompts
├── tests/                  # Test suite (no Ollama required)
├── docs/                   # Documentation
└── .github/                # CI and issue templates
```

## Testing

```bash
python -m pytest tests/ -v
```

Tests don't require Ollama to be running.

## Roadmap

- Local RAG (retrieval-augmented generation)
- Conversation memory
- Model benchmarking
- Web UI (Streamlit/Gradio)
- Streaming responses (SSE)
- Docker support
- Plugin/tool support
- Better OpenAI compatibility

See [docs/roadmap.md](docs/roadmap.md) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. All contributions welcome!

## License

MIT License. See [LICENSE](LICENSE) for details.

**This repository does not include any model weights.** All models are downloaded and managed by Ollama.
