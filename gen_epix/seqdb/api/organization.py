from pydantic import Field

from gen_epix.common.api import UpdateUserRequestBody as CommonUpdateUserRequestBody
from gen_epix.common.api import (
    UserInvitationRequestBody as CommonUserInvitationRequestBody,
)
from gen_epix.seqdb.domain import enum


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
