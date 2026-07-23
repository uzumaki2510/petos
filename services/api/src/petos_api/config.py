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

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
