import datetime
import gzip
import importlib
import pickle
import re
import shutil
from enum import Enum
from pathlib import Path
from typing import Hashable

import pandas as pd

from gen_epix.common.config.cfg import AppCfg
from gen_epix.common.domain.enum import AppType
from gen_epix.common.test.enum import RepositoryType
from gen_epix.common.util import generate_ulid
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.repositories.dict import DictRepository
from gen_epix.fastapp.repositories.sa import SARepository


def create_data_fixture(
    repository_cfg: dict,
    services: set[Hashable],
    repository_type: RepositoryType,
    load_target: str,
    test_dir: Path,
) -> None:
    for service_type in services:
        service_type_str = (
            str(service_type.value)
            if isinstance(service_type, Enum)
            else str(service_type)
        )
        curr_cfg = repository_cfg[service_type_str]
        if not curr_cfg:
            # No repository
            continue
        match repository_type:
            case RepositoryType.DICT:
                curr_cfg["file"] = re.sub(
                    r"\.[A-Za-z]+\.pkl\.gz",
                    f".{load_target.lower()}.pkl.gz",
                    curr_cfg["file"],
                    flags=re.IGNORECASE,
                )
            case RepositoryType.SA_SQLITE:
                # Copy sqlite files to test output directory
                source_file = Path(
                    re.sub(
                        r"\.[A-Za-z]+\.sqlite",
                        f".{load_target.lower()}.sqlite",
                        curr_cfg["file"],
                        flags=re.IGNORECASE,
                    )
                )
                if not source_file.is_file():
                    continue
                target_file = test_dir / source_file.name
                curr_cfg["file"] = str(target_file.absolute())
                shutil.copyfile(source_file, target_file)
            case RepositoryType.SA_SQL:
                # Nothing to do
                pass
            case _:
                raise NotImplementedError(
                    f"repository_type {repository_type} not implemented"
                )


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

    # Get classes and config for the app type
    enum = importlib.import_module(f"{module_root}.domain.enum")
    model = importlib.import_module(f"{module_root}.domain.model")
    domain: Domain = importlib.import_module(f"{module_root}.domain").DOMAIN
    cfg = AppCfg(app_type.value, enum.ServiceType, enum.RepositoryType)
    service_data: dict[Enum, dict] = importlib.import_module(
        f"{module_root}.env"
    ).AppEnv.SERVICE_DATA
    user_id = cfg.cfg.SECRET.root.user.id
    for service_type, data in service_data.items():
        # # TODO: TEMPORARY for debugging, remove later
        # if service_type.value != "CASE":
        #     continue
        if "repository_class" not in data:
            continue
        entities = domain.get_dag_sorted_entities(
            service_type=service_type, persistable=True
        )
        # Create dict repository, which is assumed to always be available
        dict_repository_class: DictRepository = data["repository_class"][
            enum.RepositoryType.DICT
        ]
        repository_cfg = cfg.cfg.SECRET.repository.dict[service_type.value]
        file = Path(repository_cfg["file"]).absolute()
        zip_file: str = str(file).replace(".pkl.gz", ".zip")
        start_time = datetime.datetime.now()
        dict_repository = dict_repository_class.from_json(
            dict_repository_class, entities, zip_file
        )
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: demo data parsed in {end_time - start_time}s"
            )
        # Write empty and demo dict repository to file
        start_time = datetime.datetime.now()
        with gzip.open(str(file).replace(".full.", ".empty."), "wb") as handle:
            pickle.dump({x: {} for x in dict_repository._db}, handle)
        with gzip.open(file, "wb") as handle:
            pickle.dump(dict_repository._db, handle)
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: dict repository written to file in {end_time - start_time}s"
            )
        # Create empty and demo SA_SQLITE repositories
        repository_cfg = cfg.cfg.SECRET.repository.sa_sqlite[service_type.value]
        file = Path(repository_cfg["file"]).absolute()
        connection_string = "sqlite:///" + str(file.as_posix())
        sa_repository_class: SARepository = data["repository_class"][
            enum.RepositoryType.SA_SQL
        ]
        start_time = datetime.datetime.now()
        # Empty repository
        sa_repository_class.create_sa_repository(
            entities,
            connection_string.replace(".full.", ".empty."),
            name=service_type.value,
        )
        # Full repository
        sa_repository = sa_repository_class.create_sa_repository(
            entities,
            connection_string,
            name=service_type.value,
            recreate_sqlite_file=True,
        )
        _create_from_repository(user_id, entities, dict_repository, sa_repository)
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: sa_sqlite repository written to file in {end_time - start_time}s"
            )
        # Create empty SA_SQL repository or loaded with demo data
        repository_cfg = cfg.cfg.SECRET.repository.sa_sql[service_type.value]
        connection_string = repository_cfg["connection_string"]
        sa_repository_class: SARepository = data["repository_class"][
            enum.RepositoryType.SA_SQL
        ]
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
        sa_repository = sa_repository_class.create_sa_repository(
            entities,
            connection_string,
            name=service_type.value,
        )
        _create_from_repository(user_id, entities, dict_repository, sa_repository)
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: sa_sql repository loaded in {end_time - start_time}s"
            )
