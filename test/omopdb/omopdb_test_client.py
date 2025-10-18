import logging
from pathlib import Path
from test.omopdb.omopdb_endpoint_test_client import OmopdbEndpointTestClient
from test.test_client.util import get_test_name, get_test_output_dir
from typing import Any

from gen_epix.commondb.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config import AppCfg, BaseAppCfg
from gen_epix.commondb.test.test_client import TestClient
from gen_epix.omopdb.api.organization import (
    UpdateUserRequestBody,
    UserInvitationRequestBody,
)
from gen_epix.omopdb.api.router import create_routers
from gen_epix.omopdb.domain import command, enum, model
from gen_epix.omopdb.domain.policy import RoleGenerator
from gen_epix.omopdb.env import AppEnv


class OmopdbTestClient(TestClient):
    TEST_CLIENTS: dict[str, "OmopdbTestClient"] = {}

    MODEL_KEY_MAP = TestClient.MODEL_KEY_MAP | {
        model.User: "name",
        model.UserInvitation: "email",
        model.OrganizationAdminPolicy: ("organization_id", "user_id"),
        model.DataCollection: "name",
    }

    DUMMY_VALUES = {}

    @classmethod
    def get_test_client(
        cls,
        test_type: str,
        app_cfg: AppCfg,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        log_setup: bool = False,
        **kwargs: Any,
    ) -> "TestClient":
        """
        Create a test environment for the given test type and repository type. A
        single environment, with a common test directory, is kept for each test type.
        """
        if app_cfg.name not in cls.TEST_CLIENTS:
            test_name = get_test_name(test_type)
            test_dir = get_test_output_dir(test_name)
            is_new_test_dir = True
            # Find existing test dir for same test type and use that if found,
            # so all results come in the same dir
            for stored_name, stored_env in cls.TEST_CLIENTS.items():
                if stored_name.startswith(test_type):
                    test_name = stored_env.test_name
                    test_dir = stored_env.test_dir
                    is_new_test_dir = False
                    break
            # Adjust config to new dir and copy any repository files there
            if is_new_test_dir:
                app_cfg.copy_repository_files(test_dir)
            cls.TEST_CLIENTS[app_cfg.name] = cls(
                test_name,
                test_dir,
                app_cfg,
                verbose=verbose,
                log_level=log_level,
                log_setup=log_setup,
                **kwargs,
            )
        return cls.TEST_CLIENTS[app_cfg.name]  # type: ignore[no-any-return]

    def __init__(
        self,
        test_name: str,
        test_dir: Path,
        app_cfg: BaseAppCfg,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        log_setup: bool = False,
        use_endpoints: bool = False,
        default_route_prefix: str | None = None,
        **kwargs: Any,
    ):
        # Set and adjust cfg
        app_cfg.cfg["app"]["debug"] = True
        curr_cfg = app_cfg.cfg["service"]["auth"]["props"]["root"]
        curr_cfg["organization"]["name"] = "org1"
        curr_cfg["user"]["key"] = "root1_1@org1.org"
        curr_cfg["user"]["email"] = "root1_1@org1.org"
        curr_cfg["user"]["name"] = "root1_1"

        # Create app
        TestClient._set_log_level(app_cfg, log_level)
        app_env = AppEnv(app_cfg, log_setup=log_setup, **kwargs)

        # Create endpoint test client if endpoints are to be used (including own
        # app_env), otherwise construct app env separately
        endpoint_test_client: OmopdbEndpointTestClient | None = None
        app_last_handled_exception: dict | None = None
        if use_endpoints:
            fast_api = create_fast_api(
                app_cfg.cfg,
                app=app_env.app,
                create_routers_fn=create_routers,
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
            endpoint_test_client = OmopdbEndpointTestClient(
                app_env.app,
                fast_api,
                app_last_handled_exception,
                user_class=model.User,
                user_invitation_class=model.UserInvitation,
                user_invitation_constraints_class=model.UserInvitationConstraints,
                organization_admin_policy_class=model.OrganizationAdminPolicy,
                user_crud_command_class=command.UserCrudCommand,
                user_invitation_crud_command_class=command.UserInvitationCrudCommand,
                organization_admin_policy_crud_command_class=command.OrganizationAdminPolicyCrudCommand,
                retrieve_invite_user_constraints_command_class=command.RetrieveInviteUserConstraintsCommand,
                invite_user_command_class=command.InviteUserCommand,
                register_invited_user_command_class=command.RegisterInvitedUserCommand,
                retrieve_organization_admin_name_emails_command_class=command.RetrieveOrganizationAdminNameEmailsCommand,
                update_user_command_class=command.UpdateUserCommand,
                user_invitation_request_body=UserInvitationRequestBody,
                update_user_request_body=UpdateUserRequestBody,
                **kwargs,
            )

        # Call base class constructor
        super().__init__(
            test_name,
            test_dir,
            app_cfg,
            app_env,
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
            register_invited_user_command_class=command.RegisterInvitedUserCommand,
            retrieve_organization_admin_name_emails_command_class=command.RetrieveOrganizationAdminNameEmailsCommand,
            update_user_command_class=command.UpdateUserCommand,
            verbose=verbose,
            log_level=log_level,
            use_endpoints=use_endpoints,
            endpoint_test_client=endpoint_test_client,
            app_last_handled_exception=app_last_handled_exception,
            **kwargs,
        )

    # def create_concept(
    #     self,
    #     user_or_str: str | model.User,
    #     code: str,
    #     concept_set_or_str: str | model.ConceptSet | None = None,
    #     set_dummy_concept_set: bool = False,
    # ) -> model.Concept:
    #     user: model.User = self._get_obj(
    #         model.User, user_or_str
    #     )  # type:ignore[assignment]
    #     concept_set: model.ConceptSet = (
    #         self._get_obj(model.ConceptSet, concept_set_or_str)
    #         if concept_set_or_str
    #         else None
    #     )  # type:ignore[assignment]
    #     if set_dummy_concept_set:
    #         if concept_set:
    #             raise ValueError(
    #                 "concept_set_or_str must be None if set_dummy_concept_set is True"
    #             )
    #         concept_set_id = self.generate_id()
    #     else:
    #         concept_set_id = concept_set.id
    #     concept = self.handle(
    #         command.ConceptCrudCommand(
    #             user=user,
    #             operation=CrudOperation.CREATE_ONE,
    #             objs=model.Concept(
    #                 concept_set_id=concept_set_id,
    #                 code=code,
    #             ),
    #         )
    #     )
    #     return self._set_obj(concept)  # type:ignore[return-value]
