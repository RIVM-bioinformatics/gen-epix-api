"""Expose seqdb api.organization API adapters and request representations."""

from enum import Enum

from pydantic import BaseModel

from gen_epix.fastapp.enum import PermissionType
from gen_epix.fastapp.model import Permission
from gen_epix.seqdb.domain import DOMAIN
from gen_epix.util import copy_model_field

CommandName = Enum("CommandName", {x: x for x in DOMAIN.command_names})  # type: ignore[misc] # Dynamic Enum required


class ApiPermission(BaseModel, frozen=True):
    """Represents a seqdb command permission in organization API payloads."""

    command_name: CommandName = (  # pyright: ignore[reportInvalidTypeForm]
        copy_model_field(Permission, "command_name")
    )
    permission_type: PermissionType = copy_model_field(Permission, "permission_type")
