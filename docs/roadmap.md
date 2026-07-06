# Roadmap

## MVP (v0.1.0) ✓

- [x] Local compound-AI pipeline (router → workers → critic → judge)
- [x] FastAPI server with four endpoints
- [x] Async parallel model calls
- [x] Prompt classification routing
- [x] OpenAI-compatible `/v1/chat/completions`
- [x] Critic and judge passes for quality
- [x] Error handling for missing models and Ollama downtime

## Upcoming

### Local RAG
- Add document ingestion (PDF, TXT, Markdown)
- Local embeddings with sentence-transformers
- Retrieval-augmented generation over user documents
- Support ChromaDB or LanceDB for vector storage

### Memory
- Conversation history persistence
- Session-based context management
- SQLite-based storage for chat logs

### Model Benchmarking
- Track per-model latency and token usage
- Compare model quality on different task types
- Auto-suggest optimal model combinations

### Web UI
- Simple chat interface (Streamlit or Gradio)
- Model configuration panel
- Real-time latency and model usage display
- Raw output inspector for debugging

### Streaming Responses
- Server-Sent Events (SSE) support
- Stream each worker output as it completes
- Real-time critic and judge progress

### Docker Support
- Dockerfile for the fusion runtime
- docker-compose with Ollama service
- One-command startup

### Plugin / Tool Support
- Allow user-defined tool functions
- Web search, calculator, code execution plugins
- Plugin marketplace concept for community contributions

### Better OpenAI Compatibility
- Support streaming in `/v1/chat/completions`
- Support function/tool calling format
- Token usage reporting
- Multi-turn conversation awareness

## How to Contribute

Pick any item from the roadmap, open an issue to discuss your approach, and submit a PR. See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
