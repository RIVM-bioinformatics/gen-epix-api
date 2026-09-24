"""API schemas extending shared organization endpoint permissions for OmopDB."""

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
        copy_model_field(Permission, "command_name")
    )
    permission_type: PermissionType = copy_model_field(Permission, "permission_type")
