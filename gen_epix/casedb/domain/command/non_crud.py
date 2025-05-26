# pylint: disable=useless-import-alias

from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from gen_epix.casedb.domain import DOMAIN, enum, model
from gen_epix.casedb.domain.command.base import Command, UpdateAssociationCommand
from gen_epix.fastapp.services import auth
from gen_epix.filter import TypedDatetimeRangeFilter


# auth
class GetIdentityProvidersCommand(auth.GetIdentityProvidersCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.AUTH


# organization
class OrganizationSetOrganizationUpdateAssociationCommand(UpdateAssociationCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION
    ASSOCIATION_CLASS: ClassVar = model.OrganizationSetMember
    LINK_FIELD_NAME1: ClassVar = "organization_set_id"
    LINK_FIELD_NAME2: ClassVar = "organization_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.OrganizationSetMember]


class DataCollectionSetDataCollectionUpdateAssociationCommand(UpdateAssociationCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION
    ASSOCIATION_CLASS: ClassVar = model.DataCollectionSetMember
    LINK_FIELD_NAME1: ClassVar = "data_collection_set_id"
    LINK_FIELD_NAME2: ClassVar = "data_collection_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.DataCollectionSetMember]


class InviteUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION

    email: str
    roles: set[enum.Role]
    organization_id: UUID


class RegisterInvitedUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION

    token: str


class RetrieveOrganizationContactCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION

    organization_ids: list[UUID] | None = None
    site_ids: list[UUID] | None = None
    contact_ids: list[UUID] | None = None


class UpdateUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION

    tgt_user_id: UUID
    is_active: bool | None
    roles: set[enum.Role] | None
    organization_id: UUID | None


# geo
class RetrieveContainingRegionCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.GEO

    region_ids: list[UUID]
    region_set_id: UUID
    level: int


# case


class CaseTypeSetCaseTypeUpdateAssociationCommand(UpdateAssociationCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE
    ASSOCIATION_CLASS: ClassVar = model.CaseTypeSetMember
    LINK_FIELD_NAME1: ClassVar = "case_type_set_id"
    LINK_FIELD_NAME2: ClassVar = "case_type_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.CaseTypeSetMember]


class CaseTypeColSetCaseTypeColUpdateAssociationCommand(UpdateAssociationCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE
    ASSOCIATION_CLASS: ClassVar = model.CaseTypeColSetMember
    LINK_FIELD_NAME1: ClassVar = "case_type_col_set_id"
    LINK_FIELD_NAME2: ClassVar = "case_type_col_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.CaseTypeColSetMember]


class CaseSetCreateCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

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
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

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
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

    case_set_ids: list[UUID] | None = Field(
        default=None,
        description="The case set ids to retrieve stats for, if not all. UNIQUE",
    )

    @field_validator("case_set_ids", mode="after")
    def _validate_case_set_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case set ids")
        return value


class RetrieveCaseTypeStatsCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

    case_type_ids: set[UUID] | None = Field(
        default=None,
        description="The case type ids to retrieve stats for, if not all.",
    )
    datetime_range_filter: TypedDatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range to filter cases by, if any. The key attribute fo the filter should be left empty.",
    )

    @field_validator("case_type_ids", mode="after")
    def _validate_case_type_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case type ids")
        return value


class RetrieveCompleteCaseTypeCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

    case_type_id: UUID


class RetrieveCasesByQueryCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

    case_query: model.CaseQuery


class RetrieveCasesByIdCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

    case_ids: list[UUID] = Field(
        description="The case ids to retrieve cases for. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseRightsCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

    case_ids: list[UUID] = Field(
        description="The case ids to retrieve access for. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseSetRightsCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

    case_set_ids: list[UUID] = Field(
        description="The case set ids to retrieve access for. UNIQUE"
    )

    @field_validator("case_set_ids", mode="after")
    def _validate_case_set_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case set ids")
        return value


class RetrievePhylogeneticTreeBySequencesCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE
    tree_algorithm_code: enum.TreeAlgorithmType
    seqdb_seq_distance_protocol_id: UUID
    sequence_ids: list[UUID]


class RetrievePhylogeneticTreeByCasesCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE
    tree_algorithm: enum.TreeAlgorithmType
    genetic_distance_case_type_col_id: UUID
    case_ids: list[UUID]


class RetrieveGeneticSequenceByCaseCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

    genetic_sequence_case_type_col_id: UUID
    case_ids: list[UUID]


class RetrieveAlleleProfileCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.CASE

    sequence_ids: list[UUID]


# seq
class RetrieveGeneticSequenceByIdCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.SEQDB

    seq_ids: list[UUID]


# abac
class RetrieveCompleteUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ABAC


class RetrieveOrganizationAdminNameEmailsCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ABAC


class UpdateUserOwnOrganizationCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ABAC

    organization_id: UUID
    is_new_user: bool = False


# ontology
class ConceptSetConceptUpdateAssociationCommand(UpdateAssociationCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ONTOLOGY
    ASSOCIATION_CLASS: ClassVar = model.ConceptSetMember
    LINK_FIELD_NAME1: ClassVar = "concept_set_id"
    LINK_FIELD_NAME2: ClassVar = "concept_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.ConceptSetMember]


class DiseaseEtiologicalAgentUpdateAssociationCommand(UpdateAssociationCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ONTOLOGY
    ASSOCIATION_CLASS: ClassVar = model.Etiology
    LINK_FIELD_NAME1: ClassVar = "disease_id"
    LINK_FIELD_NAME2: ClassVar = "etiological_agent_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.Etiology]


# system
class RetrieveOutagesCommand(Command):
    SERVICE_TYPE = enum.ServiceType.SYSTEM


# rbac
class GetOwnPermissionsCommand(Command):
    SERVICE_TYPE = enum.ServiceType.RBAC


DOMAIN.register_locals(locals())
