"""Comandi dall'API al motore, passando da Postgres.

L'API scrive il comando nella tabella `engine_commands` e manda un
`NOTIFY engine_commands`; il motore è in ascolto (`LISTEN`) e lo esegue subito.
Il comando resta salvato: se il motore è spento, lo trova al riavvio.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime
from enum import StrEnum
from typing import Any

import psycopg
from sqlalchemy import DateTime, Enum, String, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from app.core.clock import Clock
from app.core.observability import correlation_scope, get_logger, observed
from app.core.types import CommandId
from app.db.base import Base, TimestampMixin

CHANNEL = "engine_commands"
log = get_logger(__name__)


class CommandKind(StrEnum):
    START = "start"
    STOP = "stop"
    EMERGENCY_STOP = "emergency_stop"
    RELOAD = "reload"


class CommandStatus(StrEnum):
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"


def _enum_values(enum: type[StrEnum]) -> list[str]:
    return [member.value for member in enum]


class EngineCommand(TimestampMixin, Base):
    __tablename__ = "engine_commands"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[CommandKind] = mapped_column(
        Enum(CommandKind, name="engine_command_kind", values_callable=_enum_values)
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")
    status: Mapped[CommandStatus] = mapped_column(
        Enum(CommandStatus, name="engine_command_status", values_callable=_enum_values),
        default=CommandStatus.PENDING,
        server_default=CommandStatus.PENDING.value,
        index=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(String(2000))


@observed(name="engine.send_command")
async def send_command(
    session: AsyncSession, kind: CommandKind, payload: dict[str, Any] | None = None
) -> CommandId:
    """Salva un comando e sveglia il motore. Va chiamato dentro una transazione dell'API."""
    command = EngineCommand(kind=kind, payload=payload or {})
    session.add(command)
    await session.flush()
    # NOTIFY parte solo al commit: il motore non vede mai un comando non ancora salvato.
    await session.execute(
        text("SELECT pg_notify(:channel, :id)"), {"channel": CHANNEL, "id": str(command.id)}
    )
    return CommandId(command.id)


CommandHandler = Callable[[EngineCommand], Awaitable[None]]


class CommandListener:
    """Il lato motore: ascolta i NOTIFY ed esegue i comandi in attesa, in ordine."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        database_url: str,
        handler: CommandHandler,
        clock: Clock,
    ) -> None:
        self._sessions = session_factory
        # psycopg vuole l'URL senza il prefisso del driver SQLAlchemy.
        self._dsn = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
        self._handler = handler
        self._clock = clock

    @observed(name="engine.process_pending_commands")
    async def process_pending(self) -> int:
        """Esegue tutti i comandi in attesa. Restituisce quanti ne ha eseguiti."""
        processed = 0
        while True:
            async with self._sessions() as session, session.begin():
                command = await session.scalar(
                    select(EngineCommand)
                    .where(EngineCommand.status == CommandStatus.PENDING)
                    .order_by(EngineCommand.id)
                    .limit(1)
                    .with_for_update(skip_locked=True)
                )
                if command is None:
                    return processed
                with correlation_scope(f"command-{command.id}", command_kind=command.kind.value):
                    try:
                        await self._handler(command)
                        command.status = CommandStatus.DONE
                    except Exception as exc:
                        log.error("engine.command_failed", command_id=command.id, exc_info=exc)
                        command.status = CommandStatus.FAILED
                        command.error = str(exc)[:2000]
                    command.processed_at = self._clock.now()
                processed += 1

    async def run(self, stop: asyncio.Event) -> None:
        """Ascolta finché `stop` non viene impostato."""
        async with await psycopg.AsyncConnection.connect(self._dsn, autocommit=True) as conn:
            await conn.execute(f"LISTEN {CHANNEL}")
            log.info("engine.listening", channel=CHANNEL)
            # Comandi arrivati mentre il motore era spento.
            await self.process_pending()
            while not stop.is_set():
                async for _ in conn.notifies(timeout=1.0, stop_after=1):
                    await self.process_pending()
