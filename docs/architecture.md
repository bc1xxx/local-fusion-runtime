# Architecture

```
User Prompt
     │
     ▼
┌──────────┐    ┌──────────────┐
│  Router   │───▶│  Classify    │
│ (llama3.2 │    │  mode:       │
│  :3b)     │    │  general /   │
└──────────┘    │  reasoning /  │
                │  code /       │
                │  writing      │
                └──────┬───────┘
                       │
                       ▼
┌──────────────────────────────────┐
│         Worker Models           │
│                                 │
│  ┌──────────┐ ┌──────────┐     │
│  │ phi4-mini│ │ qwen3.5  │     │
│  │          │ │ :4b      │     │
│  └──────────┘ └──────────┘     │
│  ┌──────────┐ ┌──────────┐     │
│  │ gemma3   │ │ llama3.2 │     │
│  │ :4b      │ │ :3b      │     │
│  └──────────┘ └──────────┘     │
│         (async parallel)       │
└──────────────┬─────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│           Critic                │
│  (phi4-mini)                     │
│  • Find incorrect claims        │
│  • Find missing details         │
│  • Find contradictions          │
│  • Find weak logic              │
│  • Suggest strongest ideas      │
└──────────────┬──────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│           Judge                 │
│  (qwen3.5:4b)                    │
│  • Merge strongest outputs      │
│  • Remove unsupported claims    │
│  • Return final answer          │
└──────────────┬──────────────────┘
               │
               ▼
         Final Answer
```

## Flow

1. **Router** classifies the user prompt into one of four categories.
2. **Workers** are selected based on the mode and called in parallel via async HTTP.
3. **Critic** reviews all worker outputs for quality, accuracy, and consistency.
4. **Judge** synthesizes the best content into a single final answer.

All inference runs locally through Ollama. No data leaves your machine.
