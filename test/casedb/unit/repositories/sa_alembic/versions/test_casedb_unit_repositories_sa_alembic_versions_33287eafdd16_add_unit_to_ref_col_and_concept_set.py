"""Exercise the migration's Alembic operations without requiring a database."""

import importlib.util
from pathlib import Path
from test.util.mock_compat import call, patch

import sqlalchemy as sa

from gen_epix.casedb.domain import enum

_MODULE_PATH = (
    Path(__file__).resolve().parents[6]
    / "gen_epix/casedb/repositories/sa_alembic/versions/"
    "33287eafdd16_add_unit_to_ref_col_and_concept_set.py"
)
_MODULE_SPEC = importlib.util.spec_from_file_location("unit_migration", _MODULE_PATH)
assert _MODULE_SPEC is not None and _MODULE_SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(_MODULE_SPEC)
_MODULE_SPEC.loader.exec_module(MIGRATION)


def test_upgrade_adds_nullable_unit_columns_to_both_tables() -> None:
    """Verify upgrade adds nullable unit enums to both schema-qualified tables."""
    with patch.object(MIGRATION.op, "add_column") as add_column:
        MIGRATION.upgrade()

    expected_columns = [("ref_col", "case"), ("concept_set", "ontology")]
    assert add_column.call_count == len(expected_columns)
    for call_args, (table_name, schema_name) in zip(
        add_column.call_args_list, expected_columns
    ):
        column = call_args.args[1]
        assert call_args.args[0] == table_name
        assert call_args.kwargs["schema"] == schema_name
        assert column.name == "unit"
        assert isinstance(column.type, sa.Enum)
        assert column.type.enums == [unit.value for unit in enum.Unit]
        assert column.nullable is True


def test_downgrade_drops_unit_columns_in_reverse_order() -> None:
    """Verify downgrade removes both unit columns in reverse order."""
    with patch.object(MIGRATION.op, "drop_column") as drop_column:
        MIGRATION.downgrade()

    assert drop_column.call_args_list == [
        call("concept_set", "unit", schema="ontology"),
        call("ref_col", "unit", schema="case"),
    ]
