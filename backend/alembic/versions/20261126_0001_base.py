"""Base: TimescaleDB extension, users and engine commands.

Revision ID: 0001
Revises:
Create Date: 2026-11-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

user_role = postgresql.ENUM("admin", "user", "observer", name="user_role", create_type=False)
command_kind = postgresql.ENUM("start", "stop", "emergency_stop", "reload", name="engine_command_kind", create_type=False)
command_status = postgresql.ENUM("pending", "done", "failed", name="engine_command_status", create_type=False)


def upgrade() -> None:
    # TimescaleDB is needed from the "Market data" phase on, for candles.
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")

    user_role.create(op.get_bind(), checkfirst=True)
    command_kind.create(op.get_bind(), checkfirst=True)
    command_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "engine_commands",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", command_kind, nullable=False),
        sa.Column("payload", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column("status", command_status, server_default="pending", nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_engine_commands"),
    )
    op.create_index("ix_engine_commands_status", "engine_commands", ["status"])


def downgrade() -> None:
    op.drop_index("ix_engine_commands_status", table_name="engine_commands")
    op.drop_table("engine_commands")
    op.drop_table("users")
    command_status.drop(op.get_bind(), checkfirst=True)
    command_kind.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
