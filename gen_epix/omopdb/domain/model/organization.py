from enum import Enum
from typing import ClassVar, Type

import gen_epix.common.domain.model as common_model
from gen_epix.common.util import copy_model_field
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.util import create_links
from gen_epix.omopdb.domain import enum

_SERVICE_TYPE = enum.ServiceType.ORGANIZATION
_ENTITY_KWARGS = {
    "schema_name": _SERVICE_TYPE.value.lower(),
    "_model_class": None,
}

assert common_model.User.ENTITY
assert common_model.UserInvitation.ENTITY


class User(common_model.User):
    """"""

    __doc__ = common_model.User.__doc__
    ENTITY: ClassVar = Entity(
        **common_model.User.ENTITY.model_dump(
            exclude_unset=True, exclude_defaults=True, exclude={"schema_name"}
        ),
        **_ENTITY_KWARGS,
    )
    ROLE_ENUM: ClassVar[Type[Enum]] = enum.Role
    roles: set[enum.Role] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        copy_model_field(common_model.User, "roles")  # type: ignore[assignment]
    )


class UserInvitation(common_model.UserInvitation):
    """"""

    __doc__ = common_model.UserInvitation.__doc__

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
    # Override invited_by_user to ensure it uses the correct User model
    # fmt: off
    invited_by_user: User | None = (  # pyright: ignore[reportIncompatibleVariableOverride]
        copy_model_field(
            common_model.UserInvitation, "invited_by_user"
        )
    )
    # fmt: on
    # Override roles to ensure it is a set of enum.Role
    roles: set[enum.Role] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        copy_model_field(common_model.UserInvitation, "roles")  # type: ignore[assignment]
    )
