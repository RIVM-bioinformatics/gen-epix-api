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

Every mode first resolves the SQLAlchemy repository config of all service
types and waits, with retries up to ``DB_WAKE_TIMEOUT_SECONDS``, until each
distinct database is reachable (an Azure SQL serverless database needs about a
minute to resume from auto-pause). Nothing is changed before then. Any
failure, including a database that stays unreachable, exits non-zero.

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
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import tenacity
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

# Login timeout of a single connection attempt, in seconds.
CONNECTION_TIMEOUT: float = 30
# Deadline for a database to become reachable, and the wait between attempts.
# Read at call time, so tests can override them.
DB_WAKE_TIMEOUT_SECONDS: float = 300
DB_WAKE_WAIT: tenacity.wait.wait_base = tenacity.wait_exponential(multiplier=2, max=30)
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
    """Build dialect-appropriate login-timeout kwargs for a connection attempt."""
    if "mssql" in connection_string:
        # pyodbc's login timeout; unknown keywords would end up in the ODBC
        # connection string instead.
        return {"timeout": CONNECTION_TIMEOUT}
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


@dataclass(frozen=True)
class _SaTarget:
    """The SQLAlchemy repository of one service type, resolved from the app cfg.

    Attributes:
        service_type: Member of the app's ``ServiceType`` enum.
        repository_class: SARepository class configured for the service type.
        connection_string: SQLAlchemy URL of the service type's database.
    """

    service_type: Any
    repository_class: type[SARepository]
    connection_string: str


def _resolve_sa_targets(
    app_type: AppType, service_type_enum: ModuleType
) -> list[_SaTarget]:
    """Resolve the SA repository of every service type that has one, without DB access.

    Args:
        app_type: App to resolve the repositories for.
        service_type_enum: The app's ``domain.enum`` module, providing
            ``ServiceType`` and ``RepositoryType``.

    Returns:
        One target per service type with a repository config, in
        ``ServiceType`` order.
    """
    app_cfg = get_app_cfg_class(app_type)(
        app_type.value,
        service_type_enum.ServiceType,
        service_type_enum.RepositoryType,
        log_setup=False,
    )
    targets: list[_SaTarget] = []
    for service_type in service_type_enum.ServiceType:
        repository_cfg = _repository_cfg(app_type, app_cfg, service_type.value)
        if not repository_cfg:
            continue
        targets.append(
            _SaTarget(
                service_type=service_type,
                repository_class=cast(type[SARepository], repository_cfg["class"]),
                connection_string=repository_cfg["props"]["connection_string"],
            )
        )
    return targets


def _distinct_connection_strings(targets: list[_SaTarget]) -> list[str]:
    """Return the targets' distinct connection strings, in first-seen order."""
    return list(dict.fromkeys(target.connection_string for target in targets))


def _wait_for_database(
    app_type: AppType,
    repository_class: type[SARepository],
    connection_string: str,
    service_type_values: list[str],
) -> None:
    """Probe a database until it accepts a connection, or exit when the deadline passes.

    Each failed attempt is printed with its exception, so the job log shows a
    database that is waking up. The connection string is never printed, since
    it contains the password.

    Args:
        app_type: App the database belongs to, for the log lines.
        repository_class: SARepository class whose ``test_connection`` probes
            the database.
        connection_string: SQLAlchemy URL of the database.
        service_type_values: Service types that use the database, for the log
            lines.

    Raises:
        SystemExit: With code 1 if the database is not reachable within
            ``DB_WAKE_TIMEOUT_SECONDS``.
    """
    label = f"App {app_type.value}, service(s) {', '.join(service_type_values)}"

    def _print_failed_attempt(retry_state: tenacity.RetryCallState) -> None:
        exception = retry_state.outcome.result() if retry_state.outcome else None
        elapsed = retry_state.seconds_since_start or 0.0
        print(
            f"{label}: database not reachable yet "
            f"(attempt {retry_state.attempt_number}, {elapsed:.0f}s): {exception}"
        )

    retrying = tenacity.Retrying(
        retry=tenacity.retry_if_result(lambda exception: exception is not None),
        stop=tenacity.stop_after_delay(DB_WAKE_TIMEOUT_SECONDS),
        wait=DB_WAKE_WAIT,
        before_sleep=_print_failed_attempt,
    )
    try:
        retrying(
            repository_class.test_connection,
            connection_string,
            **_connect_args(connection_string),
        )
    except tenacity.RetryError as retry_error:
        print(
            f"{label}: database not reachable within {DB_WAKE_TIMEOUT_SECONDS:.0f}s "
            f"({retry_error.last_attempt.attempt_number} attempts), giving up. "
            f"Last error: {retry_error.last_attempt.result()}"
        )
        sys.exit(1)
    attempts = retrying.statistics.get("attempt_number", 1)
    if attempts > 1:
        print(f"{label}: database reachable after {attempts} attempts")


def _wait_for_databases(app_type: AppType, targets: list[_SaTarget]) -> None:
    """Wait once for each distinct database the targets use, in order.

    Raises:
        SystemExit: With code 1 if one of the databases stays unreachable.
    """
    for connection_string in _distinct_connection_strings(targets):
        group = [t for t in targets if t.connection_string == connection_string]
        _wait_for_database(
            app_type,
            group[0].repository_class,
            connection_string,
            [target.service_type.value for target in group],
        )


def _exit_on_schema_problems(
    app_type: AppType,
    service_type_value: str,
    problems: list[str],
    context: str,
    module_root: str | None = None,
) -> None:
    """Print the schema problems of a service type and exit, if there are any.

    Args:
        app_type: App the service type belongs to.
        service_type_value: Service type whose schema was checked.
        problems: Result of ``SARepository.check_schema_matches`` or
            ``SARepository.find_remaining_content``; empty means there is
            nothing wrong and nothing happens.
        context: What the mismatch means, appended to the header line.
        module_root: If given, also print the ``alembic upgrade head`` command
            for this module, as a hint that the migration may not have run.

    Raises:
        SystemExit: With code 1 if ``problems`` is not empty.
    """
    if not problems:
        return
    print(
        f"App {app_type.value}, service {service_type_value}: "
        f"schema mismatch, {context}:"
    )
    for problem in problems:
        print(f"  - {problem}")
    if module_root is not None:
        alembic_ini = (
            Path(module_root.replace(".", "/")) / "repositories" / "alembic.ini"
        )
        print(
            "Has the Alembic migration been run for this database? "
            f"(alembic -c {alembic_ini} upgrade head)"
        )
    sys.exit(1)


def _exit_if_no_targets(app_type: AppType, targets: list[_SaTarget]) -> None:
    """Exit non-zero if no service type has an SA repository, so nothing would happen."""
    if not targets:
        print(
            f"App {app_type.value}: no service type has an SA repository config, "
            "nothing to do"
        )
        sys.exit(1)


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

    Every database is waited for before any service type is cleared, so a
    database that is still resuming cannot leave a half-cleared reset behind.
    All service types of one app share a single connection string/database
    and a single Alembic revision chain, so the migration itself runs once,
    after every service type's tables have been cleared - not once per
    service type, which would re-drop the just-written alembic_version row
    and make Alembic try to recreate tables that already exist. Because
    ``clear_repository_content`` ignores most errors, the clear is verified
    before the migration (no entity table and no ``alembic_version`` left), and
    the schema of every service type is checked against its entities after it.

    Raises:
        SystemExit: With code 1 if no service type has an SA repository, a
            database stays unreachable, a table is left after clearing, or a
            schema does not match after the migration.
    """
    targets = _resolve_sa_targets(app_type, service_type_enum)
    _exit_if_no_targets(app_type, targets)
    _wait_for_databases(app_type, targets)

    entities_per_target = [
        (
            target,
            domain.get_dag_sorted_entities(
                service_type=target.service_type, persistable=True
            ),
        )
        for target in targets
    ]
    for target, entities in entities_per_target:
        service_type_value = target.service_type.value
        print(f" STARTING RESET FOR {app_type.value} - {service_type_value} =====")
        target.repository_class.clear_repository_content(
            entities=entities,
            connection_string=target.connection_string,
            alembic_schema=ALEMBIC_SCHEMA,
        )

    for target, entities in entities_per_target:
        service_type_value = target.service_type.value
        remaining = target.repository_class.find_remaining_content(
            entities=entities,
            connection_string=target.connection_string,
            alembic_schema=ALEMBIC_SCHEMA,
        )
        _exit_on_schema_problems(
            app_type, service_type_value, remaining, "reset could not clear it"
        )
        print(f"App {app_type.value}, service {service_type_value}: database cleared")

    for connection_string in _distinct_connection_strings(targets):
        run_migrate(module_root, connection_string)
    print(f"App {app_type.value}: migrated to head")

    for target, entities in entities_per_target:
        problems = target.repository_class.check_schema_matches(
            entities=entities, connection_string=target.connection_string
        )
        _exit_on_schema_problems(
            app_type,
            target.service_type.value,
            problems,
            "reset did not produce the expected schema",
        )


def run_migrate_database(
    module_root: str,
    app_type: AppType,
    service_type_enum: ModuleType,
) -> None:
    """Run each service's Alembic migrations up to head, without touching data.

    All service types of one app share a single connection string/database
    and a single Alembic revision chain, so the migration itself runs once,
    not once per service type.

    Raises:
        SystemExit: With code 1 if no service type has an SA repository or a
            database stays unreachable.
    """
    targets = _resolve_sa_targets(app_type, service_type_enum)
    _exit_if_no_targets(app_type, targets)
    _wait_for_databases(app_type, targets)

    print(f" STARTING MIGRATE FOR {app_type.value} =====")
    for connection_string in _distinct_connection_strings(targets):
        run_migrate(module_root, connection_string)
    print(f"App {app_type.value}: migrated to head")


def run_load_demodata(
    envvar_prefix: str,
    module_root: str,
    app_type: AppType,
    service_type_enum: ModuleType,
    domain: Any,
) -> None:
    """Verify each service's schema, then load demo data into it.

    Every database is waited for first, with the job's own environment,
    before the loop switches the environment to the demo dict repositories.

    Raises:
        SystemExit: With code 1 if a database stays unreachable, a service
            type's SA connection string differs from the one waited for, or a
            schema does not match its entities.
    """
    original_settings_files_environ = os.environ.get(envvar_prefix + "SETTINGS_FILES")
    original_log_config_file_environ = os.environ.get(envvar_prefix + "LOG_CONFIG_FILE")

    sa_targets = _resolve_sa_targets(app_type, service_type_enum)
    _wait_for_databases(app_type, sa_targets)
    sa_target_by_service_type = {target.service_type: target for target in sa_targets}

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
        dict_repository_cfg = _repository_cfg(
            app_type, dict_app_cfg, service_type.value
        )
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

        # The loop's environment differs slightly from the one the databases
        # were waited for with, so make sure it still points at the same one.
        sa_target = sa_target_by_service_type.get(service_type)
        if sa_target is None or sa_target.connection_string != connection_string:
            print(
                f"App {app_type.value}, service {service_type.value}: SA connection "
                "string differs from the one checked before loading, cannot load "
                "demo data"
            )
            sys.exit(1)

        problems = sa_repository_class.check_schema_matches(
            entities=entities, connection_string=connection_string
        )
        _exit_on_schema_problems(
            app_type,
            service_type.value,
            problems,
            "cannot load demo data",
            module_root=module_root,
        )

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
            "MODE is 'load_demodata' (default), 'migrate' or 'reset_database' "
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
