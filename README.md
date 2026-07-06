# Local Fusion Runtime

**A fully local compound AI runtime** — route prompts across multiple small Ollama models, run critic and judge passes, and get one synthesized answer. All inference runs on your machine. No cloud, no API keys, no telemetry.

```
                    ┌──────────┐
User Prompt ──────▶│  Router  │────▶ Classification
                    └──────────┘         │
                                         ▼
                              ┌──────────────────┐
                              │  Worker Models   │
                              │  (async in parallel)
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │     Critic       │
                              │  (quality check) │
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │     Judge        │
                              │  (synthesize)    │
                              └────────┬─────────┘
                                       ▼
                                 Final Answer
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
- [Ollama](https://ollama.com) installed and running

## Install

```bash
# Clone the repo
git clone https://github.com/your-username/local-fusion-runtime.git
cd local-fusion-runtime

# Install dependencies
pip install -r requirements.txt
```

## Pull Models

The runtime uses four default models. Pull them with Ollama:

```bash
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull qwen3.5:4b
ollama pull gemma3:4b
```

> **Note:** Model names are configured in `app/config.py` and can be overridden via environment variables. If a model doesn't exist yet, swap it for an available model (see [docs/models.md](docs/models.md)).

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

Set environment variables with the `LFR_` prefix to override defaults:

```bash
# Change any model
export LFR_ROUTER_MODEL="llama3.2:3b"
export LFR_REASONER_MODEL="phi4-mini"
export LFR_CODER_MODEL="qwen3.5:4b"
export LFR_GENERAL_MODEL="gemma3:4b"
export LFR_CRITIC_MODEL="phi4-mini"
export LFR_JUDGE_MODEL="qwen3.5:4b"

# Change Ollama URL
export LFR_OLLAMA_URL="http://localhost:11434"

# Change timeout (seconds)
export LFR_OLLAMA_TIMEOUT=60
```

Or copy `.env.example` to `.env` and uncomment the variables you need.

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
