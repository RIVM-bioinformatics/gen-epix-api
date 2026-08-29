from collections.abc import Hashable
from typing import Any

from gen_epix.commondb.domain.model import ModelNoId
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
        # Go over each relevant field in the domain model and compare it to the corresponding field in the SA row. Update the SA row if the values differ.
        is_updated = False
        modified_by_row_field_name: str | None = None
        obj_dict = obj.model_dump(
            exclude_none=False
        )  # Explicitly include None values (to ensure Pydantic always returns all fields, even if they are None and possible future defaults change)
        for field_name, row_field_name in zip(
            self._field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
            self._row_field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
        ):
            if field_name in ModelNoId.METADATA_FIELDS:
                if field_name == ModelNoId.MODIFIED_BY_FIELD_NAME:
                    # Switch to mapped
                    modified_by_row_field_name = row_field_name
                continue
            curr_value = getattr(row, row_field_name)
            new_value = obj_dict[field_name]
            if curr_value != new_value:
                setattr(row, row_field_name, new_value)
                is_updated = True

        # Set modified_by if the row was updated
        if is_updated:
            assert modified_by_row_field_name is not None
            setattr(row, modified_by_row_field_name, user_id)

        return is_updated

    def dump(self, user_id: Hashable | None, obj: Model, **kwargs: Any) -> Any:
        """
        Dump `obj` to a dict, applying commondb metadata-field rules.

        For users without privileged roles, this means masking out the metadata fields
        by setting them to None, so that they are not exposed by the API.
        """
        row = super().dump(user_id, obj, **kwargs)

        # TODO: this should not happen here, but in the service layer.  The service layer should know if the user has the right to see the metadata fields.  The mapper should just do a straight dump.
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
