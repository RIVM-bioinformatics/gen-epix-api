import datetime
import gzip
import importlib
import pickle
from enum import Enum
from pathlib import Path
from typing import Type

import pandas as pd

from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
from gen_epix.commondb.util import generate_ulid, set_env_variables
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.repositories.dict import DictRepository
from gen_epix.fastapp.repositories.sa import SARepository


def get_test_name(test_type: Enum | str) -> str:
    return (
        datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        + "_"
        + (test_type if isinstance(test_type, str) else test_type.value)
    )


def get_test_root_output_dir() -> Path:
    dir = Path(__file__).parent.parent / "output"
    dir.mkdir(parents=True, exist_ok=True)
    return dir


def get_test_output_dir(test_name: str) -> Path:
    output_dir = get_test_root_output_dir() / test_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_uuids(n_rows: int = 1000, n_cols: int = 100) -> None:
    df = pd.DataFrame.from_dict(
        {f"uuid{i}": [generate_ulid() for j in range(n_rows)] for i in range(100)}
    )
    xls_file = Path(__file__).parent.parent / "output" / "generated_uuids.xlsx"
    df.to_excel(xls_file, sheet_name="uuid", index=False)
    print(
        f"Total of {n_rows} uuids times {df.shape[1]} columns generated and written to file {str(xls_file)}"
    )


def load_demo_data(
    app_type: AppType,
    module_root: str,
    connect_timeout: float = 1,
    verbose: bool = True,
) -> None:

    def _create_from_repository(
        user_id: str,
        entities: list,
        dict_repository: DictRepository,
        sa_repository: SARepository,
    ) -> None:
        # Delete all first in reverse order
        for entity in entities[::-1]:
            model_class = entity.model_class
            with sa_repository.uow() as sa_uow:
                sa_repository.crud(
                    sa_uow,
                    user_id,
                    model_class,
                    None,
                    None,
                    CrudOperation.DELETE_ALL,
                )
        for entity in entities:
            model_class = entity.model_class
            with (
                dict_repository.uow() as dict_uow,
                sa_repository.uow() as sa_uow,
            ):
                objs: list[model.Model] = dict_repository.crud(  # type: ignore[assignment]
                    dict_uow,
                    user_id,
                    model_class,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    return_copy=False,
                )
                sa_repository.crud(
                    sa_uow,
                    user_id,
                    model_class,
                    objs,
                    None,
                    CrudOperation.CREATE_SOME,
                )

    # Import the sa_model module to register the models
    importlib.import_module(f"{module_root}.repositories.sa_model")
    # Get classes and config for the app type
    enum = importlib.import_module(f"{module_root}.domain.enum")
    model = importlib.import_module(f"{module_root}.domain.model")
    domain: Domain = importlib.import_module(f"{module_root}.domain").DOMAIN
    set_env_variables(app_type, DevIdpConfig.MOCK, DevRepositoryConfig.DICT_DEMO)
    dict_app_cfg = AppCfg(
        app_type.value, enum.ServiceType, enum.RepositoryType, log_setup=False
    )
    set_env_variables(app_type, DevIdpConfig.MOCK, DevRepositoryConfig.SA_SQLITE_DEMO)
    sa_sqlite_app_cfg = AppCfg(
        app_type.value, enum.ServiceType, enum.RepositoryType, log_setup=False
    )
    set_env_variables(app_type, DevIdpConfig.MOCK, DevRepositoryConfig.SA_SQL)
    sa_sql_app_cfg = AppCfg(
        app_type.value, enum.ServiceType, enum.RepositoryType, log_setup=False
    )
    user_id = dict_app_cfg.cfg["service"]["auth"]["props"]["root"]["user"]["id"]
    for service_type in enum.ServiceType:
        # # TODO: TEMPORARY for debugging, remove later
        # if service_type.value != "CASE":
        #     continue
        dict_repository_cfg = dict_app_cfg.cfg["repository"].get(service_type.value)
        if not dict_repository_cfg:
            continue
        entities = domain.get_dag_sorted_entities(
            service_type=service_type, persistable=True
        )
        # Create dict repository, which is assumed to always be available
        dict_repository_class: Type[DictRepository] = dict_repository_cfg["class"]
        demo_dict_file = Path(dict_repository_cfg["props"]["file"]).absolute()
        empty_dict_file = Path(
            str(demo_dict_file).replace(".full.", ".empty.")
        ).absolute()
        zip_file: str = str(demo_dict_file).replace(".pkl.gz", ".zip")
        start_time = datetime.datetime.now()
        dict_repository: DictRepository = (
            dict_repository_class.create_repository(  # type:ignore[assignment]
                entities=entities, file=zip_file
            )
        )
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: demo data parsed in {end_time - start_time}s"
            )
        # Write empty and demo dict repository to file
        start_time = datetime.datetime.now()
        with gzip.open(empty_dict_file, "wb") as handle:
            pickle.dump({x: {} for x in dict_repository.db}, handle)
        with gzip.open(demo_dict_file, "wb") as handle:
            pickle.dump(dict_repository.db, handle)
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: dict repository written to file in {end_time - start_time}s"
            )
        # Create empty and demo SA_SQLITE repositories
        sa_sqlite_repository_cfg = sa_sqlite_app_cfg.cfg["repository"][
            service_type.value
        ]
        sa_repository_class: Type[SARepository] = sa_sqlite_repository_cfg["class"]
        demo_sa_sqlite_file = Path(sa_sqlite_repository_cfg["props"]["file"]).absolute()
        empty_sa_sqlite_file = Path(
            str(demo_sa_sqlite_file).replace(".full", ".empty")
        ).absolute()
        start_time = datetime.datetime.now()
        # Empty repository
        sa_repository_class.create_repository(
            entities=entities,
            file=empty_sa_sqlite_file,
            name=service_type.value,
            recreate_sqlite_file=True,
        )
        # Full repository
        sa_sqlite_repository: SARepository = (
            sa_repository_class.create_repository(  # type:ignore[assignment]
                entities=entities,
                file=demo_sa_sqlite_file,
                name=service_type.value,
                recreate_sqlite_file=True,
            )
        )
        _create_from_repository(
            user_id, entities, dict_repository, sa_sqlite_repository
        )
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: sa_sqlite repository written to file in {end_time - start_time}s"
            )
        # Create empty SA_SQL repository or loaded with demo data
        sa_sql_repository_cfg = sa_sql_app_cfg.cfg["repository"][service_type.value]
        connection_string = sa_sql_repository_cfg["props"]["connection_string"]
        if "mssql" in connection_string:
            connect_args = {
                "timeout": connect_timeout,
                "login_timeout": connect_timeout,
            }
        elif "pyodcb" in connection_string:
            connect_args = {
                "connect_timeout": connect_timeout,
                "timeout": connect_timeout,
            }
        else:
            connect_args = {}
        # Skip load if no connection can be made
        if exception := sa_repository_class.test_connection(
            connection_string, **connect_args
        ):
            if verbose:
                print(
                    # f"App {app_type.value}, service {service_type.value}: sa_sql connection failed: {exception}"
                    f"App {app_type.value}, service {service_type.value}: sa_sql connection failed"
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
        _create_from_repository(user_id, entities, dict_repository, sa_sql_repository)
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: sa_sql repository loaded in {end_time - start_time}s"
            )
