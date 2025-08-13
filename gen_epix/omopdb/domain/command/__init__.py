from typing import Type

from gen_epix import fastapp
from gen_epix.common.domain.command import Command as Command
from gen_epix.common.domain.command import ContactCrudCommand as ContactCrudCommand
from gen_epix.common.domain.command import CrudCommand as CrudCommand
from gen_epix.common.domain.command import (
    DataCollectionCrudCommand as DataCollectionCrudCommand,
)
from gen_epix.common.domain.command import (
    DataCollectionSetCrudCommand as DataCollectionSetCrudCommand,
)
from gen_epix.common.domain.command import (
    DataCollectionSetDataCollectionUpdateAssociationCommand as DataCollectionSetDataCollectionUpdateAssociationCommand,
)
from gen_epix.common.domain.command import (
    DataCollectionSetMemberCrudCommand as DataCollectionSetMemberCrudCommand,
)
from gen_epix.common.domain.command import (
    GetIdentityProvidersCommand as GetIdentityProvidersCommand,
)
from gen_epix.common.domain.command import (
    IdentifierIssuerCrudCommand as IdentifierIssuerCrudCommand,
)
from gen_epix.common.domain.command import InviteUserCommand as InviteUserCommand
from gen_epix.common.domain.command import (
    OrganizationCrudCommand as OrganizationCrudCommand,
)
from gen_epix.common.domain.command import (
    OrganizationSetCrudCommand as OrganizationSetCrudCommand,
)
from gen_epix.common.domain.command import (
    OrganizationSetMemberCrudCommand as OrganizationSetMemberCrudCommand,
)
from gen_epix.common.domain.command import (
    OrganizationSetOrganizationUpdateAssociationCommand as OrganizationSetOrganizationUpdateAssociationCommand,
)
from gen_epix.common.domain.command import OutageCrudCommand as OutageCrudCommand
from gen_epix.common.domain.command import (
    RegisterInvitedUserCommand as RegisterInvitedUserCommand,
)
from gen_epix.common.domain.command import (
    RetrieveOrganizationContactCommand as RetrieveOrganizationContactCommand,
)
from gen_epix.common.domain.command import (
    RetrieveOutagesCommand as RetrieveOutagesCommand,
)
from gen_epix.common.domain.command import (
    RetrieveOwnPermissionsCommand as RetrieveOwnPermissionsCommand,
)
from gen_epix.common.domain.command import SiteCrudCommand as SiteCrudCommand
from gen_epix.common.domain.command import (
    UpdateAssociationCommand as UpdateAssociationCommand,
)
from gen_epix.common.domain.command import UpdateUserCommand as UpdateUserCommand
from gen_epix.common.domain.command import (
    UpdateUserOwnOrganizationCommand as UpdateUserOwnOrganizationCommand,
)
from gen_epix.omopdb.domain import DOMAIN, enum
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
from gen_epix.omopdb.domain.command.omop import EtlCrudCommand as EtlCrudCommand
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
    ProvenanceCrudCommand as ProvenanceCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    ProviderCrudCommand as ProviderCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import (
    RelationshipCrudCommand as RelationshipCrudCommand,
)
from gen_epix.omopdb.domain.command.omop import SourceCrudCommand as SourceCrudCommand
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

COMMANDS_BY_SERVICE: dict[enum.ServiceType, list[Type[fastapp.Command]]] = {
    enum.ServiceType.OMOP: [
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
        EtlCrudCommand,
        FactRelationshipCrudCommand,
        LocationCrudCommand,
        LocationHistoryCrudCommand,
        MeasurementCrudCommand,
        MetadataCrudCommand,
        NoteCrudCommand,
        NoteNlpCrudCommand,
        ObservationCrudCommand,
        ObservationPeriodCrudCommand,
        PayerPlanPeriodCrudCommand,
        PersonCrudCommand,
        ProcedureOccurrenceCrudCommand,
        ProvenanceCrudCommand,
        ProviderCrudCommand,
        RelationshipCrudCommand,
        SourceCrudCommand,
        SourceToConceptMapCrudCommand,
        SpecimenCrudCommand,
        SurveyConductCrudCommand,
        VisitDetailCrudCommand,
        VisitOccurrenceCrudCommand,
        VocabularyCrudCommand,
    ],
    enum.ServiceType.AUTH: [
        GetIdentityProvidersCommand,
    ],
    enum.ServiceType.ORGANIZATION: [
        ContactCrudCommand,
        DataCollectionCrudCommand,
        DataCollectionSetCrudCommand,
        DataCollectionSetDataCollectionUpdateAssociationCommand,
        DataCollectionSetMemberCrudCommand,
        IdentifierIssuerCrudCommand,
        InviteUserCommand,
        OrganizationCrudCommand,
        OrganizationSetCrudCommand,
        OrganizationSetMemberCrudCommand,
        OrganizationSetOrganizationUpdateAssociationCommand,
        RegisterInvitedUserCommand,
        RetrieveOrganizationContactCommand,
        SiteCrudCommand,
        UpdateUserCommand,
        UpdateUserOwnOrganizationCommand,
        UserCrudCommand,
        UserInvitationCrudCommand,
    ],
    enum.ServiceType.RBAC: [
        RetrieveOwnPermissionsCommand,
    ],
    enum.ServiceType.SYSTEM: [
        OutageCrudCommand,
        RetrieveOutagesCommand,
    ],
}

for service_type, command_classes in COMMANDS_BY_SERVICE.items():
    for command_class in command_classes:
        DOMAIN.register_command(command_class, service_type=service_type)
