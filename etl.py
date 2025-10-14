import datetime
import os
import sys
from pathlib import Path
from typing import Type

from gen_epix.casedb import domain
from gen_epix.casedb.domain.enum import RepositoryType, ServiceType
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain.enum import (
    AppType,
    AppTypeSet,
    DevIdpConfig,
    DevRepositoryConfig,
)
from gen_epix.commondb.util import create_demo_data_from_repository, set_env_variables
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository

if len(sys.argv) != 4:
    print("Usage: etl.py ENVVAR_PREFIX MODULE_ROOT APP_TYPE")
    print("Example: etl.py CASEDB_ gen_epix.casedb CASEDB")
    sys.exit(1)

ENVVAR_PREFIX = str(sys.argv[1]) #"CASEDB_"
MODULE_ROOT = str(sys.argv[2]) # "gen_epix.casedb"
APP_TYPE = AppType[sys.argv[3]] # AppType.CASEDB
CONNECTION_TIMEOUT: float = 1

if not ENVVAR_PREFIX.isupper() or not ENVVAR_PREFIX.endswith("_"):
    raise ValueError(f"Invalid envvar prefix: {ENVVAR_PREFIX}")

if not MODULE_ROOT.startswith("gen_epix."):
    raise ValueError(f"Invalid module root: {MODULE_ROOT}")

if APP_TYPE not in AppTypeSet.ALL.value:
    raise ValueError(f"Invalid app type: {APP_TYPE}")

original_settings_files_environ = os.environ.get(ENVVAR_PREFIX + "SETTINGS_FILES")
original_log_config_file_environ = os.environ.get(
    ENVVAR_PREFIX + "LOG_CONFIG_FILE"
)

for service_type in ServiceType:
    set_env_variables(APP_TYPE, DevIdpConfig.MOCK, DevRepositoryConfig.DICT_DEMO)
    os.environ[ENVVAR_PREFIX + "LOG_CONFIG_FILE"] = original_log_config_file_environ

    dict_app_cfg = AppCfg(
        APP_TYPE.value, ServiceType, RepositoryType, log_setup=False
    )
    dict_repository_cfg = dict_app_cfg.cfg["repository"].get(service_type.value)
    if not dict_repository_cfg:
        continue
    entities = domain.DOMAIN.get_dag_sorted_entities(
        service_type=service_type, persistable=True
    )
    # Create dict repository, which is assumed to always be available
    dict_repository_class: Type[DictRepository] = dict_repository_cfg["class"]
    demo_dict_file = Path(dict_repository_cfg["props"]["file"]).resolve()
    empty_dict_file = Path(
        str(demo_dict_file).replace(".full.", ".empty.")
    ).resolve()
    zip_file: str = str(demo_dict_file).replace(".pkl.gz", ".zip")
    start_time = datetime.datetime.now()
    dict_repository: DictRepository = (
        dict_repository_class.create_repository(  # type:ignore[assignment]
            entities=entities, file=zip_file
        )
    )

    os.environ[ENVVAR_PREFIX + "SETTINGS_FILES"] = original_settings_files_environ
    os.environ[ENVVAR_PREFIX + "LOG_CONFIG_FILE"] = original_log_config_file_environ

    sa_sql_app_cfg = AppCfg(
        APP_TYPE.value, ServiceType, RepositoryType, log_setup=False
    )
    # Create empty SA_SQL repository or loaded with demo data
    sa_sql_repository_cfg = sa_sql_app_cfg.cfg["repository"][service_type.value]
    sa_repository_class: Type[SARepository] = sa_sql_repository_cfg["class"]
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
            # f"App {app_type.value}, service {service_type.value}: sa_sql connection failed: {exception}"
            f"App {APP_TYPE.value}, service {service_type.value}: sa_sql connection failed"
        )
        continue

    start_time = datetime.datetime.now()
    sa_sql_repository: SARepository = (
        sa_repository_class.create_repository(  # type:ignore[assignment]
            entities=entities,
            connection_string=connection_string,
            name=service_type.value,
        )
    )
    user_id = sa_sql_repository_cfg["service"]["auth"]["props"]["root"]["user"]["id"]
    create_demo_data_from_repository(user_id, entities, dict_repository, sa_sql_repository, MODULE_ROOT)
    end_time = datetime.datetime.now()
    print(
        f"App {APP_TYPE.value}, service {service_type.value}: sa_sql repository loaded in {end_time - start_time}s"
    )
