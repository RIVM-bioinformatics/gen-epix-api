"""Verify SQL Server cleanup and downgrade behavior for the legacy-code migration."""

from importlib import import_module
from test.util.mock_compat import MagicMock

import pytest

migration = import_module(
    "gen_epix.seqdb.repositories.sa_alembic.versions."
    "6f2f4fb9b3d1_drop_legacy_code_constraints"
)


@pytest.mark.parametrize(
    ("constraint_exists", "index_exists", "expected_operation"),
    [
        (True, False, "constraint"),
        (False, True, "index"),
        (False, False, None),
    ],
    ids=["unique-constraint", "standalone-unique-index", "already-absent"],
)
def test_drop_legacy_unique_constraint_handles_sql_server_catalog_results(
    monkeypatch: pytest.MonkeyPatch,
    constraint_exists: bool,
    index_exists: bool,
    expected_operation: str | None,
) -> None:
    """Drop whichever legacy SQL Server object exists, if either one exists."""
    connection = MagicMock()
    connection.dialect.name = "mssql"
    connection.execute.side_effect = [
        MagicMock(scalar=MagicMock(return_value=constraint_exists)),
        MagicMock(scalar=MagicMock(return_value=index_exists)),
    ]
    drop_constraint = MagicMock()
    drop_index = MagicMock()
    monkeypatch.setattr(migration.op, "get_bind", lambda: connection)
    monkeypatch.setattr(migration.op, "drop_constraint", drop_constraint)
    monkeypatch.setattr(migration.op, "drop_index", drop_index)

    migration._drop_legacy_unique_constraint("sample", "uq_sample_code")

    if expected_operation == "constraint":
        drop_constraint.assert_called_once_with(
            "uq_sample_code", "sample", schema="seq", type_="unique"
        )
        drop_index.assert_not_called()
        assert connection.execute.call_count == 1
    elif expected_operation == "index":
        drop_constraint.assert_not_called()
        drop_index.assert_called_once_with(
            "uq_sample_code", table_name="sample", schema="seq"
        )
        assert connection.execute.call_count == 2
    else:
        drop_constraint.assert_not_called()
        drop_index.assert_not_called()
        assert connection.execute.call_count == 2


def test_drop_legacy_unique_constraint_skips_non_sql_server_dialects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Leave other database dialects unchanged without querying their catalogs."""
    connection = MagicMock()
    connection.dialect.name = "sqlite"
    drop_constraint = MagicMock()
    drop_index = MagicMock()
    monkeypatch.setattr(migration.op, "get_bind", lambda: connection)
    monkeypatch.setattr(migration.op, "drop_constraint", drop_constraint)
    monkeypatch.setattr(migration.op, "drop_index", drop_index)

    migration._drop_legacy_unique_constraint("sample", "uq_sample_code")

    connection.execute.assert_not_called()
    drop_constraint.assert_not_called()
    drop_index.assert_not_called()


def test_upgrade_targets_each_legacy_sequence_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Remove the three legacy code uniqueness objects during upgrade."""
    dropped_objects: list[tuple[str, str]] = []
    monkeypatch.setattr(
        migration,
        "_drop_legacy_unique_constraint",
        lambda table_name, constraint_name: dropped_objects.append(
            (table_name, constraint_name)
        ),
    )

    migration.upgrade()

    assert dropped_objects == [
        ("sample", "uq_sample_code"),
        ("read_set", "uq_read_set_code"),
        ("seq", "uq_seq_code"),
    ]


def test_downgrade_does_not_recreate_legacy_constraints() -> None:
    """Keep downgrade non-destructive when duplicate codes may exist."""
    assert migration.downgrade() is None
