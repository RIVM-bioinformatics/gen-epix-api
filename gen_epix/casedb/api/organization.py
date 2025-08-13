from enum import Enum

from pydantic import BaseModel, Field

from gen_epix.casedb.domain import DOMAIN, enum
from gen_epix.common.api import UpdateUserRequestBody as CommonUpdateUserRequestBody
from gen_epix.common.api import (
    UserInvitationRequestBody as CommonUserInvitationRequestBody,
)
from gen_epix.fastapp.enum import PermissionType
from gen_epix.fastapp.model import Permission

CommandName = Enum("CommandName", {x: x for x in DOMAIN.command_names})  # type: ignore[misc] # Dynamic Enum required

class ApiPermission(BaseModel, frozen=True):
    command_name: CommandName = Field(description=Permission.model_fields["command_name"].description) # pyright: ignore[reportInvalidTypeForm] # Dynamic type annotation required
    permission_type: PermissionType = Field(description=Permission.model_fields["permission_type"].description)

class UserInvitationRequestBody(CommonUserInvitationRequestBody):
    roles: set[enum.Role] = (  # pyright: ignore[reportIncompatibleVariableOverride] # Enum not subclassable
        Field(description=CommonUserInvitationRequestBody.model_fields['roles'].description, min_length=1)  # type: ignore[assignment]
    )

class UpdateUserRequestBody(CommonUpdateUserRequestBody):
    roles: set[enum.Role] | None = ( # pyright: ignore[reportIncompatibleVariableOverride] # Enum not subclassable
        Field(  # type: ignore[assignment]
            description=CommonUpdateUserRequestBody.model_fields['roles'].description,
        )
    )

