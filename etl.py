"""
ETL (Extract, Transform, Load) script for Gen-EpiX genomic epidemiology platform.

This module has three modes, dispatched on the trailing MODE argument:

- ``load_demodata`` (default): loads demo data from dictionary repositories
  (file-based) into the SQLAlchemy repository, for an already-migrated
  schema. Fails fast with a clear message if the schema doesn't match the
  entities (e.g. the Alembic migration hasn't been run yet).
- ``reset_database``: wipes the database completely, including the Alembic
  version-tracking table/schema, then runs that service's Alembic migrations
  up to head. A one-time cutover/bootstrap step, not part of the regular
  deploy loop.
- ``migrate``: runs that service's Alembic migrations up to head, without
  touching any existing data or dropping anything. Lets a standalone
  per-deploy migration job be wired up later with no further code changes.

Usage:
    python etl.py ENVVAR_PREFIX MODULE_ROOT APP_TYPE [MODE]

Examples:
    python etl.py CASEDB_ gen_epix.casedb CASEDB
    python etl.py CASEDB_ gen_epix.casedb CASEDB load_demodata
    python etl.py CASEDB_ gen_epix.casedb CASEDB reset_database
    python etl.py CASEDB_ gen_epix.casedb CASEDB migrate

For backward compatibility with existing callers, the legacy tokens
``empty``, ``false``, ``0``, ``no``, ``off`` are still accepted as aliases
for ``reset_database``; any other value (or omitting MODE) means
``load_demodata``.
"""

import datetime
import importlib
import os
import sys
from collections.abc import Mapping
from pathlib import Path
from types import ModuleType
from typing import Any, cast

from alembic import command
from alembic.config import Config

from gen_epix.casedb.config.cfg_types import ResolvedCasedbAppCfgSettingsDict
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.config.cfg_types import (
    ResolvedAppCfgSettingsDict,
    ResolvedRepositoryEntryDict,
)
from gen_epix.commondb.domain.enum import (
    AppType,
    AppTypeSet,
    DevIdpConfig,
    DevRepositoryConfig,
)
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.util import (
    create_demo_data_from_repository,
    get_app_cfg_class,
    set_env_variables,
)
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository

CONNECTION_TIMEOUT: float = 1
ALEMBIC_SCHEMA = "alembic"
RESET_DATABASE_MODE_ALIASES = frozenset(
    {"empty", "false", "0", "no", "off", "reset_database"}
)


def _parse_mode(raw_mode: str | None) -> str:
    """Map the trailing CLI argument to a canonical MODE, aliases included."""
    if raw_mode is not None and raw_mode.lower() in RESET_DATABASE_MODE_ALIASES:
        return "reset_database"
    if raw_mode is not None and raw_mode.lower() == "migrate":
        return "migrate"
    return "load_demodata"


def _restore_env(key: str, value: str | None) -> None:
    """Restore an environment variable, unsetting it if it was unset before."""
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value


def _connect_args(connection_string: str) -> dict[str, float]:
    """Build dialect-appropriate short connect-timeout kwargs."""
    if "mssql" in connection_string:
        return {"timeout": CONNECTION_TIMEOUT, "login_timeout": CONNECTION_TIMEOUT}
    if "pyodcb" in connection_string:
        return {"connect_timeout": CONNECTION_TIMEOUT, "timeout": CONNECTION_TIMEOUT}
    return {}


def _resolved_cfg_for_app(
    app_type: AppType, app_cfg: AppCfg
) -> ResolvedAppCfgSettingsDict | ResolvedCasedbAppCfgSettingsDict:
    """Return the app-specific resolved cfg type for dynamic repository lookup."""
    if app_type == AppType.CASEDB:
        return cast(ResolvedCasedbAppCfgSettingsDict, app_cfg.cfg)
    return app_cfg.cfg


def _repository_cfg(
    app_type: AppType, app_cfg: AppCfg, service_type_value: str
) -> ResolvedRepositoryEntryDict | None:
    """Return the repository config for a dynamic service type key, if present."""
    resolved_cfg = _resolved_cfg_for_app(app_type, app_cfg)
    if "repository" not in resolved_cfg:
        return None
    return cast(
        Mapping[str, ResolvedRepositoryEntryDict], resolved_cfg["repository"]
    ).get(service_type_value)


def _require_repository_cfg(
    app_type: AppType, app_cfg: AppCfg, service_type_value: str
) -> ResolvedRepositoryEntryDict:
    """Return the repository config for a service type, raising if it is absent."""
    repository_cfg = _repository_cfg(app_type, app_cfg, service_type_value)
    if repository_cfg is None:
        raise KeyError(service_type_value)
    return repository_cfg


def run_migrate(module_root: str, connection_string: str) -> None:
    """Run this service's Alembic migrations up to head.

    Kept as its own function so it can also be wired up as a standalone
    step/job later, independent of ``run_reset_database``.
    """
    alembic_ini = Path(module_root.replace(".", "/")) / "repositories" / "alembic.ini"
    cfg = Config(str(alembic_ini))
    cfg.set_main_option("sqlalchemy.url", connection_string)
    # Every service's sa_alembic/env.py resolves its URL from -x url=/ALEMBIC_URL
    # (not from Config.set_main_option), so that's what actually has to be set.
    previous_alembic_url = os.environ.get("ALEMBIC_URL")
    os.environ["ALEMBIC_URL"] = connection_string
    try:
        command.upgrade(cfg, "head")
    finally:
        _restore_env("ALEMBIC_URL", previous_alembic_url)


def run_reset_database(
    module_root: str,
    app_type: AppType,
    service_type_enum: ModuleType,
    domain: Any,
) -> None:
    """Wipe each service's database, including Alembic tracking, then migrate to head.

    All service types of one app share a single connection string/database
    and a single Alembic revision chain, so the migration itself runs once,
    after every service type's tables have been cleared - not once per
    service type, which would re-drop the just-written alembic_version row
    and make Alembic try to recreate tables that already exist.
    """
    migrate_connection_string: str | None = None
    for service_type in service_type_enum.ServiceType:
        print(f" STARTING RESET FOR {app_type.value} - {service_type.value} =====")

        sa_sql_app_cfg = get_app_cfg_class(app_type)(
            app_type.value,
            service_type_enum.ServiceType,
            service_type_enum.RepositoryType,
            log_setup=False,
        )
        sa_sql_repository_cfg = _repository_cfg(
            app_type, sa_sql_app_cfg, service_type.value
        )
        if not sa_sql_repository_cfg:
            continue
        entities = domain.get_dag_sorted_entities(
            service_type=service_type, persistable=True
        )
        sa_repository_class: type[SARepository] = sa_sql_repository_cfg["class"]
        connection_string = sa_sql_repository_cfg["props"]["connection_string"]

        if sa_repository_class.test_connection(
            connection_string, **_connect_args(connection_string)
        ):
            print(
                f"App {app_type.value}, service {service_type.value}: sa_sql connection failed"
            )
            continue

        sa_repository_class.clear_repository_content(
            entities=entities,
            connection_string=connection_string,
            alembic_schema=ALEMBIC_SCHEMA,
        )
        print(f"App {app_type.value}, service {service_type.value}: database cleared")
        migrate_connection_string = connection_string

    if migrate_connection_string:
        run_migrate(module_root, migrate_connection_string)
        print(f"App {app_type.value}: migrated to head")


def run_migrate_database(
    module_root: str,
    app_type: AppType,
    service_type_enum: ModuleType,
) -> None:
    """Run each service's Alembic migrations up to head, without touching data.

    All service types of one app share a single connection string/database
    and a single Alembic revision chain, so the migration itself runs once,
    not once per service type.
    """
    migrate_connection_string: str | None = None
    for service_type in service_type_enum.ServiceType:
        sa_sql_app_cfg = get_app_cfg_class(app_type)(
            app_type.value,
            service_type_enum.ServiceType,
            service_type_enum.RepositoryType,
            log_setup=False,
        )
        sa_sql_repository_cfg = _repository_cfg(
            app_type, sa_sql_app_cfg, service_type.value
        )
        if not sa_sql_repository_cfg:
            continue
        sa_repository_class: type[SARepository] = sa_sql_repository_cfg["class"]
        connection_string = sa_sql_repository_cfg["props"]["connection_string"]

        if sa_repository_class.test_connection(
            connection_string, **_connect_args(connection_string)
        ):
            print(
                f"App {app_type.value}, service {service_type.value}: sa_sql connection failed"
            )
            continue

        migrate_connection_string = connection_string

    if migrate_connection_string:
        print(f" STARTING MIGRATE FOR {app_type.value} =====")
        run_migrate(module_root, migrate_connection_string)
        print(f"App {app_type.value}: migrated to head")


def run_load_demodata(
    envvar_prefix: str,
    module_root: str,
    app_type: AppType,
    service_type_enum: ModuleType,
    domain: Any,
) -> None:
    """Verify each service's schema, then load demo data into it."""
    original_settings_files_environ = os.environ.get(envvar_prefix + "SETTINGS_FILES")
    original_log_config_file_environ = os.environ.get(envvar_prefix + "LOG_CONFIG_FILE")

    for service_type in service_type_enum.ServiceType:
        print(f" STARTING ETL FOR {app_type.value} - {service_type.value} =====")

        set_env_variables(app_type, DevIdpConfig.MOCK, DevRepositoryConfig.DICT_DEMO)
        _restore_env(
            envvar_prefix + "LOG_CONFIG_FILE", original_log_config_file_environ
        )

        dict_app_cfg = get_app_cfg_class(app_type)(
            app_type.value,
            service_type_enum.ServiceType,
            service_type_enum.RepositoryType,
            log_setup=False,
        )
        dict_repository_cfg = _repository_cfg(app_type, dict_app_cfg, service_type.value)
        if not dict_repository_cfg:
            continue
        entities = domain.get_dag_sorted_entities(
            service_type=service_type, persistable=True
        )
        dict_repository_class: type[DictRepository] = dict_repository_cfg["class"]
        demo_dict_file = Path(dict_repository_cfg["props"]["file"]).resolve()
        zip_file: str = str(demo_dict_file).replace(".pkl.gz", ".zip")
        dict_repository: DictRepository = (
            dict_repository_class.create_repository(  # type: ignore[assignment]
                entities=entities, file=zip_file
            )
        )

        _restore_env(envvar_prefix + "SETTINGS_FILES", original_settings_files_environ)
        _restore_env(
            envvar_prefix + "LOG_CONFIG_FILE", original_log_config_file_environ
        )

        sa_sql_app_cfg = get_app_cfg_class(app_type)(
            app_type.value,
            service_type_enum.ServiceType,
            service_type_enum.RepositoryType,
            log_setup=False,
        )
        sa_sql_repository_cfg = _require_repository_cfg(
            app_type, sa_sql_app_cfg, service_type.value
        )
        sa_repository_class: type[SARepository] = sa_sql_repository_cfg["class"]
        connection_string = sa_sql_repository_cfg["props"]["connection_string"]

        if sa_repository_class.test_connection(
            connection_string, **_connect_args(connection_string)
        ):
            print(
                f"App {app_type.value}, service {service_type.value}: sa_sql connection failed"
            )
            continue

        problems = sa_repository_class.check_schema_matches(
            entities=entities, connection_string=connection_string
        )
        if problems:
            print(
                f"App {app_type.value}, service {service_type.value}: "
                "schema mismatch, cannot load demo data:"
            )
            for problem in problems:
                print(f"  - {problem}")
            alembic_ini = (
                Path(module_root.replace(".", "/")) / "repositories" / "alembic.ini"
            )
            print(
                "Has the Alembic migration been run for this database? "
                f"(alembic -c {alembic_ini} upgrade head)"
            )
            sys.exit(1)

        start_time = datetime.datetime.now(datetime.timezone.utc)
        sa_sql_repository: SARepository = (
            sa_repository_class.create_repository(  # type: ignore[assignment]
                entities=entities,
                connection_string=connection_string,
                name=service_type.value,
            )
        )
        user_id = sa_sql_app_cfg.cfg["service"]["auth"]["props"]["root"]["user"].get(
            "id", NULL_ID
        )
        create_demo_data_from_repository(
            user_id, entities, dict_repository, sa_sql_repository, module_root
        )
        end_time = datetime.datetime.now(datetime.timezone.utc)
        print(
            f"App {app_type.value}, service {service_type.value}: sa_sql repository loaded in {end_time - start_time}s"
        )


def main() -> None:
    """Parse CLI arguments and dispatch to the matching MODE handler."""
    if len(sys.argv) not in (4, 5):
        print("Usage: etl.py ENVVAR_PREFIX MODULE_ROOT APP_TYPE [MODE]")
        print("Example: etl.py CASEDB_ gen_epix.casedb CASEDB")
        print(
            "MODE is 'load_demodata' (default) or 'reset_database' "
            "(legacy aliases: empty, false, 0, no, off)"
        )
        print("Example: etl.py CASEDB_ gen_epix.casedb CASEDB reset_database")
        sys.exit(1)

    envvar_prefix = str(sys.argv[1])  # "CASEDB_"
    module_root = str(sys.argv[2])  # "gen_epix.casedb"
    app_type = AppType[sys.argv[3]]  # AppType.CASEDB
    mode = _parse_mode(sys.argv[4] if len(sys.argv) == 5 else None)

    if not envvar_prefix.isupper() or not envvar_prefix.endswith("_"):
        raise ValueError(f"Invalid envvar prefix: {envvar_prefix}")

    if not module_root.startswith("gen_epix."):
        raise ValueError(f"Invalid module root: {module_root}")

    if app_type not in AppTypeSet.ALL.value:
        raise ValueError(f"Invalid app type: {app_type}")

    importlib.import_module(f"{module_root}.repositories.sa_model")
    service_type_enum = importlib.import_module(f"{module_root}.domain.enum")
    domain = importlib.import_module(f"{module_root}.domain").DOMAIN

    print(f" ===== {mode.upper()} STARTED FOR {app_type.value} =====")
    if mode == "reset_database":
        run_reset_database(module_root, app_type, service_type_enum, domain)
    elif mode == "migrate":
        run_migrate_database(module_root, app_type, service_type_enum)
    else:
        run_load_demodata(
            envvar_prefix, module_root, app_type, service_type_enum, domain
        )


if __name__ == "__main__":
    main()
