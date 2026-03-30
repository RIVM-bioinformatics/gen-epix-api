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

from typing import Any

from gen_epix.commondb.domain import enum, model
from gen_epix.fastapp.model import Command, Policy


class ModelMetadataPolicy(Policy):
    """
    AFTER policy that nulls out created_at, modified_at, and modified_by on
    returned objects.
    """

    def __init__(
        self, role_set_map: dict[enum.RoleSet | enum.Enum, frozenset[str]]
    ) -> None:
        self._privileged_roles = role_set_map[enum.RoleSet.GE_APP_ADMIN]

    def filter(self, cmd: Command, retval: Any) -> Any:
        """
        If the user does not have a privileged role, null out created_at, modified_at,
        and modified_by on returned models.
        """
        if not retval:
            # Any falsy return value (e.g. None, empty list) does not need to be processed
            return retval

        user: model.User | None = cmd.user  # type: ignore[assignment]
        if user is None:
            # No user interpreted as policy not applicable
            return retval
        user_roles = user.roles
        if user_roles & self._privileged_roles:
            # User has privileged role, so return unmodified retval
            return retval

        # Recursively find all models in the return value
        # TODO: if performance becomes an issue, CrudCommands could be handled separately with a more efficient implementation that only looks for models in the expected return type, rather than recursively traversing the entire return value.
        ModelMetadataPolicy.mask_models(retval)

        return retval

    @staticmethod
    def mask_models(obj: Any) -> None:
        if isinstance(obj, model.ModelNoId):
            # Mask metadata fields
            obj.created_at = None
            obj.modified_at = None
            obj.modified_by = None
            # Process any nested models in the fields of this model
            for field_value in obj.__dict__.values():
                ModelMetadataPolicy.mask_models(field_value)
        elif isinstance(obj, list):
            for item in obj:
                ModelMetadataPolicy.mask_models(item)
        elif isinstance(obj, dict):
            for item in obj.values():
                ModelMetadataPolicy.mask_models(item)
