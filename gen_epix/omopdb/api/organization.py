from enum import Enum

from pydantic import BaseModel

from gen_epix.commondb.api import UpdateUserRequestBody as CommonUpdateUserRequestBody
from gen_epix.commondb.api import (
    UserInvitationRequestBody as CommonUserInvitationRequestBody,
)
from gen_epix.commondb.util import copy_model_field
from gen_epix.fastapp.enum import PermissionType
from gen_epix.fastapp.model import Permission
from gen_epix.omopdb.domain import DOMAIN, enum

CommandName = Enum("CommandName", {x: x for x in DOMAIN.command_names})  # type: ignore[misc] # Dynamic Enum required


class ApiPermission(BaseModel, frozen=True):
    command_name: CommandName = (  # pyright: ignore[reportInvalidTypeForm]
        copy_model_field(Permission, "command_name")
    )
    permission_type: PermissionType = copy_model_field(Permission, "permission_type")


class UserInvitationRequestBody(CommonUserInvitationRequestBody):
    roles: set[enum.Role] = (
        copy_model_field(  # pyright: ignore[reportIncompatibleVariableOverride] # Enum not subclassable
            CommonUserInvitationRequestBody, "roles"
        )
    )  # type:ignore[assignment]


class UpdateUserRequestBody(CommonUpdateUserRequestBody):
    roles: set[enum.Role] | None = (
        copy_model_field(  # pyright: ignore[reportIncompatibleVariableOverride] # Enum not subclassable
            CommonUpdateUserRequestBody, "roles"
        )
    )  # type:ignore[assignment]
