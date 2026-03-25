"""
Policies for handling model metadata like created_at, modified_at and modified_by.

For both operational and refdata it is important to keep track of created/modified date as well as modified by user.
This allows e.g. retrieving and inspecting data based on these properties,
e.g. for automated ETL operations like retrieve all persons modified since a certain date.

This implies that they are returned by the API for read/retrieve operations.

Any command that returns models should apply:
set all 3 properties to None unless user has role APP_ADMIN or ROOT.

The setting of these properties on create/update is handled by the SAMapper layer,
not by a policy, since it involves more complex rules around when to
set/override these fields and when to leave them alone.

"""

from typing import Any, cast

from gen_epix.commondb.domain.model.base import ModelNoId
from gen_epix.fastapp.model import Command, Policy


class MaskModelProcessMetadataPolicy(Policy):
    """
    AFTER policy that nulls out created_at, modified_at, and modified_by on
    returned objects, unless the user holds a privileged role.
    """

    def __init__(self, privileged_roles: frozenset[str]) -> None:
        self._privileged_roles = privileged_roles

    def filter(self, cmd: Command, retval: Any) -> Any:
        user_roles: frozenset[str] = getattr(cmd.user, "roles", frozenset())
        if not cmd.user or user_roles & self._privileged_roles:
            return retval
        objs = (
            retval
            if isinstance(retval, list)
            else ([retval] if retval is not None else [])
        )
        for obj in objs:
            if not hasattr(obj, "created_at"):
                continue
            model_obj = cast(ModelNoId, obj)
            model_obj.created_at = None
            model_obj.modified_at = None
            model_obj.modified_by = None
        return retval
