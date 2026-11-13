import importlib.util
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

_MODULE_PATH = (
    Path(__file__).resolve().parents[6]
    / "gen_epix/casedb/repositories/sa_alembic/versions/"
    "31d021dcf0ae_refactored_case_date_to_timed_at.py"
)
_MODULE_SPEC = importlib.util.spec_from_file_location(
    "case_date_migration", _MODULE_PATH
)
assert _MODULE_SPEC is not None and _MODULE_SPEC.loader is not None
migration = importlib.util.module_from_spec(_MODULE_SPEC)
_MODULE_SPEC.loader.exec_module(migration)


def _run_migration(
    monkeypatch: pytest.MonkeyPatch,
    migration_function: Callable[[], None],
    source_column: str,
    target_column: str,
) -> list[datetime | None]:
    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        connection.exec_driver_sql('ATTACH DATABASE ":memory:" AS "case"')
        source_table = sa.Table(
            "case",
            sa.MetaData(),
            sa.Column(source_column, sa.DateTime(), nullable=True),
            schema="case",
        )
        source_table.create(connection)
        connection.execute(
            source_table.insert(),
            [
                {source_column: datetime(2024, 2, 3, 4, 5, 6)},
                {source_column: None},
            ],
        )
        operations = Operations(MigrationContext.configure(connection))
        monkeypatch.setattr(operations, "alter_column", lambda *args, **kwargs: None)
        monkeypatch.setattr(migration, "op", operations)

        migration_function()

        target_table = sa.table(
            "case",
            sa.column(target_column, sa.DateTime()),
            schema="case",
        )
        return list(
            connection.execute(
                sa.select(target_table.c[target_column]).order_by(sa.text("rowid"))
            ).scalars()
        )


def test_upgrade_preserves_case_date_values(monkeypatch) -> None:
    assert _run_migration(monkeypatch, migration.upgrade, "case_date", "timed_at") == [
        datetime(2024, 2, 3, 4, 5, 6),
        None,
    ]


def test_downgrade_preserves_timed_at_values(monkeypatch) -> None:
    assert _run_migration(
        monkeypatch, migration.downgrade, "timed_at", "case_date"
    ) == [datetime(2024, 2, 3, 4, 5, 6), None]
