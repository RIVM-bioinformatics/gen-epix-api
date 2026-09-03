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
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if not isinstance(node.func.value, ast.Name) or node.func.value.id != "op":
                continue
            if node.func.attr != "create_table" or not node.args:
                continue
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
            tables[(schema, node.args[0].value)] = columns
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
            missing_columns = (
                {column.name for column in table.columns} - migration_tables[table_key]
            )
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
