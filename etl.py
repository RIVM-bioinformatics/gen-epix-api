"""
ETL (Extract, Transform, Load) script for Gen-EpiX genomic epidemiology platform.

This module performs data loading operations between different repository types
(dictionary-based and SQLAlchemy-based) for Gen-EpiX services. It transfers
demo data from dictionary repositories to SQL repositories, enabling testing
and development with realistic datasets.

Usage:
    python etl.py ENVVAR_PREFIX MODULE_ROOT APP_TYPE

Examples:
    python etl.py CASEDB_ gen_epix.casedb CASEDB
    python etl.py SEQDB_ gen_epix.seqdb SEQDB
    python etl.py OMOPDB_ gen_epix.omopdb OMOPDB

The script:
1. Loads demo data from dictionary repositories (file-based)
2. Creates corresponding SQLAlchemy repositories (database-based)
3. Transfers data between repositories using the service's domain entities
4. Handles connection testing and error reporting for database operations

This enables seamless migration of demo data from development dictionary
repositories to production SQL repositories across all Gen-EpiX services.
"""

import datetime
import importlib
import os
import sys
from pathlib import Path

from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain.enum import (AppType, AppTypeSet, DevIdpConfig,
                                           DevRepositoryConfig)
from gen_epix.commondb.domain.util import (create_demo_data_from_repository,
                                           set_env_variables)
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository

if len(sys.argv) != 4:
    print("Usage: etl.py ENVVAR_PREFIX MODULE_ROOT APP_TYPE")
    print("Example: etl.py CASEDB_ gen_epix.casedb CASEDB")
    sys.exit(1)

ENVVAR_PREFIX = str(sys.argv[1])  # "CASEDB_"
MODULE_ROOT = str(sys.argv[2])  # "gen_epix.casedb"
APP_TYPE = AppType[sys.argv[3]]  # AppType.CASEDB
CONNECTION_TIMEOUT: float = 1

importlib.import_module(f"{MODULE_ROOT}.repositories.sa_model")
enum = importlib.import_module(f"{MODULE_ROOT}.domain.enum")
domain = importlib.import_module(f"{MODULE_ROOT}.domain").DOMAIN

if not ENVVAR_PREFIX.isupper() or not ENVVAR_PREFIX.endswith("_"):
    raise ValueError(f"Invalid envvar prefix: {ENVVAR_PREFIX}")

if not MODULE_ROOT.startswith("gen_epix."):
    raise ValueError(f"Invalid module root: {MODULE_ROOT}")

if APP_TYPE not in AppTypeSet.ALL.value:
    raise ValueError(f"Invalid app type: {APP_TYPE}")

original_settings_files_environ = os.environ.get(ENVVAR_PREFIX + "SETTINGS_FILES")
original_log_config_file_environ = os.environ.get(ENVVAR_PREFIX + "LOG_CONFIG_FILE")

print(f" ===== ETL STARTED FOR {APP_TYPE.value} =====")

for service_type in enum.ServiceType:
    print(f" STARTING ETL FOR {APP_TYPE.value} - {service_type.value} =====")

    set_env_variables(APP_TYPE, DevIdpConfig.MOCK, DevRepositoryConfig.DICT_DEMO)
    os.environ[ENVVAR_PREFIX + "LOG_CONFIG_FILE"] = original_log_config_file_environ

    dict_app_cfg = AppCfg(
        APP_TYPE.value, enum.ServiceType, enum.RepositoryType, log_setup=False
    )
    dict_repository_cfg = dict_app_cfg.cfg["repository"].get(service_type.value)
    if not dict_repository_cfg:
        continue
    entities = domain.get_dag_sorted_entities(
        service_type=service_type, persistable=True
    )
    # Create dict repository, which is assumed to always be available
    dict_repository_class: type[DictRepository] = dict_repository_cfg["class"]
    demo_dict_file = Path(dict_repository_cfg["props"]["file"]).resolve()
    empty_dict_file = Path(str(demo_dict_file).replace(".full.", ".empty.")).resolve()
    zip_file: str = str(demo_dict_file).replace(".pkl.gz", ".zip")
    start_time = datetime.datetime.now(datetime.timezone.utc)
    dict_repository: DictRepository = (
        dict_repository_class.create_repository(  # type: ignore[assignment]
            entities=entities, file=zip_file
        )
    )

    os.environ[ENVVAR_PREFIX + "SETTINGS_FILES"] = original_settings_files_environ
    os.environ[ENVVAR_PREFIX + "LOG_CONFIG_FILE"] = original_log_config_file_environ

    sa_sql_app_cfg = AppCfg(
        APP_TYPE.value, enum.ServiceType, enum.RepositoryType, log_setup=False
    )
    # Create empty SA_SQL repository or loaded with demo data
    sa_sql_repository_cfg = sa_sql_app_cfg.cfg["repository"][service_type.value]
    sa_repository_class: type[SARepository] = sa_sql_repository_cfg["class"]
    connection_string = sa_sql_repository_cfg["props"]["connection_string"]
    if "mssql" in connection_string:
        connect_args = {
            "timeout": CONNECTION_TIMEOUT,
            "login_timeout": CONNECTION_TIMEOUT,
        }
    elif "pyodcb" in connection_string:
        connect_args = {
            "connect_timeout": CONNECTION_TIMEOUT,
            "timeout": CONNECTION_TIMEOUT,
        }
    else:
        connect_args = {}
    # Skip load if no connection can be made
    if exception := sa_repository_class.test_connection(
        connection_string, **connect_args
    ):
        print(
            f"App {APP_TYPE.value}, service {service_type.value}: sa_sql connection failed"
        )
        continue

    start_time = datetime.datetime.now(datetime.timezone.utc)
    sa_repository_class.clear_repository_content(
        entities=entities, connection_string=connection_string
    )
    sa_sql_repository: SARepository = (
        sa_repository_class.create_repository(  # type: ignore[assignment]
            entities=entities,
            connection_string=connection_string,
            name=service_type.value,
        )
    )
    user_id = sa_sql_app_cfg.cfg["service"]["auth"]["props"]["root"]["user"]["id"]
    create_demo_data_from_repository(
        user_id, entities, dict_repository, sa_sql_repository, MODULE_ROOT
    )
    end_time = datetime.datetime.now(datetime.timezone.utc)
    print(
        f"App {APP_TYPE.value}, service {service_type.value}: sa_sql repository loaded in {end_time - start_time}s"
    )
