from collections.abc import Hashable
from typing import Any

from gen_epix.fastapp.enum import FieldTypeSet
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.sa.mapper import (
    BaseSAMapper,
    BaseSAMapperFactory,
    SAMapper,
)

# Fields that are managed exclusively by the database layer and must never be written
# from Python during an update.  `created_at` has a server_default only (set once on
# INSERT by the DB).  `modified_at` is refreshed on every UPDATE via the SA
# `onupdate=ServerUtcCurrentTime()` parameter on the RowMetadataMixin column — writing
# it from Python would bypass that mechanism and produce stale/wrong timestamps.
_NEVER_UPDATE_FIELDS: frozenset[str] = frozenset({"created_at", "modified_at"})


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

        # Strip fields that are owned exclusively by the DB and must never be touched
        # from Python during an update.
        for field in _NEVER_UPDATE_FIELDS:
            mapped_dict.pop(field, None)

        # Always stamp modified_by with the acting user, overriding any value the
        # domain object might carry.
        if user_id is not None:
            mapped_dict["modified_by"] = user_id
        else:
            # No acting user — leave whatever is already in the DB.
            mapped_dict.pop("modified_by", None)

        if kwargs:
            mapped_dict.update(kwargs)

        is_updated = False
        for key, value in mapped_dict.items():
            if value is None:
                continue
            curr_value = getattr(row, key, None)
            if curr_value != value:
                setattr(row, key, value)
                is_updated = True
        return is_updated


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
