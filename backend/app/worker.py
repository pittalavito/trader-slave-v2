"""Processo del motore, separato dall'API e sempre acceso.

Per ora ascolta i comandi dall'API e registra un battito a ogni ciclo.
Dalla fase "Simulazione 24 ore su 24" eseguirà le strategie attive
alla chiusura di ogni candela.
"""

import asyncio
import contextlib
import signal

from app.core.config import get_settings
from app.core.container import Container, build_container
from app.core.observability import configure_observability, get_logger
from app.engine.commands import CommandListener, EngineCommand

log = get_logger("worker")


async def handle_command(command: EngineCommand) -> None:
    # I bot arrivano nelle prossime fasi: per ora il comando viene solo registrato.
    log.info(
        "engine.command_received", command_id=command.id, kind=command.kind.value, payload=command.payload
    )


async def heartbeat(container: Container, stop: asyncio.Event) -> None:
    tick = container.settings.engine_tick_seconds
    while not stop.is_set():
        log.info("engine.tick", active_bots=0, at=container.clock.now().isoformat())
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=tick)


async def main() -> None:
    settings = get_settings()
    configure_observability(
        level=settings.log_level, json_logs=settings.is_production, otel_console=settings.otel_console
    )
    container = build_container(settings)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)

    listener = CommandListener(
        container.session_factory, settings.database_url, handle_command, container.clock
    )
    log.info("engine.started", tick_seconds=settings.engine_tick_seconds)
    try:
        await asyncio.gather(listener.run(stop), heartbeat(container, stop))
    finally:
        await container.close()
        log.info("engine.stopped")


if __name__ == "__main__":
    asyncio.run(main())
