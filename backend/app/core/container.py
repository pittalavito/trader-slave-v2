"""Component wiring (composition root).

The only place that decides which implementations to use: API and engine take
the real components from here; backtests and tests build one with a simulated
clock and clients. Classes receive their dependencies in the constructor and do
not know where they come from.
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
        self.tokens = TokenService(self.settings.jwt_secret.get_secret_value(), self.settings.jwt_expire_minutes, self.clock)
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
