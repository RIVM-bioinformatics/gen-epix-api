from typing import Type

from gen_epix import fastapp
from gen_epix.commondb.domain import command as common_command
from gen_epix.commondb.domain import enum as common_enum
from gen_epix.commondb.domain.command import (
    COMMANDS_BY_SERVICE_TYPE as _COMMON_COMMANDS_BY_SERVICE_TYPE,
)
from gen_epix.commondb.domain.command import Command as Command
from gen_epix.commondb.domain.command import ContactCrudCommand as ContactCrudCommand
from gen_epix.commondb.domain.command import CrudCommand as CrudCommand
from gen_epix.commondb.domain.command import (
    DataCollectionCrudCommand as DataCollectionCrudCommand,
)
from gen_epix.commondb.domain.command import (
    DataCollectionSetCrudCommand as DataCollectionSetCrudCommand,
)
from gen_epix.commondb.domain.command import (
    DataCollectionSetDataCollectionUpdateAssociationCommand as DataCollectionSetDataCollectionUpdateAssociationCommand,
)
from gen_epix.commondb.domain.command import (
    DataCollectionSetMemberCrudCommand as DataCollectionSetMemberCrudCommand,
)
from gen_epix.commondb.domain.command import (
    GetIdentityProvidersCommand as GetIdentityProvidersCommand,
)
from gen_epix.commondb.domain.command import (
    IdentifierIssuerCrudCommand as IdentifierIssuerCrudCommand,
)
from gen_epix.commondb.domain.command import InviteUserCommand as InviteUserCommand
from gen_epix.commondb.domain.command import (
    OrganizationCrudCommand as OrganizationCrudCommand,
)
from gen_epix.commondb.domain.command import (
    OrganizationSetCrudCommand as OrganizationSetCrudCommand,
)
from gen_epix.commondb.domain.command import (
    OrganizationSetMemberCrudCommand as OrganizationSetMemberCrudCommand,
)
from gen_epix.commondb.domain.command import (
    OrganizationSetOrganizationUpdateAssociationCommand as OrganizationSetOrganizationUpdateAssociationCommand,
)
from gen_epix.commondb.domain.command import OutageCrudCommand as OutageCrudCommand
from gen_epix.commondb.domain.command import (
    RegisterInvitedUserCommand as RegisterInvitedUserCommand,
)
from gen_epix.commondb.domain.command import (
    RetrieveOrganizationContactCommand as RetrieveOrganizationContactCommand,
)
from gen_epix.commondb.domain.command import (
    RetrieveOutagesCommand as RetrieveOutagesCommand,
)
from gen_epix.commondb.domain.command import (
    RetrieveOwnPermissionsCommand as RetrieveOwnPermissionsCommand,
)
from gen_epix.commondb.domain.command import SiteCrudCommand as SiteCrudCommand
from gen_epix.commondb.domain.command import (
    UpdateAssociationCommand as UpdateAssociationCommand,
)
from gen_epix.commondb.domain.command import UpdateUserCommand as UpdateUserCommand
from gen_epix.commondb.domain.command import (
    UpdateUserOwnOrganizationCommand as UpdateUserOwnOrganizationCommand,
)
from gen_epix.commondb.domain.command.abac import (
    RetrieveOrganizationsUnderAdminCommand as RetrieveOrganizationsUnderAdminCommand,
)
from gen_epix.commondb.domain.command.organization import (
    RetrieveInviteUserConstraintsCommand as RetrieveInviteUserConstraintsCommand,
)
from gen_epix.commondb.domain.command.rbac import (
    RetrieveSubRolesCommand as RetrieveSubRolesCommand,
)
from gen_epix.omopdb.domain import enum
from gen_epix.omopdb.domain.command.abac import (
    OrganizationAdminPolicyCrudCommand as OrganizationAdminPolicyCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    CareSiteCrudCommand as CareSiteCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    CdmSourceCrudCommand as CdmSourceCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import CohortCrudCommand as CohortCrudCommand
from gen_epix.omopdb.domain.command.omop import (
    CohortDefinitionCrudCommand as CohortDefinitionCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    ConceptAncestorCrudCommand as ConceptAncestorCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    ConceptClassCrudCommand as ConceptClassCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import ConceptCrudCommand as ConceptCrudCommand
from gen_epix.omopdb.domain.command.omop import (
    ConceptRelationshipCrudCommand as ConceptRelationshipCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    ConceptSynonymCrudCommand as ConceptSynonymCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    ConditionEraCrudCommand as ConditionEraCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    ConditionOccurrenceCrudCommand as ConditionOccurrenceCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import CostCrudCommand as CostCrudCommand
from gen_epix.omopdb.domain.command.omop import (
    DeviceExposureCrudCommand as DeviceExposureCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import DomainCrudCommand as DomainCrudCommand
from gen_epix.omopdb.domain.command.omop import DoseEraCrudCommand as DoseEraCrudCommand
from gen_epix.omopdb.domain.command.omop import DrugEraCrudCommand as DrugEraCrudCommand
from gen_epix.omopdb.domain.command.omop import (
    DrugExposureCrudCommand as DrugExposureCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    DrugStrengthCrudCommand as DrugStrengthCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    FactRelationshipCrudCommand as FactRelationshipCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    LocationCrudCommand as LocationCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    LocationHistoryCrudCommand as LocationHistoryCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    MeasurementCrudCommand as MeasurementCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    MeasurementRelationCrudCommand as MeasurementRelationCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    MetadataCrudCommand as MetadataCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import NoteCrudCommand as NoteCrudCommand
from gen_epix.omopdb.domain.command.omop import NoteNlpCrudCommand as NoteNlpCrudCommand
from gen_epix.omopdb.domain.command.omop import (
    ObservationCrudCommand as ObservationCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    ObservationPeriodCrudCommand as ObservationPeriodCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    PayerPlanPeriodCrudCommand as PayerPlanPeriodCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import PersonCrudCommand as PersonCrudCommand
from gen_epix.omopdb.domain.command.omop import (
    ProcedureOccurrenceCrudCommand as ProcedureOccurrenceCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    ProviderCrudCommand as ProviderCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    RelationshipCrudCommand as RelationshipCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    SourceToConceptMapCrudCommand as SourceToConceptMapCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    SpecimenCrudCommand as SpecimenCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    SurveyConductCrudCommand as SurveyConductCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    VisitDetailCrudCommand as VisitDetailCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    VisitOccurrenceCrudCommand as VisitOccurrenceCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import VocabularyCrudCommand
from gen_epix.omopdb.domain.command.omop import (
    VocabularyCrudCommand as VocabularyCrudCommand,
)
from gen_epix.omopdb.domain.command.organization import (
    UserCrudCommand as UserCrudCommand,
)
from gen_epix.omopdb.domain.command.organization import (
    UserInvitationCrudCommand as UserInvitationCrudCommand,
)

COMMANDS_BY_SERVICE_TYPE: dict[enum.ServiceType, set[Type[fastapp.Command]]] = {
    # Specific commands
    enum.ServiceType.ABAC: set(
        _COMMON_COMMANDS_BY_SERVICE_TYPE[common_enum.ServiceType.ABAC]
    )
    | set(),
    enum.ServiceType.OMOP: {
        CareSiteCrudCommand,
        CdmSourceCrudCommand,
        CohortCrudCommand,
        CohortDefinitionCrudCommand,
        ConceptAncestorCrudCommand,
        ConceptClassCrudCommand,
        ConceptCrudCommand,
        ConceptRelationshipCrudCommand,
        ConceptSynonymCrudCommand,
        ConditionEraCrudCommand,
        ConditionOccurrenceCrudCommand,
        CostCrudCommand,
        DeviceExposureCrudCommand,
        DomainCrudCommand,
        DoseEraCrudCommand,
        DrugEraCrudCommand,
        DrugExposureCrudCommand,
        DrugStrengthCrudCommand,
        FactRelationshipCrudCommand,
        LocationCrudCommand,
        LocationHistoryCrudCommand,
        MeasurementCrudCommand,
        MeasurementRelationCrudCommand,
        MetadataCrudCommand,
        NoteCrudCommand,
        NoteNlpCrudCommand,
        ObservationCrudCommand,
        ObservationPeriodCrudCommand,
        PayerPlanPeriodCrudCommand,
        PersonCrudCommand,
        ProcedureOccurrenceCrudCommand,
        ProviderCrudCommand,
        RelationshipCrudCommand,
        SourceToConceptMapCrudCommand,
        SpecimenCrudCommand,
        SurveyConductCrudCommand,
        VisitDetailCrudCommand,
        VisitOccurrenceCrudCommand,
        VocabularyCrudCommand,
    },
    # Common commands
    enum.ServiceType.AUTH: set(
        _COMMON_COMMANDS_BY_SERVICE_TYPE[common_enum.ServiceType.AUTH]
    ),
    enum.ServiceType.SYSTEM: set(
        _COMMON_COMMANDS_BY_SERVICE_TYPE[common_enum.ServiceType.SYSTEM]
    ),
    enum.ServiceType.RBAC: set(
        _COMMON_COMMANDS_BY_SERVICE_TYPE[common_enum.ServiceType.RBAC]
    ),
    enum.ServiceType.ORGANIZATION: set(
        _COMMON_COMMANDS_BY_SERVICE_TYPE[common_enum.ServiceType.ORGANIZATION]
    ),
}

COMMON_COMMAND_MAP: dict[Type[fastapp.Command], Type[fastapp.Command]] = {
    common_command.UserCrudCommand: UserCrudCommand,
    common_command.UserInvitationCrudCommand: UserInvitationCrudCommand,
    common_command.OrganizationAdminPolicyCrudCommand: OrganizationAdminPolicyCrudCommand,
}
