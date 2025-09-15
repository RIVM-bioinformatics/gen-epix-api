import datetime
import logging
import re
from collections.abc import Hashable
from enum import Enum
from pathlib import Path
from time import sleep
from typing import Any, Dict, List, Type, TypeVar, cast
from uuid import UUID

from gen_epix.commondb.config import BaseAppCfg
from gen_epix.commondb.domain import command, model
from gen_epix.commondb.env import BaseAppEnv
from gen_epix.commondb.test.endpoint_test_client import EndpointTestClient
from gen_epix.commondb.test.util import set_log_level
from gen_epix.commondb.util import map_paired_elements
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.model import Command

BASE_MODEL_TYPE = TypeVar("BASE_MODEL_TYPE", bound=model.Model)


class TestClient:
    TEST_CLIENTS: dict[Hashable, Any] = {}

    MODEL_KEY_MAP: dict[Type[model.Model], str | tuple[str, ...]] = {
        model.User: "name",
        model.UserInvitation: "email",
        model.Organization: "name",
        model.DataCollection: "name",
    }

    def __init__(
        self,
        test_name: str,
        test_dir: Path,
        app_cfg: BaseAppCfg,
        app_env: BaseAppEnv,
        roles: set[Enum] | None = None,
        role_hierarchy: dict[Hashable, set] | None = None,
        user_class: Type[model.User] = model.User,
        user_invitation_class: Type[model.UserInvitation] = model.UserInvitation,
        user_crud_command_class: Type[
            command.UserCrudCommand
        ] = command.UserCrudCommand,
        user_invitation_crud_command_class: Type[
            command.UserInvitationCrudCommand
        ] = command.UserInvitationCrudCommand,
        retrieve_invite_user_constraints_class: Type[
            command.RetrieveInviteUserConstraintsCommand
        ] = command.RetrieveInviteUserConstraintsCommand,
        invite_user_command_class: Type[
            command.InviteUserCommand
        ] = command.InviteUserCommand,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        **kwargs: Any,
    ):
        # Set provided parameters
        self.test_name = test_name
        self.test_dir = test_dir
        self.app_cfg = app_cfg
        self.app_env = app_env
        self.roles = set() if roles is None else roles
        self.role_hierarchy: dict[Hashable, set] = (
            {} if role_hierarchy is None else role_hierarchy
        )
        self.user_class = user_class
        self.user_invitation_class = user_invitation_class
        self.user_crud_command_class = user_crud_command_class
        self.user_invitation_crud_command_class = user_invitation_crud_command_class
        self.retrieve_invite_user_constraints_class = (
            retrieve_invite_user_constraints_class
        )
        self.invite_user_command_class = invite_user_command_class
        self.log_level = log_level
        self.verbose = verbose

        # Set log level
        TestClient._set_log_level(app_cfg, log_level)

        # Set additional parameters
        self.app = self.app_env.app
        self.cfg = self.app_cfg.cfg
        self.services = self.app_env.services
        self.repositories = self.app_env.repositories
        self.db: Dict[Type[model.Model], Dict[Hashable, model.Model]] = {}
        self.props: dict = {}
        self.use_endpoints: bool = kwargs.pop("use_endpoints", False)
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

    def update_object(
        self,
        user_or_key: str | model.User,
        model_class: Type[model.Model],
        obj_or_key: model.Model | str,
        props: dict[str, Any | None],
        set_dummy_link: dict[str, bool] | bool = False,
        exclude_none: bool = True,
    ) -> model.Model:
        user: model.User = self._get_obj(self.user_class, user_or_key)  # type: ignore[assignment]
        obj: model.Model = self._get_obj(
            model_class, obj_or_key, copy=True
        )  # type:ignore[assignment]
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
        TestClient._verify_updated_obj(obj, updated_obj, user.id)
        return self._set_obj(updated_obj, update=True)

    def delete_object(
        self,
        user_or_key: str | model.User,
        model_class: Type[model.Model],
        obj_or_key: model.Model | str | tuple[UUID, UUID],
        retry_obj: tuple[UUID, UUID] | None = None,
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
        # verify if deleted
        # is_existing_obj = self.app.handle(
        #     self.app.domain.get_crud_command_for_model(model_class)(
        #         user=user,
        #         operation=CrudOperation.EXISTS_ONE,
        #         obj_ids=deleted_obj_id,
        #     )
        # )
        # if is_existing_obj:
        #     raise ValueError(f"Object {deleted_obj_id} not deleted")
        self._delete_obj(model_class, deleted_obj_id)
        return deleted_obj_id

    def read_all(
        self,
        user_or_key: model.User | str,
        model_class: Type[model.Model],
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
        model_class: Type[model.Model],
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
                    else obj_ids  # type:ignore[arg-type]
                ),
                props={"cascade_read": cascade},
            ),
            use_endpoint=False,
        )
        return retval

    def read_some_by_property(
        self,
        user_or_key: model.User | str,
        model_class: Type[model.Model],
        name: str,
        value: Any,
        cascade: bool = False,
    ) -> List[model.Model]:
        objs = self.read_all(user_or_key, model_class, cascade=cascade)
        return [x for x in objs if getattr(x, name) == value]

    def read_one_by_property(
        self,
        user_or_key: model.User | str,
        model_class: Type[model.Model],
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

    def verify_read_all(
        self,
        user_or_str: model.User | str,
        model_class: Type[model.Model],
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
                    self._get_obj(model_class, x)  # type:ignore[arg-type]
                )
                for x in extra_ids
            ]
            missing_names = [
                self._get_key_for_obj(
                    self._get_obj(model_class, x)  # type:ignore[arg-type]
                )
                for x in missing_ids
            ]
            raise ValueError(
                f"Difference in read all. Extra: {extra_names}. Missing: {missing_names}. User: {user.name}. Model: {model_class}"
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
        link_map: dict[str, tuple[str, Type[model.Model]]] = {
            x.relationship_field_name: (
                x.link_field_name,
                x.link_model_class,
            )  # type:ignore[misc]
            for x in model_class.ENTITY.links.values()
            if x.relationship_field_name
        }
        default_set_dummy_link = False
        if isinstance(set_dummy_link, bool):
            default_set_dummy_link = set_dummy_link
            set_dummy_link = {}

        # Set value fields and any links
        for field_name, value in props.items():
            if field_name in link_map:
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
                    value = getattr(
                        self._get_obj(link_model_class, value), id_field_name
                    )
            if exclude_none and value is None:
                continue
            setattr(obj, field_name, value)

    def _get_obj_key(
        self,
        table: dict,
        model_class: Type[model.Model],
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
            ]  # type:ignore[assignment]
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
            key = obj  # type:ignore[assignment]
        else:
            raise ValueError(f"Invalid object: {obj}")
        key = key if len(key) > 1 else key[0]  # type:ignore[assignment]
        return key  # type:ignore[return-value]

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

    def _delete_obj(self, model_class: Type[model.Model], obj_id: UUID) -> model.Model:
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        key = [x for x, y in table.items() if y.id == obj_id]
        if key:
            key = key[0]  # type:ignore[assignment]
        else:
            raise ValueError(f"{model_class} {obj_id} not found")
        if key not in table:  # type:ignore[comparison-overlap]
            raise ValueError(f"{model_class} {obj_id} not found")
        obj = table[key]  # type:ignore[index]
        del table[key]  # type:ignore[arg-type]
        return obj

    @staticmethod
    def _set_log_level(app_cfg: BaseAppCfg, log_level: int) -> None:
        set_log_level(app_cfg.app_name.lower(), log_level)

    @staticmethod
    def _verify_updated_obj(
        in_obj: model.Model, out_obj: model.Model, user_id: UUID, **kwargs: Any
    ) -> None:
        # TODO: verifying modified_by and modified_at is no longer possible here as the
        # persistence metadata no longer exists in the object. This should instead
        # be tested through unit tests on the repository in question.
        # verify_modified = kwargs.get("verify_modified", True)
        # if verify_modified and out_obj._modified_by != user_id:
        #     raise ValueError(f"_modified_by not updated: {out_obj._modified_by}")
        # if verify_modified and out_obj._modified_at <= in_obj._modified_at:
        #     raise ValueError(f"modified_at not updated: {out_obj._modified_at}")
        # if (
        #     out_obj.model_copy(
        #         update={
        #             "_modified_by": in_obj._modified_by,
        #             "_modified_at": in_obj._modified_at,
        #         }
        #     )
        #     != in_obj
        # ):
        #     raise ValueError(f"Object not updated: {in_obj}, {out_obj}")
        if out_obj != in_obj:
            raise ValueError(f"Object not updated: {in_obj}, {out_obj}")

    def generate_id(self) -> UUID:
        # Type cast needed because app.generate_id() returns Hashable
        return cast(UUID, self.app.generate_id())

    def get_root_user(self) -> model.User:
        return self.user_class(
            organization_id=self.cfg.secret.root.organization.id,
            **self.cfg.secret.root.user,
        )

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
    ) -> model.User:
        root_user: model.User = self.get_root_user()
        user: model.User = self._get_obj(self.user_class, user_or_str)  # type: ignore[assignment]
        m = re.match(r"^(.*?)(\d+)_(\d+)$", user_name.lower())
        if not m:
            raise ValueError(f"Invalid user name {user_name}")
        role = [x for x in self.roles if x.value.lower() == m.group(1).lower()][0]
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
                email=f"{user_name}@{organization_name}.org",
                roles={role},
                organization_id=organization_id,
            )
        )
        if set_dummy_token:
            user_invitation.token = str(self.generate_id())
        tgt_user: model.User = self.handle(
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
        # Verify if the right role(s) were assigned
        if tgt_user.roles != {role}:
            raise ValueError(
                f"User {tgt_user.name} has incorrect roles {tgt_user.roles}, expected {role}"
            )
        # Verify against user invitation constraints
        user_invitation_constraints: model.UserInvitationConstraints = self.handle(
            self.retrieve_invite_user_constraints_class(
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
        if any(x.email == tgt_user.email for x in remaining_invitations):
            raise ValueError(
                f"Some user invitations remaining for email {tgt_user.email}"
            )
        retval: model.User = self._set_obj(tgt_user)  # type:ignore[assignment]
        return retval

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

    def check_user_has_role(
        self, user_or_str: str | model.User, role: Enum, exclusive: bool = True
    ) -> bool:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type:ignore[assignment]
        roles = user.roles
        if exclusive:
            return role in roles and len(roles) == 1
        return role in roles

    def print_organizations(self) -> None:
        organizations: list[model.Organization] = self.read_all(
            self.get_root_user(), model.Organization, cascade=True
        )  # type:ignore[assignment]
        print("\nOrganizations:")
        for x in sorted(organizations, key=lambda x: x.name):
            print(f"{x.name} ({x.id})")

    def print_data_collections(self) -> None:
        data_collections: list[model.DataCollection] = self.read_all(
            self.get_root_user(), model.DataCollection, cascade=True
        )  # type:ignore[assignment]
        print("\nDataCollections:")
        for x in sorted(data_collections, key=lambda x: x.name):
            print(f"{x.name} ({x.id})")

    def print_users(self) -> None:
        root_user: model.User = self.get_root_user()
        users: list[model.User] = self.read_all(
            root_user, model.User
        )  # type:ignore[assignment]
        organizations: dict[UUID, model.Organization] = {
            x.id: x  # type:ignore[misc]
            for x in self.read_all(root_user, model.Organization)
        }
        print("\nUsers:")
        for x in sorted(
            users, key=lambda x: (organizations[x.organization_id].name, x.email)
        ):
            print(
                f"{organizations[x.organization_id].name} / {x.email}: "
                + ", ".join([z for z in sorted(y.name for y in x.roles)])
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
