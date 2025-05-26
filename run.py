import importlib.resources
import os
from datetime import datetime
from enum import Enum
from pathlib import Path

import fire
import pandas as pd
import pytest
import uvicorn

from util.util import generate_ulid


class AppType(Enum):
    CASEDB = "casedb"
    SEQDB = "seqdb"
    OMOPDB = "omopdb"
    ALL = "all"


class AppConfigType(Enum):
    IDPS = "idps"
    MOCK_IDPS = "mock_idps"
    NO_AUTH = "no_auth"
    DEBUG = "debug"
    NO_SSL = "no_ssl"


class ConfigDiscovery:
    """
    Config discovery class.
    Highest priority is the config path in the environment variable.
    Second is the local config path.
    Third is the config path in the package.
    """

    @staticmethod
    def get_config_path(
        app_type: str, env_var_substring: str = "", extension: str = ""
    ) -> str:
        """
        Config path picked in the following order:
        1. Environment variable
        2. Local config path
        3. Package config path
        4. Raise error if not found
        """
        path = ConfigDiscovery.get_config_path_from_env(
            app_type, env_var_substring=env_var_substring, extension=extension
        )
        if path:
            print(f"Config path found in environment variable: {path}")
            return path
        path = ConfigDiscovery.get_config_path_from_local(app_type, extension=extension)
        if path:
            print(f"Config path found in local file: {path}")
            return path
        path = ConfigDiscovery.get_config_path_from_package(
            app_type, extension=extension
        )
        if path:
            print(f"Config path found in package: {path}")
            return path
        raise ValueError(
            f"Config path not found for app type {app_type}. Please set the environment variable {app_type.upper()}_CONFIG_PATH."
        )

    @staticmethod
    def get_config_path_from_env(
        app_type: str, env_var_substring: str, extension: str = ""
    ) -> str | None:
        """Get config path from environment variable, if not return None."""
        env_var_name = f"{app_type.upper()}_{env_var_substring}"
        if env_var_name in os.environ:
            env_config_path = Path(os.environ[env_var_name])
            if extension:
                return str(env_config_path / extension)
            return str(env_config_path)
        return None

    @staticmethod
    def get_config_path_from_local(app_type: str, extension: str = "") -> str | None:
        """Get config path from local file, if not return None."""
        local_config_path = Path(f"./config/{app_type}")
        if local_config_path.exists():
            if extension:
                return str(local_config_path / extension)
            return str(local_config_path)
        return None

    @staticmethod
    def get_config_path_from_package(app_type: str, extension: str = "") -> str | None:
        """Get config path from package, if not return None."""
        with importlib.resources.path("gen_epix", "") as package_path:
            package_config_path = package_path / app_type / "config"
        if package_config_path.exists():
            if extension:
                return str(package_config_path / extension)
            return str(package_config_path)
        return None


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
            "module_root": "gen_epix_demo.gen_epix_demo.casedb",
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
            "module_root": "gen_epix_demo.gen_epix_demo.seqdb",
            "targets": ["organization", "system", "seq"],
        },
        AppType.OMOPDB: {
            "module_root": "gen_epix_demo.gen_epix_demo.omopdb",
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
            for app2 in AppType:
                if app2 == AppType.ALL:
                    continue
                Run.set_env_variables(app2, idp_config)
            return
        elif app_type == AppType.CASEDB:
            Run.set_env_variables(AppType.SEQDB, idp_config)
        # Set environment variables
        for name, value in Run.APP_SECRETS_ENV_VARIABLES[app_type].items():
            env_var_name = app_type.value.upper() + "_" + name
            if env_var_name not in os.environ:
                os.environ[env_var_name] = value
        key = (app_type, idp_config)
        for name, value in Run.APP_IDP_ENV_VARIABLES[key].items():
            env_var_name = app_type.value.upper() + "_" + name
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

    ## Test
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
                "gen_epix_demo/test/unit",
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
                "test/omopdb/omopdb/unit/",
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
        xls_file = os.path.join(
            os.path.dirname(__file__), "test", "data", "output", "generated_uuids.xlsx"
        )
        df.to_excel(xls_file, sheet_name="uuid", index=False)
        print(
            f"Total of {n_rows} uuids times {df.shape[1]} columns generated and written to file {xls_file}"
        )

    def other_general_run_linters(self) -> None:
        from util.linter import Linter

        file_basename = Path(__file__).parent / "test" / "data" / "output" / "linter"

        linter = Linter()
        linter.run_all(file_basename=file_basename)

    def other_general_run_pylint(self) -> None:
        from util.linter import Linter

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
        from util.linter import Linter

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

        path = path or os.path.join("test", "data", "output", "log.debug.txt")
        out_log_excel_file = os.path.join(os.path.dirname(path), "log.debug.xlsx")
        out_user_journey_file = os.path.join(
            os.path.dirname(path), "log.user_journey.pkl.gz"
        )
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

    def other_seqdb_parse_ncbi_taxonomy(self) -> None:
        dir = os.path.join(os.getcwd(), ".ete")
        os.environ["HOME"] = dir
        os.environ["XDG_DATA_HOME"] = os.path.join(dir, "data")
        os.environ["XDG_CONFIG_HOME"] = os.path.join(dir, "config")
        os.environ["XDG_CACHE_HOME"] = os.path.join(dir, "cache")
        from util.ncbi_taxonomy import parse_ncbi_taxonomy

        parse_ncbi_taxonomy()

    def other_seqdb_parse_alleles(self) -> None:
        dir = os.path.join(os.getcwd(), ".ete")
        os.environ["HOME"] = dir
        from util.wgmlst import parse_alleles

        parse_alleles()

    def other_seqdb_parse_allele_profiles(self) -> None:
        from util.wgmlst import parse_allele_profiles

        parse_allele_profiles()

    def other_seq_from_distance_matrix(self) -> None:
        from util.seqs_from_distance_matrix import main

        main()


if __name__ == "__main__":
    fire.Fire(Run)
