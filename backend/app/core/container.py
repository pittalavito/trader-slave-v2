"""Assemblaggio dei componenti.

È l'unico punto che decide quali implementazioni usare: API e motore prendono
i componenti veri da qui; backtest e test ne costruiscono uno con orologio e
client simulati. Le classi ricevono le dipendenze nel costruttore e non sanno
da dove arrivano.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.clock import Clock, SystemClock
from app.core.config import Settings
from app.core.security import PasswordHasher, SecretBox, TokenService
from app.db.session import create_engine, create_session_factory


@dataclass
class Container:
    settings: Settings
    clock: Clock
    db_engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    passwords: PasswordHasher = field(default_factory=PasswordHasher)
    tokens: TokenService = field(init=False)
    secrets: SecretBox = field(init=False)

    def __post_init__(self) -> None:
        self.tokens = TokenService(
            self.settings.jwt_secret.get_secret_value(), self.settings.jwt_expire_minutes, self.clock
        )
        key = self.settings.secrets_key
        self.secrets = SecretBox(key.get_secret_value() if key else None)

    async def close(self) -> None:
        await self.db_engine.dispose()


def build_container(settings: Settings, clock: Clock | None = None) -> Container:
    engine = create_engine(settings.database_url)
    return Container(
        settings=settings,
        clock=clock or SystemClock(),
        db_engine=engine,
        session_factory=create_session_factory(engine),
    )
