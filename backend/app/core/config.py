"""Configurazione letta dalle variabili d'ambiente (vedi .env.example)."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_JWT_SECRET = "cambia-questo-segreto-in-produzione"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://trader:trader@db:5432/trader"

    # Ogni quanti secondi il motore controlla se una candela si è chiusa.
    engine_tick_seconds: int = 60

    # Firma dei token di accesso. In produzione va sempre cambiata.
    jwt_secret: SecretStr = SecretStr(_DEFAULT_JWT_SECRET)
    jwt_expire_minutes: int = 60

    # Chiave Fernet che cifra le chiavi API e dei wallet nel database.
    # Si genera con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    secrets_key: SecretStr | None = None

    # Se vero, le tracce OpenTelemetry vengono stampate sulla console.
    otel_console: bool = False

    @model_validator(mode="after")
    def _production_needs_real_secrets(self) -> "Settings":
        if self.app_env == "production":
            secret = self.jwt_secret.get_secret_value()
            if secret == _DEFAULT_JWT_SECRET or len(secret) < 32:
                raise ValueError("In produzione JWT_SECRET va impostato, lungo almeno 32 caratteri")
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
