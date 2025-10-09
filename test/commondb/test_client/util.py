import logging
from collections.abc import Hashable
from test.test_client.util import (
    create_data_fixture,
    get_test_name,
    get_test_output_dir,
)
from typing import Any

from gen_epix.commondb.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.domain.policy.permission import RoleGenerator
from gen_epix.commondb.env import AppEnv
from gen_epix.commondb.test.endpoint_test_client import EndpointTestClient
from gen_epix.commondb.test.test_client import TestClient

APP_NAME = "COMMONDB"
APP_CFG = AppCfg(APP_NAME, enum.ServiceType, enum.RepositoryType)
APP_CFG.setup_logger.setLevel(logging.WARNING)

TEST_CLIENTS: dict[Hashable, TestClient] = {}

DEFAULT_DATA_FIXTURE_NAME = "empty"
DEFAULT_ROUTE_PREFIX = "/v1"


def get_test_client(
    test_type: str,
    app_cfg: AppCfg = APP_CFG,
    repository_type: enum.RepositoryType = enum.RepositoryType.DICT,
    data_fixture_name: str = DEFAULT_DATA_FIXTURE_NAME,
    use_endpoints: bool = False,
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
    key: tuple[str, enum.RepositoryType, str] = (
        test_type,
        repository_type,
        data_fixture_name,
    )
    if key not in TEST_CLIENTS:
        test_name = get_test_name(test_type)
        test_dir = get_test_output_dir(test_name)
        # Find existing test dir for same test type and use that if found,
        # so all results come in the same dir
        for stored_key, stored_env in TEST_CLIENTS.items():
            stored_test_type, _, _ = stored_key  # type: ignore[misc]
            if stored_test_type == test_type:  # type: ignore[has-type]
                test_name = stored_env.test_name
                test_dir = stored_env.test_dir
                break

        # Set and adjust cfg
        app_cfg.cfg.app.debug = True
        app_cfg.cfg.secret["db"]["repository_type"] = repository_type
        # Adjust cfg for root user
        curr_cfg = app_cfg.cfg.secret.root
        curr_cfg.organization.name = "org1"
        curr_cfg.user.email = "root1_1@org1.org"
        curr_cfg.user.name = "root1_1"
        # Copy any repository files to test directory
        create_data_fixture(
            app_cfg.cfg.secret.repository[repository_type.value],
            set(enum.ServiceType),
            repository_type,
            data_fixture_name,
            test_dir,
        )

        # Create app
        TestClient._set_log_level(app_cfg, log_level)
        app_env = AppEnv(app_cfg, log_setup=log_setup, **kwargs)

        # Create endpoint test client if endpoints are to be used (including own
        # app_env), otherwise construct app env separately
        endpoint_test_client: EndpointTestClient | None = None
        app_last_handled_exception: dict | None = None
        if use_endpoints:
            fast_api = create_fast_api(
                app_cfg.cfg,
                app=app_env.app,
                registered_user_dependency=app_env.registered_user_dependency,
                new_user_dependency=app_env.new_user_dependency,
                idp_user_dependency=app_env.idp_user_dependency,
                app_id=app_env.app.generate_id(),
                setup_logger=app_cfg.setup_logger if log_setup else None,
                api_logger=app_cfg.api_logger,
                debug=True,
                update_openapi_schema=True,
            )
            app_last_handled_exception = LAST_HANDLED_EXCEPTION
            endpoint_test_client = EndpointTestClient(
                app_env.app,
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
            app_env,
            data_fixture_name=data_fixture_name,
            roles=set(enum.Role),
            role_hierarchy=RoleGenerator.ROLE_HIERARCHY,  # type: ignore
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
            user_invitation_constraints_class=model.UserInvitationConstraints,
            organization_admin_policy_class=model.OrganizationAdminPolicy,
            user_crud_command_class=command.UserCrudCommand,
            user_invitation_crud_command_class=command.UserInvitationCrudCommand,
            organization_admin_policy_crud_command_class=command.OrganizationAdminPolicyCrudCommand,
            retrieve_invite_user_constraints_command_class=command.RetrieveInviteUserConstraintsCommand,
            invite_user_command_class=command.InviteUserCommand,
            retrieve_organization_admin_name_emails_command_class=command.RetrieveOrganizationAdminNameEmailsCommand,
            update_user_command_class=command.UpdateUserCommand,
            verbose=verbose,
            log_level=log_level,
            use_endpoints=use_endpoints,
            endpoint_test_client=endpoint_test_client,
            app_last_handled_exception=app_last_handled_exception,
            **kwargs,
        )

        TEST_CLIENTS[key] = test_client
    return TEST_CLIENTS[key]  # type: ignore[no-any-return]
