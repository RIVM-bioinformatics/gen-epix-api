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

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

from gen_epix.commondb.domain.model.base import ModelNoId
from gen_epix.fastapp.model import Command, CrudCommand, Policy


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
        if not cmd.is_create() and not cmd.is_update():
            return True
        # To safeguard against the possibility of cmd.user being None or not having a roles attribute,
        # we should skip the metadata mutation in those cases,
        #  which means that created_at, modified_at and modified_by will not be set for those commands,
        # but this is unavoidable if we want to avoid errors in those cases,
        # and it is also a reasonable fallback behavior since if there is no user information available,
        # we cannot set the metadata fields anyway.
        if not cmd.user:
            return True
        user_roles: frozenset[str] = getattr(cmd.user, "roles", frozenset())

        privileged_user = False
        if user_roles & self._privileged_roles:
            privileged_user = True

        user_id: UUID = cmd.user.id  # type: ignore[assignment]
        objs = (
            cmd.objs
            if isinstance(cmd.objs, list)
            else ([cmd.objs] if cmd.objs is not None else [])
        )
        for obj in objs:
            if not hasattr(obj, "set_created"):
                continue
            model_obj = cast(ModelNoId, obj)
            if cmd.is_create():

                # Ibn case of privileged users, we should still call
                # all the set_created/set_modified methods to ensure that created_at, modified_at and modified_by are set for new objects,
                # to ensure that it is always set for created objects,
                # even if the privileged user does not provide a value for it,
                # but we should not override a provided value for created_at, modified_at or modified_by,
                # since privileged users should be able to set these values in the command if they want to.
                if privileged_user:
                    self._set_metadata_if_missing(model_obj, user_id)
                else:
                    model_obj.set_created(user_id)
            elif cmd.is_update():
                # for updates we should always call set_modified to ensure that modified_at and
                # modified_by are always updated to reflect the update operation,
                if privileged_user:
                    self._set_metadata_if_missing(model_obj, user_id)
                else:
                    model_obj.set_modified(user_id)
                    model_obj.created_at = None

                    # Backfill created_at if it was never set (e.g. objects created via nested
                    # commands that bypass the BEFORE policy). Use modified_at as a proxy
                    # since we cannot know the original creation time.
                    # TODO 2953 double check if this is OK,
                    # since it means that created_at will be overwritten on update if it was originally None,
                    if model_obj.created_at is None:
                        model_obj.created_at = model_obj.modified_at

        return True

    @staticmethod
    def _set_metadata_if_missing(obj: ModelNoId, user_id: UUID) -> None:
        now = datetime.now(UTC)
        if obj.created_at is None:
            obj.created_at = now
        if obj.modified_at is None:
            obj.modified_at = now
        if obj.modified_by is None:
            obj.modified_by = user_id


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
