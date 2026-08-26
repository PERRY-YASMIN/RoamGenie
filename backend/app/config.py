from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RoamGenie"
    app_env: str = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Database Configuration
    database_url: str | None = None
    local_database_url: str | None = None
    database_env: Literal["supabase", "local"] = "supabase"
    db_connect_timeout_seconds: int = 5

    # Supabase Secrets (Backend only)
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    # Security & JWT Authentication
    secret_key: str = "roamgenie-insecure-dev-secret-key-change-in-prod-2026"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # AI & External Providers
    ai_provider: str = "mock"  # "mock", "gemini", "openai", "groq"
    ai_api_key: str | None = None
    ai_model: str | None = None
    ai_timeout_seconds: int = 15
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    groq_api_key: str | None = None

    # Weather Integration (Open-Meteo)
    weather_provider: str = "open-meteo"  # "open-meteo", "mock"
    weather_api_key: str | None = None
    open_meteo_base_url: str = "https://api.open-meteo.com/v1"
    open_meteo_geocoding_url: str = "https://geocoding-api.open-meteo.com/v1"
    weather_timeout_seconds: int = 5

    # Google Maps & Places API Integration
    google_maps_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [value.strip() for value in self.cors_origins.split(",") if value.strip()]

    @property
    def effective_database_url(self) -> str | None:
        """Select one database explicitly; auto-normalizes driver prefix to psycopg."""
        raw_url = self.local_database_url if self.database_env == "local" else self.database_url
        if not raw_url:
            return None
        # Auto-normalize legacy postgres:// or standard postgresql:// to postgresql+psycopg://
        if raw_url.startswith("postgres://"):
            return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
        if raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+"):
            return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return raw_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
