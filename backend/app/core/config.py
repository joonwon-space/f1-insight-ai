from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "f1_insight"

    # Elasticsearch
    elasticsearch_url: str = "http://localhost:9200"

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: str = "ollama"
    llm_model: str = "llama3.1:8b"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 1024

    # Unsplash
    unsplash_access_key: str = ""

    # Alerts
    discord_webhook_url: str = ""
    slack_webhook_url: str = ""

    # Logging
    json_logs: bool = True

    # FastF1
    fastf1_cache_dir: str = "/tmp/fastf1_cache"

    # Transcript
    transcript_download_dir: str = "/tmp/f1_transcripts"

    # FastAPI
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()


def get_settings() -> Settings:
    """Return the global settings instance."""
    return settings
