from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    local_fusion_provider: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    lmstudio_base_url: str = "http://localhost:1234/v1"

    local_fusion_profile: str = "lite"

    router_model: str = "llama3.2:3b"
    reasoner_model: str = "phi4-mini"
    coder_model: str = "qwen3.5:4b"
    general_model: str = "gemma3:4b"
    critic_model: str = "phi4-mini"
    judge_model: str = "qwen3.5:4b"
    judge_model_strong: str = "qwen3:8b"

    lmstudio_router_model: str = ""
    lmstudio_reasoner_model: str = ""
    lmstudio_coder_model: str = ""
    lmstudio_general_model: str = ""
    lmstudio_critic_model: str = ""
    lmstudio_judge_model: str = ""

    request_timeout: int = 180

    model_config = {"env_file": ".env", "extra": "ignore"}

    def get_model_for_role(self, role: str) -> str:
        field = f"{role}_model"
        override = ""
        if self.local_fusion_provider == "lmstudio":
            override = getattr(self, f"lmstudio_{role}_model", None) or ""
        return override or (getattr(self, field, "") or "")


settings = Settings()
