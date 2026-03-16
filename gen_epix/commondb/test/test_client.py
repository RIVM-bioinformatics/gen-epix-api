import datetime
import logging
import re
from collections.abc import Hashable
from enum import Enum
from pathlib import Path
from time import sleep
from typing import Any, TypeVar, cast
from uuid import UUID

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.base_env import BaseAppComposer
from gen_epix.commondb.config import BaseAppCfg
from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.test.endpoint_test_client import EndpointTestClient
from gen_epix.commondb.test.util import set_log_level
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.model import Command
from gen_epix.util import map_paired_elements

BASE_MODEL_TYPE = TypeVar("BASE_MODEL_TYPE", bound=model.Model)


class TestClient:

    DEFAULT_ROUTE_PREFIX_VALUE = "/v1"

    MODEL_KEY_MAP: dict[type[model.Model], str | tuple[str, ...]] = {
        model.User: "name",
        model.UserInvitation: "email",
        model.Organization: "name",
        model.DataCollection: "name",
        model.OrganizationAdminPolicy: ("organization_id", "user_id"),
        model.Site: ("name"),
        model.Contact: ("name"),
        model.IdentifierIssuer: "code",
        model.OrganizationIdentifierIssuerLink: (
            "organization_id",
            "identifier_issuer_id",
        ),
    }

    def __init__(
        self,
        test_name: str,
        test_dir: Path,
        app_cfg: BaseAppCfg,
        app_composer: BaseAppComposer,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        use_endpoints: bool = False,
        default_route_prefix: str | None = None,
        **kwargs: Any,
    ):
        # Set provided parameters
        self.test_name = test_name
        self.test_dir = test_dir
        self.app_cfg = app_cfg
        self.app_composer = app_composer
        self.default_route_prefix = (
            default_route_prefix or self.DEFAULT_ROUTE_PREFIX_VALUE
        )
        self.log_level = log_level
        self.verbose = verbose

        # Get implementation details
        app_impl: AppImplDetails = app_composer.app.impl
        self.user_class: type[model.User] = app_impl.get_mapped_class(model.User)
        self.user_invitation_class: type[model.UserInvitation] = (
            app_impl.get_mapped_class(model.UserInvitation)
        )
        self.user_invitation_constraints_class: type[
            model.UserInvitationConstraints
        ] = app_impl.get_mapped_class(model.UserInvitationConstraints)
        self.organization_admin_policy_class: type[model.OrganizationAdminPolicy] = (
            app_impl.get_mapped_class(model.OrganizationAdminPolicy)
        )
        self.user_crud_command_class: type[command.UserCrudCommand] = (
            app_impl.get_mapped_class(command.UserCrudCommand)
        )
        self.user_invitation_crud_command_class: type[
            command.UserInvitationCrudCommand
        ] = app_impl.get_mapped_class(command.UserInvitationCrudCommand)
        self.organization_admin_policy_crud_command_class: type[
            command.OrganizationAdminPolicyCrudCommand
        ] = app_impl.get_mapped_class(command.OrganizationAdminPolicyCrudCommand)
        self.retrieve_invite_user_constraints_command_class: type[
            command.RetrieveInviteUserConstraintsCommand
        ] = app_impl.get_mapped_class(command.RetrieveInviteUserConstraintsCommand)
        self.invite_user_command_class: type[command.InviteUserCommand] = (
            app_impl.get_mapped_class(command.InviteUserCommand)
        )
        self.register_invited_user_command_class: type[
            command.RegisterInvitedUserCommand
        ] = app_impl.get_mapped_class(command.RegisterInvitedUserCommand)
        self.retrieve_organization_admin_name_emails_command_class: type[
            command.RetrieveOrganizationAdminNameEmailsCommand
        ] = app_impl.get_mapped_class(
            command.RetrieveOrganizationAdminNameEmailsCommand
        )
        self.update_user_command_class: type[command.UpdateUserCommand] = (
            app_impl.get_mapped_class(command.UpdateUserCommand)
        )
        self.role_map = app_impl.role_map
        self.rev_role_map = app_impl.rev_role_map
        self.role_set_map = app_impl.role_set_map
        self.role_permissions_map = app_impl.role_permissions_map
        self.app = self.app_composer.app
        self.cfg = self.app.cfg
        self.services = app_impl.services
        self.repositories = app_impl.repositories

        # Set log level
        TestClient._set_log_level(app_cfg, log_level)

        # Set additional parameters
        self.root_role: str = self.role_map[enum.Role.ROOT]
        self.guest_role: str = self.role_map[enum.Role.GUEST]
        self.db: dict[type[model.Model], dict[Hashable, model.Model]] = {}
        self.props: dict = {}
        self.use_endpoints = use_endpoints
        self.default_route_prefix = (
            default_route_prefix or self.DEFAULT_ROUTE_PREFIX_VALUE
        )
        self.endpoint_test_client: EndpointTestClient | None = kwargs.pop(
            "endpoint_test_client"
        )
        self.app_last_handled_exception: dict | None = kwargs.pop(
            "app_last_handled_exception"
        )
        if self.use_endpoints:
            if not self.endpoint_test_client:
                raise ValueError(
                    "Endpoint test client not provided while use_endpoints=True"
                )
            if not self.app_last_handled_exception:
                raise ValueError(
                    "App last handled exception not provided while use_endpoints=True"
                )

        # Store remainder of kwargs
        self.props = kwargs

    def _get_obj(
        self,
        model_class: type[model.Model],
        obj: (
            str
            | UUID
            | model.Model
            | list[str | UUID | model.Model]
            | tuple[UUID, UUID]
        ),
        copy: bool = False,
        on_missing: str = "raise",
    ) -> model.Model | list[model.Model]:
        if isinstance(obj, list):
            return [self._get_obj(model_class, x) for x in obj]
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        key = self._get_obj_key(table, model_class, obj, on_missing)
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

        if key not in table:
            if on_missing == "raise":
                raise ValueError(f"{model_class.__name__} {obj} not found")
            elif on_missing == "return_none":
                return None
            else:
                raise NotImplementedError()
        return table[key] if not copy else table[key].model_copy()

    def handle(
        self,
        cmd: Command,
        return_response: bool = False,
        use_endpoint: bool | None = None,
        route_prefix: str | None = None,
        **kwargs: Any,
    ) -> Any:
        use_endpoint = use_endpoint if use_endpoint is not None else self.use_endpoints
        if use_endpoint:
            assert self.app_last_handled_exception is not None
            assert self.endpoint_test_client is not None

            route_prefix = route_prefix or self.default_route_prefix
            previous_exception_id = self.app_last_handled_exception["id"]
            retval, response = self.endpoint_test_client.handle(
                cmd,
                return_response=True,
                route_prefix=route_prefix,
                **kwargs,
            )

            # Check if an exception was raised before generating the HTTP response, and
            # if so, raise it
            exception_id = self.app_last_handled_exception["id"]
            if exception_id != previous_exception_id:
                exception = self.app_last_handled_exception["exception"]
                raise exception

            if return_response:
                return retval, response
            return retval

        else:
            return self.app.handle(cmd)

    def retrieve_user_by_key(self, user_key: str) -> model.User:
        user: model.User = self.app.user_manager.retrieve_user_by_key(user_key)  # type: ignore[assignment]
        return user

    def create_organization(
        self, user_or_str: str | model.User, organization_name: str
    ) -> model.Organization:
        user: model.User = self._get_obj(self.user_class, user_or_str)  # type: ignore[assignment]
        organization = self.app.handle(
            command.OrganizationCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Organization(
                    name=organization_name, legal_entity_code=organization_name
                ),
            )
        )
        retval: model.Organization = self._set_obj(organization)  # type: ignore[assignment]
        return retval

    def invite_and_register_user(
        self,
        user_or_str: str | model.User,
        user_name: str,
        set_dummy_organization: bool = False,
        set_dummy_token: bool = False,
        set_key: bool = True,
    ) -> model.User:
        root_user: model.User = self.get_root_user()
        user: model.User = self._get_obj(self.user_class, user_or_str)  # type: ignore[assignment]
        m = re.match(r"^(.*?)(\d+)_(\d+)$", user_name.lower())
        if not m:
            raise ValueError(f"Invalid user name {user_name}")
        role = [
            y for x, y in self.role_map.items() if x.name.lower() == m.group(1).lower()
        ][0]
        organization_name = "org" + m.group(2)
        organization_id: UUID
        if organization_name not in self.db[model.Organization]:
            if set_dummy_organization:
                organization_id = self.generate_id()
            else:
                raise ValueError(f"Organization {organization_name} not found")
        else:
            organization_id = self.db[model.Organization][organization_name].id  # type: ignore[assignment]
        user_invitation: model.UserInvitation = self.handle(
            self.invite_user_command_class(
                user=user,
                key=f"{user_name}@{organization_name}.org" if set_key else None,
                email=f"{user_name}@{organization_name}.org",
                roles={role},
                organization_id=organization_id,
            )
        )
        if set_dummy_token:
            user_invitation.token = str(self.generate_id())
        tgt_user: model.User = self.handle(
            self.register_invited_user_command_class(
                user=self.user_class(
                    key=f"{user_name}@{organization_name}.org",
                    email=f"{user_name}@{organization_name}.org",
                    name=user_name,
                    organization_id=organization_id,
                    roles={role},
                ),
                token=user_invitation.token,
            )
        )
        tgt_user.name = user_name
        # Verify if the right role(s) were assigned
        if tgt_user.roles != {role}:
            raise ValueError(
                f"User {tgt_user.name} has incorrect roles {tgt_user.roles}, expected {role}"
            )
        # Verify against user invitation constraints
        user_invitation_constraints: model.UserInvitationConstraints = self.handle(
            self.retrieve_invite_user_constraints_command_class(
                user=user,
            )
        )
        if tgt_user.organization_id not in user_invitation_constraints.organization_ids:
            raise ValueError("User invitation constraints not met for organization_id")
        if not tgt_user.roles.issubset(user_invitation_constraints.roles):
            raise ValueError("User invitation constraints not met for roles")
        # Verify no invitations remain for the user
        remaining_invitations: list[model.UserInvitation] = self.handle(
            self.user_invitation_crud_command_class(
                user=root_user,
                operation=CrudOperation.READ_ALL,
                obj_ids=None,
            )
        )
        if tgt_user.key is not None and any(
            x.key == tgt_user.key for x in remaining_invitations
        ):
            raise ValueError(f"Some user invitations remaining for key {tgt_user.key}")
        retval: model.User = self._set_obj(tgt_user)  # type: ignore[assignment]
        return retval

    def create_data_collection(
        self,
        user_or_str: str | model.User,
        name: str,
        created_at: datetime.datetime | None = None,
        modified_at: datetime.datetime | None = None,
        modified_by: UUID | None = None,
    ) -> model.DataCollection:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type: ignore[assignment]
        data_collection = self.handle(
            command.DataCollectionCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.DataCollection(
                    name=name,
                    created_at=created_at,
                    modified_at=modified_at,
                    modified_by=modified_by,
                ),
            )
        )
        return self._set_obj(data_collection)  # type: ignore[return-value]

    def create_org_admin_policy(
        self,
        user_or_str: str | model.User,
        tgt_user_or_str: str | model.User,
        organization_or_str: str | model.Organization,
        is_active: bool = True,
    ) -> model.OrganizationAdminPolicy:
        user: model.User = self._get_obj(self.user_class, user_or_str)  # type: ignore[assignment]
        tgt_user: model.User = self._get_obj(
            self.user_class, tgt_user_or_str
        )  # type: ignore[assignment]
        organization: model.Organization = self._get_obj(
            model.Organization, organization_or_str
        )  # type: ignore[assignment]
        assert organization.id is not None
        organization_admin_policy: model.OrganizationAdminPolicy = self.app.handle(
            self.organization_admin_policy_crud_command_class(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=self.organization_admin_policy_class(
                    organization_id=organization.id,
                    user_id=tgt_user.id,
                    is_active=is_active,
                ),
            )
        )
        return self._set_obj(organization_admin_policy)  # type: ignore[return-value]

    def create_identifier_issuer(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
        description: str | None = None,
    ) -> model.IdentifierIssuer:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type: ignore[assignment]
        identifier_issuer = self.handle(
            command.IdentifierIssuerCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.IdentifierIssuer(
                    code=code,
                    name=name or code,
                    description=description,
                ),
            )
        )
        return self._set_obj(identifier_issuer)  # type: ignore[return-value]

    def create_organization_identifier_issuer_link(
        self,
        user_or_str: str | model.User,
        organization_or_str: str | model.Organization,
        identifier_issuer_or_str: str | model.IdentifierIssuer,
    ) -> model.OrganizationIdentifierIssuerLink:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type: ignore[assignment]
        organization: model.Organization = self._get_obj(
            model.Organization, organization_or_str
        )  # type: ignore[assignment]
        identifier_issuer: model.IdentifierIssuer = self._get_obj(
            model.IdentifierIssuer, identifier_issuer_or_str
        )  # type: ignore[assignment]
        assert organization.id is not None
        assert identifier_issuer.id is not None
        organization_identifier_issuer_link: model.OrganizationIdentifierIssuerLink = (
            self.app.handle(
                command.OrganizationIdentifierIssuerLinkCrudCommand(
                    user=user,
                    operation=CrudOperation.CREATE_ONE,
                    objs=model.OrganizationIdentifierIssuerLink(
                        organization_id=organization.id,
                        identifier_issuer_id=identifier_issuer.id,
                    ),
                )
            )
        )
        return self._set_obj(
            organization_identifier_issuer_link
        )  # type: ignore[return-value]

    def read_all_user_invitations(
        self, user_or_str: str | model.User
    ) -> list[model.UserInvitation]:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type: ignore[assignment]
        invitations: list[model.UserInvitation] = self.handle(
            self.user_invitation_crud_command_class(
                user=user,
                operation=CrudOperation.READ_ALL,
            )
        )
        return invitations

    def read_organization_admin_name_emails(
        self, user_or_str: str | model.User
    ) -> list[model.UserNameEmail]:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type: ignore[assignment]
        user_name_emails: list[model.UserNameEmail] = self.app.handle(
            self.retrieve_organization_admin_name_emails_command_class(user=user)
        )
        return user_name_emails

    def read_all_users(self) -> list[model.User]:
        root_user = self.get_root_user()
        retval: list[model.User] = self.app.handle(
            self.user_crud_command_class(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        return retval

    def read_users_by_role(self, role: Enum) -> list[model.User]:
        users = self.read_all_users()
        return [x for x in users if role in x.roles]

    def update_user(
        self,
        user_or_str: str | model.User,
        tgt_user_or_str: str | model.User,
        is_active: bool | None = None,
        roles: set[str] | None = None,
        organization_or_str: str | None = None,
        set_dummy_organization: bool = False,
    ) -> model.User:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type: ignore[assignment]
        tgt_user: model.User = self._get_obj(
            self.user_class, tgt_user_or_str, copy=True
        )  # type: ignore[assignment]
        if not organization_or_str:
            if set_dummy_organization:
                organization_id = self.generate_id()
            else:
                organization_id = None
        else:
            if set_dummy_organization:
                raise ValueError("Organization given and set_dummy_organization True")
            organization: model.Organization = self._get_obj(
                model.Organization, organization_or_str
            )  # type: ignore[assignment]
            organization_id = organization.id
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
        assert tgt_user.id is not None
        updated_tgt_user = self.handle(
            self.update_user_command_class(
                user=user,
                tgt_user_id=tgt_user.id,
                is_active=tgt_user.is_active,
                roles=tgt_user.roles,
                organization_id=tgt_user.organization_id,
            )
        )
        updated_tgt_user.name = tgt_user.name
        is_privileged = bool(user.roles & self.role_set_map[enum.RoleSet.ROOT])
        TestClient._verify_updated_obj(
            tgt_user,
            updated_tgt_user,
            user.id,
            verify_modified=has_updates,
            is_privileged=is_privileged,
        )
        return self._set_obj(updated_tgt_user, update=True)  # type: ignore[return-value]

    def get_root_user(self, user_key: str | None = None) -> model.User:
        if user_key is None:
            user_key = self.cfg["service"]["auth"]["props"]["root"]["user"]["key"]
        user: model.User = self.app.user_manager.retrieve_user_by_key(user_key)  # type: ignore[assignment]
        return user

    def get_org_ids_for_org_admin(
        self,
        user_or_str: str | model.User,
        include_self: bool = False,
        on_no_admin: str = "raise",
    ) -> list[model.Organization]:
        user: model.User = self._get_obj(self.user_class, user_or_str)  # type: ignore[assignment]
        org_admin_policies: list[model.OrganizationAdminPolicy] = [  # type: ignore[assignment]
            x
            for x in self.db[self.organization_admin_policy_class].values()
            if x.user_id == user.id
        ]
        if not org_admin_policies:
            if on_no_admin == "raise":
                raise ValueError(f"User {user.name} is not an organization admin")
            elif on_no_admin == "return":
                return []
        organization_ids = {x.organization_id for x in org_admin_policies}
        if include_self:
            organization_ids.add(user.organization_id)
        return organization_ids

    def get_own_org_admin_users(
        self,
        user_or_str: str | model.User,
        include_self: bool = False,
    ) -> list[model.User]:
        user: model.User = self._get_obj(self.user_class, user_or_str)  # type: ignore[assignment]
        org_admin_policies: list[model.OrganizationAdminPolicy] = [
            x
            for x in self.db[self.organization_admin_policy_class].values()
            if x.organization_id == user.organization_id and x.is_active
        ]
        user_ids = {x.user_id for x in org_admin_policies}
        if include_self:
            user_ids.add(user.id)
        return [
            x
            for x in self.db[self.user_class].values()
            if x.id in user_ids and x.is_active
        ]

    def get_users_for_org(
        self,
        user_or_str: str | model.User,
        on_no_admin: str = "raise",
    ) -> list[model.User]:
        user: model.User = self._get_obj(self.user_class, user_or_str)  # type: ignore[assignment]
        return [
            x
            for x in self.db[self.user_class].values()
            if x.organization_id == user.organization_id
        ]

    def get_users_for_org_admin(
        self,
        user_or_str: str | model.User,
        include_self: bool = False,
        include_other_org_admins: bool = False,
        on_no_admin: str = "raise",
    ) -> list[model.User]:
        user: model.User = self._get_obj(self.user_class, user_or_str)  # type: ignore[assignment]
        org_admin_policies: list[model.OrganizationAdminPolicy] = (
            [  # type: ignore[assignment]
                x
                for x in self.db[self.organization_admin_policy_class].values()
                if x.user_id == user.id and x.is_active
            ]
        )
        if not org_admin_policies:
            if on_no_admin == "raise":
                raise ValueError(f"User {user.name} is not an organization admin")
            elif on_no_admin == "return":
                return []
        organization_ids = {x.organization_id for x in org_admin_policies}
        user_ids = {user.id} if include_self else set()
        if include_other_org_admins:
            other_org_admin_policies: list[model.OrganizationAdminPolicy] = (
                [  # type: ignore[assignment]
                    x
                    for x in self.db[self.organization_admin_policy_class].values()
                    if x.organization_id in organization_ids and x.is_active
                ]
            )
            user_ids.update({x.user_id for x in other_org_admin_policies})
        tgt_users: list[model.User] = list(self.db[self.user_class].values())
        return [
            x
            for x in tgt_users
            if x.id in user_ids or x.organization_id in organization_ids
        ]

    def is_sub_role(
        self,
        sub_role: str,
        role: str,
        allow_equal: bool = False,
    ) -> bool:
        """
        Check if sub_role is indeed a sub-role of role based on the permissions
        they each have. Set allow_equal=True to allow sub_role to be equal to role.
        """
        permissions = self.role_permissions_map[role]
        sub_permissions = self.role_permissions_map[sub_role]
        if allow_equal:
            return sub_permissions.issubset(permissions[role])
        return len(permissions) != len(sub_permissions) and sub_permissions.issubset(
            permissions
        )

    def read_all(
        self,
        user_or_key: model.User | str,
        model_class: type[model.Model],
        cascade: bool = False,
    ) -> list[model.Model]:
        user: model.User = self._get_obj(self.user_class, user_or_key)  # type: ignore[assignment]
        retval: list[model.Model] = self.handle(
            self.app.domain.get_crud_command_for_model(model_class)(
                user=user,
                operation=CrudOperation.READ_ALL,
                props={"cascade_read": cascade},
            ),
            use_endpoint=False,
        )
        return retval

    def read_some(
        self,
        user_or_key: model.User | str,
        model_class: type[model.Model],
        obj_ids: list[UUID] | set[UUID],
        cascade: bool = False,
    ) -> list[model.Model]:
        user: model.User = self._get_obj(self.user_class, user_or_key)  # type: ignore[assignment]
        retval: list[model.Model] = self.handle(
            self.app.domain.get_crud_command_for_model(model_class)(
                user=user,
                operation=CrudOperation.READ_SOME,
                obj_ids=(
                    list(obj_ids)
                    if isinstance(obj_ids, set)
                    else obj_ids  # type: ignore[arg-type]
                ),
                props={"cascade_read": cascade},
            ),
            use_endpoint=False,
        )
        return retval

    def read_some_by_property(
        self,
        user_or_key: model.User | str,
        model_class: type[model.Model],
        name: str,
        value: Any,
        cascade: bool = False,
    ) -> list[model.Model]:
        objs = self.read_all(user_or_key, model_class, cascade=cascade)
        return [x for x in objs if getattr(x, name) == value]

    def read_one_by_property(
        self,
        user_or_key: model.User | str,
        model_class: type[model.Model],
        name: str,
        value: Any,
        cascade: bool = False,
    ) -> model.Model:
        objs = self.read_some_by_property(
            user_or_key, model_class, name, value, cascade=cascade
        )
        if len(objs) == 0:
            raise ValueError(f"{model_class} with {name}='{value}' not found")
        if len(objs) > 1:
            raise ValueError(f"Multiple {model_class} with {name}='{value}' found")
        return objs[0]

    def update_object(
        self,
        user_or_key: str | model.User,
        model_class: type[model.Model],
        obj_or_key: model.Model | str,
        props: dict[str, Any | None],
        set_dummy_link: dict[str, bool] | bool = False,
        exclude_none: bool = True,
    ) -> model.Model:
        user: model.User = self._get_obj(self.user_class, user_or_key)  # type: ignore[assignment]
        obj: model.Model = self._get_obj(
            model_class, obj_or_key, copy=True
        )  # type: ignore[assignment]
        self._update_object_properties(
            obj, props, set_dummy_link, exclude_none=exclude_none
        )
        sleep(0.000000001)
        updated_obj = self.handle(
            self.app.domain.get_crud_command_for_model(model_class)(
                user=user,
                operation=CrudOperation.UPDATE_ONE,
                objs=obj,
            )
        )
        assert user.id
        is_privileged = bool(user.roles & self.role_set_map[enum.RoleSet.ROOT])
        TestClient._verify_updated_obj(
            obj, updated_obj, user.id, is_privileged=is_privileged
        )
        return self._set_obj(updated_obj, update=True)

    def delete_object(
        self,
        user_or_key: str | model.User,
        model_class: type[model.Model],
        obj_or_key: model.Model | str | tuple[UUID, UUID],
        retry_obj: tuple[UUID, UUID] | None = None,
        verify: bool = False,
        delete_user_or_str: str | model.User | None = None,
    ) -> UUID:
        user: model.User = self._get_obj(self.user_class, user_or_key)  # type: ignore[assignment]
        obj: model.Model = self._get_obj(model_class, obj_or_key, copy=True)  # type: ignore[assignment]

        if not obj and retry_obj:
            obj = self._get_obj(model_class, retry_obj, copy=True)  # type: ignore[assignment]

        deleted_obj_id: UUID = self.handle(
            self.app.domain.get_crud_command_for_model(model_class)(
                user=user,
                operation=CrudOperation.DELETE_ONE,
                obj_ids=obj.id,
            )
        )
        # Verify if the object was deleted
        if verify:
            sleep(0.000000001)
            if delete_user_or_str is None:
                delete_user: model.User = user
            else:
                delete_user = self._get_obj(
                    self.user_class, delete_user_or_str
                )  # type: ignore[assignment]

            is_existing_obj = self.app.handle(
                self.app.domain.get_crud_command_for_model(model_class)(
                    user=delete_user,
                    operation=CrudOperation.EXISTS_ONE,
                    obj_ids=deleted_obj_id,
                )
            )
            if is_existing_obj:
                raise ValueError(f"Object {deleted_obj_id} not deleted")
        self._delete_obj(model_class, deleted_obj_id)
        return deleted_obj_id

    def verify_read_all(
        self,
        user_or_str: model.User | str,
        model_class: type[model.Model],
        expected_ids: set[UUID] | list[model.Model],
    ) -> None:
        user: model.User = self._get_obj(self.user_class, user_or_str)  # type: ignore[assignment]
        objs = self.handle(
            self.app.domain.get_crud_command_for_model(model_class)(
                user=user, operation=CrudOperation.READ_ALL
            )
        )
        actual_ids = {x.id for x in objs}
        if not isinstance(expected_ids, set):
            expected_ids = {x.id for x in expected_ids if x.id is not None}
        if actual_ids != expected_ids:
            extra_ids = actual_ids - expected_ids
            missing_ids = expected_ids - actual_ids
            extra_names = [
                self._get_key_for_obj(
                    self._get_obj(model_class, x)  # type: ignore[arg-type]
                )
                for x in extra_ids
            ]
            missing_names = [
                self._get_key_for_obj(
                    self._get_obj(model_class, x)  # type: ignore[arg-type]
                )
                for x in missing_ids
            ]
            raise ValueError(
                f"Difference in read all. Extra: {extra_names}. Missing: {missing_names}. User: {user.name}. Model: {model_class}"
            )

    def verify_user_has_role(
        self, user_or_str: str | model.User, role: Enum, exclusive: bool = True
    ) -> bool:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type: ignore[assignment]
        roles = user.roles
        if exclusive:
            return role in roles and len(roles) == 1
        return role in roles

    def generate_id(self) -> UUID:
        # Type cast needed because app.generate_id() returns Hashable
        return cast(UUID, self.app.generate_id())

    def print_organizations(self) -> None:
        organizations: list[model.Organization] = self.read_all(
            self.get_root_user(), model.Organization, cascade=True
        )  # type: ignore[assignment]
        print("\nOrganizations:")
        for x in sorted(organizations, key=lambda x: x.name):
            print(f"{x.name} ({x.id})")

    def print_data_collections(self) -> None:
        data_collections: list[model.DataCollection] = self.read_all(
            self.get_root_user(), model.DataCollection, cascade=True
        )  # type: ignore[assignment]
        print("\nDataCollections:")
        for x in sorted(data_collections, key=lambda x: x.name):
            print(f"{x.name} ({x.id})")

    def print_users(self) -> None:
        root_user: model.User = self.get_root_user()
        users: list[model.User] = self.read_all(
            root_user, self.user_class
        )  # type: ignore[assignment]
        organizations: dict[UUID, model.Organization] = {
            x.id: x  # type: ignore[misc]
            for x in self.read_all(root_user, model.Organization)
        }
        print("\nUsers:")
        for x in sorted(
            users, key=lambda x: (organizations[x.organization_id].name, x.key)
        ):
            print(
                f"{organizations[x.organization_id].name} / {x.key}: "
                + ", ".join(
                    [z for z in sorted(self.rev_role_map[y].name for y in x.roles)]
                )
                + f" ({x.id})"
            )

    def print_user_permissions(self, user_or_str: str | model.User) -> None:
        user: model.User = self._get_obj(self.user_class, user_or_str)  # type: ignore[assignment]
        user_permissions = self.app.user_manager.retrieve_user_permissions(user)
        command_permissions = map_paired_elements(
            ((x.command_name, x.permission_type) for x in user_permissions), as_set=True
        )
        print(
            f"\nPermissions for user {user.name} (n_commands={len(command_permissions)}):"
        )
        for x in sorted(list(user_permissions), key=lambda x: x.sort_key):  # type: ignore[arg-type,return-value]
            print(f"{x}")

    def print_org_admin_policies(self) -> None:
        org_admin_policies: list[model.OrganizationAdminPolicy] = self.read_all(  # type: ignore[assignment]
            "root1_1", self.organization_admin_policy_class, cascade=True
        )
        print("\nOrganizationAdminPolicies:")
        for x in sorted(
            org_admin_policies,
            key=lambda x: (x.organization.name, x.user.name),  # type: ignore[union-attr]
        ):
            print(
                f"{x.organization.name}: user={x.user.name} (is_active={x.is_active}) ({x.id})"  # type: ignore[union-attr]
            )

    def print_identifier_issuers(self) -> None:
        identifier_issuers: list[model.IdentifierIssuer] = self.read_all(  # type: ignore[assignment]
            "root1_1", model.IdentifierIssuer
        )
        print("\nIdentifierIssuers:")
        for x in sorted(identifier_issuers, key=lambda x: x.code):
            print(f"{x.code}: name={x.name} ({x.id})")

    def print_organization_identifier_issuer_links(self) -> None:
        organization_identifier_issuer_links: list[
            model.OrganizationIdentifierIssuerLink
        ] = self.read_all(  # type: ignore[assignment]
            "root1_1", model.OrganizationIdentifierIssuerLink
        )
        organization_ids = set(
            x.organization_id for x in organization_identifier_issuer_links
        )
        identifier_issuer_ids = set(
            x.identifier_issuer_id for x in organization_identifier_issuer_links
        )
        organizations: dict[UUID, model.Organization] = {
            x.id: x  # type: ignore[misc]
            for x in self.read_some("root1_1", model.Organization, organization_ids)
        }
        identifier_issuers: dict[UUID, model.IdentifierIssuer] = {
            x.id: x  # type: ignore[misc]
            for x in self.read_some(
                "root1_1", model.IdentifierIssuer, identifier_issuer_ids
            )
        }
        print("\nOrganizationIdentifierIssuerLinks:")
        for x in sorted(
            organization_identifier_issuer_links,
            key=lambda x: (
                organizations[x.organization_id].name,
                identifier_issuers[x.identifier_issuer_id].code,
            ),  # type: ignore[union-attr]
        ):
            print(
                f"{organizations[x.organization_id].name} -> {identifier_issuers[x.identifier_issuer_id].code} ({x.id})"  # type: ignore[union-attr]
            )

    def _get_key_for_obj(self, obj: model.Model) -> Any:
        key_fields = self.MODEL_KEY_MAP[obj.__class__]
        if isinstance(key_fields, str):
            return getattr(obj, key_fields)
        return tuple(getattr(obj, x) for x in key_fields)

    def _update_object_properties(
        self,
        obj: model.Model,
        props: dict[str, Any | None],
        set_dummy_link: dict[str, bool] | bool = False,
        exclude_none: bool = True,
    ) -> None:
        """
        Helper function for update methods. All the (field_name, value) pairs in props
        are set as attributes of obj. If the field_name is a relationship field, the value
        is set as the id of the linked object. If set_dummy_link is provided for a
        relationship field and no real linked obj is provided, a dummy id is put instead.
        If exclude_none is True, fields or link fields with value None are not set.
        """
        # Parse input
        model_class = obj.__class__
        assert model_class.ENTITY
        id_field_name = model_class.ENTITY.id_field_name
        assert id_field_name
        link_map = self._generate_link_map(model_class)
        set_dummy_link, default_set_dummy_link = self._get_dummy_link_defaults(
            set_dummy_link
        )
        # Set value fields and any links
        for field_name, value in props.items():
            if field_name in link_map:
                field_name, value = self._get_resolved_link_value(
                    set_dummy_link,
                    model_class,
                    id_field_name,
                    link_map,
                    default_set_dummy_link,
                    field_name,
                    value,
                )
            if exclude_none and value is None:
                continue
            setattr(obj, field_name, value)

    def _generate_link_map(
        self, model_class: type[model.Model]
    ) -> dict[str, tuple[str, type[model.Model]]]:
        link_map: dict[str, tuple[str, type[model.Model]]] = {
            x.relationship_field_name: (
                x.link_field_name,
                x.link_model_class,
            )  # type: ignore[misc]
            for x in model_class.ENTITY.links.values()  # type: ignore[union-attr]
            if x.relationship_field_name
        }

        return link_map

    def _get_dummy_link_defaults(
        self, set_dummy_link: dict[str, bool] | bool
    ) -> tuple[dict[str, bool], bool]:
        default_set_dummy_link = False
        if isinstance(set_dummy_link, bool):
            default_set_dummy_link = set_dummy_link
            set_dummy_link = {}

        return set_dummy_link, default_set_dummy_link

    def _get_resolved_link_value(
        self,
        set_dummy_link: dict[str, bool],
        model_class: type[model.Model],
        id_field_name: str,
        link_map: dict[str, tuple[str, type[model.Model]]],
        default_set_dummy_link: bool,
        field_name: str,
        value: Any,
    ) -> tuple[str, UUID | None]:
        field_name, link_model_class = link_map[field_name]
        if not value:
            if set_dummy_link.get(field_name, default_set_dummy_link):
                value = self.generate_id()
            else:
                value = None
        else:
            if set_dummy_link.get(field_name, default_set_dummy_link):
                raise ValueError(
                    f"{model_class.__name__} given and set dummy link True"
                )
            value = getattr(self._get_obj(link_model_class, value), id_field_name)

        return field_name, value

    def _get_obj_key(
        self,
        table: dict,
        model_class: type[model.Model],
        obj: (
            str
            | UUID
            | model.Model
            | list[str | UUID | model.Model]
            | tuple[UUID, UUID]
        ),
        on_missing: str,
    ) -> tuple[UUID, UUID] | UUID | None:
        key_fields = self.MODEL_KEY_MAP[model_class]
        assert model_class.ENTITY
        get_obj_id = model_class.ENTITY.get_obj_id
        if not isinstance(key_fields, tuple):
            key_fields = (key_fields,) if len(key_fields) > 1 else key_fields
        if isinstance(obj, str) or isinstance(obj, datetime.datetime):
            key = (obj,)
        elif isinstance(obj, UUID):
            key = [
                x for x, y in table.items() if get_obj_id(y) == obj
            ]  # type: ignore[assignment]
            if key:
                pass
            elif on_missing == "raise":
                raise ValueError(f"{model_class.__name__} {obj} not found")
            elif on_missing == "return_none":
                return None
            else:
                raise NotImplementedError()
        elif isinstance(obj, model.Model):
            key = tuple(getattr(obj, x) for x in key_fields)
        elif isinstance(obj, tuple):
            key = obj  # type: ignore[assignment]
        else:
            raise ValueError(f"Invalid object: {obj}")
        key = key if len(key) > 1 else key[0]  # type: ignore[assignment]
        return key  # type: ignore[return-value]

    def _get_obj(
        self,
        model_class: type[model.Model],
        obj: (
            str
            | UUID
            | model.Model
            | list[str | UUID | model.Model]
            | tuple[UUID, UUID]
        ),
        copy: bool = False,
        on_missing: str = "raise",
    ) -> model.Model | list[model.Model] | None:
        if model_class not in self.db:
            self.db[model_class] = {}
        if isinstance(obj, list):
            return [self._get_obj(model_class, x) for x in obj]  # type: ignore[misc]
        table = self.db[model_class]
        key = self._get_obj_key(table, model_class, obj, on_missing)
        if key not in table:
            if on_missing == "raise":
                raise ValueError(f"{model_class.__name__} {obj} not found")
            elif on_missing == "return_none":
                return None
            else:
                raise NotImplementedError()
        return table[key] if not copy else table[key].model_copy()

    def _set_obj(self, obj: model.Model, update: bool = False) -> model.Model:
        model_class = type(obj)
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        key_fields = self.MODEL_KEY_MAP[model_class]
        if not isinstance(key_fields, tuple):
            key_fields = (key_fields,) if len(key_fields) > 1 else key_fields
        model_name = model_class.__name__
        key = tuple(getattr(obj, x) for x in key_fields)
        key = (
            key if len(key) > 1 else key[0]  # pyright: ignore[reportGeneralTypeIssues]
        )
        if key in table:
            if update:
                table[key] = obj
            else:
                raise ValueError(f"{model_name} {obj} already exists")
        else:
            table[key] = obj
        return obj

    def _delete_obj(self, model_class: type[model.Model], obj_id: UUID) -> model.Model:
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        key = [x for x, y in table.items() if y.id == obj_id]
        if key:
            key = key[0]  # type: ignore[assignment]
        else:
            raise ValueError(f"{model_class} {obj_id} not found")
        if key not in table:  # type: ignore[comparison-overlap]
            raise ValueError(f"{model_class} {obj_id} not found")
        obj = table[key]  # type: ignore[index]
        del table[key]  # type: ignore[arg-type]
        return obj

    @staticmethod
    def _set_log_level(app_cfg: BaseAppCfg, log_level: int) -> None:
        set_log_level(app_cfg.app_name.lower(), log_level)

    @staticmethod
    def _verify_updated_obj(
        in_obj: model.Model, out_obj: model.Model, user_id: UUID, **kwargs: Any
    ) -> None:
        is_privileged: bool = kwargs.get("is_privileged", False)
        verify_modified: bool = kwargs.get("verify_modified", True)

        if in_obj.created_at and out_obj.created_at != in_obj.created_at:
            raise ValueError(f"created_at should not be updated: {out_obj.created_at}")
        if not out_obj.created_at:
            raise ValueError(f"created_at should be set: {out_obj.created_at}")
        if verify_modified and not is_privileged:

            # TODO 2952: Where does the native datetime come from?
            # Why is it not timezone aware? Should we enforce timezone aware datetimes everywhere?
            in_modified_at = in_obj.modified_at
            if in_modified_at and in_modified_at.tzinfo is None:
                in_modified_at = in_modified_at.replace(tzinfo=datetime.UTC)

            if in_modified_at and out_obj.modified_at < in_modified_at:
                raise ValueError(
                    f"modified_at should be larger : {out_obj.modified_at}"
                )
            if out_obj.modified_by != user_id:
                raise ValueError(
                    f"modified_by should be updated: {out_obj.modified_by}"
                )

        out_obj_dict = out_obj.model_dump(
            exclude={"created_at", "modified_at", "modified_by"}
        )
        in_obj_dict = in_obj.model_dump(
            exclude={"created_at", "modified_at", "modified_by"}
        )

        if out_obj_dict != in_obj_dict:
            raise ValueError(f"Object not updated: {in_obj}, {out_obj}")
