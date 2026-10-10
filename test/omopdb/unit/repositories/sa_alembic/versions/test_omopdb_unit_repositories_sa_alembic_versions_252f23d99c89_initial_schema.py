"""Unit tests for the initial OMOP Alembic revision."""

from __future__ import annotations

import importlib
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

import pytest
import sqlalchemy as sa

initial_schema = importlib.import_module(
    "gen_epix.omopdb.repositories.sa_alembic.versions.252f23d99c89_initial_schema"
)


class _OperationsRecorder:
    def __init__(self, dialect_name: str) -> None:
        self.dialect_name = dialect_name
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def get_bind(self) -> SimpleNamespace:
        return SimpleNamespace(dialect=SimpleNamespace(name=self.dialect_name))

    def __getattr__(self, operation: str) -> Callable[..., None]:
        def record(*args: Any, **kwargs: Any) -> None:
            self.calls.append((operation, args, kwargs))

        return record


@pytest.mark.parametrize(
    ("dialect_name", "expected_schemas"),
    [
        ("mssql", ["abac", "organization", "system", "omop"]),
        ("sqlite", []),
    ],
    ids=["mssql-creates-missing-schemas", "sqlite-does-not-create-schemas"],
)
def test_create_schemas_for_supported_dialect(
    monkeypatch: pytest.MonkeyPatch,
    dialect_name: str,
    expected_schemas: list[str],
) -> None:
    recorder = _OperationsRecorder(dialect_name)
    monkeypatch.setattr(initial_schema, "op", recorder)

    initial_schema._create_schemas()

    executed = [str(args[0]) for name, args, _ in recorder.calls if name == "execute"]
    assert [
        schema
        for schema in expected_schemas
        if any(f"SCHEMA_ID('{schema}')" in statement for statement in executed)
    ] == expected_schemas
    assert len(executed) == len(expected_schemas)


def test_upgrade_creates_tables_with_schema_and_timestamp_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder = _OperationsRecorder("mssql")
    monkeypatch.setattr(initial_schema, "op", recorder)

    initial_schema.upgrade()

    table_calls = [
        (args, kwargs)
        for name, args, kwargs in recorder.calls
        if name == "create_table"
    ]
    assert table_calls
    assert {kwargs["schema"] for _, kwargs in table_calls} == {
        "abac",
        "omop",
        "organization",
        "system",
    }
    created_tables = {
        (kwargs["schema"], args[0]) for args, kwargs in table_calls
    }
    assert ("organization", "data_collection") in created_tables
    assert ("abac", "organization_admin_policy") in created_tables
    assert ("system", "outage") in created_tables
    assert ("omop", "person") in created_tables

    timestamp_columns = [
        column
        for args, _ in table_calls
        for column in args[1:]
        if isinstance(column, sa.Column)
        and column.name in {"created_at", "modified_at"}
    ]
    assert timestamp_columns
    assert all(
        column.server_default is not None
        and str(column.server_default.arg) == "GETUTCDATE()"
        for column in timestamp_columns
    )


def test_downgrade_drops_created_tables_in_reverse_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder = _OperationsRecorder("mssql")
    monkeypatch.setattr(initial_schema, "op", recorder)

    initial_schema.upgrade()
    created_tables = [
        (kwargs["schema"], args[0])
        for name, args, kwargs in recorder.calls
        if name == "create_table"
    ]
    recorder.calls.clear()

    initial_schema.downgrade()

    dropped_tables = [
        (kwargs["schema"], args[0])
        for name, args, kwargs in recorder.calls
        if name == "drop_table"
    ]
    assert dropped_tables == list(reversed(created_tables))
