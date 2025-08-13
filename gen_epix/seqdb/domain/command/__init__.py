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
from gen_epix.seqdb.domain import DOMAIN, enum
from gen_epix.seqdb.domain.command.organization import (
    UserCrudCommand as UserCrudCommand,
)
from gen_epix.seqdb.domain.command.organization import (
    UserInvitationCrudCommand as UserInvitationCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    AlignmentProtocolCrudCommand as AlignmentProtocolCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    AlleleAlignmentCrudCommand as AlleleAlignmentCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import AlleleCrudCommand as AlleleCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    AlleleProfileCrudCommand as AlleleProfileCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    AssemblyProtocolCrudCommand as AssemblyProtocolCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    AstMeasurementCrudCommand as AstMeasurementCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    AstPredictionCrudCommand as AstPredictionCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    AstProtocolCrudCommand as AstProtocolCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    GenerateMultipleAlignmentCommand as GenerateMultipleAlignmentCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    GeneratePhylogeneticTreeCommand as GeneratePhylogeneticTreeCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    KmerDetectionProtocolCrudCommand as KmerDetectionProtocolCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    KmerProfileCrudCommand as KmerProfileCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    LibraryPrepProtocolCrudCommand as LibraryPrepProtocolCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import LocusCrudCommand as LocusCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    LocusDetectionProtocolCrudCommand as LocusDetectionProtocolCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import LocusSetCrudCommand as LocusSetCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    LocusSetMemberCrudCommand as LocusSetMemberCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    PcrMeasurementCrudCommand as PcrMeasurementCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    PcrProtocolCrudCommand as PcrProtocolCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import RawSeqCrudCommand as RawSeqCrudCommand
from gen_epix.seqdb.domain.command.seq import ReadSetCrudCommand as ReadSetCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    RefAlleleCrudCommand as RefAlleleCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import RefSeqCrudCommand as RefSeqCrudCommand
from gen_epix.seqdb.domain.command.seq import RefSnpCrudCommand as RefSnpCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    RefSnpSetCrudCommand as RefSnpSetCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RefSnpSetMemberCrudCommand as RefSnpSetMemberCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RetrieveCompleteAlleleProfileCommand as RetrieveCompleteAlleleProfileCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RetrieveCompleteContigCommand as RetrieveCompleteContigCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RetrieveCompleteSampleCommand as RetrieveCompleteSampleCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RetrieveCompleteSeqCommand as RetrieveCompleteSeqCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RetrieveCompleteSnpProfileCommand as RetrieveCompleteSnpProfileCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RetrieveMultipleAlignmentCommand as RetrieveMultipleAlignmentCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    RetrievePhylogeneticTreeCommand as RetrievePhylogeneticTreeCommand,
)
from gen_epix.seqdb.domain.command.seq import SampleCrudCommand as SampleCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    SeqAlignmentCrudCommand as SeqAlignmentCrudCommand,
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
from gen_epix.seqdb.domain.command.seq import (
    SeqClassificationProtocolCrudCommand as SeqClassificationProtocolCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import SeqCrudCommand as SeqCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    SeqDistanceCrudCommand as SeqDistanceCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SeqDistanceProtocolCrudCommand as SeqDistanceProtocolCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SeqTaxonomyCrudCommand as SeqTaxonomyCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SnpDetectionProtocolCrudCommand as SnpDetectionProtocolCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SnpProfileCrudCommand as SnpProfileCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    SubtypingSchemeCrudCommand as SubtypingSchemeCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import TaxonCrudCommand as TaxonCrudCommand
from gen_epix.seqdb.domain.command.seq import (
    TaxonLocusLinkCrudCommand as TaxonLocusLinkCrudCommand,
)
from gen_epix.seqdb.domain.command.seq import (
    TaxonomyProtocolCrudCommand as TaxonomyProtocolCrudCommand,
)
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

COMMANDS_BY_SERVICE: dict[enum.ServiceType, list[Type[fastapp.Command]]] = {
    enum.ServiceType.SEQ: [
        AlignmentProtocolCrudCommand,
        AlleleAlignmentCrudCommand,
        AlleleCrudCommand,
        AlleleProfileCrudCommand,
        AssemblyProtocolCrudCommand,
        AstMeasurementCrudCommand,
        AstPredictionCrudCommand,
        AstProtocolCrudCommand,
        GenerateMultipleAlignmentCommand,
        GeneratePhylogeneticTreeCommand,
        KmerDetectionProtocolCrudCommand,
        KmerProfileCrudCommand,
        LibraryPrepProtocolCrudCommand,
        LocusCrudCommand,
        LocusDetectionProtocolCrudCommand,
        LocusSetCrudCommand,
        LocusSetMemberCrudCommand,
        PcrMeasurementCrudCommand,
        PcrProtocolCrudCommand,
        RawSeqCrudCommand,
        ReadSetCrudCommand,
        RefAlleleCrudCommand,
        RefSeqCrudCommand,
        RefSnpCrudCommand,
        RefSnpSetCrudCommand,
        RefSnpSetMemberCrudCommand,
        RetrieveCompleteAlleleProfileCommand,
        RetrieveCompleteContigCommand,
        RetrieveCompleteSampleCommand,
        RetrieveCompleteSeqCommand,
        RetrieveCompleteSnpProfileCommand,
        RetrieveMultipleAlignmentCommand,
        RetrievePhylogeneticTreeCommand,
        SampleCrudCommand,
        SeqAlignmentCrudCommand,
        SeqCategoryCrudCommand,
        SeqCategorySetCrudCommand,
        SeqClassificationCrudCommand,
        SeqClassificationProtocolCrudCommand,
        SeqCrudCommand,
        SeqDistanceCrudCommand,
        SeqDistanceProtocolCrudCommand,
        SeqTaxonomyCrudCommand,
        SnpDetectionProtocolCrudCommand,
        SnpProfileCrudCommand,
        SubtypingSchemeCrudCommand,
        TaxonCrudCommand,
        TaxonLocusLinkCrudCommand,
        TaxonomyProtocolCrudCommand,
        TaxonSetCrudCommand,
        TaxonSetMemberCrudCommand,
        TreeAlgorithmClassCrudCommand,
        TreeAlgorithmCrudCommand,
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
