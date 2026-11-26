from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazione letta dalle variabili d'ambiente (vedi .env.example)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg://trader:trader@db:5432/trader"
    # Ogni quanti secondi il motore esegue un ciclo dei bot.
    engine_tick_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
