from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    app_version: str = "0.1.0"
    environment: str = "development"
    api_cors_origins: List[str] = ["http://localhost:3000"]
    database_url: str = (
        "postgresql+asyncpg://petos:petos_dev_password@localhost:5432/petos_db"
    )
    redis_url: str = "redis://:petos_redis_password@localhost:6379/0"
    log_level: str = "info"

    APP_ORIGIN: str = "http://localhost:3000"
    TRUSTED_ORIGINS: List[str] = ["http://localhost:3000"]
    BFF_INTERNAL_SECRET: str = "default_bff_secret_for_local_dev"
    RATE_LIMIT_HMAC_SECRET: str = "default_hmac_secret_for_local_dev"
    SESSION_COOKIE_NAME: str = "petos_session"
    SESSION_IDLE_TTL_SECONDS: int = 604800
    SESSION_ABSOLUTE_TTL_SECONDS: int = 2592000
    SESSION_LAST_SEEN_UPDATE_INTERVAL_SECONDS: int = 300
    COOKIE_SECURE: bool = False

    LOGIN_RATE_LIMIT_IP_MAX: int = 20
    LOGIN_RATE_LIMIT_IDENTITY_MAX: int = 5
    LOGIN_RATE_LIMIT_COMBINED_MAX: int = 5
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 900

    REGISTRATION_RATE_LIMIT_IP_MAX: int = 10
    REGISTRATION_RATE_LIMIT_IDENTITY_MAX: int = 3
    REGISTRATION_RATE_LIMIT_WINDOW_SECONDS: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
