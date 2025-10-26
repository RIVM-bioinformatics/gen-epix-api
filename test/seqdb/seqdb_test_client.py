import hashlib
import logging
import uuid
from pathlib import Path
from test.seqdb.seqdb_endpoint_test_client import SeqdbEndpointTestClient
from test.test_client.util import get_test_name, get_test_output_dir
from typing import Any, Type
from uuid import UUID

from gen_epix.commondb.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config import AppCfg, BaseAppCfg
from gen_epix.commondb.test.test_client import TestClient
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.api.organization import (
    UpdateUserRequestBody,
    UserInvitationRequestBody,
)
from gen_epix.seqdb.api.router import create_routers
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.policy import RoleGenerator
from gen_epix.seqdb.env import AppEnv


class SeqdbTestClient(TestClient):
    TEST_CLIENTS: dict[str, "SeqdbTestClient"] = {}

    MODEL_KEY_MAP = TestClient.MODEL_KEY_MAP | {
        model.User: "name",
        model.UserInvitation: "email",
        model.OrganizationAdminPolicy: ("organization_id", "user_id"),
        model.DataCollection: "name",
        model.LibraryPrepProtocol: "name",
        model.File: "id",
        model.ReadSet: "id",
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
        endpoint_test_client: SeqdbEndpointTestClient | None = None
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
            endpoint_test_client = SeqdbEndpointTestClient(
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

    def create_library_prep_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
    ) -> model.LibraryPrepProtocol:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type:ignore[assignment]
        library_prep_protocol: model.LibraryPrepProtocol = self.app.handle(
            command.LibraryPrepProtocolCrudCommand(
                operation=CrudOperation.CREATE_ONE,
                user=user,
                objs=model.LibraryPrepProtocol(
                    code=code, name=name if name else code
                ),  # type:ignore
            )
        )
        return self._set_obj(library_prep_protocol)

    def create_file(
        self, user_or_str: str | model.User, content: bytes | str | list[str]
    ) -> model.File:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type:ignore[assignment]
        content: bytes
        if isinstance(content, str):
            content = content.encode()
        elif isinstance(content, list):
            content = "\n".join(content).encode()
        else:
            content = content
        file_obj: model.File = self.app.handle(
            command.FileCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.File(content=content),
            )
        )

        return self._set_obj(file_obj)

    def create_read_set(
        self,
        user_or_str: str | model.User,
        library_prep_protocol_or_str: model.LibraryPrepProtocol | str | None = None,
        fwd_uri: str | None = None,
        rev_uri: str | None = None,
        fwd_file_id: UUID | None = None,
        rev_file_id: UUID | None = None,
        fwd_reads_hash_sha256_or_content: bytes | str | None = None,
        rev_reads_hash_sha256_or_content: bytes | str | None = None,
        sequencing_run_code: str = "",
        set_dummy_library_prep_protocol: bool = False,
    ) -> model.ReadSet:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type:ignore[assignment]
        library_prep_protocol_id: UUID
        if set_dummy_library_prep_protocol:
            if library_prep_protocol_or_str is not None:
                raise ValueError(
                    "library_prep_protocol_or_str must be None when "
                    "set_dummy_library_prep_protocol is True"
                )
            library_prep_protocol_id = uuid.uuid4()
        else:
            library_prep_protocol_id: UUID = (  # type:ignore[union-attr]
                self._get_obj(  # type:ignore[assignment]
                    model.LibraryPrepProtocol, library_prep_protocol_or_str
                )
            ).id  # type:ignore[assignment]
        fwd_reads_hash_sha256: bytes | None
        if isinstance(fwd_reads_hash_sha256_or_content, str):
            fwd_reads_hash_sha256 = hashlib.sha256(
                fwd_reads_hash_sha256_or_content.encode()
            ).digest()
        else:
            fwd_reads_hash_sha256 = fwd_reads_hash_sha256_or_content
        rev_reads_hash_sha256: bytes | None
        if isinstance(rev_reads_hash_sha256_or_content, str):
            rev_reads_hash_sha256 = hashlib.sha256(
                rev_reads_hash_sha256_or_content.encode()
            ).digest()
        else:
            rev_reads_hash_sha256 = rev_reads_hash_sha256_or_content
        read_set: model.ReadSet = self.app.handle(
            command.ReadSetCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.ReadSet(
                    library_prep_protocol_id=library_prep_protocol_id,
                    fwd_uri=fwd_uri,
                    rev_uri=rev_uri,
                    fwd_file_id=fwd_file_id,
                    rev_file_id=rev_file_id,
                    fwd_reads_hash_sha256=fwd_reads_hash_sha256,
                    rev_reads_hash_sha256=rev_reads_hash_sha256,
                    sequencing_run_code=sequencing_run_code,
                ),
            )
        )
        assert read_set.library_prep_protocol_id == library_prep_protocol_id
        assert read_set.fwd_reads_hash_sha256 == fwd_reads_hash_sha256
        assert read_set.rev_reads_hash_sha256 == rev_reads_hash_sha256
        assert read_set.fwd_file_id == fwd_file_id
        assert read_set.rev_file_id == rev_file_id
        assert read_set.fwd_uri == fwd_uri
        assert read_set.rev_uri == rev_uri
        return self._set_obj(read_set)

    def get_default_kwargs(self, model_class: Type[model.Model]) -> dict:
        if model_class == model.ReadSet:
            return {
                "fwd_uri": "http://reads/sample_x_1.fastq",
                "rev_uri": "http://reads/sample_x_2.fastq",
                "fwd_reads_hash_sha256_or_content": "a" * 64,
                "rev_reads_hash_sha256_or_content": "b" * 64,
            }
        raise NotImplementedError(f"No default kwargs for model class {model_class}")
