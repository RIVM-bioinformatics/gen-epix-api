from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_validator, model_validator

import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.command import (
    Command,
    CrudCommand,
    UpdateAssociationCommand,
)
from gen_epix.commondb.util import copy_model_field
from gen_epix.filter.datetime_range import TypedDatetimeRangeFilter

# Non-CRUD


class CaseTypeSetCaseTypeUpdateAssociationCommand(UpdateAssociationCommand):
    ASSOCIATION_CLASS: ClassVar = model.CaseTypeSetMember
    LINK_FIELD_NAME1: ClassVar = "case_type_set_id"
    LINK_FIELD_NAME2: ClassVar = "case_type_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.CaseTypeSetMember]


class CaseTypeColSetCaseTypeColUpdateAssociationCommand(UpdateAssociationCommand):
    ASSOCIATION_CLASS: ClassVar = model.CaseTypeColSetMember
    LINK_FIELD_NAME1: ClassVar = "case_type_col_set_id"
    LINK_FIELD_NAME2: ClassVar = "case_type_col_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.CaseTypeColSetMember]


class CreateCaseSetCommand(Command):
    """
    Create a new case set and associate it with the specified data collections and
    cases.
    """

    case_set: model.CaseSet = Field(description="The case set to create.")
    data_collection_ids: set[UUID] = Field(
        description="The data collections to associate with the case set, other than the created_in_data_collection. The latter will be removed from the set if present.",
    )
    case_ids: set[UUID] | None = Field(
        description="The cases to associate with the case set upon creation, if any. These cases must have the same case type as the case set.",
        default=None,
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        self.data_collection_ids.discard(self.case_set.created_in_data_collection_id)
        return self


class ValidateCasesCommand(Command):
    """
    Validate case data and return a validation report.
    """

    case_type_id: UUID = Field(description="The case type ID that the cases belong to.")
    created_in_data_collection_id: UUID = copy_model_field(
        model.CaseValidationReport, "created_in_data_collection_id"
    )
    data_collection_ids: set[UUID] = copy_model_field(
        model.CaseValidationReport, "data_collection_ids"
    )
    is_update: bool = Field(description="Whether this is an update operation.")
    cases: list[model.CaseForCreateUpdate] = Field(description="The cases to validate.")

    @model_validator(mode="after")
    def _validate_cases(self) -> Self:
        if self.created_in_data_collection_id in self.data_collection_ids:
            raise ValueError(
                "The created in data collection ID may not be in the additional data collection IDs."
            )
        if self.is_update and any(x.id is None for x in self.cases):
            raise ValueError("All cases must have an ID when updating")
        return self


class CreateCasesCommand(ValidateCasesCommand):
    """
    Create the corresponding cases and return them.
    """

    pass


class RetrieveCaseSetStatsCommand(Command):
    """
    Retrieve statistics for a set of case sets.
    """

    case_set_ids: list[UUID] | None = Field(
        default=None,
        description="The case set ids to retrieve stats for, if not all. UNIQUE",
    )


class RetrieveCaseTypeStatsCommand(Command):
    """
    Retrieve statistics for a set of case types.
    """

    case_type_ids: set[UUID] | None = Field(
        default=None,
        description="The case type ids to retrieve stats for, if not all.",
    )
    datetime_range_filter: TypedDatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range to filter cases by, if any. The key attribute fo the filter should be left empty.",
    )


class RetrieveCompleteCaseTypeCommand(Command):
    """
    Retrieve a complete case type.
    """

    case_type_id: UUID = Field(description="The ID of the case type to retrieve.")


class RetrieveCasesByQueryCommand(Command):
    """
    Retrieve cases based on a query.
    """

    case_query: model.CaseQuery = Field(description="The query to filter cases by.")


class RetrieveCasesByIdCommand(Command):
    """
    Retrieve cases by their IDs.
    """

    case_ids: list[UUID] = Field(
        description="The case ids to retrieve cases for. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseRightsCommand(Command):
    """
    Retrieve access rights for a set of cases.
    """

    case_ids: list[UUID] = Field(
        description="The case ids to retrieve access for. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseSetRightsCommand(Command):
    """
    Retrieve access rights for a set of case sets.
    """

    case_set_ids: list[UUID] = Field(
        description="The case set ids to retrieve access for. UNIQUE"
    )

    @field_validator("case_set_ids", mode="after")
    def _validate_case_set_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case set ids")
        return value


class RetrievePhylogeneticTreeBySequencesCommand(Command):
    """
    Calculate a phylogenetic tree based on a set of sequence IDs, a tree algorithm, and
    a sequence distance protocol.
    """

    tree_algorithm_code: enum.TreeAlgorithmType = Field(
        description="The algorithm to use for constructing the phylogenetic tree."
    )
    seqdb_seq_distance_protocol_id: UUID = Field(
        description="The ID of the sequence distance protocol to use."
    )
    sequence_ids: list[UUID] = Field(
        description="The IDs of the sequences to calculate the phylogenetic tree for."
    )


class RetrievePhylogeneticTreeByCasesCommand(Command):
    """
    Retrieve a phylogenetic tree based on a set of case IDs, a tree algorithm, and
    a genetic distance case type column.
    """

    tree_algorithm: enum.TreeAlgorithmType = Field(
        description="The algorithm to use for constructing the phylogenetic tree."
    )
    genetic_distance_case_type_col_id: UUID = Field(
        description="The ID of the genetic distance case type column to use."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of the cases to calculate the phylogenetic tree for."
    )


class RetrieveGeneticSequenceByCaseCommand(Command):
    """
    Retrieve a set of genetic sequences based on a set of case IDs and a genetic
    sequence case type column.
    """

    genetic_sequence_case_type_col_id: UUID = Field(
        description="The ID of the genetic sequence case type column to use."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of the cases to retrieve genetic sequences for."
    )


class RetrieveGeneticSequenceFastaByCaseCommand(Command):
    """
    Retrieve a set of genetic sequences in FASTA format based on a set of case IDs and a genetic
    sequence case type column. An iterator is returned that yields the FASTA lines.
    """

    genetic_sequence_case_type_col_id: UUID = Field(
        description="The ID of the genetic sequence case type column to use."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of the cases to retrieve genetic sequences for."
    )


class RetrieveAlleleProfileCommand(Command):
    """
    Retrieve a set of allele profiles based on a set of case IDs and a genetic distance
    case type column.
    """

    genetic_distance_case_type_col_id: UUID = Field(
        description="The ID of the genetic distance case type column to use."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of the cases to retrieve allele profiles for."
    )


# CRUD


class TreeAlgorithmClassCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TreeAlgorithmClass


class TreeAlgorithmCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TreeAlgorithm


class GeneticDistanceProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.GeneticDistanceProtocol


class CaseTypeCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseType


class CaseTypeSetCategoryCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeSetCategory


class CaseTypeSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeSet


class CaseTypeSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeSetMember


class DimCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Dim


class ColCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Col


class CaseTypeColSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeColSet


class CaseTypeColSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeColSetMember


class CaseTypeColCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeCol


class CaseCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Case


class CaseDataCollectionLinkCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseDataCollectionLink


class CaseSetCategoryCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseSetCategory


class CaseSetStatusCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseSetStatus


class CaseSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseSet


class CaseSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseSetMember


class CaseSetDataCollectionLinkCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseSetDataCollectionLink
