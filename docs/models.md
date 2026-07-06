# Models

## Default Models

| Role | Model | Size | Purpose |
|------|-------|------|---------|
| Router | `llama3.2:3b` | 3B | Classify prompt category |
| Reasoner | `phi4-mini` | ~4B | Step-by-step reasoning |
| Coder | `qwen3.5:4b` | 4B | Code generation |
| General | `gemma3:4b` | 4B | General Q&A, writing |
| Critic | `phi4-mini` | ~4B | Review and critique outputs |
| Judge | `qwen3.5:4b` | 4B | Synthesize final answer |

## Swapping Models

Override any model via environment variables:

```bash
export LFR_REASONER_MODEL="llama3.1:8b"
export LFR_GENERAL_MODEL="mistral:7b"
```

Or create a `.env` file:

```
LFR_ROUTER_MODEL=llama3.2:3b
LFR_REASONER_MODEL=phi4-mini
LFR_CODER_MODEL=qwen3.5:4b
LFR_GENERAL_MODEL=gemma3:4b
LFR_CRITIC_MODEL=phi4-mini
LFR_JUDGE_MODEL=qwen3.5:4b
LFR_OLLAMA_URL=http://localhost:11434
LFR_OLLAMA_TIMEOUT=60
```

## Model Selection Guide

- **Router:** Needs good instruction-following. Any 3B+ model works.
- **Reasoner:** Best with models fine-tuned for math/logic (Phi, Mistral, DeepSeek).
- **Coder:** Best with code-focused models (CodeQwen, DeepSeek-Coder, StarCoder).
- **General:** Versatile chat model. Gemma, Llama, Mistral all work well.
- **Critic:** Needs strong instruction following. Phi and Qwen work well.
- **Judge:** Needs good synthesis ability. Qwen and larger Llama models work best.

## Hardware Profile Guidance

Which models you should pull depends on your hardware. See [hardware-profiles.md](hardware-profiles.md) for:

- **16 GB profile** (lite) — lightweight models for laptops
- **32 GB profile** (strong) — stronger models for desktops/workstations
- Per-profile pull commands and expected performance

## Requirements

At minimum, pull the core models:

```bash
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull qwen3.5:4b
ollama pull gemma3:4b
```
