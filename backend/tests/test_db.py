from sqlalchemy import text

from app.core.container import Container


async def test_timescaledb_extension_is_installed(container: Container) -> None:
    async with container.db_engine.connect() as conn:
        version = await conn.scalar(text("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'"))
    assert version is not None


async def test_base_tables_exist(container: Container) -> None:
    async with container.db_engine.connect() as conn:
        rows = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"))
        tables = {r[0] for r in rows}
    assert {"users", "engine_commands", "alembic_version"} <= tables
