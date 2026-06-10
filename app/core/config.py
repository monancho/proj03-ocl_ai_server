from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "ai-server"
    version: str = "0.1.0"
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    ai_server_api_key: str | None = Field(default=None, alias="AI_SERVER_API_KEY")
    ai_text_model: str = Field(default="gpt-5.4-mini", alias="AI_TEXT_MODEL")
    image_moderation_model: str = Field(
        default="omni-moderation-latest", alias="IMAGE_MODERATION_MODEL"
    )
    max_source_chars: int = Field(default=12000, alias="MAX_SOURCE_CHARS")
    max_image_size_mb: int = Field(default=5, alias="MAX_IMAGE_SIZE_MB")
    request_timeout_seconds: int = Field(default=15, alias="REQUEST_TIMEOUT_SECONDS")
    ai_daily_request_limit: int = Field(default=1000, alias="AI_DAILY_REQUEST_LIMIT")
    ai_rate_limit_per_minute: int = Field(default=120, alias="AI_RATE_LIMIT_PER_MINUTE")
    log_level: str = Field(default="info", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()
