from enum import Enum
from typing import Any, Hashable, Type
from uuid import UUID

from pydantic import BaseModel, Field

import gen_epix.common.domain.model.organization
from gen_epix.casedb.domain import DOMAIN, model
from gen_epix.fastapp import Permission as ServicePermission

CommandName = Enum("CommandName", {x: x for x in DOMAIN.command_names})  # type: ignore[misc]


class Model(BaseModel):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the obj.",
    )


def _permission_map_model(
    obj: Any, map_to: bool, command_name_class: Type[Enum]
) -> dict:
    fun = (lambda x: x.value) if map_to else (lambda x: command_name_class[x])
    return {
        x: (getattr(obj, x) if x != "command_name" else fun(obj.command_name))
        for x in obj.model_fields.keys()
    }


def permission_from_model(
    permission: ServicePermission | None, command_name_class: Type[Enum]
) -> Any:
    return (
        None
        if permission is None
        else Permission(**_permission_map_model(permission, False, command_name_class))
    )


def permission_to_model(
    permission: Any, command_name_class: Type[Enum]
) -> ServicePermission | None:
    return (
        None
        if permission is None
        else ServicePermission(
            **_permission_map_model(permission, True, command_name_class)
        )
    )


def _complete_user_map_model(
    obj: Any, map_to: bool, command_name_class: Type[Enum]
) -> dict:
    fun = permission_to_model if map_to else permission_from_model
    return {
        x: (
            {fun(y, command_name_class) for y in obj.permissions}
            if x == "permissions"
            else getattr(obj, x)
        )
        for x in obj.model_fields.keys()
    }


def complete_user_from_model(
    complete_user: gen_epix.common.domain.model.organization.CompleteUser | None,
    command_name_class: Type[Enum],
) -> Any:
    return (
        None
        if complete_user is None
        else CompleteUser(
            **_complete_user_map_model(complete_user, False, command_name_class)
        )
    )


def complete_user_to_model(
    complete_user: Any, command_name_class: Type[Enum]
) -> gen_epix.common.domain.model.organization.CompleteUser | None:
    return (
        None
        if complete_user is None
        else gen_epix.common.domain.model.organization.CompleteUser(
            **_complete_user_map_model(complete_user, True, command_name_class)
        )
    )


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
    permissions: set[ServicePermission]
    roles: set[Hashable]
