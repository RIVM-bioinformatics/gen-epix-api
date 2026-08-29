# pylint: disable=useless-import-alias
from gen_epix import fastapp
from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.command.abac import (
    OrganizationAccessCasePolicyCrudCommand as OrganizationAccessCasePolicyCrudCommand,
)
from gen_epix.casedb.domain.command.abac import (
    OrganizationShareCasePolicyCrudCommand as OrganizationShareCasePolicyCrudCommand,
)
from gen_epix.casedb.domain.command.abac import (
    UserAccessCasePolicyCrudCommand as UserAccessCasePolicyCrudCommand,
)
from gen_epix.casedb.domain.command.abac import (
    UserShareCasePolicyCrudCommand as UserShareCasePolicyCrudCommand,
)
from gen_epix.casedb.domain.command.case import CaseCrudCommand as CaseCrudCommand
from gen_epix.casedb.domain.command.case import (
    CaseDataCollectionLinkCrudCommand as CaseDataCollectionLinkCrudCommand,
)
from gen_epix.casedb.domain.command.case import (
    CaseIdentifierCrudCommand as CaseIdentifierCrudCommand,
)
from gen_epix.casedb.domain.command.case import (
    CaseSetCategoryCrudCommand as CaseSetCategoryCrudCommand,
)
from gen_epix.casedb.domain.command.case import CaseSetCrudCommand as CaseSetCrudCommand
from gen_epix.casedb.domain.command.case import (
    CaseSetDataCollectionLinkCrudCommand as CaseSetDataCollectionLinkCrudCommand,
)
from gen_epix.casedb.domain.command.case import (
    CaseSetMemberCrudCommand as CaseSetMemberCrudCommand,
)
from gen_epix.casedb.domain.command.case import (
    CaseSetStatusCrudCommand as CaseSetStatusCrudCommand,
)
from gen_epix.casedb.domain.command.case import (
    CaseTypeCrudCommand as CaseTypeCrudCommand,
)
from gen_epix.casedb.domain.command.case import (
    CaseTypeSetCaseTypeUpdateAssociationCommand as CaseTypeSetCaseTypeUpdateAssociationCommand,
)
from gen_epix.casedb.domain.command.case import (
    CaseTypeSetCategoryCrudCommand as CaseTypeSetCategoryCrudCommand,
)
from gen_epix.casedb.domain.command.case import (
    CaseTypeSetCrudCommand as CaseTypeSetCrudCommand,
)
from gen_epix.casedb.domain.command.case import (
    CaseTypeSetMemberCrudCommand as CaseTypeSetMemberCrudCommand,
)
from gen_epix.casedb.domain.command.case import ColCrudCommand as ColCrudCommand
from gen_epix.casedb.domain.command.case import (
    ColSetColUpdateAssociationCommand as ColSetColUpdateAssociationCommand,
)
from gen_epix.casedb.domain.command.case import ColSetCrudCommand as ColSetCrudCommand
from gen_epix.casedb.domain.command.case import (
    ColSetMemberCrudCommand as ColSetMemberCrudCommand,
)
from gen_epix.casedb.domain.command.case import (
    CreateCaseSetCommand as CreateCaseSetCommand,
)
from gen_epix.casedb.domain.command.case import (
    CreateFileForReadSetCommand as CreateFileForReadSetCommand,
)
from gen_epix.casedb.domain.command.case import (
    CreateFileForSeqCommand as CreateFileForSeqCommand,
)
from gen_epix.casedb.domain.command.case import DimCrudCommand as DimCrudCommand
from gen_epix.casedb.domain.command.case import (
    GeneticDistanceProtocolCrudCommand as GeneticDistanceProtocolCrudCommand,
)
from gen_epix.casedb.domain.command.case import RefColCrudCommand as RefColCrudCommand
from gen_epix.casedb.domain.command.case import RefDimCrudCommand as RefDimCrudCommand
from gen_epix.casedb.domain.command.case import (
    RetrieveCaseCohortLinksByCaseTypeCommand as RetrieveCaseCohortLinksByCaseTypeCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveCaseRightsCommand as RetrieveCaseRightsCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveCasesByIdCommand as RetrieveCasesByIdCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveCasesByQueryCommand as RetrieveCasesByQueryCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveCaseSetRightsCommand as RetrieveCaseSetRightsCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveCaseSetStatsCommand as RetrieveCaseSetStatsCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveCaseTypeStatsCommand as RetrieveCaseTypeStatsCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveCompleteCaseTypeCommand as RetrieveCompleteCaseTypeCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveGeneticSequenceFastaByCaseCommand as RetrieveGeneticSequenceFastaByCaseCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveIsOwnCasesCommand as RetrieveIsOwnCasesCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrievePhylogeneticTreeByCasesCommand as RetrievePhylogeneticTreeByCasesCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrievePhylogeneticTreeByProfilesCommand as RetrievePhylogeneticTreeByProfilesCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveProtocolsCommand as RetrieveProtocolsCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveSimilarCasesCommand as RetrieveSimilarCasesCommand,
)
from gen_epix.casedb.domain.command.case import (
    RetrieveSimilarCasesReturnValue as RetrieveSimilarCasesReturnValue,
)
from gen_epix.casedb.domain.command.case import (
    TreeAlgorithmClassCrudCommand as TreeAlgorithmClassCrudCommand,
)
from gen_epix.casedb.domain.command.case import (
    TreeAlgorithmCrudCommand as TreeAlgorithmCrudCommand,
)
from gen_epix.casedb.domain.command.case import UploadCasesCommand as UploadCasesCommand
from gen_epix.casedb.domain.command.geo import RegionCrudCommand as RegionCrudCommand
from gen_epix.casedb.domain.command.geo import (
    RegionRelationCrudCommand as RegionRelationCrudCommand,
)
from gen_epix.casedb.domain.command.geo import (
    RegionSetCrudCommand as RegionSetCrudCommand,
)
from gen_epix.casedb.domain.command.geo import (
    RegionSetShapeCrudCommand as RegionSetShapeCrudCommand,
)
from gen_epix.casedb.domain.command.geo import (
    RetrieveContainingRegionCommand as RetrieveContainingRegionCommand,
)
from gen_epix.casedb.domain.command.ontology import (
    ConceptCrudCommand as ConceptCrudCommand,
)
from gen_epix.casedb.domain.command.ontology import (
    ConceptRelationCrudCommand as ConceptRelationCrudCommand,
)
from gen_epix.casedb.domain.command.ontology import (
    ConceptSetCrudCommand as ConceptSetCrudCommand,
)
from gen_epix.casedb.domain.command.ontology import (
    DiseaseCrudCommand as DiseaseCrudCommand,
)
from gen_epix.casedb.domain.command.ontology import (
    DiseaseEtiologicalAgentUpdateAssociationCommand as DiseaseEtiologicalAgentUpdateAssociationCommand,
)
from gen_epix.casedb.domain.command.ontology import (
    EtiologicalAgentCrudCommand as EtiologicalAgentCrudCommand,
)
from gen_epix.casedb.domain.command.ontology import (
    EtiologyCrudCommand as EtiologyCrudCommand,
)
from gen_epix.casedb.domain.command.seqdb import (
    RetrieveGeneticSequenceByIdCommand as RetrieveGeneticSequenceByIdCommand,
)
from gen_epix.casedb.domain.command.seqdb import (
    RetrieveGeneticSequenceFastaByIdCommand as RetrieveGeneticSequenceFastaByIdCommand,
)
from gen_epix.commondb.domain import enum as common_enum
from gen_epix.commondb.domain.command import (
    COMMANDS_BY_SERVICE_TYPE as _COMMON_COMMANDS_BY_SERVICE_TYPE,
)
from gen_epix.commondb.domain.command import (
    AnonymizeUserCommand as AnonymizeUserCommand,
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
    OrganizationAdminPolicyCrudCommand as OrganizationAdminPolicyCrudCommand,
)
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
    RetrieveOrganizationAdminNameEmailsCommand as RetrieveOrganizationAdminNameEmailsCommand,
)
from gen_epix.commondb.domain.command import (
    RetrieveOrganizationContactsCommand as RetrieveOrganizationContactsCommand,
)
from gen_epix.commondb.domain.command import (
    RetrieveOrganizationsUnderAdminCommand as RetrieveOrganizationsUnderAdminCommand,
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
from gen_epix.commondb.domain.command import UserCrudCommand as UserCrudCommand
from gen_epix.commondb.domain.command import (
    UserInvitationCrudCommand as UserInvitationCrudCommand,
)
from gen_epix.commondb.domain.command.organization import (
    RetrieveInviteUserConstraintsCommand as RetrieveInviteUserConstraintsCommand,
)
from gen_epix.commondb.domain.command.rbac import (
    RetrieveSubRolesCommand as RetrieveSubRolesCommand,
)

COMMANDS_BY_SERVICE_TYPE: dict[enum.ServiceType, set[type[fastapp.Command]]] = {
    # Specific commands
    enum.ServiceType.ABAC: set(
        _COMMON_COMMANDS_BY_SERVICE_TYPE[common_enum.ServiceType.ABAC]
    ).union(
        {
            OrganizationAccessCasePolicyCrudCommand,
            OrganizationShareCasePolicyCrudCommand,
            UserAccessCasePolicyCrudCommand,
            UserShareCasePolicyCrudCommand,
        }
    ),
    enum.ServiceType.CASE: {
        CaseCrudCommand,
        CaseIdentifierCrudCommand,
        CaseDataCollectionLinkCrudCommand,
        CaseSetCategoryCrudCommand,
        CaseSetCrudCommand,
        CaseSetDataCollectionLinkCrudCommand,
        CaseSetMemberCrudCommand,
        CaseSetStatusCrudCommand,
        ColCrudCommand,
        ColSetColUpdateAssociationCommand,
        ColSetCrudCommand,
        ColSetMemberCrudCommand,
        CaseTypeCrudCommand,
        CaseTypeSetCaseTypeUpdateAssociationCommand,
        CaseTypeSetCategoryCrudCommand,
        CaseTypeSetCrudCommand,
        CaseTypeSetMemberCrudCommand,
        DimCrudCommand,
        RefColCrudCommand,
        UploadCasesCommand,
        CreateCaseSetCommand,
        CreateFileForReadSetCommand,
        CreateFileForSeqCommand,
        RefDimCrudCommand,
        GeneticDistanceProtocolCrudCommand,
        RetrieveProtocolsCommand,
        RetrieveCaseCohortLinksByCaseTypeCommand,
        RetrieveCaseRightsCommand,
        RetrieveCasesByIdCommand,
        RetrieveCasesByQueryCommand,
        RetrieveCaseSetRightsCommand,
        RetrieveCaseSetStatsCommand,
        RetrieveCaseTypeStatsCommand,
        RetrieveCompleteCaseTypeCommand,
        RetrieveGeneticSequenceFastaByCaseCommand,
        RetrievePhylogeneticTreeByCasesCommand,
        RetrieveSimilarCasesCommand,
        RetrieveIsOwnCasesCommand,
        RetrievePhylogeneticTreeByProfilesCommand,
        TreeAlgorithmClassCrudCommand,
        TreeAlgorithmCrudCommand,
    },
    enum.ServiceType.GEO: {
        RegionCrudCommand,
        RegionRelationCrudCommand,
        RegionSetCrudCommand,
        RegionSetShapeCrudCommand,
        RetrieveContainingRegionCommand,
    },
    enum.ServiceType.ONTOLOGY: {
        ConceptCrudCommand,
        ConceptRelationCrudCommand,
        ConceptSetCrudCommand,
        DiseaseCrudCommand,
        DiseaseEtiologicalAgentUpdateAssociationCommand,
        EtiologicalAgentCrudCommand,
        EtiologyCrudCommand,
    },
    enum.ServiceType.SEQDB: {
        RetrieveGeneticSequenceByIdCommand,
        RetrieveGeneticSequenceFastaByIdCommand,
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

COMMON_COMMAND_MAP: dict[type[fastapp.Command], type[fastapp.Command]] = {}

COMMON_COMMAND_MAP: dict[type[fastapp.Command], type[fastapp.Command]] = {}

COMMON_COMMAND_MAP: dict[type[fastapp.Command], type[fastapp.Command]] = {}
