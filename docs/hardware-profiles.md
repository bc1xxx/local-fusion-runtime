# Hardware Profiles

Local Fusion Runtime is designed to run small local models through Ollama.
Each model should stay around the **7–8 GB or lower** range when quantized, but total system RAM still matters because multiple models may be called during one request.

The two recommended profiles are:

* **Lite Profile** — for 16 GB RAM machines
* **Strong Local Profile** — for 32 GB RAM machines

> Effective scores are rough project estimates, not official LLM Stats scores. Real scoring requires benchmarking the full system.

---

## 16 GB RAM — Lite Profile

The 16 GB profile is designed for normal laptops and small desktops.

This setup should avoid loading too many models at the same time. It works best with sequential model calls and only 1–2 worker models per request.

```txt
                         ┌──────────────────────────┐
                         │        USER PROMPT       │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────┐
                  │ ROUTER                         │
                  │ Llama 3.2 3B Instruct          │
                  │ Fast task classifier            │
                  └────────────┬───────────────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                                   ▼

┌────────────────────────────┐       ┌────────────────────────────┐
│ SELECTED WORKER MODEL      │       │ GENERAL FALLBACK MODEL     │
│ Phi-4 Mini or Qwen3.5 4B   │       │ Gemma 3 4B                 │
│ Reasoning, code, writing,  │       │ summaries, broad answers   │
│ or planning task           │       │ and simple responses       │
└─────────────┬──────────────┘       └─────────────┬──────────────┘
              │                                    │
              └─────────────────┬──────────────────┘
                                ▼
                  ┌────────────────────────────────┐
                  │ OPTIONAL RAG / EMBEDDINGS      │
                  │ nomic-embed-text               │
                  │ local docs, code, memory        │
                  └────────────┬───────────────────┘
                               ▼
                  ┌────────────────────────────────┐
                  │ CRITIC                         │
                  │ Phi-4 Mini                     │
                  │ finds weak logic / bad claims   │
                  └────────────┬───────────────────┘
                               ▼
                  ┌────────────────────────────────┐
                  │ JUDGE                          │
                  │ Qwen3.5 4B                     │
                  │ merges final answer             │
                  └────────────┬───────────────────┘
                               ▼
                  ┌────────────────────────────────┐
                  │ FINAL LOCAL FUSION ANSWER      │
                  └────────────────────────────────┘
```

### Recommended models

```txt
Router:        llama3.2:3b
Reasoner:      phi4-mini
Coder:         qwen3.5:4b
General:       gemma3:4b
Critic:        phi4-mini
Judge:         qwen3.5:4b
Embeddings:    nomic-embed-text
```

### Recommended Ollama pulls

```bash
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull qwen3.5:4b
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

### Runtime behavior

```txt
Default mode: auto
Worker count: 1–2 per request
Judge: qwen3.5:4b
Best for: writing, summaries, basic code, planning, local Q&A
Avoid: heavy all-mode usage, long context, deep math, complex coding
```

### Estimated effective score

```txt
Single small model:                 350–550
16 GB Local Fusion Runtime:          550–700
Well-tuned 16 GB setup with RAG:     650–750
```

---

## 32 GB RAM — Strong Local Profile

The 32 GB profile is designed for stronger laptops, desktops, and Apple Silicon machines with more unified memory.

This setup can use more workers per request and can use a stronger 8B judge.

```txt
                         ┌──────────────────────────┐
                         │        USER PROMPT       │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────┐
                  │ ROUTER                         │
                  │ Llama 3.2 3B Instruct          │
                  │ Fast task classifier            │
                  └────────────┬───────────────────┘
                               │
       ┌───────────────────────┼────────────────────────┐
       ▼                       ▼                        ▼

┌──────────────────┐   ┌──────────────────┐    ┌──────────────────┐
│ REASONING MODEL  │   │ CODING MODEL     │    │ GENERAL MODEL    │
│ Phi-4 Mini       │   │ Qwen3.5 4B       │    │ Gemma 3 4B       │
│ Logic, math,     │   │ code, APIs,      │    │ writing, summary,│
│ analysis         │   │ debugging        │    │ broad answers    │
└────────┬─────────┘   └────────┬─────────┘    └────────┬─────────┘
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                ▼
                  ┌────────────────────────────────┐
                  │ OPTIONAL STRONG WORKER         │
                  │ Qwen3 8B Q4                    │
                  │ deeper reasoning / judging      │
                  └────────────┬───────────────────┘
                               ▼
                  ┌────────────────────────────────┐
                  │ RAG / EMBEDDINGS               │
                  │ nomic-embed-text or bge-m3     │
                  │ local docs, code, memory        │
                  └────────────┬───────────────────┘
                               ▼
                  ┌────────────────────────────────┐
                  │ CRITIC                         │
                  │ Phi-4 Mini or Qwen3.5 4B       │
                  │ finds weak logic / bad claims   │
                  └────────────┬───────────────────┘
                               ▼
                  ┌────────────────────────────────┐
                  │ JUDGE                          │
                  │ Qwen3 8B Q4                    │
                  │ merges final answer             │
                  └────────────┬───────────────────┘
                               ▼
                  ┌────────────────────────────────┐
                  │ FINAL LOCAL FUSION ANSWER      │
                  └────────────────────────────────┘
```

### Recommended models

```txt
Router:        llama3.2:3b
Reasoner:      phi4-mini
Coder:         qwen3.5:4b
General:       gemma3:4b
Strong worker: qwen3:8b
Critic:        phi4-mini or qwen3.5:4b
Judge:         qwen3:8b
Embeddings:    nomic-embed-text or bge-m3
```

### Recommended Ollama pulls

```bash
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull qwen3.5:4b
ollama pull gemma3:4b
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

Optional stronger embedding model:

```bash
ollama pull bge-m3
```

### Runtime behavior

```txt
Default mode: auto
Worker count: 2–3 per request
Judge: qwen3:8b
Best for: better reasoning, code review, planning, RAG, local research
Can use: all mode for testing
Avoid: expecting frontier cloud model performance
```

### Estimated effective score

```txt
Single small model:                 350–550
32 GB Local Fusion Runtime:          650–800
Well-tuned 32 GB setup with RAG:     750–850
```

---

## Profile Comparison

| Profile      |   RAM | Best for                                                      | Worker count | Judge model  | Estimated effective score |
| ------------ | ----: | ------------------------------------------------------------- | -----------: | ------------ | ------------------------: |
| Lite         | 16 GB | Simple local AI, writing, summaries, basic code, planning     |          1–2 | `qwen3.5:4b` |                   550–700 |
| Strong Local | 32 GB | Better reasoning, coding, RAG, local research, all-mode tests |          2–3 | `qwen3:8b`   |                   650–850 |

---

## Important Note About Effective Score

The effective score is an estimate of the whole compound system, not a verified benchmark.

The system can perform better than one small model because it uses:

```txt
1. Task routing
2. Multiple model perspectives
3. Critic review
4. Judge synthesis
5. Optional local RAG
6. Better prompts per model role
```

Do not market these numbers as official LLM Stats scores until the project includes a real benchmark suite.

Recommended language:

```txt
Estimated effective capability: 550–700 on 16 GB RAM.
Estimated effective capability: 650–850 on 32 GB RAM.
Official benchmark score: not yet measured.
```
