from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_serializer

from gen_epix import fastapp
from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.case.persistable import Case
from gen_epix.casedb.domain.model.seqdb import ReadSet as ReadSet
from gen_epix.casedb.domain.model.seqdb import Seq as Seq
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.util import copy_model_field
from gen_epix.fastapp.domain import Entity
from gen_epix.filter import TypedCompositeFilter, TypedDatetimeRangeFilter


class CaseForCreateUpdate(Model):
    """
    A class representing a case to be created or updated.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="cases_for_create_update",
        persistable=False,
    )
    subject_id: UUID | None = copy_model_field(Case, "subject_id")
    count: int | None = copy_model_field(Case, "count")
    case_date: datetime | None = Field(
        description="The date of the case. Required when creating a case, ignored when updating.",
        default=None,
    )
    content: dict[UUID, str | None] = Field(
        description="The column data of the case as {col_id: str_value}. If None and the model is used for update, then any existing value will be deleted."
    )

    @field_serializer("content", mode="plain")
    def _serialize_content(
        self, value: dict[UUID, str | None]
    ) -> dict[str, str | None]:
        return {str(x): y for x, y in value.items()}


class CaseTypeStat(fastapp.Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_type_stats",
        persistable=False,
    )
    case_type_id: UUID = Field(description="The ID of the case type.")
    n_cases: int | None = Field(
        default=None, description="The number of cases for the case type."
    )
    first_case_date: datetime | None = Field(
        default=None,
        description="The date of the first case. In case the user has rights only to lower time resolution for the case date, the first day of the week, month, quarter, year, as available to the user, is used during calculation.",
    )
    last_case_date: datetime | None = Field(
        default=None,
        description="The date of the last case. In case the user has rights only to lower time resolution for the case date, the first day of the week, month, quarter, year, as available to the user, is used during calculation.",
    )


class CaseSetStat(fastapp.Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_stats",
        persistable=False,
    )
    case_set_id: UUID = Field(description="The ID of the case set.")
    n_cases: int | None = Field(
        default=None, description="The number of cases in the case set."
    )
    n_own_cases: int | None = Field(
        default=None, description="The number of own cases in the case set."
    )
    first_case_date: datetime | None = Field(
        default=None,
        description="The date of the first case. In case the user has rights only to lower time resolution for the case date, the first day of the week, month, quarter, year, as available to the user, is used during calculation.",
    )
    last_case_date: datetime | None = Field(
        default=None,
        description="The date of the last case. In case the user has rights only to lower time resolution for the case date, the first day of the week, month, quarter, year, as available to the user, is used during calculation.",
    )


class CaseQuery(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_queries",
        persistable=False,
    )
    label: str | None = Field(default=None, description="The label for the query.")
    case_type_id: UUID = Field(
        description="The ID of the case type that the cases must belong to.",
    )
    case_set_ids: set[UUID] | None = Field(
        default=None,
        description="The IDs of the case set(s) that the case must belong to. Not applied if not provided. All case sets must belong to the same case type as case_type_id.",
    )
    datetime_range_filter: TypedDatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range filter to apply to the case date. Not applied if not provided.",
    )
    # TODO: add data_collection_id
    filter: TypedCompositeFilter | None = Field(
        default=None, description="The filter to apply. Not applied if not provided."
    )


class CaseSetQuery(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_queries",
        persistable=False,
    )
    label: str = Field(description="The label for the query.")
    filter: TypedCompositeFilter = Field(description="The filter to apply.")


class BaseCaseRights(Model):
    created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection where the item was created",
    )
    case_type_id: UUID = Field(description="The ID of the case type")
    data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections in which the item is currently shared, including the created_in_data_collection_id",
    )
    is_full_access: bool = Field(
        description="Whether the user has full access to the item, i.e. all rights on all data collections",
    )
    add_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections to which the item is allowed to be added",
    )
    remove_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections from which the item is allowed to be removed. If remove_data_collection_ids is equal to data_collection_ids, the item is allowed to be deleted",
    )
    can_delete: bool = Field(
        description="Whether the item can be deleted.",
    )
    shared_in_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections in which the item is currently shared, excluding the created_in_data_collection_id",
    )


class CaseRights(BaseCaseRights):
    """
    Describes all the rights that a user has on one particular case, based on the data
    collections in which it is currently shared.
    """

    NAME: ClassVar = "CaseRights"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_rights",
        persistable=False,
    )
    case_id: UUID = Field(description="The ID of the case")
    read_case_type_col_ids: set[UUID] = Field(
        description="The IDs of the case type columns that are allowed to be read for the case",
    )
    write_case_type_col_ids: set[UUID] = Field(
        description="The IDs of the case type columns that are allowed to be written for the case",
    )


class CaseSetRights(BaseCaseRights):
    """
    Describes all the rights that a user has on one particular case set, based on the
    data collections in which it is currently shared.
    """

    NAME: ClassVar = "CaseSetRights"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_rights",
        persistable=False,
    )
    case_set_id: UUID = Field(description="The ID of the case set")
    read_case_set: bool = Field(
        description="Whether the case set is allowed to be read",
    )
    write_case_set: bool = Field(
        description="Whether the case set is allowed to be written",
    )


class CaseDataIssue(PydanticBaseModel):
    case_type_col_id: UUID = Field(description="The ID of the case type column")
    original_value: str | None = Field(description="The value of the case type column")
    updated_value: str | None = Field(
        description="The new value of the case type column after potential resolution. If not resolved, this will be None.",
    )
    data_rule: enum.CaseColDataRule = Field(description="The type of validation issue")
    details: str | None = Field(description="The details of the data issue")


class ValidatedCase(PydanticBaseModel):
    case: CaseForCreateUpdate = Field(description="The case with validated content.")
    data_issues: list[CaseDataIssue] = Field(
        description="The data issues found for the case."
    )


class CaseValidationReport(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_validation_reports",
        persistable=False,
    )
    case_type_id: UUID = Field(description="The case type ID that the cases belong to.")
    created_in_data_collection_id: UUID = Field(
        description="The data collection ID in which the cases would be created."
    )
    is_update: bool = Field(
        description="Whether the cases are intended to be updated or newly created."
    )
    data_collection_ids: set[UUID] = Field(
        description="The additional data collections that the cases would be put in, other than the created_in_data_collection."
    )
    validated_cases: list[ValidatedCase] = Field(
        description="The cases containing validated content and any data issues found during validation."
    )


class CaseReadSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_read_sets",
        persistable=False,
    )
    case_id: UUID = Field(
        description="The ID of the case that the read set is or will be associated with."
    )
    case_type_col_id: UUID = Field(
        description="The ID of the case type column that the read set is or will be associated with."
    )
    read_set_id: UUID | None = Field(
        description="The ID of the read set.", default=None
    )
    read_set: ReadSet | None = Field(default=None, description="The read set.")


class CaseSeq(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_seq",
        persistable=False,
    )
    case_id: UUID = Field(
        description="The ID of the case that the sequence is or will be associated with."
    )
    case_type_col_id: UUID = Field(
        description="The ID of the case type column that the sequence is or will be associated with."
    )
    seq_id: UUID | None = Field(description="The ID of the sequence.", default=None)
    seq: Seq | None = Field(default=None, description="The sequence.")


class CaseQueryResult(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_query_results",
        persistable=False,
    )
    case_query: CaseQuery = Field(
        description="The case query that was executed, provided back."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of the cases matching the query, possibly limited by CaseSettings.read_max_n_cases. If limited, the most recent cases according to CaseSettings.stats_time_dim_id are returned"
    )
    is_max_results_exceeded: bool = Field(
        description="Whether the number of results was limited."
    )
