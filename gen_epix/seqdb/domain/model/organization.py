from enum import Enum
from typing import ClassVar, Type

from pydantic import Field

import gen_epix.common.domain.model as common_model
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.util import create_links
from gen_epix.seqdb.domain import enum

_SERVICE_TYPE = enum.ServiceType.ORGANIZATION
_ENTITY_KWARGS = {
    "schema_name": _SERVICE_TYPE.value.lower(),
    "_model_class": None,
}

assert common_model.User.ENTITY
assert common_model.UserInvitation.ENTITY

class User(common_model.User):
    ENTITY: ClassVar = Entity(
        **common_model.User.ENTITY.model_dump(
            exclude_unset=True, exclude_defaults=True, exclude={"schema_name"}
        ),
        **_ENTITY_KWARGS,
    )
    ROLE_ENUM: ClassVar[Type[Enum]] = enum.Role
    roles: set[enum.Role] = ( # pyright: ignore[reportIncompatibleVariableOverride] # Enum not subclassable
        Field(  # type: ignore[assignment]
            description=common_model.User.model_fields["roles"].description,
            min_length=1,
        )
    )


class UserInvitation(common_model.UserInvitation):
    ENTITY: ClassVar = Entity(
        **common_model.UserInvitation.ENTITY.model_dump(
            exclude_unset=True, exclude_defaults=True, exclude={"schema_name", "links"}
        ),
        links=create_links(
            {
                1: ("organization_id", common_model.Organization, "organization"),
                2: ("invited_by_user_id", User, "invited_by_user"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    ROLE_ENUM: ClassVar[Type[Enum]] = enum.Role
    invited_by_user: User | None = Field(
        default=None,
        description=common_model.UserInvitation.model_fields["invited_by_user"].description,
    )
    roles: set[enum.Role] = Field( # pyright: ignore[reportIncompatibleVariableOverride] # Enum not subclassable
        description=common_model.UserInvitation.model_fields["roles"].description, # type: ignore[assignment]
        min_length=1,
    )
