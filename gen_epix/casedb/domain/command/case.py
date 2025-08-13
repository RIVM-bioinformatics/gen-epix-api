from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_validator, model_validator

import gen_epix.casedb.domain.model.case as model
from gen_epix.casedb.domain import enum
from gen_epix.common.domain.command import (
    Command,
    CrudCommand,
    UpdateAssociationCommand,
)
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


class CaseSetCreateCommand(Command):

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


class CasesCreateCommand(Command):

    cases: list[model.Case] = Field(
        description="The cases to create. All cases must have the same case type and created_in_data_collection."
    )
    data_collection_ids: set[UUID] = Field(
        description="The data collections to associate with the cases, other than the created_in_data_collection. The latter will be removed from the set if present."
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if len(set(x.case_type_id for x in self.cases)) > 1:
            raise ValueError("Not all cases have the same case type.")
        case_ids = set()
        for i, case in enumerate(self.cases):
            if case.id in case_ids:
                raise ValueError(f"Duplicate case id: {case.id}")
            if case.id is not None:
                case_ids.add(case.id)
        if self.cases:
            self.data_collection_ids.discard(
                self.cases[0].created_in_data_collection_id
            )
        return self


class RetrieveCaseSetStatsCommand(Command):

    case_set_ids: list[UUID] | None = Field(
        default=None,
        description="The case set ids to retrieve stats for, if not all. UNIQUE",
    )


class RetrieveCaseTypeStatsCommand(Command):

    case_type_ids: set[UUID] | None = Field(
        default=None,
        description="The case type ids to retrieve stats for, if not all.",
    )
    datetime_range_filter: TypedDatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range to filter cases by, if any. The key attribute fo the filter should be left empty.",
    )


class RetrieveCompleteCaseTypeCommand(Command):

    case_type_id: UUID


class RetrieveCasesByQueryCommand(Command):

    case_query: model.CaseQuery


class RetrieveCasesByIdCommand(Command):

    case_ids: list[UUID] = Field(
        description="The case ids to retrieve cases for. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseRightsCommand(Command):

    case_ids: list[UUID] = Field(
        description="The case ids to retrieve access for. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseSetRightsCommand(Command):

    case_set_ids: list[UUID] = Field(
        description="The case set ids to retrieve access for. UNIQUE"
    )

    @field_validator("case_set_ids", mode="after")
    def _validate_case_set_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case set ids")
        return value


class RetrievePhylogeneticTreeBySequencesCommand(Command):
    tree_algorithm_code: enum.TreeAlgorithmType
    seqdb_seq_distance_protocol_id: UUID
    sequence_ids: list[UUID]


class RetrievePhylogeneticTreeByCasesCommand(Command):
    tree_algorithm: enum.TreeAlgorithmType
    genetic_distance_case_type_col_id: UUID
    case_ids: list[UUID]


class RetrieveGeneticSequenceByCaseCommand(Command):

    genetic_sequence_case_type_col_id: UUID
    case_ids: list[UUID]


class RetrieveAlleleProfileCommand(Command):

    sequence_ids: list[UUID]


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
