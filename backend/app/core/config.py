"""Settings read from environment variables (see .env.example)."""

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

    # How often (seconds) the engine checks whether a candle has closed.
    engine_tick_seconds: int = 60

    # Signing key of access tokens. Must always be changed in production.
    jwt_secret: SecretStr = SecretStr(_DEFAULT_JWT_SECRET)
    jwt_expire_minutes: int = 60

    # Fernet key that encrypts API and wallet keys in the database.
    # Generate it with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    secrets_key: SecretStr | None = None

    # If true, OpenTelemetry spans are printed to the console.
    otel_console: bool = False

    @model_validator(mode="after")
    def _production_needs_real_secrets(self) -> "Settings":
        if self.app_env == "production":
            secret = self.jwt_secret.get_secret_value()
            if secret == _DEFAULT_JWT_SECRET or len(secret) < 32:
                raise ValueError("In production JWT_SECRET must be set and at least 32 characters long")
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
