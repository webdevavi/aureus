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

    s3_endpoint: str = Field(..., alias="S3_ENDPOINT")
    s3_access_key: str = Field(..., alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(..., alias="S3_SECRET_KEY")
    s3_bucket: str = Field("reports", alias="S3_BUCKET")
    s3_region: str = Field("us-east-1", alias="S3_REGION")
    s3_secure: bool = Field(False, alias="S3_SECURE")

    rabbitmq_url: str = Field(..., alias="RABBITMQ_URL")
    rabbitmq_exchange: str = Field(..., alias="RABBITMQ_EXCHANGE")

    cors_origins: str = Field(..., alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
