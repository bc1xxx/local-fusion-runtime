from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    profile: str = "lite"
    ollama_url: str = "http://localhost:11434"
    ollama_timeout: int = 60

    router_model: str = "llama3.2:3b"
    reasoner_model: str = "phi4-mini"
    coder_model: str = "qwen3.5:4b"
    general_model: str = "gemma3:4b"
    critic_model: str = "phi4-mini"
    judge_model: str = "qwen3.5:4b"
    judge_model_strong: str = "qwen3:8b"

    model_config = {"env_prefix": "LFR_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
