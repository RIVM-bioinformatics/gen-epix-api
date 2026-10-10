import importlib.util
from pathlib import Path
from test.util.mock_compat import patch
from types import SimpleNamespace

import pytest

_MODULE_PATH = (
    Path(__file__).resolve().parents[6]
    / "gen_epix/casedb/repositories/sa_alembic/versions/"
    "bbc386e12a58_initial_schema.py"
)
_MODULE_SPEC = importlib.util.spec_from_file_location("initial_schema", _MODULE_PATH)
assert _MODULE_SPEC is not None and _MODULE_SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(_MODULE_SPEC)
_MODULE_SPEC.loader.exec_module(MIGRATION)


@pytest.mark.parametrize(
    ("dialect_name", "expected_schema_names"),
    [
        (
            "mssql",
            ("abac", "organization", "system", "geo", "ontology", "case"),
        ),
        ("sqlite", ()),
    ],
    ids=["sql-server", "sqlite"],
)
def test_create_schemas_only_creates_schemas_for_sql_server(
    dialect_name: str, expected_schema_names: tuple[str, ...]
) -> None:
    bind = SimpleNamespace(dialect=SimpleNamespace(name=dialect_name))
    with (
        patch.object(MIGRATION.op, "get_bind", return_value=bind),
        patch.object(MIGRATION.op, "execute") as execute,
    ):
        MIGRATION._create_schemas()

    statements = [call.args[0].text for call in execute.call_args_list]
    assert statements == [
        f"IF SCHEMA_ID('{schema}') IS NULL EXEC('CREATE SCHEMA [{schema}]')"
        for schema in expected_schema_names
    ]


def test_downgrade_drops_upgrade_tables_in_reverse_order() -> None:
    with (
        patch.object(MIGRATION, "_create_schemas") as create_schemas,
        patch.object(MIGRATION.op, "create_table") as create_table,
        patch.object(MIGRATION.op, "drop_table") as drop_table,
    ):
        MIGRATION.upgrade()
        MIGRATION.downgrade()

    created_tables = [
        (operation.args[0], operation.kwargs["schema"])
        for operation in create_table.call_args_list
    ]
    dropped_tables = [
        (operation.args[0], operation.kwargs["schema"])
        for operation in drop_table.call_args_list
    ]
    assert created_tables
    assert dropped_tables == list(reversed(created_tables))
    create_schemas.assert_called_once_with()
