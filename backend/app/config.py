from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RoamGenie"
    app_env: str = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173"
    database_url: str | None = None
    local_database_url: str | None = None
    database_env: Literal["supabase", "local"] = "supabase"
    db_connect_timeout_seconds: int = 5
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    ai_provider: str = "mock"
    ai_timeout_seconds: int = 15

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [value.strip() for value in self.cors_origins.split(",") if value.strip()]

    @property
    def effective_database_url(self) -> str | None:
        """Select one database explicitly; never try to synchronize two targets."""
        return self.local_database_url if self.database_env == "local" else self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
