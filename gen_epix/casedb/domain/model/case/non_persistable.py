from datetime import datetime
from typing import ClassVar, Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from gen_epix import fastapp
from gen_epix.commondb.domain.model import Model
from gen_epix.fastapp.domain import Entity
from gen_epix.filter import TypedCompositeFilter, TypedDatetimeRangeFilter
from gen_epix.filter.uuid_set import UuidSetFilter


class CaseStats(fastapp.Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_stats",
        persistable=False,
    )
    case_type_id: UUID = Field(description="The ID of the CaseType.")
    case_set_id: UUID | None = Field(
        default=None, description="The ID of the case set, if applicable."
    )
    n_cases: int = Field(
        default=0, description="The number of cases in the case set.", ge=0
    )
    n_own_cases: int = Field(
        default=0, description="The number of own cases in the case set.", ge=0
    )
    first_case_date: datetime | None = Field(
        default=None,
        description="The date of the first case. In case the user has rights only to lower time resolution for the case date, the first day of the week, month, quarter, year, as available to the user, is used during calculation.",
    )
    last_case_date: datetime | None = Field(
        default=None,
        description="The date of the last case. In case the user has rights only to lower time resolution for the case date, the first day of the week, month, quarter, year, as available to the user, is used during calculation.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        if self.n_own_cases > self.n_cases:
            raise ValueError("n_own_cases cannot be greater than n_cases")
        if self.n_cases == 0:
            if self.first_case_date is not None or self.last_case_date is not None:
                raise ValueError(
                    "first_case_date and last_case_date must be None when n_cases is 0"
                )
        else:
            if self.first_case_date is None or self.last_case_date is None:
                raise ValueError(
                    "first_case_date and last_case_date must be provided when n_cases is greater than 0"
                )
            if self.first_case_date > self.last_case_date:
                raise ValueError(
                    "first_case_date must be before or equal to last_case_date"
                )
        return self


class CaseQuery(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_queries",
        persistable=False,
    )
    label: str | None = Field(default=None, description="The label for the query.")
    case_type_id: UUID = Field(
        description="The ID of the CaseType that the cases must belong to.",
    )
    case_set_ids: set[UUID] | None = Field(
        default=None,
        description="The IDs of the case set(s) that the case must belong to. Not applied if not provided. All case sets must belong to the same CaseType as case_type_id.",
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
    """
    Base class describing all the rights that a user has on one particular item,
    based on the data collections in which it is currently shared.
    """

    created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection where the item was created",
    )
    case_type_id: UUID = Field(description="The ID of the CaseType")
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
    read_col_ids: set[UUID] = Field(
        description="The IDs of the Cols that are allowed to be read for the case",
    )
    write_col_ids: set[UUID] = Field(
        description="The IDs of the Cols that are allowed to be written for the case",
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


class CaseCohortIds(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_cohort_ids",
        persistable=False,
    )
    case_id: UUID = Field(description="The ID of the case.")
    cohort_ids: list[UUID] = Field(
        default_factory=list,
        description="The IDs of the omopdb cohorts linked to this case.",
    )


class RefDataAccess(Model):
    """
    Describes the reference data that a user has access to. This is a lightweight
    representation that can be cached and can e.g. be used to filter the reference
    data that the user can access.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="readable_reference_data",
        persistable=False,
    )
    user_id: UUID | None = Field(description="The ID of the user")
    is_full_access: bool = Field(
        description="Whether the user has full access to all reference data. If so, the corresponding fields are left empty and should not be used.",
    )
    case_type_set_ids: set[UUID] = Field(
        default_factory=set, description="The IDs of the allowed CaseTypeSets."
    )
    case_type_ids: set[UUID] = Field(
        default_factory=set, description="The IDs of the allowed CaseTypes."
    )
    col_set_ids: set[UUID] = Field(
        default_factory=set, description="The IDs of the allowed ColSets."
    )
    col_ids: set[UUID] = Field(
        default_factory=set, description="The IDs of the allowed Cols."
    )
    dim_ids: set[UUID] = Field(
        default_factory=set, description="The IDs of the allowed Dims."
    )
    ref_dim_ids: set[UUID] = Field(
        default_factory=set, description="The IDs of the allowed RefDims."
    )
    ref_col_ids: set[UUID] = Field(
        default_factory=set, description="The IDs of the allowed RefCols."
    )

    def get_case_type_set_filter(self, field_name: str) -> UuidSetFilter | None:
        """
        Get a filter for the allowed CaseTypeSets. Returns None if the user has full
        access to all CaseTypeSets.
        """
        return self._get_filter(field_name, self.case_type_set_ids)

    def get_case_type_filter(self, field_name: str) -> UuidSetFilter | None:
        """
        Get a filter for the allowed CaseTypes. Returns None if the user has full
        access to all CaseTypes.
        """
        return self._get_filter(field_name, self.case_type_ids)

    def get_col_set_filter(self, field_name: str) -> UuidSetFilter | None:
        """
        Get a filter for the allowed column sets. Returns None if the user has full
        access to all column sets.
        """
        return self._get_filter(field_name, self.col_set_ids)

    def get_col_filter(self, field_name: str) -> UuidSetFilter | None:
        """
        Get a filter for the allowed columns. Returns None if the user has full
        access to all columns.
        """
        return self._get_filter(field_name, self.col_ids)

    def get_dim_filter(self, field_name: str) -> UuidSetFilter | None:
        """
        Get a filter for the allowed dimensions. Returns None if the user has full
        access to all dimensions.
        """
        return self._get_filter(field_name, self.dim_ids)

    def get_ref_dim_filter(self, field_name: str) -> UuidSetFilter | None:
        """
        Get a filter for the allowed reference dimensions. Returns None if the user has full
        access to all reference dimensions.
        """
        return self._get_filter(field_name, self.ref_dim_ids)

    def get_ref_col_filter(self, field_name: str) -> UuidSetFilter | None:
        """
        Get a filter for the allowed reference columns. Returns None if the user has full
        access to all reference columns.
        """
        return self._get_filter(field_name, self.ref_col_ids)

    def _get_filter(self, field_name: str, members: set[UUID]) -> UuidSetFilter | None:
        """
        Get a filter for the allowed members of a reference data type. Returns None if
        the user has full access to all members of the reference data type.
        """
        if self.is_full_access:
            return None
        return UuidSetFilter(
            key=field_name,
            members=members,
        )


class CaseIdAndDate(BaseModel):
    """
    Represents a case with its ID and date.
    """

    id: UUID = Field(description="The case ID.")
    case_date: datetime = Field(description="The case date, if any.")
