import logging
import uuid
from enum import Enum
from test.fastapp.command import (
    Model1_1CrudCommand,
    Model1_2CrudCommand,
    Model2_1CrudCommand,
    Model2_2CrudCommand,
)
from test.fastapp.enum import ServiceType
from test.fastapp.model import Model1_1, Model1_2, Model2_1, Model2_2
from test.fastapp.service_test_client import ServiceTestClient
from test.fastapp.user_manager import UserManager
from typing import Hashable, Type

import pytest

from gen_epix.fastapp.enum import CrudOperation, PermissionTypeSet
from gen_epix.fastapp.model import CrudCommand, Model
from gen_epix.fastapp.model import User as ServiceUser
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.services.rbac import BaseRbacService


class Role(Enum):
    ROOT = "ROOT"
    ADMIN = "ADMIN"
    WRITER = "WRITER"
    READER = "READER"
    TEST = "TEST"


class User(ServiceUser):
    id: uuid.UUID
    name: str
    email: str
    roles: set[Role]

    def get_key(self) -> str:
        return self.email


class RbacService(BaseRbacService):
    def retrieve_user_roles(self, user: User) -> set[Hashable]:
        return user.roles

    def retrieve_user_is_root(self, user: User) -> bool:
        return Role.ROOT in user.roles


class RBACTestClient(ServiceTestClient):

    def __init__(
        self,
        repository_class: Type[BaseRepository],
        logger: logging.Logger | None = None,
        **kwargs: dict,
    ) -> None:
        super().__init__(repository_class, logger=logger, **kwargs)
        # Create RBAC service
        rbac_service = RbacService(self.app, service_type=ServiceType.RBAC)
        rbac_service.register_handlers()
        for permission in rbac_service.app.domain.get_permissions_for_command(
            Model1_1CrudCommand
        ):
            rbac_service.register_permission_without_rbac(permission)
        # Register roles and policies
        f = lambda x, y: rbac_service.app.domain.get_permissions_for_command(
            x, frozen=False, permission_type_set=y
        )
        command_classes = {
            Model1_2CrudCommand,
            Model2_1CrudCommand,
            Model2_2CrudCommand,
        }
        permission_map = {
            Role.READER: set.union(
                *[f(x, PermissionTypeSet.R) for x in command_classes]
            ),
            Role.WRITER: set.union(
                *[f(x, PermissionTypeSet.CU) for x in command_classes]
            ),
            Role.ADMIN: set.union(
                *[f(x, PermissionTypeSet.D) for x in command_classes]
            ),
            Role.ROOT: self.app.domain.permissions,
        }
        permission_map[Role.WRITER].update(permission_map[Role.READER])
        permission_map[Role.ADMIN].update(permission_map[Role.WRITER])
        for role, permissions in permission_map.items():
            rbac_service.register_role(role, permissions)
        rbac_service.register_rbac_policies()
        # Set attributes
        self.rbac_service = rbac_service
        self.user_manager = UserManager(user_class=User)
        self.app.user_manager = self.user_manager
        self.users_by_role = {role: [] for role in Role}
        # Create users
        for i, role in enumerate(Role):
            claims = self.get_user(i, {role}).model_dump()
            if role == Role.ROOT:
                user = self.user_manager.create_root_user_from_claims(claims)
            else:
                user = self.user_manager.create_user_from_claims(claims)
            self.users_by_role[role].append(user)
        # Create some objs
        self.create_all_fixture_model_instances(self.users_by_role[Role.ROOT][0].id)

    def get_user(self, user_idx: int, roles: set[Role]) -> User:
        if user_idx < 0:
            user_idx = len(self.user_ids) + user_idx
        return User(
            id=self.user_ids[user_idx],
            name=f"user{user_idx}",
            email=f"user{user_idx}@test.org",
            roles=roles,
        )

    def create_one(self, model_class: Type[Model], user: User | None) -> CrudCommand:
        crud_command_class = self.app.domain.get_crud_command_for_model(model_class)
        obj = self.get_model_instance_for_class(model_class, set_id=False)
        if isinstance(obj, Model1_2):
            obj.model1_1_id = list(self.df[Model1_1].values())[0].id
        elif isinstance(obj, Model2_1):
            obj.model1_2_id = list(self.df[Model1_2].values())[0].id
        elif isinstance(obj, Model2_2):
            obj.model2_1_id = list(self.df[Model2_1].values())[0].id
        instance_created = self.app.handle(
            crud_command_class(user=user, objs=obj, operation=CrudOperation.CREATE_ONE)
        )
        return instance_created

    def read_one(self, model_class: Type[Model], user: User | None) -> Model:
        crud_command_class = self.app.domain.get_crud_command_for_model(model_class)
        obj = list(self.df[model_class].values())[0]
        instance_read = self.app.handle(
            crud_command_class(
                user=user, obj_ids=obj.id, operation=CrudOperation.READ_ONE
            )
        )
        return instance_read

    def update_one(self, obj: Model, user: User | None) -> Model:
        crud_command_class = self.app.domain.get_crud_command_for_model(type(obj))

        def update_link(current_id, available_ids):
            for id_ in available_ids:
                if id_ != current_id:
                    return id_
            raise ValueError("No available ids")

        if isinstance(obj, Model1_2):
            obj.model1_1_id = update_link(
                obj.model1_1_id, list(self.df[Model1_1].keys())
            )
        elif isinstance(obj, Model2_1):
            obj.model1_2_id = update_link(
                obj.model1_2_id, list(self.df[Model1_2].keys())
            )
        elif isinstance(obj, Model2_2):
            obj.model2_1_id = update_link(
                obj.model2_1_id, list(self.df[Model2_1].keys())
            )
        instance_updated = self.app.handle(
            crud_command_class(user=user, objs=obj, operation=CrudOperation.UPDATE_ONE)
        )
        return instance_updated

    def delete_one(self, obj: Model, user: User | None) -> None:
        crud_command_class = self.app.domain.get_crud_command_for_model(type(obj))
        self.app.handle(
            crud_command_class(
                user=user, obj_ids=obj.id, operation=CrudOperation.DELETE_ONE
            )
        )


@pytest.fixture(scope="module", name="env")
def get_test_client() -> RBACTestClient:
    return RBACTestClient.get_test_client(DictRepository)


class TestRBAC:

    def test_get_user_roles(self, env: RBACTestClient) -> None:
        for role in Role:
            for user in env.users_by_role[role]:
                assert role in env.rbac_service.retrieve_user_roles(user)

    def test_create_one(self, env: RBACTestClient) -> None:
        for role in Role:
            user = env.users_by_role[role][0]
            # No RBAC policy on Model1_1CrudCommand
            env.create_one(Model1_1, user=user)
            # RBAC policy on other commands
            for command_class in [Model1_2, Model2_1, Model2_2]:
                if role in {Role.READER, Role.TEST}:
                    with pytest.raises(Exception):
                        env.create_one(command_class, user=user)
                else:
                    env.create_one(command_class, user=user)

    def test_read_one(self, env: RBACTestClient) -> None:
        for role in Role:
            user = env.users_by_role[role][0]
            # No RBAC policy on Model1_1CrudCommand
            env.read_one(Model1_1, user=user)
            for model_class in [Model1_2, Model2_1, Model2_2]:
                if role in {Role.TEST}:
                    with pytest.raises(Exception):
                        env.read_one(model_class, user=user)
                else:
                    env.read_one(model_class, user=user)

    def test_update_one(self, env: RBACTestClient) -> None:
        for role in Role:
            user = env.users_by_role[role][0]
            # No RBAC policy on Model1_1CrudCommand
            obj = env.create_one(Model1_1, user=user)
            env.update_one(obj, user=user)
            for model_class in [Model1_2, Model2_1, Model2_2]:
                if role in {Role.READER, Role.TEST}:
                    with pytest.raises(Exception):
                        obj = list(env.df[model_class].values())[0]
                        env.update_one(obj, user=user)
                else:
                    obj = env.create_one(model_class, user=user)
                    env.update_one(obj, user=user)

    def test_delete_one(self, env: RBACTestClient) -> None:
        for role in Role:
            user = env.users_by_role[role][0]
            # No RBAC policy on Model1_1CrudCommand
            obj = env.create_one(Model1_1, user=user)
            env.delete_one(obj, user=user)
            for model_class in [Model1_2, Model2_1, Model2_2]:
                if role in {Role.WRITER, Role.READER, Role.TEST}:
                    with pytest.raises(Exception):
                        obj = list(env.df[model_class].values())[0]
                        env.delete_one(obj, user=user)
                else:
                    obj = env.create_one(model_class, user=user)
                    env.delete_one(obj, user=user)

    def test_create_role(self, env: RBACTestClient) -> None:
        role = Role.TEST
        permissions = env.app.domain.get_permissions_for_command(
            Model1_2CrudCommand, frozen=False
        )
        permissions.update(
            env.app.domain.get_permissions_for_command(
                Model2_1CrudCommand, permission_type_set=PermissionTypeSet.C
            )
        )
        env.rbac_service.register_role(role, permissions)
        user = env.get_user(-1, {role})
        # No RBAC policy on Model1_1CrudCommand
        obj = env.create_one(Model1_1, user=user)
        env.read_one(Model1_1, user=user)
        env.update_one(obj, user=user)
        env.delete_one(obj, user=user)
        # RBAC policy on Model1_2CrudCommand, role allows every operation
        obj = env.create_one(Model1_2, user=user)
        env.read_one(Model1_2, user=user)
        env.update_one(obj, user=user)
        env.delete_one(obj, user=user)
        # RBAC policy on Model2_1CrudCommand, role allows only create operation
        obj = env.create_one(Model2_1, user=user)
        with pytest.raises(Exception):
            env.read_one(Model2_1, user=user)
        with pytest.raises(Exception):
            env.update_one(obj, user=user)
        with pytest.raises(Exception):
            env.delete_one(obj, user=user)
        # RBAC policy on Model2_2CrudCommand, role allows no operations
        with pytest.raises(Exception):
            obj = env.create_one(Model2_2, user=user)

    def test_update_role(self, env: RBACTestClient) -> None:
        # Update role permissions
        role = Role.TEST
        permissions = {x for x in env.rbac_service.permissions_by_role[Role.TEST]}
        permissions.update(
            env.app.domain.get_permissions_for_command(
                Model2_2CrudCommand, permission_type_set=PermissionTypeSet.C
            )
        )
        env.rbac_service.register_role(role, permissions)
        user = env.get_user(-1, {role})
        # RBAC policy on Model2_2CrudCommand, role allows only create operation
        obj = env.create_one(Model2_2, user=user)
        with pytest.raises(Exception):
            env.read_one(Model2_2, user=user)
        with pytest.raises(Exception):
            env.update_one(obj, user=user)
        with pytest.raises(Exception):
            env.delete_one(obj, user=user)
