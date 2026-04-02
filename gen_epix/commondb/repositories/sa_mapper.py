from collections.abc import Hashable
from typing import Any

from gen_epix.fastapp.enum import FieldTypeSet
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.sa.mapper import (
    BaseSAMapperFactory,
    SAMapper,
)


class CommondbSAMapper(SAMapper):
    """
    SAMapper subclass for all databases that use RowMetadataMixin.

    Overrides `update()` to enforce the following rules on every UPDATE:
    - `created_at`  — never written; the DB server_default owns it.
    - `modified_at` — never written from Python; SA's onupdate=ServerUtcCurrentTime()
                      on RowMetadataMixin handles it automatically.
    - `modified_by` — always set to the `user_id` passed in, regardless of the value
                      carried on the incoming domain object.
    - All other fields — standard behaviour: skip if the new value is None (keep the
                         existing DB value), otherwise write the new value.

    This class intentionally knows nothing about process-specific fields in casedb,
    seqdb, etc.  Those dbs create their own subclass of CommondbSAMapper (or of this
    class) and override `update()` further if they need additional rules.
    """

    def update(
        self, user_id: Hashable | None, obj: Model, row: Any, **kwargs: Any
    ) -> bool:
        """
        Update `row` from `obj`, applying commondb metadata-field rules.

        Returns True if at least one field was actually changed.
        """
        # Build the base update dict, skipping fields whose new value is None so that
        # existing DB values are preserved when the incoming object omits a field.
        if self._is_identical_common_field_names:
            mapped_dict: dict[str, Any] = obj.model_dump(exclude_none=True)
        else:
            obj_dict = obj.model_dump(exclude_none=False)

            mapped_dict = {
                row_field_name: obj_dict[field_name]
                for field_name, row_field_name in zip(
                    self._field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
                    self._row_field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
                )
                if obj_dict[field_name] is not None
            }

        if kwargs:
            mapped_dict.update(kwargs)

        # Strip fields that are owned exclusively by the DB and must never be touched
        # from Python during an update.
        mapped_dict.pop("created_at", None)
        mapped_dict.pop("modified_at", None)
        # Always stamp modified_by with the acting user, overriding any value the
        # domain object might carry.
        mapped_dict["modified_by"] = user_id

        is_updated = False
        for key, value in mapped_dict.items():

            curr_value = getattr(row, key, None)
            if curr_value != value:
                setattr(row, key, value)
                is_updated = True
        return is_updated

    def dump(self, user_id: Hashable | None, obj: Model, **kwargs: Any) -> Any:
        """
        Dump `obj` to a dict, applying commondb metadata-field rules.

        For users without privileged roles, this means masking out the metadata fields
        by setting them to None, so that they are not exposed by the API.
        """
        row = super().dump(user_id, obj, **kwargs)

        row.created_at = None
        row.modified_at = None
        row.modified_by = user_id

        return row


class CommondbSAMapperFactory(BaseSAMapperFactory):
    """
    Factory that produces CommondbSAMapper instances for all SA-backed databases that
    inherit from RowMetadataMixin (casedb, seqdb, omopdb, …).

    Injected into SARepository at construction time by commondb/env.py so that the
    fastapp layer never needs to know which fields are metadata-protected.
    """

    def create_mapper(
        self,
        model_class: type[Model],
        row_class: type,
        field_name_map: dict[str, str] | None = None,
    ) -> CommondbSAMapper:
        return CommondbSAMapper(
            model_class,
            row_class,
            field_name_map=field_name_map,
        )
