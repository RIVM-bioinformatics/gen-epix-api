"""
Policies for handling model metadata like created_at, modified_at and modified_by.

For both operational and refdata it is important to keep track of created/modified date as well as modified by user.
This allows e.g. retrieving and inspecting data based on these properties,
e.g. for automated ETL operations like retrieve all persons modified since a certain date.

This implies that they are returned by the API for read/retrieve operations, and possibly set by the API for create/update operations

Any command that returns models should apply:
set all 3 properties to None unless user has role APP_ADMIN or ROOT.

Any command that updates or creates models should apply:
call set_modified or set_created unless user has role APP_ADMIN or ROOT.


"""

from typing import Any
from uuid import UUID

from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.model import Command, CrudCommand, Policy

_CREATE_OPS = frozenset(
    {
        CrudOperation.CREATE_ONE,
        CrudOperation.CREATE_SOME,
        CrudOperation.UPSERT_ONE,
        CrudOperation.UPSERT_SOME,
    }
)
_UPDATE_OPS = frozenset(
    {
        CrudOperation.UPDATE_ONE,
        CrudOperation.UPDATE_SOME,
    }
)


class SetModelProcessMetadataPolicy(Policy):
    """
    BEFORE policy that calls set_created or set_modified on objects being written,
    unless the user holds a privileged role. Always returns True.
    """

    def __init__(self, privileged_roles: frozenset[str]) -> None:
        self._privileged_roles = privileged_roles

    # Note: is_allowed is used this is a bit of a misnomer
    # since it has side effects, but it is the only pre-handler hook available.
    def is_allowed(self, cmd: Command) -> bool:
        if not isinstance(cmd, CrudCommand):
            return True
        if cmd.operation not in _CREATE_OPS and cmd.operation not in _UPDATE_OPS:
            return True
        user_roles: frozenset[str] = getattr(cmd.user, "roles", frozenset())
        if not cmd.user or user_roles & self._privileged_roles:
            return True
        user_id: UUID = cmd.user.id  # type: ignore[assignment]
        objs = (
            cmd.objs
            if isinstance(cmd.objs, list)
            else ([cmd.objs] if cmd.objs is not None else [])
        )
        for obj in objs:
            if not hasattr(obj, "set_created"):
                continue
            if cmd.operation in _CREATE_OPS:
                obj.set_created(user_id)
            else:
                obj.set_modified(user_id)
        return True


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
            if hasattr(obj, "created_at"):
                obj.created_at = None
                obj.modified_at = None
                obj.modified_by = None
        return retval
