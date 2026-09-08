"""
Schema-creation coverage for SQL Server.

Historically the SA metadata was only ever exercised against SQLite (the
``SA_SQLITE`` build tests and the in-memory demo repositories). A field whose
``max_length`` exceeded the SQL Server ``NVARCHAR(n)`` limit (n <= 4000) or the
``VARCHAR(n)`` limit (n <= 8000) therefore produced DDL that SQLite accepts but
SQL Server rejects at ``CREATE TABLE`` time with::

    pyodbc.ProgrammingError: ('42000', "... The size (8000) given to the column
    ... exceeds the maximum allowed for any data type (4000) ... (2717)")

The concrete regression was ``CaseSet.description`` (``max_length=8000`` ->
``NVARCHAR(8000)``), which broke casedb startup against SQL Server.

The general guard now lives in
``gen_epix.fastapp.repositories.sa.util.create_sa_type_from_field_info``: a
str/Unicode column whose length exceeds the dialect limit is emitted as an
unbounded text type (``NVARCHAR(MAX)`` / ``VARCHAR(MAX)`` on SQL Server, ``TEXT``
elsewhere) instead of ``NVARCHAR(n)`` / ``VARCHAR(n)``.

This module verifies, for every persistable entity in all four apps (commondb,
casedb, seqdb, omopdb), that:

* ``test_no_oversized_string_columns`` - the ``CREATE TABLE`` DDL compiled with
  the ``mssql`` dialect contains no ``NVARCHAR(n)`` with n > 4000 and no
  ``VARCHAR(n)`` with n > 8000. Pure compilation, no database - always runs.
* ``test_case_set_description_is_unbounded`` - a focused regression assertion
  that ``CaseSet.__table__.c.description`` compiles to ``NVARCHAR(max)`` (or an
  in-bounds ``NVARCHAR(<=4000)``) under the mssql dialect. Always runs.
* ``test_create_all_against_live_sql_server`` - creates every app's full
  metadata against a real SQL Server via ``SARepository.create_sa_repository``
  (exactly the path a service takes on startup) and drops it again. Runs
  whenever a SQL Server is reachable: either ``FASTAPP_MSSQL_TEST_URL`` is set,
  or the standard local dev instance is up (``make start-db`` /
  ``docker compose -f docker-compose.sql.yml up -d lsp_sql init-db``). Skips
  with an instruction when neither is available.
"""

from __future__ import annotations

import importlib
import os
import re
from collections.abc import Iterator
from typing import Any

import pytest
import sqlalchemy as sa
from sqlalchemy.dialects import mssql
from sqlalchemy.schema import CreateTable

# SQL Server hard limits for length-bounded character types (error 2717).
MSSQL_MAX_NVARCHAR_LENGTH = 4000
MSSQL_MAX_VARCHAR_LENGTH = 8000

# Optional explicit override; otherwise the standard local dev instance is used.
MSSQL_URL_ENV = "FASTAPP_MSSQL_TEST_URL"

# Default local dev SQL Server, matching docker-compose.sql.yml and the
# `make start-db` helper (same credentials lsp-data's integration suite uses).
_LOCAL_MSSQL_URL = (
    "mssql+pyodbc://sa:Your_password123@127.0.0.1:1433/{database}"
    "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)

# deprecate_large_types=True mirrors what the mssql dialect auto-enables against
# any SQL Server >= 2012 (all supported versions): unbounded text types compile
# to NVARCHAR(max) / VARCHAR(max) rather than the deprecated NTEXT / TEXT.
_MSSQL_DIALECT = mssql.dialect(deprecate_large_types=True)

# NVARCHAR(255), VARCHAR(50) -> ("NVARCHAR", "255") ; NVARCHAR(max) does not match.
_BOUNDED_CHAR_TYPE_RE = re.compile(r"\b(N?VARCHAR)\((\d+)\)", re.IGNORECASE)


def _iter_app_domains() -> Iterator[tuple[str, Any]]:
    """Yield (app_name, Domain) for every app, importing its SA models first.

    Importing ``gen_epix.<app>.repositories.sa_model`` registers the SQLAlchemy
    row classes on the app's ``DOMAIN`` (sets ``entity.db_model_class``), which
    is what builds the ``__table__`` objects this module inspects.
    """
    for app in ("commondb", "casedb", "seqdb", "omopdb"):
        importlib.import_module(f"gen_epix.{app}.repositories.sa_model")
    from gen_epix.casedb.domain import DOMAIN as CASEDB_DOMAIN
    from gen_epix.commondb.domain import DOMAIN as COMMONDB_DOMAIN
    from gen_epix.omopdb.domain import DOMAIN as OMOPDB_DOMAIN
    from gen_epix.seqdb.domain import DOMAIN as SEQDB_DOMAIN

    yield "commondb", COMMONDB_DOMAIN
    yield "casedb", CASEDB_DOMAIN
    yield "seqdb", SEQDB_DOMAIN
    yield "omopdb", OMOPDB_DOMAIN


def _iter_persistable_tables() -> Iterator[tuple[str, sa.Table]]:
    """Yield (app_name, Table) for every persistable entity across all apps.

    Tables shared between apps (e.g. the commondb ``organization`` table, which
    casedb/seqdb/omopdb all reference) are only yielded once.
    """
    seen: set[str] = set()
    for app_name, domain in _iter_app_domains():
        for entity in domain.get_dag_sorted_entities(persistable=True):
            db_model_class = entity.db_model_class
            if db_model_class is None:
                continue
            table: sa.Table = db_model_class.__table__
            if table.key in seen:
                continue
            seen.add(table.key)
            yield app_name, table


def _resolve_mssql_base_url() -> str | None:
    """Return a reachable SQL Server URL (env override, else local dev), or None.

    Always probes with a short timeout so a missing/unreachable server makes the
    test skip quickly rather than hang on per-app connects.
    """
    env_url = os.environ.get(MSSQL_URL_ENV)
    base_url_str = env_url or _LOCAL_MSSQL_URL.format(database="master")
    probe_url = sa.engine.make_url(base_url_str).set(database="master")
    try:
        engine = sa.create_engine(probe_url, connect_args={"timeout": 3})
        engine.connect().close()
        engine.dispose()
    except Exception:  # pyodbc missing, driver missing, server down, ...
        return None
    return probe_url.render_as_string(hide_password=False)


def test_no_oversized_string_columns() -> None:
    """Every persistable table's mssql CREATE TABLE DDL stays within the NVARCHAR/VARCHAR limits."""
    violations: list[str] = []
    n_tables = 0
    for app_name, table in _iter_persistable_tables():
        n_tables += 1
        ddl = str(CreateTable(table).compile(dialect=_MSSQL_DIALECT))
        for type_name, length_str in _BOUNDED_CHAR_TYPE_RE.findall(ddl):
            length = int(length_str)
            limit = (
                MSSQL_MAX_NVARCHAR_LENGTH
                if type_name.upper() == "NVARCHAR"
                else MSSQL_MAX_VARCHAR_LENGTH
            )
            if length > limit:
                violations.append(
                    f"{app_name}.{table.key}: {type_name}({length}) exceeds "
                    f"SQL Server limit {limit} - use an unbounded text type "
                    f"(drop max_length, or set it <= {limit})"
                )

    assert n_tables > 0, "no persistable tables discovered"
    assert not violations, "SQL Server DDL violations:\n" + "\n".join(violations)


def test_case_set_description_is_unbounded() -> None:
    """Regression: CaseSet.description must not compile to NVARCHAR(n>4000) under mssql (LSP: error 2717)."""
    import gen_epix.casedb.repositories.sa_model as casedb_sa_model

    description_col = casedb_sa_model.CaseSet.__table__.c.description
    compiled = str(description_col.type.compile(dialect=_MSSQL_DIALECT)).upper()

    match = _BOUNDED_CHAR_TYPE_RE.fullmatch(compiled)
    assert compiled == "NVARCHAR(MAX)" or (
        match is not None and int(match.group(2)) <= MSSQL_MAX_NVARCHAR_LENGTH
    ), (
        f"CaseSet.description compiles to {compiled!r} on mssql; expected "
        f"NVARCHAR(max) or NVARCHAR(n<={MSSQL_MAX_NVARCHAR_LENGTH})"
    )


@pytest.mark.integration
def test_create_all_against_live_sql_server() -> None:
    """Build every app's full metadata against a real SQL Server, mirroring service startup.

    Each app is built into its own throwaway ``fastapp_schema_test_<app>``
    database, which is dropped afterwards - the shared casedb / seqdb / omopdb
    dev databases are never touched.
    """
    base_url_str = _resolve_mssql_base_url()
    if not base_url_str:
        pytest.skip(
            "no SQL Server reachable on 127.0.0.1:1433 - start it with "
            "`make start-db` (or `docker compose -f docker-compose.sql.yml "
            f"up -d lsp_sql init-db`), or set {MSSQL_URL_ENV}"
        )

    from gen_epix.fastapp.repositories.sa.repository import SARepository

    master_url = sa.engine.make_url(base_url_str)  # already points at master
    master_engine = sa.create_engine(
        master_url, connect_args={"timeout": 30}, isolation_level="AUTOCOMMIT"
    )
    tested_apps: list[str] = []
    try:
        for app_name, domain in _iter_app_domains():
            entities = [
                e
                for e in domain.get_dag_sorted_entities(persistable=True)
                if e.db_model_class is not None
            ]
            db_name = f"fastapp_schema_test_{app_name}"
            _recreate_database(master_engine, db_name)
            try:
                # Exact production startup path: engine + schemas + full DDL.
                SARepository.create_sa_repository(
                    entities,
                    connection_string=master_url.set(database=db_name).render_as_string(
                        hide_password=False
                    ),
                    register_mappers=False,
                )
                tested_apps.append(app_name)
            finally:
                _drop_database(master_engine, db_name)
    finally:
        master_engine.dispose()

    assert sorted(tested_apps) == ["casedb", "commondb", "omopdb", "seqdb"]


def _recreate_database(master_engine: sa.Engine, db_name: str) -> None:
    """Drop and (re)create ``db_name`` for an isolated run."""
    _drop_database(master_engine, db_name)
    with master_engine.connect() as conn:
        conn.execute(sa.text(f"CREATE DATABASE [{db_name}]"))


def _drop_database(master_engine: sa.Engine, db_name: str) -> None:
    """Drop ``db_name`` if it exists, forcing out any lingering connections."""
    with master_engine.connect() as conn:
        conn.execute(
            sa.text(
                f"IF DB_ID('{db_name}') IS NOT NULL BEGIN "
                f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
                f"DROP DATABASE [{db_name}]; END"
            )
        )
