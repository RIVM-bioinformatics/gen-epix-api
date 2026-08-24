"""Alembic environment for omopdb."""

from __future__ import annotations

import os

from alembic import context
import sqlalchemy as sa
from sqlalchemy import engine_from_config, pool

from gen_epix.omopdb.repositories.sa_alembic.metadata import target_metadata

config = context.config


def _compare_nullable(
    context: object,
    inspected_column: object,
    metadata_column: object,
    inspected_nullable: bool,
    metadata_nullable: bool,
) -> bool | None:
    """Ignore SQL Server's mandatory NOT NULL primary-key invariant."""
    if getattr(inspected_column, "primary_key", False) and metadata_nullable:
        return False
    return None


def _configure_url() -> None:
    url = context.get_x_argument(as_dictionary=True).get("url") or os.getenv(
        "ALEMBIC_URL"
    )
    if not url:
        raise ValueError("Provide the database URL with -x url=... or ALEMBIC_URL")
    config.set_main_option("sqlalchemy.url", url)


def run_migrations_offline() -> None:
    _configure_url()
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        include_schemas=True,
        compare_type=True,
        compare_server_default=False,
        compare_nullable=_compare_nullable,
        version_table_schema="alembic",
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    _configure_url()
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        if connection.dialect.name == "mssql":
            connection.execute(
                sa.text(
                    "IF SCHEMA_ID('alembic') IS NULL EXEC('CREATE SCHEMA alembic')"
                )
            )
            connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            compare_type=True,
            compare_server_default=False,
            compare_nullable=_compare_nullable,
            version_table_schema="alembic",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
