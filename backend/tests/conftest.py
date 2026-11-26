"""Shared fixtures. Database tests use a real Postgres with TimescaleDB.

Locally: `docker compose up -d db`, then `uv run pytest`.
Override the URL with TEST_DATABASE_URL.
"""

import os
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime

import pytest
from alembic.config import Config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from alembic import command
from app.core.clock import SimulatedClock
from app.core.config import Settings
from app.core.container import Container, build_container
from app.main import create_app

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg://trader:trader@localhost:5432/trader_test")
START = datetime(2026, 1, 1, tzinfo=UTC)


def _alembic_config() -> Config:
    cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    cfg.attributes["database_url"] = TEST_DATABASE_URL
    return cfg


@pytest.fixture(scope="session")
def migrated_db() -> Iterator[str]:
    cfg = _alembic_config()
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    yield TEST_DATABASE_URL


@pytest.fixture
def settings(migrated_db: str) -> Settings:
    return Settings(
        app_env="test",
        database_url=migrated_db,
        jwt_secret="segreto-di-test-lungo-almeno-32-caratteri",
        secrets_key=None,
    )


@pytest.fixture
def clock() -> SimulatedClock:
    return SimulatedClock(START)


@pytest.fixture
async def container(settings: Settings, clock: SimulatedClock) -> AsyncIterator[Container]:
    c = build_container(settings, clock=clock)
    async with c.db_engine.begin() as conn:
        await conn.execute(text("TRUNCATE users, engine_commands RESTART IDENTITY"))
    yield c
    await c.close()


@pytest.fixture
def app(settings: Settings, container: Container) -> FastAPI:
    application = create_app(settings, container)
    application.state.container = container
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
