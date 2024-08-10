from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    CHAT_SEARCH_KWARG_K: int = 3
    CHAT_DOC_SPLIT_SIZE: int = 3000
    EMBEDDING_DIMENSION: int = 768
    CHAT_SEARCH_KWARG_SCORE_THRESHOLD: float = 0.7
    CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD: float = 0.10

    ANTHROPIC_MODEL_NAME: str = os.getenv(
        "ANTHROPIC_MODEL_NAME", "claude-3-5-sonnet@20240620"
    )
    ANTHROPIC_REGION: str = os.getenv("GCP_REGION", "us-east-1")
    FILE_INGESTION_SERVICE_URL: str = os.getenv("FILE_INGESTION_SERVICE_URL")


settings = Settings()
