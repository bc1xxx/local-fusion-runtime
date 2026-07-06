# Hardware Profiles

The runtime is designed for small local models, usually under 7–8 GB each when quantized. Total RAM still matters because multiple models may be loaded or called during the same request. These profiles help you pick the right setup for your machine.

| Profile | RAM | Best for | Workers | Judge | Est. Score |
|---------|-----|----------|---------|-------|-----------|
| Lite | 16 GB | Simple local AI, writing, basic code, planning | 1–2 | qwen3.5:4b | 550–700 |
| Strong Local | 32 GB | Better reasoning, coding, RAG, all-mode tests | 2–3 | qwen3:8b | 650–850 |

> **Effective score** is a project estimate, not an official benchmark. Do not treat it as a verified LLM benchmark score until the project has its own benchmark suite.

---

## 16 GB RAM Profile

A lightweight setup for a normal laptop or small desktop.

### Goal

- Simple local use
- Avoid keeping too many models loaded at once
- Prefer sequential model calls over parallel
- Use smaller 3B–4B models
- Judge capped at 4B

### Recommended Models

| Role | Model | Size |
|------|-------|------|
| Router | `llama3.2:3b` | 3B |
| General | `gemma3:4b` | 4B |
| Reasoner | `phi4-mini` | ~4B |
| Coder | `qwen3.5:4b` | 4B |
| Critic | `phi4-mini` | ~4B |
| Judge | `qwen3.5:4b` | 4B |
| Embeddings | `nomic-embed-text` | ~0.5B |

### Pull Commands

```bash
ollama pull llama3.2:3b
ollama pull gemma3:4b
ollama pull phi4-mini
ollama pull qwen3.5:4b
ollama pull nomic-embed-text
```

### Runtime Behavior

- Default to `auto` mode
- Router selects only 1 worker per request
- Critic + judge run after worker output
- Avoid `all` mode unless you understand it will be slower

### Expected Performance

- Good for writing, summaries, basic coding, planning, local Q&A, lightweight reasoning
- Slower when many models are called
- May struggle with complex coding, deep math, long context, advanced reasoning

### Effective Score Estimate

| Configuration | Score |
|---|---|
| Single small model | 350–550 |
| 16 GB Local Fusion Runtime | 550–700 |
| Well-tuned 16 GB + good prompts + RAG | 650–750 |

---

## 32 GB RAM Profile

A stronger local setup for a capable desktop or workstation.

### Goal

- Better compound reasoning
- Use more workers per request
- Use a stronger 8B judge
- Comfortable with local RAG and all-mode experiments
- Still avoid giant 30B/70B/120B models

### Recommended Models

| Role | Model | Size |
|------|-------|------|
| Router | `llama3.2:3b` | 3B |
| General | `gemma3:4b` | 4B |
| Reasoner | `phi4-mini` | ~4B |
| Coder | `qwen3.5:4b` | 4B |
| Optional second coder/reasoner | `qwen3:8b` | 8B |
| Critic | `phi4-mini` | ~4B |
| Judge | `qwen3:8b` | 8B |
| Embeddings | `nomic-embed-text` or `bge-m3` | ~0.5B |

### Pull Commands

```bash
ollama pull llama3.2:3b
ollama pull gemma3:4b
ollama pull phi4-mini
ollama pull qwen3.5:4b
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

Optional:

```bash
ollama pull bge-m3
```

### Runtime Behavior

- Default to `auto` mode
- Can comfortably use 2–3 workers per request
- `all` mode is more realistic on 32 GB than 16 GB
- Judge should use the strongest available local model (`qwen3:8b`)
- Falls back to `qwen3.5:4b` if 8B model not installed

### Expected Performance

- Better final answers because the system compares more model outputs
- Better for code review, reasoning, planning, local research, and RAG
- Still not equal to frontier cloud models
- Main advantage is privacy, local control, and better results than one small model alone

### Effective Score Estimate

| Configuration | Score |
|---|---|
| Single small model | 350–550 |
| 32 GB Local Fusion Runtime | 650–800 |
| Well-tuned 32 GB + 8B judge + RAG | 750–850 |

> The compound system can score higher than one small model because it uses routing, multiple model perspectives, critic review, judge synthesis, and optional RAG.

---

## Score Methodology

"Scores" are rough effective-capability estimates based on the project maintainers' experience with local models. They are not official LLM benchmark results. The real score should be measured with proper benchmarks once the project has its own benchmark suite.

Do not market these scores as verified LLM Stats results.

---

## Configuration

Set the profile via environment variable:

```bash
export LFR_PROFILE=lite    # 16 GB behavior (default)
export LFR_PROFILE=strong  # 32 GB behavior
```

## How Profile Affects Behavior

| Setting | `lite` (16 GB) | `strong` (32 GB) |
|---------|----------------|------------------|
| Workers per mode | 1 | 2–3 |
| `all` mode workers | 4 | 4 |
| Judge model | `qwen3.5:4b` | `qwen3:8b` (if available) |
| Parallel calls | Minimized | Full parallel |
| Best for | Laptops, efficiency | Workstations, quality |
