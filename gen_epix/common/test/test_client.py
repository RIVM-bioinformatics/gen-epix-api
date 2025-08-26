import datetime
import logging
import re
from enum import Enum
from pathlib import Path
from test.casedb.casedb_endpoint_test_client import CasedbEndpointTestClient
from gen_epix.common.test.enum import RepositoryType
from test.test_client.service_test_client import ServiceTestClient
from test.test_client.util import get_test_name, get_test_output_dir
from time import sleep
from typing import Any, Type, TypeVar
from uuid import UUID

from gen_epix.casedb.app_setup import create_fast_api

# Import role from casedb, since there is no complete role hierarchy in common
from gen_epix.casedb.domain.enum import Role
from gen_epix.casedb.domain.policy import RoleGenerator
from gen_epix.common.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.common.config import AppCfg
from gen_epix.common.domain import command, enum, model
from gen_epix.common.domain.enum import ServiceType
from gen_epix.common.env import BaseAppEnv
from gen_epix.common.util import map_paired_elements
from gen_epix.fastapp import CrudOperation

APP_CFG = AppCfg(
    app_name="CASEDB",
    service_type_enum=enum.ServiceType,
    repository_type_enum=enum.RepositoryType,
)
APP_CFG.setup_logger.setLevel(logging.WARNING)

BASE_MODEL_TYPE = TypeVar("T", bound=model.Model)


class OrganismType(enum.Enum):
    ORGANISM = "ORGANISM"
    TOXIN = "TOXIN"
    UNKNOWN = "UNKNOWN"


class TestClient(ServiceTestClient):

    DEFAULT_LOAD_TARGET = "empty"

    MODEL_KEY_MAP = {
        model.User: "name",
        model.UserInvitation: "email",
        model.Organization: "name",
        model.DataCollection: "name",
    }

    @classmethod
    def get_test_client(
        cls,
        repository_type: Enum,
        test_type: Enum,
        load_target: str,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        log_setup: bool = False,
        **kwargs: Any,
    ) -> "TestClient":
        """
        Create a test environment for the given test type and repository type. A
        single environment, with a common test directory, is kept for each test type.
        """
        key = (test_type, repository_type, load_target)
        if key not in ServiceTestClient.TEST_CLIENTS:
            test_dir = None
            for stored_key, stored_env in ServiceTestClient.TEST_CLIENTS.items():
                stored_test_type, _, _ = stored_key
                if stored_test_type == test_type:
                    test_dir = stored_env.test_dir
                    break
            ServiceTestClient.TEST_CLIENTS[key] = TestClient(
                test_type=test_type,
                repository_type=repository_type,
                load_target=load_target,
                verbose=verbose,
                log_level=log_level,
                log_setup=log_setup,
                test_dir=test_dir,
                **kwargs,
            )
        return ServiceTestClient.TEST_CLIENTS[key]

    def __init__(
        self,
        app_cfg: AppCfg,
        app_env_class: Type[BaseAppEnv],
        repository_type: Enum,
        test_type: Enum,
        load_target: str,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        log_setup: bool = False,
        test_dir: Path | None = None,
        **kwargs: bool | str | int | dict,
    ):
        test_client_repository_type = RepositoryType(repository_type.value)

        # Set up test name and directory
        cfg = app_cfg.cfg
        test_name = get_test_name(test_type)
        test_dir: Path = test_dir or get_test_output_dir(test_name)

        # Set and adjust cfg
        app_cfg.cfg.app.debug = True
        app_cfg.cfg.secret["db"]["repository_type"] = repository_type
        # Adjust cfg for root user
        curr_cfg = app_cfg.cfg.secret.root
        curr_cfg.organization.name = "org1"
        curr_cfg.user.email = "root1_1@org1.org"
        # Copy any repository files to test directory
        ServiceTestClient._init_repositories(
            app_cfg.cfg.secret.repository[repository_type.value],
            set(ServiceType),
            test_client_repository_type,
            load_target,
            test_dir,
        )

        # Create app
        ServiceTestClient._set_log_level(app_cfg, log_level)
        app_env = app_env_class(app_cfg, log_setup=log_setup, **kwargs)

        # Create endpoint test client if endpoints are to be used (including own
        # app_env), otherwise construct app env separately
        use_endpoints: bool = kwargs.pop("use_endpoints", False)
        endpoint_test_client: CasedbEndpointTestClient | None = None
        app_last_handled_exception: dict | None = None
        if use_endpoints:
            fast_api = create_fast_api(
                cfg,
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
            endpoint_test_client = CasedbEndpointTestClient(
                app_env.app, fast_api, app_last_handled_exception, **kwargs
            )

        # Call base class constructor
        super().__init__(
            app_env,
            app_cfg,
            test_type=test_type,
            test_name=test_name,
            test_dir=test_dir,
            repository_type=test_client_repository_type,
            load_target=load_target,
            roles=enum.Role,
            role_hierarchy=RoleGenerator.ROLE_HIERARCHY,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
            verbose=verbose,
            log_level=log_level,
            use_endpoints=use_endpoints,
            endpoint_test_client=endpoint_test_client,
            app_last_handled_exception=app_last_handled_exception,
            **kwargs,
        )

    def get_root_user(self) -> model.User:
        return model.User(
            organization_id=self.cfg.secret.root.organization.id,
            **self.cfg.secret.root.user,
        )

    def create_organization(
        self, user: str | model.User, organization_name: str
    ) -> model.Organization:
        user = self._get_obj(model.User, user)
        organization = self.app.handle(
            command.OrganizationCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Organization(
                    name=organization_name, legal_entity_code=organization_name
                ),
            )
        )
        return self._set_obj(organization)

    def invite_and_register_user(
        self,
        user: str | model.User,
        user_name: str,
        set_dummy_organization: bool = False,
        set_dummy_token: bool = False,
    ) -> model.User:
        user: model.User = self._get_obj(model.User, user)
        m = re.match(r"^(.*?)(\d+)_(\d+)$", user_name.lower())
        if not m:
            raise ValueError(f"Invalid user name {user_name}")
        role = [x for x in Role if x.value.lower() == m.group(1).lower()][0]
        organization_name = "org" + m.group(2)
        if organization_name not in self.db[model.Organization]:
            if set_dummy_organization:
                organization_id = self.generate_id()
            else:
                raise ValueError(f"Organization {organization_name} not found")
        else:
            organization_id = self.db[model.Organization][organization_name].id
        cmd_class = command.InviteUserCommand
        user_invitation = self.handle(
            cmd_class(
                user=user,
                email=f"{user_name}@{organization_name}.org",
                roles={role},
                organization_id=organization_id,
            )
        )
        if set_dummy_token:
            user_invitation.token = str(self.generate_id())
        tgt_user = self.handle(
            command.RegisterInvitedUserCommand(
                user=model.User(
                    email=f"{user_name}@{organization_name}.org",
                    organization_id=organization_id,
                    roles={role},
                ),
                token=user_invitation.token,
            )
        )
        tgt_user.name = user_name

        invitations = self.handle(
            command.UserInvitationCrudCommand(
                user=user,
                operation=CrudOperation.READ_ALL,
            )
        )
        if any(
            x.email == tgt_user.email and x.roles == tgt_user.roles for x in invitations
        ):
            raise ValueError(
                f"Invitation for {tgt_user.email} not removed after registration"
            )

        return self._set_obj(tgt_user)

    def create_data_collection(
        self,
        user: str | model.User,
        name: str,
    ) -> model.DataCollection:
        user: model.User = self._get_obj(model.User, user)
        data_collection = self.handle(
            command.DataCollectionCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.DataCollection(
                    name=name,
                ),
            )
        )
        return self._set_obj(data_collection)

    def update_user(
        self,
        user: str | model.User,
        tgt_user: str | model.User,
        is_active: bool | None = None,
        roles: set[enum.Role] | None = None,
        organization: str | None = None,
        set_dummy_organization: bool = False,
    ) -> model.User:
        user = self._get_obj(model.User, user)
        tgt_user = self._get_obj(model.User, tgt_user, copy=True)
        if not organization:
            if set_dummy_organization:
                organization_id = self.generate_id()
            else:
                organization_id = None
        else:
            if set_dummy_organization:
                raise ValueError("Organization given and set_dummy_organization True")
            organization_id = self._get_obj(model.Organization, organization).id
        has_updates = False
        if is_active is not None and tgt_user.is_active != is_active:
            has_updates = True
            tgt_user.is_active = is_active
        if roles is not None and tgt_user.roles != roles:
            has_updates = True
            tgt_user.roles = roles
        if organization_id is not None and tgt_user.organization_id != organization_id:
            has_updates = True
            tgt_user.organization_id = organization_id
        sleep(0.000000001)  # To avoid having same _modified_at as tgt_user
        updated_tgt_user = self.handle(
            command.UpdateUserCommand(
                user=user,
                tgt_user_id=tgt_user.id,
                is_active=is_active,
                roles=roles,
                organization_id=organization_id,
            )
        )
        updated_tgt_user.name = tgt_user.name
        ServiceTestClient._verify_updated_obj(
            tgt_user, updated_tgt_user, user.id, verify_modified=has_updates
        )
        return self._set_obj(updated_tgt_user, update=True)

    def temp_update_user_own_organization(
        self,
        user: str | model.User,
        organization: str | None = None,
        set_dummy_organization: bool = False,
    ) -> model.User:
        user: model.User = self._get_obj(model.User, user)
        root_user: model.User = self._get_obj(model.User, "root1_1")
        orig_organization_id = user.organization_id
        if not organization:
            if set_dummy_organization:
                organization_id = self.generate_id()
            else:
                raise ValueError(
                    "Organization not given and set_dummy_organization False"
                )
        else:
            if set_dummy_organization:
                raise ValueError("Organization given and set_dummy_organization True")
            organization_id = self._get_obj(model.Organization, organization).id
        # Get current policies
        prev_user_access_case_policies = self.handle(
            command.UserAccessCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        prev_user_access_case_policy_ids = {
            x.id for x in prev_user_access_case_policies if x.user_id == user.id
        }
        prev_user_share_case_policies = self.handle(
            command.UserShareCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        prev_user_share_case_policy_ids = {
            x.id for x in prev_user_share_case_policies if x.user_id == user.id
        }
        # Update user organization
        sleep(0.000000001)  # To avoid having same _modified_at as tgt_user
        user = self.handle(
            command.UpdateUserOwnOrganizationCommand(
                user=user,
                organization_id=organization_id,
            )
        )
        # Verify outcome
        if user.organization_id != organization_id:
            raise ValueError(f"organization_id not updated")
        new_user_access_case_policies = self.handle(
            command.UserAccessCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        new_user_access_case_policy_ids = {
            x.id for x in new_user_access_case_policies if x.user_id == user.id
        }
        new_user_share_case_policies = self.handle(
            command.UserShareCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        new_user_share_case_policy_ids = {
            x.id for x in new_user_share_case_policies if x.user_id == user.id
        }
        if new_user_access_case_policy_ids.intersection(
            prev_user_access_case_policy_ids
        ):
            raise ValueError(f"User case policies not updated")
        if new_user_share_case_policy_ids.intersection(prev_user_share_case_policy_ids):
            raise ValueError(f"User data collection policies not updated")
        return self._set_obj(user, update=True)

    def read_all_users(self) -> list[model.User]:
        return self.services[ServiceType.ORGANIZATION].crud(
            command.UserCrudCommand(
                user=None,
                operation=CrudOperation.READ_ALL,
            )
        )

    def read_users_by_role(self, role: enum.Role) -> list[model.User]:
        users = self.read_all_users()
        return [x for x in users if role in x.roles]

    def check_user_has_role(
        self, user: str | model.User, role: Role, exclusive: bool = True
    ) -> bool:
        user: model.User = self._get_obj(model.User, user)
        roles = user.roles
        if exclusive:
            return role in roles and len(roles) == 1
        return role in roles

    def print_organizations(self) -> None:
        organizations = self.read_all("root1_1", model.Organization, cascade=True)
        print("\nOrganizations:")
        for x in sorted(organizations, key=lambda x: x.name):
            print(f"{x.name} ({x.id})")

    def print_data_collections(self) -> None:
        data_collections = self.read_all("root1_1", model.DataCollection, cascade=True)
        print("\nDataCollections:")
        for x in sorted(data_collections, key=lambda x: x.name):
            print(f"{x.name} ({x.id})")

    def print_users(self) -> None:
        user: model.User = self._get_obj(model.User, "root1_1")
        users = self.read_all(user, model.User)
        organizations = {x.id: x for x in self.read_all(user, model.Organization)}
        print("\nUsers:")
        for x in sorted(
            users, key=lambda x: (organizations[x.organization_id].name, x.email)
        ):
            print(
                f"{organizations[x.organization_id].name} / {x.email}: "
                + ", ".join([z for z in sorted(y.name for y in x.roles)])
                + f" ({x.id})"
            )

    def print_user_permissions(self, user: str | model.User) -> None:
        user: model.User = self._get_obj(model.User, user)
        user_permissions = self.app.user_manager.get_user_permissions(user)
        command_permissions = map_paired_elements(
            ((x.command_name, x.permission_type) for x in user_permissions), as_set=True
        )
        print(
            f"\nPermissions for user {user.name} (n_commands={len(command_permissions)}):"
        )
        model.Permission
        for x in sorted(user_permissions, key=lambda x: x.sort_key):
            print(f"{x}")

    def _get_obj(
        self,
        model_class: Type[model.Model],
        obj: (
            str
            | UUID
            | model.Model
            | list[str | UUID | model.Model]
            | tuple[UUID, UUID]
        ),
        copy: bool = False,
        on_missing: str = "raise",
    ) -> BASE_MODEL_TYPE | list[BASE_MODEL_TYPE]:
        if isinstance(obj, list):
            return [self._get_obj(model_class, x) for x in obj]
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        if model_class == model.Case:
            if not isinstance(key, datetime.datetime):
                key = self._convert_case_code_to_date(key)
        if model_class == model.CaseDataCollectionLink:
            dc_id = key[0]
            case_id = key[1]

            case_data_collection_links = self.read_all(
                "root1_1", model.CaseDataCollectionLink, cascade=True
            )
            good_case_data_collection_links_list = []
            for y in case_data_collection_links:
                if y.case_id == case_id and y.data_collection_id == dc_id:
                    good_case_data_collection_links_list.append(y)

            if not good_case_data_collection_links_list:
                return None

            assert (
                len(good_case_data_collection_links_list) == 1
            ), "currently designed for one at a time"
            if copy:
                return table[key].model_copy()
            return table[key]
        else:
            key = self._get_obj_key(table, model_class, obj, on_missing)

        if key not in table:
            if on_missing == "raise":
                raise ValueError(f"{model_class.__name__} {obj} not found")
            elif on_missing == "return_none":
                return None
            else:
                raise NotImplementedError()
        return table[key] if not copy else table[key].model_copy()
