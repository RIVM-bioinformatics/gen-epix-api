"""Tests Alembic environment configuration and migration dispatch."""

import runpy
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import alembic.context
import pytest
import sqlalchemy
from sqlalchemy import pool

SOURCE_PATH = (
    Path(__file__).resolve().parents[5]
    / "gen_epix"
    / "omopdb"
    / "repositories"
    / "sa_alembic"
    / "env.py"
)


def _run_environment(
    monkeypatch: pytest.MonkeyPatch,
    *,
    offline: bool,
    x_arguments: dict[str, str],
    environment_url: str | None,
    dialect_name: str = "sqlite",
) -> tuple[
    SimpleNamespace,
    list[dict[str, object]],
    list[bool],
    list[str],
    list[bool],
    list[tuple],
]:
    """Execute env.py with isolated Alembic settings and database effects."""
    config = SimpleNamespace(config_ini_section="alembic", values={})
    config.set_main_option = lambda key, value: config.values.__setitem__(key, value)
    config.get_main_option = lambda key: config.values[key]
    config.get_section = lambda section, defaults: {
        "sqlalchemy.url": config.values["sqlalchemy.url"]
    }

    configured: list[dict[str, object]] = []
    migrations: list[bool] = []
    statements: list[str] = []
    commits: list[bool] = []
    engine_calls: list[tuple] = []
    connection = SimpleNamespace(
        dialect=SimpleNamespace(name=dialect_name),
        execute=lambda statement: statements.append(str(statement)),
        commit=lambda: commits.append(True),
    )
    connectable = SimpleNamespace(connect=lambda: nullcontext(connection))

    monkeypatch.setattr(alembic.context, "config", config, raising=False)
    monkeypatch.setattr(
        alembic.context, "get_x_argument", lambda as_dictionary: x_arguments
    )
    monkeypatch.setattr(alembic.context, "is_offline_mode", lambda: offline)
    monkeypatch.setattr(
        alembic.context, "configure", lambda **kwargs: configured.append(kwargs)
    )
    monkeypatch.setattr(alembic.context, "begin_transaction", nullcontext)
    monkeypatch.setattr(
        alembic.context, "run_migrations", lambda: migrations.append(True)
    )
    monkeypatch.setattr(
        sqlalchemy,
        "engine_from_config",
        lambda section, prefix, poolclass: (
            engine_calls.append((section, prefix, poolclass)) or connectable
        ),
    )
    if environment_url is None:
        monkeypatch.delenv("ALEMBIC_URL", raising=False)
    else:
        monkeypatch.setenv("ALEMBIC_URL", environment_url)

    runpy.run_path(str(SOURCE_PATH))
    return config, configured, migrations, statements, commits, engine_calls


def test_offline_migrations_use_cli_url_and_configure_literal_binds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, configured, migrations, _, _, _ = _run_environment(
        monkeypatch,
        offline=True,
        x_arguments={"url": "sqlite:///from-cli.db"},
        environment_url="sqlite:///from-env.db",
    )

    assert config.values["sqlalchemy.url"] == "sqlite:///from-cli.db"
    options = configured[0]
    assert options["url"] == "sqlite:///from-cli.db"
    assert options["target_metadata"]
    assert options["include_schemas"] is True
    assert options["compare_type"] is True
    assert options["compare_server_default"] is False
    assert options["version_table_schema"] == "alembic"
    assert options["literal_binds"] is True
    assert options["dialect_opts"] == {"paramstyle": "named"}
    assert migrations == [True]


def test_missing_url_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="Provide the database URL"):
        _run_environment(
            monkeypatch,
            offline=True,
            x_arguments={},
            environment_url=None,
        )


@pytest.mark.parametrize("dialect_name", ["sqlite", "mssql"])
def test_online_migrations_configure_connection_and_mssql_schema(
    monkeypatch: pytest.MonkeyPatch, dialect_name: str
) -> None:
    config, configured, migrations, statements, commits, engine_calls = (
        _run_environment(
            monkeypatch,
            offline=False,
            x_arguments={},
            environment_url="sqlite:///from-env.db",
            dialect_name=dialect_name,
        )
    )

    assert config.values["sqlalchemy.url"] == "sqlite:///from-env.db"
    options = configured[0]
    assert options["connection"]
    assert options["target_metadata"]
    assert options["include_schemas"] is True
    assert options["compare_type"] is True
    assert options["compare_server_default"] is False
    assert options["version_table_schema"] == "alembic"
    assert migrations == [True]
    assert len(engine_calls) == 1
    assert engine_calls[0][1:] == ("sqlalchemy.", pool.NullPool)
    if dialect_name == "mssql":
        assert statements == [
            "IF SCHEMA_ID('alembic') IS NULL EXEC('CREATE SCHEMA alembic')"
        ]
        assert commits == [True]
    else:
        assert statements == []
        assert commits == []
