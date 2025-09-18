import logging
from pathlib import Path
from test.test_client.util import get_test_name, get_test_output_dir
from typing import Any, Hashable

from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain import enum
from gen_epix.commondb.test.test_client import TestClient

APP_NAME = "COMMONDB"
APP_CFG = AppCfg(APP_NAME, enum.ServiceType, enum.RepositoryType)
APP_CFG.setup_logger.setLevel(logging.WARNING)

TEST_CLIENTS: dict[Hashable, TestClient] = {}

DEFAULT_DATA_FIXTURE_NAME = "empty"
DEFAULT_ROUTE_PREFIX = "/v1"


def get_test_client(
    test_type: str,
    test_dir: Path,
    app_cfg: AppCfg = APP_CFG,
    repository_type: enum.RepositoryType = enum.RepositoryType.DICT,
    data_fixture_name: str = DEFAULT_DATA_FIXTURE_NAME,
    route_prefix: str = DEFAULT_ROUTE_PREFIX,
    verbose: bool = False,
    log_level: int = logging.ERROR,
    log_setup: bool = False,
    **kwargs: Any,
) -> TestClient:
    """
    Create a test environment for the given test type and repository type. A
    single environment, with a common test directory, is kept for each test type.
    """
    test_name = get_test_name(test_type)
    test_dir = test_dir or get_test_output_dir(test_name)
    key: tuple[str, enum.RepositoryType, str] = (
        test_type,
        repository_type,
        data_fixture_name,
    )
    if key not in TEST_CLIENTS:
        for stored_key, stored_env in TEST_CLIENTS.items():
            stored_test_type, _, _ = stored_key  # type: ignore[misc]
            if stored_test_type == test_type:  # type: ignore[has-type]
                test_dir = stored_env.test_dir
                break

        TEST_CLIENTS[key] = TestClient(
            test_name=test_name,
            test_dir=test_dir,
            app_cfg=app_cfg,
            repository_type=repository_type,
            data_fixture_name=data_fixture_name,
            route_prefix=route_prefix,
            verbose=verbose,
            log_level=log_level,
            log_setup=log_setup,
            **kwargs,
        )
    return TEST_CLIENTS[key]  # type: ignore[no-any-return]
