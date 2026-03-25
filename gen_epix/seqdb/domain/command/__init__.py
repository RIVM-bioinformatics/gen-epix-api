# pylint: disable=useless-import-alias
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
from gen_epix.commondb.domain.command.abac import (
    RetrieveOrganizationsUnderAdminCommand as RetrieveOrganizationsUnderAdminCommand,
)
from gen_epix.commondb.domain.command.organization import (
    RetrieveInviteUserConstraintsCommand as RetrieveInviteUserConstraintsCommand,
)
from gen_epix.commondb.domain.command.rbac import (
    RetrieveSubRolesCommand as RetrieveSubRolesCommand,
)
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.command.file import CreateFileCommand as CreateFileCommand
from gen_epix.seqdb.domain.command.file import FileCrudCommand as FileCrudCommand
from gen_epix.seqdb.domain.command.seq import AlleleCrudCommand as AlleleCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    AstMeasurementCrudCommand as AstMeasurementCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    AstPredictionCrudCommand as AstPredictionCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    CalculatePhylogeneticTreeCommand as CalculatePhylogeneticTreeCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    CalculateSeqDistancesForNewProfilesCommand as CalculateSeqDistancesForNewProfilesCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    LocusCodeMapCrudCommand as LocusCodeMapCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import LocusCrudCommand as LocusCrudCommand
from gen_epix.seqdb.domain.command.seq import LocusSetCrudCommand as LocusSetCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    PcrMeasurementCrudCommand as PcrMeasurementCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import ProtocolCrudCommand as ProtocolCrudCommand
from gen_epix.seqdb.domain.command.seq import ReadSetCrudCommand as ReadSetCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    ReadSetIdentifierCrudCommand as ReadSetIdentifierCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RefAlleleCrudCommand as RefAlleleCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import RefSeqCrudCommand as RefSeqCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    RetrieveSamplesCommand as RetrieveSamplesCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RetrieveSeqFastaCommand as RetrieveSeqFastaCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RetrieveSimilarProfilesCommand as RetrieveSimilarProfilesCommand,
)
from gen_epix.seqdb.domain.command.seq import SampleCrudCommand as SampleCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    SampleDataCollectionLinkCrudCommand as SampleDataCollectionLinkCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SampleIdentifierCrudCommand as SampleIdentifierCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SeqCategoryCrudCommand as SeqCategoryCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SeqCategorySetCrudCommand as SeqCategorySetCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SeqClassificationCrudCommand as SeqClassificationCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import SeqCrudCommand as SeqCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    SeqDistanceCrudCommand as SeqDistanceCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SeqIdentifierCrudCommand as SeqIdentifierCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SeqProfileCrudCommand as SeqProfileCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SeqProfileIdentifierCrudCommand as SeqProfileIdentifierCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SeqTaxonomyCrudCommand as SeqTaxonomyCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import TaxonCrudCommand as TaxonCrudCommand
from gen_epix.seqdb.domain.command.seq import TaxonSetCrudCommand as TaxonSetCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    TaxonSetMemberCrudCommand as TaxonSetMemberCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    TreeAlgorithmClassCrudCommand as TreeAlgorithmClassCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    TreeAlgorithmCrudCommand as TreeAlgorithmCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    UploadSamplesCommand as UploadSamplesCommand,
)

COMMANDS_BY_SERVICE_TYPE: dict[enum.ServiceType, set[type[fastapp.Command]]] = {
    # Specific commands
    enum.ServiceType.ABAC: set(
        _COMMON_COMMANDS_BY_SERVICE_TYPE[common_enum.ServiceType.ABAC]
    )
    | set(),
    enum.ServiceType.SEQ: {
        AlleleCrudCommand,
        AstMeasurementCrudCommand,
        AstPredictionCrudCommand,
        LocusCodeMapCrudCommand,
        LocusCrudCommand,
        LocusSetCrudCommand,
        PcrMeasurementCrudCommand,
        ProtocolCrudCommand,
        UploadSamplesCommand,
        ReadSetCrudCommand,
        ReadSetIdentifierCrudCommand,
        RefAlleleCrudCommand,
        RefSeqCrudCommand,
        CalculatePhylogeneticTreeCommand,
        RetrieveSeqFastaCommand,
        RetrieveSimilarProfilesCommand,
        CalculateSeqDistancesForNewProfilesCommand,
        SampleCrudCommand,
        SampleDataCollectionLinkCrudCommand,
        SampleIdentifierCrudCommand,
        SeqCategoryCrudCommand,
        SeqCategorySetCrudCommand,
        SeqClassificationCrudCommand,
        SeqCrudCommand,
        SeqDistanceCrudCommand,
        SeqIdentifierCrudCommand,
        SeqProfileCrudCommand,
        SeqProfileIdentifierCrudCommand,
        SeqTaxonomyCrudCommand,
        TaxonCrudCommand,
        TaxonSetCrudCommand,
        TaxonSetMemberCrudCommand,
        TreeAlgorithmClassCrudCommand,
        TreeAlgorithmCrudCommand,
    },
    enum.ServiceType.FILE: {
        CreateFileCommand,
        FileCrudCommand,
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

COMMON_COMMAND_MAP: dict[type[fastapp.Command], type[fastapp.Command]] = {
    common_command.UserCrudCommand: UserCrudCommand,
    common_command.UserInvitationCrudCommand: UserInvitationCrudCommand,
    common_command.InviteUserCommand: InviteUserCommand,
    common_command.UpdateUserCommand: UpdateUserCommand,
    common_command.OrganizationAdminPolicyCrudCommand: OrganizationAdminPolicyCrudCommand,
}
