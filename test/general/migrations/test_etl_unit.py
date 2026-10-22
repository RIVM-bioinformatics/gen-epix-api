"""Unit tests for etl.py's waiting for a database and its fail-loudly behaviour.

No database is needed: cfg resolution uses SEQDB's SA_SQL dev settings offline,
and every call that would touch the database is mocked.
"""

# pylint: disable=protected-access

from __future__ import annotations

import importlib
import os
from collections.abc import Iterator
from dataclasses import dataclass
from test.util.mock_compat import Mock, patch
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
import tenacity

import etl
from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
from gen_epix.commondb.domain.util import set_env_variables
from gen_epix.fastapp.repositories.sa.repository import SARepository

MODULE_ROOT = "gen_epix.seqdb"
ENVVAR_PREFIX = "SEQDB_"
# SEQDB service types with an SA repository; AUTH and RBAC have none.
SEQDB_SA_SERVICE_TYPE_VALUES = ["ORGANIZATION", "SYSTEM", "ABAC", "SEQ", "FILE"]
PASSWORD = "not-to-be-printed"
MSSQL_URL = (
    "mssql+pyodbc:///?odbc_connect=DRIVER=ODBC Driver 18 for SQL Server;"
    f"SERVER=db;DATABASE=seqdb;UID=sa;PWD={PASSWORD}"
)


@dataclass
class _DbMocks:
    """Mocks for every database touchpoint, attached to one parent for call order."""

    calls: Mock
    test_connection: Mock
    clear_repository_content: Mock
    check_schema_matches: Mock
    run_migrate: Mock

    def call_names(self) -> list[str]:
        """Names of the mocked calls made so far, in order."""
        return [name for name, _, _ in self.calls.mock_calls]


@pytest.fixture(autouse=True)
def _seqdb_sa_sql_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Use SEQDB's SA_SQL dev settings and don't sleep between attempts."""
    with patch.dict(os.environ):
        set_env_variables(AppType.SEQDB, DevIdpConfig.MOCK, DevRepositoryConfig.SA_SQL)
        monkeypatch.setattr(etl, "DB_WAKE_WAIT", tenacity.wait_none())
        yield


@pytest.fixture(name="seqdb_enum")
def get_seqdb_enum() -> ModuleType:
    """SEQDB's ServiceType/RepositoryType module."""
    return importlib.import_module(f"{MODULE_ROOT}.domain.enum")


@pytest.fixture(name="seqdb_domain")
def get_seqdb_domain() -> Any:
    """SEQDB's domain."""
    return importlib.import_module(f"{MODULE_ROOT}.domain").DOMAIN


@pytest.fixture(name="db")
def get_db(monkeypatch: pytest.MonkeyPatch) -> _DbMocks:
    """Replace every database touchpoint with a mock; the database is reachable."""
    calls = Mock()
    db = _DbMocks(
        calls=calls,
        test_connection=Mock(return_value=None),
        clear_repository_content=Mock(),
        check_schema_matches=Mock(return_value=[]),
        run_migrate=Mock(),
    )
    for name in (
        "test_connection",
        "clear_repository_content",
        "check_schema_matches",
        "run_migrate",
    ):
        calls.attach_mock(getattr(db, name), name)
    monkeypatch.setattr(SARepository, "test_connection", db.test_connection)
    monkeypatch.setattr(
        SARepository, "clear_repository_content", db.clear_repository_content
    )
    monkeypatch.setattr(SARepository, "check_schema_matches", db.check_schema_matches)
    monkeypatch.setattr(etl, "run_migrate", db.run_migrate)
    return db


@pytest.fixture(name="unreachable_db")
def get_unreachable_db(db: _DbMocks, monkeypatch: pytest.MonkeyPatch) -> _DbMocks:
    """Make the database never reachable, with a deadline that has already passed."""
    db.test_connection.return_value = RuntimeError("Login timeout expired")
    monkeypatch.setattr(etl, "DB_WAKE_TIMEOUT_SECONDS", 0)
    return db


def _returning(*results: Exception | None) -> Any:
    """A side effect that returns the results one by one, exceptions included."""
    iterator = iter(results)
    return lambda *args, **kwargs: next(iterator)


def _seqdb_connection_string(seqdb_enum: ModuleType) -> str:
    """The single connection string all SEQDB SA service types share."""
    (connection_string,) = etl._distinct_connection_strings(
        etl._resolve_sa_targets(AppType.SEQDB, seqdb_enum)
    )
    return connection_string


def test_connect_args_mssql_has_only_login_timeout() -> None:
    assert etl._connect_args(MSSQL_URL) == {"timeout": etl.CONNECTION_TIMEOUT}


def test_connect_args_sqlite_is_empty() -> None:
    assert etl._connect_args("sqlite:///:memory:") == {}


def test_resolve_sa_targets_skips_service_types_without_sa_repository(
    seqdb_enum: ModuleType, db: _DbMocks
) -> None:
    targets = etl._resolve_sa_targets(AppType.SEQDB, seqdb_enum)

    assert [t.service_type.value for t in targets] == SEQDB_SA_SERVICE_TYPE_VALUES
    assert all(issubclass(t.repository_class, SARepository) for t in targets)
    assert db.test_connection.call_count == 0


def test_wait_for_database_succeeds_after_failures(
    db: _DbMocks, capsys: pytest.CaptureFixture[str]
) -> None:
    db.test_connection.side_effect = _returning(
        RuntimeError("Database 'seqdb' is not currently available"),
        RuntimeError("Database 'seqdb' is not currently available"),
        RuntimeError("Login timeout expired"),
        None,
    )

    etl._wait_for_database(AppType.SEQDB, SARepository, MSSQL_URL, ["SEQ", "FILE"])

    assert db.test_connection.call_count == 4
    db.test_connection.assert_called_with(MSSQL_URL, timeout=etl.CONNECTION_TIMEOUT)
    out = capsys.readouterr().out
    assert "App SEQDB, service(s) SEQ, FILE: database not reachable yet" in out
    assert "(attempt 1," in out
    assert "(attempt 3," in out
    assert "is not currently available" in out
    assert "Login timeout expired" in out
    assert "database reachable after 4 attempts" in out
    assert PASSWORD not in out


def test_wait_for_database_first_attempt_succeeds_quietly(
    db: _DbMocks, capsys: pytest.CaptureFixture[str]
) -> None:
    etl._wait_for_database(AppType.SEQDB, SARepository, MSSQL_URL, ["SEQ"])

    assert db.test_connection.call_count == 1
    assert capsys.readouterr().out == ""


def test_wait_for_database_exits_after_deadline(
    unreachable_db: _DbMocks, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        etl._wait_for_database(AppType.SEQDB, SARepository, MSSQL_URL, ["SEQ"])

    assert excinfo.value.code == 1
    assert unreachable_db.test_connection.call_count == 1
    out = capsys.readouterr().out
    assert "App SEQDB, service(s) SEQ: database not reachable within 0s" in out
    assert "Last error: Login timeout expired" in out
    assert PASSWORD not in out


def test_wait_for_databases_waits_once_per_distinct_connection_string(
    db: _DbMocks, capsys: pytest.CaptureFixture[str]
) -> None:
    db.test_connection.side_effect = _returning(RuntimeError("down"), None, None)
    targets = [
        etl._SaTarget(SimpleNamespace(value=value), SARepository, connection_string)
        for value, connection_string in [
            ("A", "sqlite:///a.sqlite"),
            ("B", "sqlite:///b.sqlite"),
            ("C", "sqlite:///a.sqlite"),
        ]
    ]

    etl._wait_for_databases(AppType.SEQDB, targets)

    assert [c.args[0] for c in db.test_connection.call_args_list] == [
        "sqlite:///a.sqlite",
        "sqlite:///a.sqlite",
        "sqlite:///b.sqlite",
    ]
    out = capsys.readouterr().out
    assert "App SEQDB, service(s) A, C: database reachable after 2 attempts" in out


def test_reset_database_clears_all_then_migrates_then_checks(
    seqdb_enum: ModuleType, seqdb_domain: Any, db: _DbMocks
) -> None:
    connection_string = _seqdb_connection_string(seqdb_enum)
    n = len(SEQDB_SA_SERVICE_TYPE_VALUES)

    etl.run_reset_database(MODULE_ROOT, AppType.SEQDB, seqdb_enum, seqdb_domain)

    assert db.call_names() == (
        ["test_connection"]
        + ["clear_repository_content"] * n
        + ["run_migrate"]
        + ["check_schema_matches"] * n
    )
    db.run_migrate.assert_called_once_with(MODULE_ROOT, connection_string)
    for clear_call in db.clear_repository_content.call_args_list:
        assert clear_call.kwargs["connection_string"] == connection_string
        assert clear_call.kwargs["alembic_schema"] == etl.ALEMBIC_SCHEMA
    seq_entities = seqdb_domain.get_dag_sorted_entities(
        service_type=seqdb_enum.ServiceType.SEQ, persistable=True
    )
    assert any(
        c.kwargs["entities"] == seq_entities
        for c in db.check_schema_matches.call_args_list
    )


def test_reset_database_unreachable_clears_nothing(
    seqdb_enum: ModuleType, seqdb_domain: Any, unreachable_db: _DbMocks
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        etl.run_reset_database(MODULE_ROOT, AppType.SEQDB, seqdb_enum, seqdb_domain)

    assert excinfo.value.code == 1
    assert unreachable_db.clear_repository_content.call_count == 0
    assert unreachable_db.run_migrate.call_count == 0
    assert unreachable_db.check_schema_matches.call_count == 0


def test_reset_database_schema_problems_exit(
    seqdb_enum: ModuleType,
    seqdb_domain: Any,
    db: _DbMocks,
    capsys: pytest.CaptureFixture[str],
) -> None:
    db.check_schema_matches.return_value = ["table seq.seq is missing"]

    with pytest.raises(SystemExit) as excinfo:
        etl.run_reset_database(MODULE_ROOT, AppType.SEQDB, seqdb_enum, seqdb_domain)

    assert excinfo.value.code == 1
    assert db.run_migrate.call_count == 1
    out = capsys.readouterr().out
    assert "reset did not produce the expected schema" in out
    assert "  - table seq.seq is missing" in out


def test_reset_database_without_sa_repositories_exits(
    seqdb_enum: ModuleType,
    seqdb_domain: Any,
    db: _DbMocks,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(etl, "_repository_cfg", Mock(return_value=None))

    with pytest.raises(SystemExit) as excinfo:
        etl.run_reset_database(MODULE_ROOT, AppType.SEQDB, seqdb_enum, seqdb_domain)

    assert excinfo.value.code == 1
    assert db.call_names() == []


def test_migrate_database_waits_then_migrates_once(
    seqdb_enum: ModuleType, db: _DbMocks
) -> None:
    connection_string = _seqdb_connection_string(seqdb_enum)

    etl.run_migrate_database(MODULE_ROOT, AppType.SEQDB, seqdb_enum)

    assert db.call_names() == ["test_connection", "run_migrate"]
    db.run_migrate.assert_called_once_with(MODULE_ROOT, connection_string)


def test_migrate_database_unreachable_does_not_migrate(
    seqdb_enum: ModuleType, unreachable_db: _DbMocks
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        etl.run_migrate_database(MODULE_ROOT, AppType.SEQDB, seqdb_enum)

    assert excinfo.value.code == 1
    assert unreachable_db.run_migrate.call_count == 0


def test_load_demodata_unreachable_exits_before_touching_env(
    seqdb_enum: ModuleType,
    seqdb_domain: Any,
    unreachable_db: _DbMocks,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_env_variables_mock = Mock()
    monkeypatch.setattr(etl, "set_env_variables", set_env_variables_mock)

    with pytest.raises(SystemExit) as excinfo:
        etl.run_load_demodata(
            ENVVAR_PREFIX, MODULE_ROOT, AppType.SEQDB, seqdb_enum, seqdb_domain
        )

    assert excinfo.value.code == 1
    assert set_env_variables_mock.call_count == 0
    assert unreachable_db.check_schema_matches.call_count == 0
