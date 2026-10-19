"""Verify the initial SQL Server migration operations and rollback order."""

from importlib import import_module
from types import SimpleNamespace

import pytest

migration = import_module(
    "gen_epix.seqdb.repositories.sa_alembic.versions.973d81851aeb_initial_schema"
)


class RecordedOperation:
    """Capture arguments for one Alembic operation."""

    def __init__(self):
        """Initialize an empty call history."""
        self.call_args_list = []

    def __call__(self, *args, **kwargs):
        """Record one invocation's positional and keyword arguments."""
        self.call_args_list.append(SimpleNamespace(args=args, kwargs=kwargs))

    def was_called(self) -> bool:
        """Return whether this operation has been invoked."""
        return bool(self.call_args_list)


class OperationRecorder:
    """Provide the Alembic operation surface used by this migration."""

    def __init__(self, dialect: str):
        """Initialize the recorder for a database dialect."""
        self.dialect = dialect
        self.operations = {}

    def get_bind(self):
        """Return a bind exposing the configured dialect name."""
        return SimpleNamespace(dialect=SimpleNamespace(name=self.dialect))

    @staticmethod
    def f(name: str) -> str:
        """Return Alembic's unchanged name in the operation recorder."""
        return name

    def __getattr__(self, name: str):
        """Return a stable call recorder for a migration operation."""
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in self.operations:
            self.operations[name] = RecordedOperation()
        return self.operations[name]


def _record_operations(monkeypatch, dialect: str):
    """Replace Alembic operations with a recorder for the requested dialect."""
    operations = OperationRecorder(dialect)
    monkeypatch.setattr(migration, "op", operations)
    return operations


def test_create_schemas_for_sql_server(monkeypatch):
    """Create each application schema through SQL Server's guarded DDL."""
    operations = _record_operations(monkeypatch, "mssql")

    migration.upgrade()

    statements = [call.args[0].text for call in operations.execute.call_args_list]
    assert statements == [
        "IF SCHEMA_ID('abac') IS NULL EXEC('CREATE SCHEMA [abac]')",
        "IF SCHEMA_ID('organization') IS NULL EXEC('CREATE SCHEMA [organization]')",
        "IF SCHEMA_ID('system') IS NULL EXEC('CREATE SCHEMA [system]')",
        "IF SCHEMA_ID('file') IS NULL EXEC('CREATE SCHEMA [file]')",
        "IF SCHEMA_ID('seq') IS NULL EXEC('CREATE SCHEMA [seq]')",
    ]


@pytest.mark.parametrize(
    "dialect", ["sqlite", "postgresql"], ids=["sqlite", "postgresql"]
)
def test_create_schemas_skips_non_sql_server_dialects(monkeypatch, dialect: str):
    """Leave schema creation to non-SQL Server dialect handling."""
    operations = _record_operations(monkeypatch, dialect)

    migration.upgrade()

    assert not operations.execute.was_called()


def test_upgrade_and_downgrade_table_order(monkeypatch):
    """Create the initial tables and remove them in reverse dependency order."""
    operations = _record_operations(monkeypatch, "mssql")

    migration.upgrade()
    created_tables = [call.args[0] for call in operations.create_table.call_args_list]
    migration.downgrade()
    dropped_tables = [
        (call.args[0], call.kwargs["schema"])
        for call in operations.drop_table.call_args_list
    ]

    created_table_keys = [
        (table_name, call.kwargs["schema"])
        for table_name, call in zip(
            created_tables, operations.create_table.call_args_list, strict=True
        )
    ]
    assert {name for name, _ in created_table_keys} >= {
        "file",
        "read_set",
        "sample",
        "seq",
        "seq_profile_identifier",
    }
    assert dropped_tables == list(reversed(created_table_keys))
