# Architecture

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

## Flow

1. **Router** classifies the user prompt into one of four categories (reasoning, code, or general).
2. **Worker Models** — selected by mode, called in parallel via async HTTP:
   - **Reasoning** (Phi-4 Mini 3.8B) — logic, math, analysis
   - **Coding** (Qwen3/Qwen3.5 4B) — code, APIs, debugging
   - **General** (Gemma 3 4B) — writing, summary, broad answers
3. **RAG / Embeddings** (nomic-embed-text / bge-m3) — retrieves context from local docs, code, and memory.
4. **Critic** reviews all worker outputs for weak logic, bad claims, and inconsistencies.
5. **Judge** — merges the strongest parts into a single coherent final answer.

All inference runs locally through Ollama. No data leaves your machine.
