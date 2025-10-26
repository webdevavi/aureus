from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = Field("development", alias="ENV")
    log_level: str = Field("info", alias="LOG_LEVEL")

    postgres_host: str = Field(..., alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(..., alias="POSTGRES_DB")
    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: str = Field(..., alias="POSTGRES_PASSWORD")

    minio_endpoint: str = Field(..., alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(..., alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field("reports", alias="MINIO_BUCKET")
    minio_region: str = Field("us-east-1", alias="MINIO_REGION")
    minio_secure: bool = Field(False, alias="MINIO_SECURE")

    rabbitmq_url: str = Field(..., alias="RABBITMQ_URL")
    rabbitmq_exchange: str = Field(..., alias="RABBITMQ_EXCHANGE")

    cors_origin: str = Field(..., alias="CORS_ORIGIN")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
