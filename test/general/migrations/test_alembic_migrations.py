"""Verify that Alembic revisions cover the SQLAlchemy database models."""

from __future__ import annotations

import ast
import importlib
from collections.abc import Iterable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects import postgresql

from gen_epix.casedb.repositories.sa_alembic.metadata import (
    target_metadata as casedb_metadata,
)
from gen_epix.commondb.repositories.sa_alembic.metadata import (
    target_metadata as commondb_metadata,
)
from gen_epix.omopdb.repositories.sa_alembic.metadata import (
    target_metadata as omopdb_metadata,
)
from gen_epix.seqdb.repositories.sa_alembic.metadata import (
    target_metadata as seqdb_metadata,
)

PROJECT_ROOT = Path(__file__).parents[3]

MIGRATION_TARGETS = {
    "commondb": commondb_metadata,
    "casedb": casedb_metadata,
    "seqdb": seqdb_metadata,
    "omopdb": omopdb_metadata,
}


def _migration_tables(
    revision_files: Iterable[Path],
) -> dict[tuple[str | None, str], set[str]]:
    """Collect table and column names created by all revisions for one service."""
    tables: dict[tuple[str | None, str], set[str]] = {}
    for revision_file in revision_files:
        tree = ast.parse(revision_file.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(
                node.func, ast.Attribute
            ):
                continue
            if not isinstance(node.func.value, ast.Name) or node.func.value.id != "op":
                continue

            # Handle op.create_table(...) calls
            if node.func.attr == "create_table" and node.args:
                if not isinstance(node.args[0], ast.Constant) or not isinstance(
                    node.args[0].value, str
                ):
                    continue
                schema = next(
                    (
                        keyword.value.value
                        for keyword in node.keywords
                        if keyword.arg == "schema"
                        and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                    ),
                    None,
                )
                columns = {
                    argument.args[0].value
                    for argument in node.args[1:]
                    if isinstance(argument, ast.Call)
                    and isinstance(argument.func, ast.Attribute)
                    and argument.func.attr == "Column"
                    and argument.args
                    and isinstance(argument.args[0], ast.Constant)
                    and isinstance(argument.args[0].value, str)
                }
                table_key = (schema, node.args[0].value)
                if table_key not in tables:
                    tables[table_key] = set()
                tables[table_key].update(columns)

            # Handle op.add_column(...) calls
            elif node.func.attr == "add_column" and len(node.args) >= 2:
                if not isinstance(node.args[0], ast.Constant) or not isinstance(
                    node.args[0].value, str
                ):
                    continue
                table_name = node.args[0].value
                schema = next(
                    (
                        keyword.value.value
                        for keyword in node.keywords
                        if keyword.arg == "schema"
                        and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                    ),
                    None,
                )
                # Extract column name from sa.Column() call (second argument)
                column_node = node.args[1]
                if (
                    isinstance(column_node, ast.Call)
                    and isinstance(column_node.func, ast.Attribute)
                    and column_node.func.attr == "Column"
                    and column_node.args
                    and isinstance(column_node.args[0], ast.Constant)
                    and isinstance(column_node.args[0].value, str)
                ):
                    column_name = column_node.args[0].value
                    table_key = (schema, table_name)
                    if table_key not in tables:
                        tables[table_key] = set()
                    tables[table_key].add(column_name)

    return tables


@pytest.mark.parametrize("service", MIGRATION_TARGETS)
def test_models_have_migration_operations(service: str) -> None:
    """Fail CI when a persistable model table or column has no revision DDL."""
    revision_files = sorted(
        (
            PROJECT_ROOT
            / "gen_epix"
            / service
            / "repositories"
            / "sa_alembic"
            / "versions"
        ).glob("*.py")
    )
    migration_tables = _migration_tables(revision_files)

    missing: list[str] = []
    for metadata in MIGRATION_TARGETS[service]:
        for table in metadata.sorted_tables:
            table_key = (table.schema, table.name)
            if table_key not in migration_tables:
                missing.append(f"table {table.fullname}")
                continue
            missing_columns = {
                column.name for column in table.columns
            } - migration_tables[table_key]
            missing.extend(
                f"column {table.fullname}.{column_name}"
                for column_name in sorted(missing_columns)
            )

    assert not missing, "Missing Alembic migration operations: " + ", ".join(missing)


def test_drop_legacy_seq_code_constraints() -> None:
    """The LSP-3497 revision drops constraints and legacy unique indexes safely."""
    migration = importlib.import_module(
        "gen_epix.seqdb.repositories.sa_alembic.versions."
        "6f2f4fb9b3d1_drop_legacy_code_constraints"
    )

    class Result:
        def __init__(self, value: bool) -> None:
            self.value = value

        def scalar(self) -> bool:
            return self.value

    class Connection:
        dialect = SimpleNamespace(name="mssql")

        def __init__(self) -> None:
            self.results = iter([True, False, True, False, False])

        def execute(self, statement: Any, params: dict[str, str]) -> Result:
            return Result(next(self.results))

    class Operations:
        def __init__(self) -> None:
            self.connection = Connection()
            self.dropped_constraints: list[tuple[str, str, str, str]] = []
            self.dropped_indexes: list[tuple[str, str, str]] = []

        def get_bind(self) -> Connection:
            return self.connection

        def drop_constraint(
            self, name: str, table_name: str, schema: str, type_: str
        ) -> None:
            self.dropped_constraints.append((name, table_name, schema, type_))

        def drop_index(self, name: str, table_name: str, schema: str) -> None:
            self.dropped_indexes.append((name, table_name, schema))

    operations = Operations()
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(migration, "op", operations)
    try:
        migration.upgrade()
    finally:
        monkeypatch.undo()

    assert operations.dropped_constraints == [
        ("uq_sample_code", "sample", "seq", "unique"),
    ]
    assert operations.dropped_indexes == [
        ("uq_read_set_code", "read_set", "seq"),
    ]


def test_seqdb_qc_migration_backfills_legacy_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preserve legacy results as machine QC and map NULL to PENDING."""
    migration = importlib.import_module(
        "gen_epix.seqdb.repositories.sa_alembic.versions."
        "274cb3c5bedf_split_qc_result_into_machine_and_human_"
    )
    engine = sa.create_engine("sqlite://")
    with engine.connect() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS seq")
        connection.exec_driver_sql(
            "CREATE TABLE seq.qc_result ("
            "id INTEGER PRIMARY KEY, qc_result VARCHAR, "
            "qc_result_machine VARCHAR, qc_result_human VARCHAR)"
        )
        connection.execute(
            sa.text(
                "INSERT INTO seq.qc_result (id, qc_result) " "VALUES (:id, :qc_result)"
            ),
            [
                {"id": 1, "qc_result": "FAIL"},
                {"id": 2, "qc_result": "PASS"},
                {"id": 3, "qc_result": None},
            ],
        )
        monkeypatch.setattr(
            migration,
            "op",
            Operations(MigrationContext.configure(connection)),
        )

        migration._backfill_qc_results("qc_result")

        rows = connection.execute(
            sa.text(
                "SELECT qc_result_machine, qc_result_human "
                "FROM seq.qc_result ORDER BY id"
            )
        ).all()

    engine.dispose()
    assert rows == [
        ("FAIL", "PENDING"),
        ("PASS", "PENDING"),
        ("PENDING", "PENDING"),
    ]


def test_seqdb_qc_migration_uses_enum_typed_backfill_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cast the fallback value to the PostgreSQL QC enum."""
    migration = importlib.import_module(
        "gen_epix.seqdb.repositories.sa_alembic.versions."
        "274cb3c5bedf_split_qc_result_into_machine_and_human_"
    )
    statements = []
    monkeypatch.setattr(migration, "op", SimpleNamespace(execute=statements.append))

    migration._backfill_qc_results("qc_result")

    compiled = str(statements[0].compile(dialect=postgresql.dialect()))
    assert "coalesce(" in compiled.lower()
    assert "CAST(" in compiled
    assert "AS qualitycontrolresult)" in compiled


def test_commondb_initial_migration_supports_sqlite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create and drop the CommonDB schema through SQLite migrations."""
    migration = importlib.import_module(
        "gen_epix.commondb.repositories.sa_alembic.versions."
        "b9c5e10bf42c_initial_schema"
    )
    engine = sa.create_engine("sqlite://")
    schema_map = {"abac": None, "organization": None, "system": None}
    with engine.connect() as connection:
        connection = connection.execution_options(schema_translate_map=schema_map)
        monkeypatch.setattr(
            migration,
            "op",
            Operations(MigrationContext.configure(connection)),
        )

        migration.upgrade()

        table_names = set(sa.inspect(connection).get_table_names())
        assert {"organization_admin_policy", "organization", "user", "outage"} <= (
            table_names
        )

        migration.downgrade()

        assert sa.inspect(connection).get_table_names() == []
    engine.dispose()
