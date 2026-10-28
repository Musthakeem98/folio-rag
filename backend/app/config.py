from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FOLIO_", env_file=".env", extra="ignore")

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Storage
    data_dir: Path = Path("/data")
    models_dir: Path = Path("/models")
    store_backend: str = "lancedb"
    lancedb_path: Path = Path("/data/lancedb")

    # Embeddings
    embed_model: str = "BAAI/bge-m3"
    embed_device: str = "cpu"

    # Reranker
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_top_k: int = 5

    # LLM
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:7b-instruct"
    ollama_host: str = "http://ollama:11434"

    # Docling (document parsing service)
    docling_host: str = "http://docling:5001"


@lru_cache
def get_settings() -> Settings:
    return Settings()
