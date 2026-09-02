# Importing Dependencies.
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
        This class automatically reads the .env file and maps the variables to
        these Python attributes. It also validates that the data types are correct.
    """
    # Application Config
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_log_level: str = "INFO"
    api_key: str

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "caso_chunks"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str

    # Postgres
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "caso_db"
    postgres_user: str = "caso_user"
    postgres_password: str
    database_url: str

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str
    redis_cache_ttl_seconds: int = 3600

    # LLM Settings
    llm_backend: str = "huggingface"
    llm_model_name: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    llm_quantization: str = "4bit"
    llm_max_new_tokens: int = 1024
    llm_temperature: float = 0.1
    llm_top_p: float = 0.9
    llm_device: str = "auto"

    embedding_model_name: str = "BAAI/bge-m3"
    embedding_batch_sizes: int = 32
    embedding_device: str = "cpu"

    reranker_model_name: str = "BAAI/bge-reranker-v2-m3"
    reranker_device: str = "cpu"
    
    hf_token: Optional[str] = None
    hf_cache_dir: str = "./data/models"

    # Tells pydantic to read from the .env file located one level-up from backend folder.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encodding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    """
        This function creates the Settings object once, and caches it in memory.
        Whenever any file in our app needs a password or port number, it just calls:
        settings = get_settings()
    """
    return Settings()