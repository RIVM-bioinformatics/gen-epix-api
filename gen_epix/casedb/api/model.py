from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from gen_epix.casedb.domain import DOMAIN, enum, model
from gen_epix.fastapp import Permission as ServicePermission
from gen_epix.fastapp import PermissionType

CommandName = Enum("CommandName", {x: x for x in DOMAIN.command_names})  # type: ignore[misc]


class Model(BaseModel):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the obj.",
    )


# TODO: investigate why just inheriting from the domain model (here ServicePermission) no longer works, as it raises a a Pydantic exception around ClassVar
# Workaround is to create the entire API model from scratch with exactly the same fields as the domain model and the relevant fields changed (here command_name)
# This means that the API model has to be kept in sync with the domain model, which is not ideal
# class Permission(ServicePermission):
class Permission(BaseModel, frozen=True):
    command_name: CommandName  # type: ignore
    permission_type: PermissionType

    @staticmethod
    def _map_model(obj: Any, map_to: bool) -> dict:
        fun = (lambda x: x.value) if map_to else (lambda x: CommandName[x])
        return {
            x: (getattr(obj, x) if x != "command_name" else fun(obj.command_name))
            for x in obj.model_fields.keys()
        }

    @staticmethod
    def from_model(permission: ServicePermission | None) -> Any:
        return (
            None
            if permission is None
            else Permission(**Permission._map_model(permission, False))
        )

    @staticmethod
    def to_model(permission: Any) -> ServicePermission | None:
        return (
            None
            if permission is None
            else ServicePermission(**Permission._map_model(permission, True))
        )


# class CompleteUser(model.CompleteUser):
class CompleteUser(Model):
    email: str = Field(description="The email of the user, UNIQUE", max_length=320)
    name: str | None = Field(
        default=None, description="The full name of the user", max_length=255
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user is active or not. An inactive user cannot perform any actions that require authorization.",
    )
    organization_id: UUID = Field(
        description="The ID of the organization of the user. FOREIGN KEY"
    )
    organization: model.Organization | None
    permissions: set[Permission]
    roles: set[enum.Role]
    # case_abac: model.CaseAbac = Field(
    #     description="The case abac of the user. This is used to determine the user's access to cases.",
    # )

    @staticmethod
    def _map_model(obj: Any, map_to: bool) -> dict:
        fun = Permission.to_model if map_to else Permission.from_model
        return {
            x: (
                {fun(y) for y in obj.permissions}
                if x == "permissions"
                else getattr(obj, x)
            )
            for x in obj.model_fields.keys()
        }

    @staticmethod
    def from_model(
        complete_user: model.CompleteUser | None,
    ) -> Any:
        return (
            None
            if complete_user is None
            else CompleteUser(**CompleteUser._map_model(complete_user, False))
        )

    @staticmethod
    def to_model(
        complete_user: Any,
    ) -> model.CompleteUser | None:
        return (
            None
            if complete_user is None
            else model.CompleteUser(**CompleteUser._map_model(complete_user, True))
        )


# Set the API model classes for the domain models
model.CompleteUser.ENTITY.set_create_api_model_class(CompleteUser)
model.CompleteUser.ENTITY.set_read_api_model_class(CompleteUser)
