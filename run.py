import gzip
import importlib
import os
import pickle
from datetime import datetime
from enum import Enum
from pathlib import Path

import fire
import pandas as pd
import pytest
import uvicorn

from docs.erm import generate_erm_diagrams
from gen_epix.common.config import AppCfg, ConfigDiscovery
from gen_epix.common.domain.enum import AppConfigType, AppType, AppTypeSet
from gen_epix.common.util import generate_ulid
from gen_epix.fastapp import Domain
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository


class Run:

    ROOT_DIR = os.getcwd()
    APP_SECRETS_ENV_VARIABLES = {
        AppType.CASEDB: {
            "SETTINGS_DIR": ConfigDiscovery.get_config_path(
                app_type=AppType.CASEDB.value, env_var_substring="SETTINGS_DIR"
            ),
            "SECRETS_DIR": ConfigDiscovery.get_config_path(
                app_type=AppType.CASEDB.value,
                env_var_substring="SECRETS_DIR",
                extension=".secret",
            ),
            "LOGGING_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.CASEDB.value,
                env_var_substring="LOGGING_CONFIG_FILE",
                extension="logging.yaml",
            ),
        },
        AppType.SEQDB: {
            "SETTINGS_DIR": ConfigDiscovery.get_config_path(
                app_type=AppType.SEQDB.value, env_var_substring="SETTINGS_DIR"
            ),
            "SECRETS_DIR": ConfigDiscovery.get_config_path(
                app_type=AppType.SEQDB.value,
                env_var_substring="SECRETS_DIR",
                extension=".secret",
            ),
            "LOGGING_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.SEQDB.value,
                env_var_substring="LOGGING_CONFIG_FILE",
                extension="logging.yaml",
            ),
        },
        AppType.OMOPDB: {
            "SETTINGS_DIR": ConfigDiscovery.get_config_path(
                app_type=AppType.OMOPDB.value, env_var_substring="SETTINGS_DIR"
            ),
            "SECRETS_DIR": ConfigDiscovery.get_config_path(
                app_type=AppType.OMOPDB.value,
                env_var_substring="SECRETS_DIR",
                extension=".secret",
            ),
            "LOGGING_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.OMOPDB.value,
                env_var_substring="LOGGING_CONFIG_FILE",
                extension="logging.yaml",
            ),
        },
    }
    APP_IDP_ENV_VARIABLES = {
        (AppType.CASEDB, AppConfigType.IDPS): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.CASEDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/identity_providers.json",
            ),
        },
        (AppType.CASEDB, AppConfigType.MOCK_IDPS): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.CASEDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/mock_identity_provider.json",
            ),
        },
        (AppType.CASEDB, AppConfigType.NO_AUTH): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.CASEDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/no_identity_providers.json",
            ),
        },
        (AppType.CASEDB, AppConfigType.DEBUG): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.CASEDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/identity_providers.json",
            ),
        },
        (AppType.CASEDB, AppConfigType.NO_SSL): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.CASEDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/identity_providers.json",
            ),
        },
        (AppType.SEQDB, AppConfigType.IDPS): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.SEQDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/identity_providers.json",
            ),
        },
        (AppType.SEQDB, AppConfigType.MOCK_IDPS): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.SEQDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/mock_identity_provider.json",
            ),
        },
        (AppType.SEQDB, AppConfigType.NO_AUTH): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.SEQDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/no_identity_providers.json",
            ),
        },
        (AppType.SEQDB, AppConfigType.DEBUG): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.SEQDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/identity_providers.json",
            ),
        },
        (AppType.SEQDB, AppConfigType.NO_SSL): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.SEQDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/identity_providers.json",
            ),
        },
        (AppType.OMOPDB, AppConfigType.IDPS): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.OMOPDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/identity_providers.json",
            ),
        },
        (AppType.OMOPDB, AppConfigType.MOCK_IDPS): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.OMOPDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/mock_identity_provider.json",
            ),
        },
        (AppType.OMOPDB, AppConfigType.NO_AUTH): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.OMOPDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/no_identity_providers.json",
            ),
        },
        (AppType.OMOPDB, AppConfigType.DEBUG): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.OMOPDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/identity_providers.json",
            ),
        },
        (AppType.OMOPDB, AppConfigType.NO_SSL): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.OMOPDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/identity_providers.json",
            ),
        },
    }

    APP_URI = {
        AppType.CASEDB: {
            "app": "gen_epix.casedb.app:FAST_API",
            "host": "0.0.0.0",
            "port": 8000,
        },
        AppType.SEQDB: {
            "app": "gen_epix.seqdb.app:FAST_API",
            "host": "0.0.0.0",
            "port": 8000,
        },
        AppType.OMOPDB: {
            "app": "gen_epix.omopdb.app:FAST_API",
            "host": "0.0.0.0",
            "port": 8000,
        },
    }

    APP_SSL_KEYFILE = "./cert/key.pem"
    APP_SSL_CERTFILE = "./cert/cert.pem"

    ETL_ENV = {
        AppType.CASEDB: {
            "module_root": "gen_epix.casedb",
            "targets": [
                "geo",
                "ontology",
                "organization",
                "subject",
                "case",
                "abac",
                "system",
            ],
            "other_targets": ["seqdb"],
        },
        AppType.SEQDB: {
            "module_root": "gen_epix.seqdb",
            "targets": ["organization", "system", "seq"],
        },
        AppType.OMOPDB: {
            "module_root": "gen_epix.omopdb",
            "targets": ["organization", "system", "omop"],
        },
    }
    DEFAULT_PYTEST_ARGS = [
        "-s",
        "-v",
        "-W",
        "ignore::DeprecationWarning",
        "-W",
        "ignore::pytest.PytestAssertRewriteWarning",
        "-W",
        "ignore::sqlalchemy.exc.SAWarning",
    ]

    @staticmethod
    def set_env_variables(app_type: AppType, idp_config: AppConfigType) -> None:
        # Special case: set environment variables for all apps
        if app_type == AppType.ALL:
            for app2 in AppTypeSet.ALL.value:
                Run.set_env_variables(app2, idp_config)
            return
        elif app_type == AppType.CASEDB:
            Run.set_env_variables(AppType.SEQDB, idp_config)
        # Set environment variables
        for name, value in Run.APP_SECRETS_ENV_VARIABLES[app_type].items():
            env_var_name = app_type.value.upper() + "_" + name
            if isinstance(value, Path):
                value = str(value.absolute())
            if env_var_name not in os.environ:
                os.environ[env_var_name] = value
        key = (app_type, idp_config)
        for name, value in Run.APP_IDP_ENV_VARIABLES[key].items():
            env_var_name = app_type.value.upper() + "_" + name
            if isinstance(value, Path):
                value = str(value.absolute())
            if env_var_name not in os.environ:
                os.environ[env_var_name] = value
        os.environ["APP_VERSION"] = "DEVELOPMENT"
        if idp_config in {"DEBUG"}:
            os.environ[app_type.value.upper() + "_LOGGING_LEVEL_FROM_SECRET"] = "0"

    ## api
    def api(self, app_type: str, env_name: str, idp_config: str) -> None:
        app_type = AppType[app_type.upper()]
        idp_config = AppConfigType[idp_config.upper()]
        env_name = env_name.upper()
        # Set environment variables
        Run.set_env_variables(app_type, idp_config)
        # Run app
        uri_cfg = Run.APP_URI[app_type]
        if idp_config not in {AppConfigType.NO_SSL}:
            ssl_keyfile = Run.APP_SSL_KEYFILE
            ssl_certfile = Run.APP_SSL_CERTFILE
        else:
            ssl_keyfile = None
            ssl_certfile = None
        # profiler = pyinstrument.Profiler(async_mode="enabled")
        # profiler.start()
        uvicorn.run(
            uri_cfg["app"],
            host=uri_cfg["host"],
            port=uri_cfg["port"],
            reload=True,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
        )

    ## env

    def env_casedb(self) -> None:
        Run.set_env_variables(AppType.CASEDB, AppConfigType.IDPS)
        import gen_epix.casedb.env as env

    def env_seqdb(self) -> None:
        Run.set_env_variables(AppType.SEQDB, AppConfigType.IDPS)
        import gen_epix.seqdb.env as env

    def env_omopdb(self) -> None:
        Run.set_env_variables(AppType.OMOPDB, AppConfigType.IDPS)
        import gen_epix.omopdb.env as env

    ## etl
    def etl_load_demo_data(
        self, app_type: AppType | str, connect_timeout: float = 1, verbose: bool = True
    ) -> None:
        if isinstance(app_type, str):
            app_type = AppType[app_type.upper()]
        assert isinstance(app_type, AppType)
        # Special case: apply to all apps
        if app_type == AppType.ALL:
            for app_type2 in AppTypeSet.ALL.value:
                self.etl_load_demo_data(app_type2)
            return
        # Set all environment variables
        Run.set_env_variables(AppType.ALL, AppConfigType.IDPS)

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
        module_root: str = Run.ETL_ENV[app_type]["module_root"]
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
            start_time = datetime.now()
            dict_repository = dict_repository_class.from_json(
                dict_repository_class, entities, zip_file
            )
            end_time = datetime.now()
            if verbose:
                print(
                    f"App {app_type.value}, service {service_type.value}: demo data parsed in {end_time - start_time}s"
                )
            # Write empty and demo dict repository to file
            start_time = datetime.now()
            with gzip.open(str(file).replace(".full.", ".empty."), "wb") as handle:
                pickle.dump({x: {} for x in dict_repository._db}, handle)
            with gzip.open(file, "wb") as handle:
                pickle.dump(dict_repository._db, handle)
            end_time = datetime.now()
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
            start_time = datetime.now()
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
            end_time = datetime.now()
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
            start_time = datetime.now()
            sa_repository = sa_repository_class.create_sa_repository(
                entities,
                connection_string,
                name=service_type.value,
            )
            _create_from_repository(user_id, entities, dict_repository, sa_repository)
            end_time = datetime.now()
            if verbose:
                print(
                    f"App {app_type.value}, service {service_type.value}: sa_sql repository loaded in {end_time - start_time}s"
                )

    ## test
    def test_all(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "--cov=gen_epix",
                "--cov-report=html:test/data/output/coverage.html",
                "--cov-report=xml:test/data/output/coverage.xml",
                "test/filter/unit",
                "test/fastapp/unit",
                "test/casedb/integration/build_db",
                "test/casedb/integration/content",
                "test/casedb/integration/case_access",
                # "test/seqdb/integration",
            ]
        )

    def test_all_incl_performance(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)

        pytest.main(Run.DEFAULT_PYTEST_ARGS + ["."])

    def test_all_unit(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/filter/unit",
                "test/fastapp/unit",
            ]
        )

    def test_all_integration(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration",
                # "test/seqdb/integration",
            ]
        )

    def test_all_performance(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/performance",
                "test/casedb/performance",
                # "test/seqdb/performance",
            ]
        )

    def test_filter_unit(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/filter/unit/",
            ]
        )

    def test_fastapp_unit(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit",
            ]
        )

    def test_fastapp_unit_auth(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/auth/",
            ]
        )

    def test_fastapp_unit_rbac(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/rbac/",
            ]
        )

    def test_fastapp_unit_repository(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/repository",
            ]
        )

    def test_omopdb_unit(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/omopdb/unit/",
            ]
        )

    def test_fastapp_performance(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/performance",
            ]
        )

    def test_fastapp_performance_repository(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/performance/repository",
            ]
        )

    def test_casedb_integration(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/build_db",
                "test/casedb/integration/case_access",
                "test/casedb/integration/content",
            ]
        )

    def test_casedb_integration_build_db(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/build_db",
            ]
        )

    def test_casedb_integration_case_access(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/case_access",
            ]
        )

    def test_casedb_integration_content(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/content",
            ]
        )

    def test_casedb_performance(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/repository",
                "test/casedb/performance/user_journey",
                "test/casedb/performance/startup",
            ]
        )

    def test_casedb_performance_repository(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/repository",
            ]
        )

    def test_casedb_performance_user_journey(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/user_journey",
            ]
        )

    def test_casedb_performance_startup(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/startup",
            ]
        )

    def test_casedb_custom(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/custom",
            ]
        )

    def test_seqdb_integration(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/integration/build_db",
                "test/seqdb/integration/content",
            ]
        )

    def test_seqdb_integration_build_db(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/integration/build_db",
            ]
        )

    def test_seqdb_integration_content(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/integration/content",
            ]
        )

    def test_seqdb_performance(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/performance/repository",
                "test/seqdb/performance/user_journey",
                "test/seqdb/performance/startup",
            ]
        )

    def test_seqdb_performance_repository(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/performance/repository",
            ]
        )

    def test_seqdb_performance_user_journey(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/performance/user_journey",
            ]
        )

    def test_seqdb_performance_startup(self) -> None:
        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/performance/startup",
            ]
        )

    ## Other

    def other_general_generate_uuids(
        self, n_rows: int = 1000, n_cols: int = 100
    ) -> None:
        df = pd.DataFrame.from_dict(
            {f"uuid{i}": [generate_ulid() for j in range(n_rows)] for i in range(100)}
        )
        xls_file = (
            Path(__file__).parent / "test" / "data" / "output" / "generated_uuids.xlsx"
        )
        df.to_excel(xls_file, sheet_name="uuid", index=False)
        print(
            f"Total of {n_rows} uuids times {df.shape[1]} columns generated and written to file {str(xls_file)}"
        )

    def other_general_run_linters(self) -> None:
        from test.linter import Linter

        file_basename = Path(__file__).parent / "test" / "data" / "output" / "linter"

        linter = Linter()
        linter.run_all(file_basename=file_basename)

    def other_general_run_pylint(self) -> None:
        from test.linter import Linter

        filter_on_codes = {
            "W0102",
            "E1101",
            "R1728",
            "W0212",
        }
        filter_on_codes = None

        file = Path(__file__).parent / "test" / "data" / "output" / "linter.pylint.txt"
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file2 = (
            Path(__file__).parent
            / "test"
            / "data"
            / "output"
            / f"linter.{now_str}.pylint.txt"
        )
        linter = Linter()
        linter.run_pylint(file=file, filter_on_codes=filter_on_codes)
        file2.write_text(file.read_text())
        for line in linter.parse_pylint_for_messages(
            file, filter_on_codes=filter_on_codes
        ):
            print(line)

    def other_general_run_mypy(self) -> None:
        from test.linter import Linter

        filter_on_codes = {
            "no-untyped-def",
            "unreachable",
        }
        # filter_on_codes = None

        file = Path(__file__).parent / "test" / "data" / "output" / "linter.mypy.txt"
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file2 = (
            Path(__file__).parent
            / "test"
            / "data"
            / "output"
            / f"linter.{now_str}.mypy.txt"
        )
        linter = Linter()
        linter.run_mypy(file=file, filter_on_codes=filter_on_codes)
        file2.write_text(file.read_text())
        for line in linter.parse_mypy_for_messages(
            file, filter_on_codes=filter_on_codes
        ):
            print(line)

    def other_casedb_parse_user_journey_from_debug_log(
        self, path: str | None = None, version: int | None = None
    ) -> None:
        from test.test_client.log_parser import LogParser, LogType
        from test.test_client.log_parser_v1 import V1LogParser
        from test.test_client.log_parser_v2 import V2LogParser

        if path:
            path_obj = Path(path)
        else:
            path_obj = Path("test") / "data" / "output" / "log.debug.txt"
        out_log_excel_file = str(path_obj.parent / "log.debug.xlsx")
        out_user_journey_file = str(path_obj.parent / "log.user_journey.pkl.gz")
        path = str(path_obj)

        log_parser: LogParser
        if not version or version == 2:
            log_parser = V2LogParser(path)
        elif version == 1:
            log_parser = V1LogParser(path, log_type=LogType.AZURE)
        else:
            raise ValueError(f"Invalid version: {version}")
        log_parser.parse()
        log_parser.to_excel(out_log_excel_file)
        user_journey = log_parser.create_user_journey()
        user_journey.to_pickle(out_user_journey_file)
        main()

    def other_general_generate_erm_diagrams(self) -> None:
        out_dir = Path(__file__).parent / "docs" / "assets"
        generate_erm_diagrams(out_dir)


if __name__ == "__main__":
    fire.Fire(Run)
