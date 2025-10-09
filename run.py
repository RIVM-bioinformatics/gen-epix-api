import os
from datetime import datetime
from pathlib import Path

import fire

from gen_epix.commondb.config import ConfigDiscovery
from gen_epix.commondb.domain.enum import AppConfigType, AppType, AppTypeSet


class Run:

    ROOT_DIR = os.getcwd()
    APP_SECRETS_ENV_VARIABLES = {
        AppType.COMMONDB: {
            "SETTINGS_DIR": ConfigDiscovery.get_config_path(
                app_type=AppType.COMMONDB.value,
                env_var_substring="SETTINGS_DIR",
                root_dir="test/",
            ),
            "SECRETS_DIR": ConfigDiscovery.get_config_path(
                app_type=AppType.COMMONDB.value,
                env_var_substring="SECRETS_DIR",
                extension=".secret",
            ),
            "LOGGING_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.COMMONDB.value,
                env_var_substring="LOGGING_CONFIG_FILE",
                extension="logging.yaml",
            ),
        },
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
        (AppType.COMMONDB, AppConfigType.IDPS): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.COMMONDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/identity_providers.json",
            ),
        },
        (AppType.COMMONDB, AppConfigType.MOCK_IDPS): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.COMMONDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/mock_identity_provider.json",
            ),
        },
        (AppType.COMMONDB, AppConfigType.NO_AUTH): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.COMMONDB.value,
                env_var_substring="IDPS_CONFIG_FILE",
                extension="idp/no_identity_providers.json",
            ),
        },
        (AppType.COMMONDB, AppConfigType.DEBUG): {
            "IDPS_CONFIG_FILE": ConfigDiscovery.get_config_path(
                app_type=AppType.COMMONDB.value,
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
            "targets": ["organization", "system", "abac", "seq"],
        },
        AppType.OMOPDB: {
            "module_root": "gen_epix.omopdb",
            "targets": ["organization", "system", "abac", "omop"],
        },
        AppType.COMMONDB: {
            "module_root": "gen_epix.commondb",
            "targets": ["organization", "system", "abac"],
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
        import uvicorn

        app_type = AppType[app_type.upper()]
        idp_config = AppConfigType[idp_config.upper()]
        env_name = env_name.upper()
        # Set environment variables
        Run.set_env_variables(app_type, idp_config)
        # Run app
        uri_cfg = Run.APP_URI[app_type]
        ssl_keyfile = Run.APP_SSL_KEYFILE
        ssl_certfile = Run.APP_SSL_CERTFILE
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

    def env_seqdb(self) -> None:
        Run.set_env_variables(AppType.SEQDB, AppConfigType.IDPS)

    def env_omopdb(self) -> None:
        Run.set_env_variables(AppType.OMOPDB, AppConfigType.IDPS)

    def env_commondb(self) -> None:
        Run.set_env_variables(AppType.COMMONDB, AppConfigType.IDPS)

    ## etl
    def etl_load_demo_data(
        self, app_type: AppType | str, connect_timeout: float = 1, verbose: bool = True
    ) -> None:
        from test.test_client.util import load_demo_data

        # Set all environment variables
        Run.set_env_variables(AppType.ALL, AppConfigType.IDPS)
        if isinstance(app_type, str):
            app_type = AppType[app_type.upper()]
        assert isinstance(app_type, AppType)
        # Special case: apply to all apps
        if app_type == AppType.ALL:
            for app_type2 in AppTypeSet.ALL.value:
                module_root: str = Run.ETL_ENV[app_type2]["module_root"]
                load_demo_data(
                    app_type2,
                    module_root,
                    connect_timeout=connect_timeout,
                    verbose=verbose,
                )
            return
        module_root: str = Run.ETL_ENV[app_type]["module_root"]
        load_demo_data(
            app_type, module_root, connect_timeout=connect_timeout, verbose=verbose
        )

    ## test
    def test_all(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "--cov=gen_epix",
                "--cov-report=html:test/output/coverage.html",
                "--cov-report=xml:test/output/coverage.xml",
                "test/filter/unit",
                "test/transform/unit",
                "test/fastapp/unit",
                "test/commondb/unit",
                "test/casedb/integration/build_db",
                "test/casedb/integration/content",
                "test/casedb/integration/case_access",
                "test/casedb/integration/case_validation",
                "test/casedb/unit",
                "test/omopdb/unit",
                # "test/seqdb/integration",
            ]
        )

    def test_all_incl_performance(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)

        pytest.main(Run.DEFAULT_PYTEST_ARGS + ["."])

    def test_all_unit(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/filter/unit",
                "test/transform/unit",
                "test/fastapp/unit",
                "test/commondb/unit",
                "test/casedb/unit",
                "test/omopdb/unit",
            ]
        )

    def test_all_integration(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration",
                # "test/seqdb/integration",
            ]
        )

    def test_all_performance(self) -> None:
        import pytest

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
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/filter/unit/",
            ]
        )

    def test_transform_unit(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/transform/unit",
            ]
        )

    def test_fastapp_unit(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit",
            ]
        )

    def test_fastapp_unit_auth(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/auth/",
            ]
        )

    def test_fastapp_unit_rbac(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/rbac/",
            ]
        )

    def test_fastapp_unit_repository(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/repository",
            ]
        )

    def test_docs_unit(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/docs/unit/",
            ]
        )

    def test_commondb_unit(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/unit/",
            ]
        )

    def test_commondb_unit_auth(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/unit/auth/",
            ]
        )

    def test_commondb_integration(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/integration/build_db",
            ]
        )

    def test_commondb_integration_build_db(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/integration/build_db",
            ]
        )

    def test_omopdb_unit(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/omopdb/unit/",
            ]
        )

    def test_fastapp_performance(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/performance",
            ]
        )

    def test_fastapp_performance_repository(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/performance/repository",
            ]
        )

    def test_casedb_integration(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/build_db",
                "test/casedb/integration/case_access",
                "test/casedb/integration/case_validation",
                "test/casedb/integration/content",
            ]
        )

    def test_casedb_integration_build_db(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/build_db",
            ]
        )

    def test_casedb_integration_case_access(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/case_access",
            ]
        )

    def test_casedb_integration_case_validation(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/case_validation",
            ]
        )

    def test_casedb_integration_content(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/content",
            ]
        )

    def test_casedb_performance(self) -> None:
        import pytest

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
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/repository",
            ]
        )

    def test_casedb_performance_user_journey(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/user_journey",
            ]
        )

    def test_casedb_performance_startup(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/startup",
            ]
        )

    def test_casedb_custom(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/custom",
            ]
        )

    def test_seqdb_integration(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/integration/build_db",
                "test/seqdb/integration/content",
            ]
        )

    def test_seqdb_integration_build_db(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/integration/build_db",
            ]
        )

    def test_seqdb_integration_content(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/integration/content",
            ]
        )

    def test_seqdb_performance(self) -> None:
        import pytest

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
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/performance/repository",
            ]
        )

    def test_seqdb_performance_user_journey(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/performance/user_journey",
            ]
        )

    def test_seqdb_performance_startup(self) -> None:
        import pytest

        Run.set_env_variables(AppType.ALL, AppConfigType.NO_AUTH)
        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/performance/startup",
            ]
        )

    ## Other

    def other_general_generate_uuids(self, n_rows: int = 1000, n_cols: int = 100):
        from test.test_client.util import generate_uuids

        generate_uuids(n_rows=n_rows, n_cols=n_cols)

    def other_general_run_linters(self) -> None:
        from test.linter import Linter

        file_basename = Path(__file__).parent / "test" / "output" / "linter"

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

        file = Path(__file__).parent / "test" / "output" / "linter.pylint.txt"
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file2 = (
            Path(__file__).parent / "test" / "output" / f"linter.{now_str}.pylint.txt"
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

        file = Path(__file__).parent / "test" / "output" / "linter.mypy.txt"
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file2 = Path(__file__).parent / "test" / "output" / f"linter.{now_str}.mypy.txt"
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
            path_obj = Path("test") / "output" / "log.debug.txt"
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
        from docs.erm import generate_erm_diagrams

        out_dir = Path(__file__).parent / "docs" / "assets" / "erm"
        generate_erm_diagrams(out_dir)


if __name__ == "__main__":
    fire.Fire(Run)
