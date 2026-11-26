from logging.config import fileConfig

from sqlalchemy.engine import Connection

from alembic import context
from app.core.config import get_settings
from app.core.runtime import run_async
from app.db.models import Base
from app.db.session import create_engine

# What is Alembic?
# Alembic keeps the database tables in sync with the code. Every change to the
# tables (new table, new column, new index...) is a small Python file in
# `alembic/versions/`, numbered in order, with an `upgrade()` and a `downgrade()`.
# The database remembers the last file it ran (table `alembic_version`), so
# `alembic upgrade head` only runs the new ones. This way local, CI and server
# databases all end up with exactly the same tables.
#
# This file (env.py) is run by Alembic on every command: it tells Alembic how to
# connect to our database and where our models are (`Base.metadata`), so that
# `alembic revision --autogenerate` can write a new migration by comparing the
# models with the real tables.

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    # A URL passed from code (e.g. by the tests) wins over the one in .env.
    url = config.attributes.get("database_url")
    return url if isinstance(url, str) else get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(url=_database_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def _run(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_engine(_database_url())
    async with engine.connect() as connection:
        await connection.run_sync(_run)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_async(run_migrations_online())
