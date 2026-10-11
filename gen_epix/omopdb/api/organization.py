"""Expose permission schemas for OmopDB organization endpoints.

`CommandName` limits API permissions to commands registered by `DOMAIN`, while
`ApiPermission` pairs those commands with the shared permission type.
"""

from enum import Enum

from pydantic import BaseModel

from gen_epix.fastapp.enum import PermissionType
from gen_epix.fastapp.model import Permission
from gen_epix.omopdb.domain import DOMAIN
from gen_epix.util import copy_model_field

CommandName = Enum("CommandName", {x: x for x in DOMAIN.command_names})  # type: ignore[misc] # Dynamic Enum required


class ApiPermission(BaseModel, frozen=True):
    """Represents an OmopDB command permission exposed by organization APIs."""

    command_name: CommandName = (  # pyright: ignore[reportInvalidTypeForm]
        copy_model_field(
            Permission,
            "command_name",
            description="Name of the OmopDB command this permission applies to.",
        )
    )
    permission_type: PermissionType = copy_model_field(
        Permission,
        "permission_type",
        description="Operation permitted for the command.",
    )
