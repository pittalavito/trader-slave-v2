import asyncio

from sqlalchemy import select

from app.core.clock import SimulatedClock
from app.core.container import Container
from app.engine.commands import CommandKind, CommandListener, CommandStatus, EngineCommand, send_command


async def test_command_reaches_listener_via_notify(container: Container, clock: SimulatedClock) -> None:
    received: list[tuple[CommandKind, dict[str, object]]] = []
    handled = asyncio.Event()

    async def handler(command: EngineCommand) -> None:
        received.append((command.kind, command.payload))
        handled.set()

    listener = CommandListener(container.session_factory, container.settings.database_url, handler, clock)
    stop = asyncio.Event()
    task = asyncio.create_task(listener.run(stop))
    await asyncio.sleep(0.5)  # il listener è in ascolto

    async with container.session_factory() as session, session.begin():
        command_id = await send_command(session, CommandKind.STOP, {"portfolio_id": 1})

    await asyncio.wait_for(handled.wait(), timeout=5)
    stop.set()
    await asyncio.wait_for(task, timeout=5)

    assert received == [(CommandKind.STOP, {"portfolio_id": 1})]
    async with container.session_factory() as session:
        saved = await session.scalar(select(EngineCommand).where(EngineCommand.id == command_id))
    assert saved is not None
    assert saved.status is CommandStatus.DONE
    assert saved.processed_at == clock.now()


async def test_failed_command_is_marked_failed(container: Container, clock: SimulatedClock) -> None:
    async def handler(command: EngineCommand) -> None:
        raise RuntimeError("bot inesistente")

    async with container.session_factory() as session, session.begin():
        await send_command(session, CommandKind.START)

    listener = CommandListener(container.session_factory, container.settings.database_url, handler, clock)
    assert await listener.process_pending() == 1

    async with container.session_factory() as session:
        saved = (await session.scalars(select(EngineCommand))).one()
    assert saved.status is CommandStatus.FAILED
    assert saved.error == "bot inesistente"
