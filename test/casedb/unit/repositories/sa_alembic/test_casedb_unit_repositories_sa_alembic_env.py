from __future__ import annotations

import importlib
import sys
from contextlib import nullcontext
from test.util.mock_compat import Mock
from types import ModuleType

import pytest
import sqlalchemy


@pytest.fixture
def alembic_env(monkeypatch: pytest.MonkeyPatch) -> tuple[ModuleType, object, object]:
    module_name = "gen_epix.casedb.repositories.sa_alembic.env"
    monkeypatch.delitem(sys.modules, module_name, raising=False)

    from alembic import context

    config = Mock()
    config.config_ini_section = "alembic"
    config.get_section.return_value = {"sqlalchemy.url": "configured-url"}
    monkeypatch.setattr(context, "config", config, raising=False)
    monkeypatch.setattr(
        context, "get_x_argument", Mock(return_value={"url": "initial-url"})
    )
    monkeypatch.setattr(context, "is_offline_mode", Mock(return_value=True))
    monkeypatch.setattr(context, "configure", Mock())
    monkeypatch.setattr(context, "begin_transaction", Mock(side_effect=nullcontext))
    monkeypatch.setattr(context, "run_migrations", Mock())
    monkeypatch.setenv("ALEMBIC_URL", "environment-url")
    monkeypatch.setattr(sqlalchemy, "engine_from_config", Mock())

    module = importlib.import_module(module_name)
    return module, context, config


def test_configure_url_prefers_alembic_argument(alembic_env, monkeypatch):
    module, context, config = alembic_env
    context.get_x_argument.return_value = {"url": "argument-url"}
    monkeypatch.setenv("ALEMBIC_URL", "environment-url")
    config.set_main_option.reset_mock()

    module._configure_url()

    config.set_main_option.assert_called_once_with("sqlalchemy.url", "argument-url")


def test_configure_url_uses_environment_fallback(alembic_env, monkeypatch):
    module, context, config = alembic_env
    context.get_x_argument.return_value = {}
    monkeypatch.setenv("ALEMBIC_URL", "environment-url")
    config.set_main_option.reset_mock()

    module._configure_url()

    config.set_main_option.assert_called_once_with("sqlalchemy.url", "environment-url")


def test_configure_url_requires_argument_or_environment(alembic_env, monkeypatch):
    module, context, _ = alembic_env
    context.get_x_argument.return_value = {}
    monkeypatch.delenv("ALEMBIC_URL")

    with pytest.raises(ValueError, match="Provide the database URL"):
        module._configure_url()


def test_run_migrations_offline_configures_context(alembic_env):
    module, context, config = alembic_env
    context.configure.reset_mock()
    context.begin_transaction.reset_mock()
    context.run_migrations.reset_mock()
    config.get_main_option.return_value = "resolved-url"

    module.run_migrations_offline()

    context.configure.assert_called_once_with(
        url="resolved-url",
        target_metadata=module.target_metadata,
        include_schemas=True,
        compare_type=True,
        compare_server_default=False,
        version_table_schema="alembic",
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    context.begin_transaction.assert_called_once_with()
    context.run_migrations.assert_called_once_with()


@pytest.mark.parametrize(
    ("dialect_name", "creates_schema"),
    [("mssql", True), ("postgresql", False)],
    ids=["sql-server", "other-dialect"],
)
def test_run_migrations_online_creates_schema_only_for_mssql(
    alembic_env, monkeypatch, dialect_name, creates_schema
):
    module, context, config = alembic_env
    connection = Mock()
    connection.dialect.name = dialect_name
    engine = Mock()
    engine.connect.return_value = nullcontext(connection)
    engine_factory = Mock(return_value=engine)
    monkeypatch.setattr(module, "engine_from_config", engine_factory)
    context.configure.reset_mock()
    context.begin_transaction.reset_mock()
    context.run_migrations.reset_mock()

    module.run_migrations_online()

    engine_factory.assert_called_once_with(
        config.get_section.return_value,
        prefix="sqlalchemy.",
        poolclass=module.pool.NullPool,
    )
    if creates_schema:
        connection.execute.assert_called_once()
        assert str(connection.execute.call_args.args[0]).startswith("IF SCHEMA_ID")
        connection.commit.assert_called_once_with()
    else:
        connection.execute.assert_not_called()
        connection.commit.assert_not_called()
    context.configure.assert_called_once_with(
        connection=connection,
        target_metadata=module.target_metadata,
        include_schemas=True,
        compare_type=True,
        compare_server_default=False,
        version_table_schema="alembic",
    )
    context.begin_transaction.assert_called_once_with()
    context.run_migrations.assert_called_once_with()
