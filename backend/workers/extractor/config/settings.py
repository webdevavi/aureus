from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = Field("development", alias="ENV")
    log_level: str = Field("info", alias="LOG_LEVEL")

    rabbitmq_url: str = Field(..., alias="RABBITMQ_URL")
    rabbitmq_exchange: str = Field(..., alias="RABBITMQ_EXCHANGE")

    api_base_url: str = Field(..., alias="API_BASE_URL")

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")

    max_workers: int = Field(2, alias="MAX_WORKERS")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
