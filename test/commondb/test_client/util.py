import logging
from collections.abc import Hashable
from test.test_client.util import get_test_name, get_test_output_dir
from typing import Any

from gen_epix.commondb.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.policy.permission import RoleGenerator
from gen_epix.commondb.env import AppComposer
from gen_epix.commondb.test.endpoint_test_client import EndpointTestClient
from gen_epix.commondb.test.test_client import TestClient

TEST_CLIENTS: dict[Hashable, TestClient] = {}


def get_test_client(
    test_type: str,
    app_cfg: AppCfg,
    use_endpoints: bool = False,
    route_prefix: str | None = None,
    verbose: bool = False,
    log_level: int = logging.ERROR,
    log_setup: bool = False,
    **kwargs: Any,
) -> TestClient:
    """
    Create a test environment for the given test type and repository type. A
    single environment, with a common test directory, is kept for each test type.
    """
    if app_cfg.name not in TEST_CLIENTS:
        test_name = get_test_name(test_type)
        test_dir = get_test_output_dir(test_name)
        is_new_test_dir = True
        # Find existing test dir for same test type and use that if found,
        # so all results come in the same dir
        for stored_key, stored_env in TEST_CLIENTS.items():
            stored_test_type, _, _ = stored_key  # type: ignore[misc]
            if stored_test_type == test_type:  # type: ignore[has-type]
                test_name = stored_env.test_name
                test_dir = stored_env.test_dir
                is_new_test_dir = False
                break
        # Adjust config to new dir and copy any repository files there
        if is_new_test_dir:
            app_cfg.copy_repository_files(test_dir)

        # Set and adjust cfg
        app_cfg.cfg["app"]["debug"] = True
        curr_cfg = app_cfg.cfg["service"]["auth"]["props"]["root"]
        curr_cfg["organization"]["name"] = "org1"
        curr_cfg["user"]["key"] = "root1_1@org1.org"
        curr_cfg["user"]["email"] = "root1_1@org1.org"
        curr_cfg["user"]["name"] = "root1_1"

        # Create app
        TestClient._set_log_level(app_cfg, log_level)
        app_composer = AppComposer(app_cfg, log_setup=log_setup, **kwargs)

        # Create endpoint test client if endpoints are to be used (including own
        # app_composer), otherwise construct app env separately
        endpoint_test_client: EndpointTestClient | None = None
        app_last_handled_exception: dict | None = None
        if use_endpoints:
            fast_api = create_fast_api(
                app=app_composer.app,
                setup_logger=app_cfg.setup_logger if log_setup else None,
                api_logger=app_cfg.api_logger,
                debug=True,
                update_openapi_schema=True,
            )
            app_last_handled_exception = LAST_HANDLED_EXCEPTION
            endpoint_test_client = EndpointTestClient(
                app_composer.app,
                fast_api,
                app_last_handled_exception,
                route_prefix=route_prefix,
                **kwargs,
            )
        # Call base class constructor
        test_client = TestClient(
            test_name,
            test_dir,
            app_cfg,
            app_composer,
            roles=set(enum.Role),
            role_hierarchy=RoleGenerator.ROLE_HIERARCHY,  # type: ignore
            verbose=verbose,
            log_level=log_level,
            use_endpoints=use_endpoints,
            endpoint_test_client=endpoint_test_client,
            app_last_handled_exception=app_last_handled_exception,
            **kwargs,
        )

        TEST_CLIENTS[app_cfg.name] = test_client
    return TEST_CLIENTS[app_cfg.name]
