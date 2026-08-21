import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import fire

from gen_epix.commondb.domain.enum import (
    AppType,
    AppTypeSet,
    DevIdpConfig,
    DevRepositoryConfig,
)
from gen_epix.commondb.domain.util import set_env_variables


class Run:

    APP_URI: dict[AppType, dict[str, str | int]] = {
        AppType.CASEDB: {
            "app": "gen_epix.casedb.app:FAST_API",
            "host": "0.0.0.0",
            "port": 8000,
        },
        AppType.SEQDB: {
            "app": "gen_epix.seqdb.app:FAST_API",
            "host": "0.0.0.0",
            "port": 8001,
        },
        AppType.OMOPDB: {
            "app": "gen_epix.omopdb.app:FAST_API",
            "host": "0.0.0.0",
            "port": 8002,
        },
        AppType.COMMONDB: {
            "app": "gen_epix.commondb.app:FAST_API",
            "host": "0.0.0.0",
            "port": 8010,
        },
    }

    APP_SSL_KEYFILE = "./cert/key.pem"
    APP_SSL_CERTFILE = "./cert/cert.pem"

    ETL_ENV: dict[AppType, dict[str, str | list[str]]] = {
        AppType.CASEDB: {
            "module_root": "gen_epix.casedb",
            "targets": [
                "geo",
                "ontology",
                "organization",
                "case",
                "abac",
                "system",
            ],
            "other_targets": ["seqdb"],
        },
        AppType.SEQDB: {
            "module_root": "gen_epix.seqdb",
            "targets": ["organization", "system", "abac", "file", "seq"],
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

    ## api
    def api(
        self,
        app_type: str,
        idp_config: str,
        dev_repository_config: str,
        reload: bool = True,
    ) -> None:
        import uvicorn

        app_type_enum = AppType[app_type.upper()]
        idp_config_enum = DevIdpConfig[idp_config.upper()]
        dev_repository_config_enum = DevRepositoryConfig[dev_repository_config.upper()]
        # Set environment variables
        set_env_variables(app_type_enum, idp_config_enum, dev_repository_config_enum)
        logging_file: str = os.environ[f"{app_type_enum.value.upper()}_LOG_CONFIG_FILE"]
        # Run app
        uri_cfg = Run.APP_URI[app_type_enum]
        ssl_keyfile = (
            Run.APP_SSL_KEYFILE if Path(Run.APP_SSL_KEYFILE).exists() else None
        )
        ssl_certfile = (
            Run.APP_SSL_CERTFILE if Path(Run.APP_SSL_CERTFILE).exists() else None
        )
        # profiler = pyinstrument.Profiler(async_mode="enabled")
        # profiler.start()
        uvicorn.run(
            uri_cfg["app"],
            host=uri_cfg["host"],
            port=uri_cfg["port"],
            reload=reload,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            log_config=logging_file,
        )

    def api_platform_local_mock_dict_demo(self) -> None:
        from test.end_to_end.casedb_seqdb_connection.envvar import set_envvar
        from test.test_client.start_all_services import run_platform

        set_envvar()
        run_platform(use_dict_repository=True, start_omopdb=True)

    def api_platform_local_mock_sa_sql_demo(self) -> None:
        from test.end_to_end.casedb_seqdb_connection.envvar import set_envvar
        from test.test_client.start_all_services import run_platform

        set_envvar()
        run_platform(use_dict_repository=False, start_omopdb=True)

    ## env

    def env_casedb(self) -> None:
        import gen_epix.casedb.env as env

    def env_seqdb(self) -> None:
        import gen_epix.seqdb.env as env

    def env_omopdb(self) -> None:
        import gen_epix.omopdb.env as env

    def env_commondb(self) -> None:
        import gen_epix.commondb.env as env

    ## etl
    def etl_load_demo_data(
        self, app_type: AppType | str, connect_timeout: float = 1, verbose: bool = True
    ) -> None:
        from gen_epix.commondb.domain.util import load_demo_data

        # Set all environment variables
        set_env_variables(
            AppType.ALL, DevIdpConfig.IDPS, DevRepositoryConfig.DICT_EMPTY
        )
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
    def test_all(self, include_e2e: bool = True) -> None:
        import subprocess

        pytest_args = (
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/filter/unit",
                "test/transform/unit",
                "test/fastapp/unit",
                "test/commondb/unit",
                "test/commondb/integration",
                "test/casedb/unit",
                "test/casedb/integration",
                "test/seqdb/unit",
                "test/seqdb/integration",
                "test/omopdb/unit",
                "test/omopdb/integration",
                "test/general/docs",
            ]
            + (["test/end_to_end"] if include_e2e else [])
            + [
                "test/util",
                # Not normally included, uncomment if needed
                # "test/casedb/performance",
                # "test/seqdb/performance",
                # "test/omopdb/performance",
                # "test/commondb/performance",
                # "test/fastapp/performance",
                # "test/general/code",
            ]
        )

        test_run = subprocess.run(
            [
                sys.executable,
                "-m",
                "coverage",
                "run",
                "--source=gen_epix",
                "-m",
                "pytest",
            ]
            + pytest_args,
            check=False,
        )
        # Generate HTML report
        html_report = subprocess.run(
            [
                sys.executable,
                "-m",
                "coverage",
                "html",
                "-d",
                "test/output/coverage.html",
            ],
            check=False,
        )
        # Generate XML report
        xml_report = subprocess.run(
            [sys.executable, "-m", "coverage", "xml", "-o", "test/output/coverage.xml"],
            check=False,
        )

        failures: list[str] = []
        if test_run.returncode != 0:
            failures.append(
                "pytest test all failed likely due to test failures or errors"
            )
        if html_report.returncode != 0:
            failures.append(
                "coverage html report generation failed with exit status "
                f"{html_report.returncode}"
            )
        if xml_report.returncode != 0:
            failures.append(
                "coverage xml report generation failed with exit status "
                f"{xml_report.returncode}"
            )
        if failures:
            raise RuntimeError("; ".join(failures))

    def test_all_incl_performance(self) -> None:
        import pytest

        pytest.main(Run.DEFAULT_PYTEST_ARGS + ["."])

    def test_all_unit(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/filter/unit",
                "test/transform/unit",
                "test/fastapp/unit",
                "test/seqdb/unit",
                "test/commondb/unit",
                "test/casedb/unit",
                "test/omopdb/unit",
            ]
        )

    def test_all_integration(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/integration",
                "test/casedb/integration",
                "test/seqdb/integration",
                "test/omopdb/integration",
            ]
        )

    def test_all_performance(self) -> None:
        import pytest

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

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/filter/unit/",
            ]
        )

    def test_transform_unit(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/transform/unit",
            ]
        )

    def test_fastapp_unit(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit",
            ]
        )

    def test_fastapp_unit_auth(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/auth/",
            ]
        )

    def test_fastapp_unit_domain(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/domain",
            ]
        )

    def test_fastapp_unit_services(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/services/",
            ]
        )

    def test_fastapp_unit_services_rbac(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/services/rbac",
            ]
        )

    def test_fastapp_unit_repository(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/repository",
            ]
        )

    def test_fastapp_unit_repositories(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/unit/repositories",
            ]
        )

    def test_fastapp_performance(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/performance",
            ]
        )

    def test_fastapp_performance_repository(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/fastapp/performance/repository",
            ]
        )

    def test_commondb_unit(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/unit/",
            ]
        )

    def test_commondb_unit_auth(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/unit/auth/",
            ]
        )

    def test_commondb_unit_config(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/unit/config/",
            ]
        )

    def test_commondb_unit_logging(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/unit/logging/",
            ]
        )

    def test_commondb_unit_upload(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/unit/upload/",
            ]
        )

    def test_commondb_unit_policies(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/unit/policies/",
            ]
        )

    def test_commondb_integration(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/integration/build_db",
            ]
        )

    def test_commondb_integration_build_db(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/integration/build_db",
            ]
        )

    def test_commondb_integration_metadata(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/commondb/integration/metadata",
            ]
        )

    def test_commondb_integration_sql_injection(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS + ["test/commondb/integration/sql_injection"]
        )

    def test_casedb_unit(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/unit/",
            ]
        )

    def test_casedb_unit_domain(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/unit/domain",
            ]
        )

    def test_casedb_unit_services(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/unit/services",
            ]
        )

    def test_casedb_unit_services_case(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/unit/services/case",
            ]
        )

    def test_casedb_unit_services_case_upload(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/unit/services/case/upload",
            ]
        )

    def test_unit_seqdb_remote_app(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + ["test/seqdb/unit/services/test_seqdb_remote_app.py"]
        )

    def test_casedb_integration(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration",
            ]
        )

    def test_casedb_integration_build_db(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/build_db",
            ]
        )

    def test_casedb_integration_case_upload(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/case_upload",
            ]
        )

    def test_casedb_integration_content(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/content",
            ]
        )

    def test_casedb_integration_data_access(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/integration/data_access",
            ]
        )

    def test_casedb_performance(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance",
            ]
        )

    def test_casedb_performance_repository(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/repository",
            ]
        )

    def test_casedb_performance_user_journey(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/user_journey",
            ]
        )

    def test_casedb_performance_startup(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/startup",
            ]
        )

    def test_casedb_performance_retrieve_stats(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/performance/retrieve_stats",
            ]
        )

    def test_casedb_custom(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/casedb/custom",
            ]
        )

    def test_seqdb_unit(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/unit",
            ]
        )

    def test_seqdb_unit_domain(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/unit/domain",
            ]
        )

    def test_seqdb_unit_domain_models_for_upload(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/unit/domain/models_for_upload",
            ]
        )

    def test_seqdb_unit_services_seq_upload(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/unit/services/seq/upload",
            ]
        )

    def test_seqdb_unit_services_seq_calculate_seq_distance(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/unit/services/seq/calculate_seq_distance",
            ]
        )

    def test_seqdb_unit_services_seq_retrieve_best(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/unit/services/seq/retrieve_best",
            ]
        )

    def test_seqdb_integration(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/integration",
            ]
        )

    def test_seqdb_integration_build_db(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/integration/build_db",
            ]
        )

    def test_seqdb_integration_content(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/integration/content",
            ]
        )

    def test_seqdb_integration_retrieve_samples(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/integration/retrieve_samples",
            ]
        )

    def test_seqdb_performance_calculate_seq_distances(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + ["-m performance"]
            + [
                "test/seqdb/performance/calculate_seq_distances",
            ]
        )

    def test_seqdb_performance_retrieve_similar_profiles(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/seqdb/performance/retrieve_similar_profiles",
            ]
        )

    def test_omopdb_unit(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/omopdb/unit/",
            ]
        )

    def test_omopdb_unit_domain(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/omopdb/unit/domain",
            ]
        )

    def test_omopdb_unit_services(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/omopdb/unit/services",
            ]
        )

    def test_omopdb_unit_services_omop(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/omopdb/unit/services/omop",
            ]
        )

    def test_omopdb_unit_services_omop_upload(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/omopdb/unit/services/omop/upload",
            ]
        )

    def test_omopdb_integration(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/omopdb/integration",
            ]
        )

    def test_omopdb_integration_build_db(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/omopdb/integration/build_db",
            ]
        )

    def test_omopdb_integration_retrieve_persons(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/omopdb/integration/retrieve_persons",
            ]
        )

    def test_general_docs(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/general/docs",
            ]
        )

    def test_general_code(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/general/code",
            ]
        )

    def test_general_code_test_model_field_properties(self) -> None:

        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/general/code/test_model_field_properties.py",
            ]
        )

    def test_general_code_test_error_code_unicity(self) -> None:

        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/general/code/test_error_code_unicity.py",
            ]
        )

    def test_end_to_end(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/end_to_end/casedb_seqdb_connection",
                "test/end_to_end/client_credential_flow",
            ]
        )

    def test_end_to_end_casedb_seqdb_connection(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/end_to_end/casedb_seqdb_connection",
            ]
        )

    def test_end_to_end_client_credential_flow(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/end_to_end/client_credential_flow",
            ]
        )

    def test_test_client_authorization_code_flow(self) -> None:
        import pytest

        pytest.main(
            Run.DEFAULT_PYTEST_ARGS
            + [
                "test/test_client/end_to_end/auth_code_flow/test_authorization_code_flow.py",
            ]
        )

    ## Other

    def other_general_generate_uuids(
        self, n_rows: int = 1000, n_cols: int = 100
    ) -> None:
        from test.test_client.util import generate_uuids

        generate_uuids(n_rows=n_rows, n_cols=n_cols)

    def other_general_generate_hex_strings(
        self, n_rows: int = 1000, length: int = 8
    ) -> None:
        from test.test_client.util import generate_hex_strings

        generate_hex_strings(n_rows=n_rows, length=length)

    def other_general_run_linters(self) -> None:
        from test.test_client.linter import Linter

        file_basename = Path(__file__).parent / "test" / "output" / "linter"

        linter = Linter()
        linter.run_all(file_basename=file_basename)

    def other_general_run_pylint(self) -> None:
        from test.test_client.linter import Linter

        filter_on_codes = {
            "W0102",
            "E1101",
            "R1728",
            "W0212",
        }
        filter_on_codes = None

        file = Path(__file__).parent / "test" / "output" / "linter.pylint.txt"
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file2 = (
            Path(__file__).parent / "test" / "output" / f"linter.{now_str}.pylint.txt"
        )
        linter = Linter()
        output = linter.run_pylint(file=file, filter_on_codes=filter_on_codes)
        file2.write_text(output, encoding="utf-8")
        for line in linter.parse_pylint_for_issue_lines(
            file, filter_on_codes=filter_on_codes
        ):
            print(line)

    def other_general_run_ruff(self) -> None:
        from test.test_client.linter import Linter

        file = Path(__file__).parent / "test" / "output" / "linter.ruff.txt"
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file2 = Path(__file__).parent / "test" / "output" / f"linter.{now_str}.ruff.txt"
        linter = Linter()
        output = linter.run_ruff(file=file)
        file2.write_text(output, encoding="utf-8")
        print(output, end="")

    def other_general_analyse_pylint_code_impact(self) -> None:

        from test.test_client.linter import Linter

        linter = Linter()
        linter.analyse_pylint_code_impact()

    def other_general_run_mypy(self) -> None:
        from test.test_client.linter import Linter

        filter_on_codes = {
            "no-untyped-def",
            "unreachable",
        }
        # filter_on_codes = None

        file = Path(__file__).parent / "test" / "output" / "linter.mypy.txt"
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file2 = Path(__file__).parent / "test" / "output" / f"linter.{now_str}.mypy.txt"
        linter = Linter()
        linter.run_mypy(file=file, filter_on_codes=filter_on_codes)
        file2.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")
        for line in linter.parse_mypy_for_issue_lines(
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

    def other_general_generate_erm_diagrams(self) -> None:
        from docs.erm.erm_graphviz import GraphvizErmGenerator
        from docs.erm.erm_mermaid import MermaidErmGenerator

        out_dir = Path(__file__).parent / "docs" / "erm"
        GraphvizErmGenerator().generate_erm_diagrams(out_dir)
        MermaidErmGenerator().generate_erm_diagrams(out_dir)

    def other_oauth_server_start(self) -> None:

        from test.test_client.oauth.start_server import start_server

        start_server()


if __name__ == "__main__":
    fire.Fire(Run)
