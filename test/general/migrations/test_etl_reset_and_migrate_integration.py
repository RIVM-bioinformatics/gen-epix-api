"""Integration test for etl.py's reset_database/load_demodata modes against a real
SQL Server, verifying the Alembic cutover end to end.

Requires a live SQL Server reachable at the SEQDB SA_SQL dev config (see
`gen_epix/seqdb/config/.example.secrets.repository.sa_sql.toml`), e.g. via:

    make start-db

The test is skipped automatically if that database is unreachable.
"""

from __future__ import annotations

import importlib
from types import ModuleType

import pytest
import sqlalchemy as sa

import etl
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
from gen_epix.commondb.domain.util import set_env_variables
from gen_epix.fastapp.repositories.sa.repository import SARepository

pytestmark = pytest.mark.integration

MODULE_ROOT = "gen_epix.seqdb"
ENVVAR_PREFIX = "SEQDB_"
BOGUS_ALEMBIC_REVISION = "deadbeef1234"


def _seq_connection_string() -> str:
    """Resolve the SA_SQL connection string for seqdb's SEQ service type."""
    seqdb_enum = importlib.import_module(f"{MODULE_ROOT}.domain.enum")
    app_cfg = AppCfg(
        AppType.SEQDB.value,
        seqdb_enum.ServiceType,
        seqdb_enum.RepositoryType,
        log_setup=False,
    )
    repository_cfg = app_cfg.cfg["repository"][seqdb_enum.ServiceType.SEQ.value]
    return str(repository_cfg["props"]["connection_string"])


@pytest.fixture(name="connection_string")
def get_connection_string() -> str:
    """Resolve the SEQDB SA_SQL connection string, skipping if unreachable."""
    set_env_variables(AppType.SEQDB, DevIdpConfig.MOCK, DevRepositoryConfig.SA_SQL)
    connection_string = _seq_connection_string()
    if exception := SARepository.test_connection(
        connection_string, timeout=2, login_timeout=2
    ):
        pytest.skip(
            f"SEQDB SA_SQL database is unreachable ({exception}); "
            "run `make start-db` first"
        )
    return connection_string


def test_reset_database_wipes_legacy_schema_and_migrates_to_head(
    connection_string: str,
) -> None:
    """A pre-existing schema (incl. stray tables and a bogus Alembic stamp) is
    fully wiped by reset_database, then correctly migrated to head, then
    load_demodata successfully loads demo data on top of it."""
    seqdb_enum: ModuleType = importlib.import_module(f"{MODULE_ROOT}.domain.enum")
    seqdb_domain = importlib.import_module(f"{MODULE_ROOT}.domain").DOMAIN
    entities_seq = seqdb_domain.get_dag_sorted_entities(
        service_type=seqdb_enum.ServiceType.SEQ, persistable=True
    )

    # 1. Simulate a pre-Alembic/legacy database: create the current tables directly
    #    (standing in for whatever legacy schema happens to be there), plus a stray
    #    table that has no corresponding entity, plus a bogus Alembic version stamp.
    SARepository.create_sa_repository(
        entities=entities_seq,
        connection_string=connection_string,
        create_database_objects=True,
    )
    engine = sa.create_engine(connection_string)
    with engine.begin() as conn:
        conn.execute(sa.text("IF SCHEMA_ID('seq') IS NULL EXEC('CREATE SCHEMA seq')"))
        conn.execute(
            sa.text(
                "IF OBJECT_ID('seq.legacy_junk_table') IS NULL "
                "CREATE TABLE seq.legacy_junk_table (id INT PRIMARY KEY)"
            )
        )
        conn.execute(
            sa.text("IF SCHEMA_ID('alembic') IS NULL EXEC('CREATE SCHEMA alembic')")
        )
        conn.execute(
            sa.text(
                "IF OBJECT_ID('alembic.alembic_version') IS NULL "
                "CREATE TABLE alembic.alembic_version "
                "(version_num VARCHAR(32) NOT NULL)"
            )
        )
        conn.execute(sa.text("DELETE FROM alembic.alembic_version"))
        conn.execute(
            sa.text("INSERT INTO alembic.alembic_version (version_num) VALUES (:v)"),
            {"v": BOGUS_ALEMBIC_REVISION},
        )
    engine.dispose()

    inspector = sa.inspect(sa.create_engine(connection_string))
    assert "legacy_junk_table" in inspector.get_table_names(schema="seq")

    # 2. reset_database: wipe everything (incl. the bogus Alembic stamp), then
    #    migrate to head. If the Alembic tracking table hadn't really been
    #    dropped, `alembic upgrade head` would fail outright (can't locate the
    #    bogus revision), so simply not raising here is itself a strong signal.
    etl.run_reset_database(MODULE_ROOT, AppType.SEQDB, seqdb_enum, seqdb_domain)

    inspector = sa.inspect(sa.create_engine(connection_string))
    assert "legacy_junk_table" not in inspector.get_table_names(schema="seq")

    problems = SARepository.check_schema_matches(
        entities=entities_seq, connection_string=connection_string
    )
    assert not problems

    engine = sa.create_engine(connection_string)
    with engine.connect() as conn:
        version_num = conn.execute(
            sa.text("SELECT version_num FROM alembic.alembic_version")
        ).scalar_one()
    engine.dispose()
    assert version_num != BOGUS_ALEMBIC_REVISION

    # 3. load_demodata: schema now matches, so demo data should load successfully.
    etl.run_load_demodata(
        ENVVAR_PREFIX, MODULE_ROOT, AppType.SEQDB, seqdb_enum, seqdb_domain
    )

    engine = sa.create_engine(connection_string)
    total_rows = 0
    with engine.connect() as conn:
        for entity in entities_seq:
            table = entity.db_model_class.__table__
            count_column = sa.func.count()  # pylint: disable=not-callable
            total_rows += conn.execute(
                sa.select(count_column).select_from(table)
            ).scalar_one()
    engine.dispose()
    assert total_rows > 0
