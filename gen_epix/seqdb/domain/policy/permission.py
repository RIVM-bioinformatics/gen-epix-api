from typing import Type

from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.enum import Role


class RoleGenerator:

    ROLE_PERMISSION_SETS: dict[
        Role, set[tuple[Type[command.Command], PermissionTypeSet]]
    ] = {
        Role.APP_ADMIN: {
            (command.IdentifierIssuerCrudCommand, PermissionTypeSet.CU),
            (command.UserCrudCommand, PermissionTypeSet.R),
            (command.UserInvitationCrudCommand, PermissionTypeSet.CRD),
            (command.InviteUserCommand, PermissionTypeSet.E),
            (command.UpdateUserCommand, PermissionTypeSet.E),
            (command.OutageCrudCommand, PermissionTypeSet.CRUD),
            (command.DataCollectionCrudCommand, PermissionTypeSet.CU),
            (command.DataCollectionSetCrudCommand, PermissionTypeSet.CRUD),
            (command.DataCollectionSetMemberCrudCommand, PermissionTypeSet.CRUD),
        },
        Role.METADATA_ADMIN: {
            # organization
            # seq.metadata CRUD commands
            (command.AlignmentProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.AssemblyProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.AstProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.RefSnpCrudCommand, PermissionTypeSet.CRU),
            (command.SnpDetectionProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.RefSnpSetCrudCommand, PermissionTypeSet.CRU),
            (command.RefSnpSetMemberCrudCommand, PermissionTypeSet.CRU),
            (command.LibraryPrepProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.LocusCrudCommand, PermissionTypeSet.CRU),
            (command.LocusDetectionProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.LocusSetCrudCommand, PermissionTypeSet.CRU),
            (command.LocusSetMemberCrudCommand, PermissionTypeSet.CRU),
            (command.RefAlleleCrudCommand, PermissionTypeSet.CRU),
            (command.PcrProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.RefSeqCrudCommand, PermissionTypeSet.CRU),
            (command.SeqCategoryCrudCommand, PermissionTypeSet.CRU),
            (command.SeqCategorySetCrudCommand, PermissionTypeSet.CRU),
            (command.SeqClassificationProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.SeqDistanceProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.SubtypingSchemeCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonLocusLinkCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonSetCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonSetMemberCrudCommand, PermissionTypeSet.CRU),
            (command.TreeAlgorithmClassCrudCommand, PermissionTypeSet.CRU),
            (command.TreeAlgorithmCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonomyProtocolCrudCommand, PermissionTypeSet.CRU),
        },
        Role.ORG_USER: {
            # organization
            (command.DataCollectionCrudCommand, PermissionTypeSet.R),
            # seq.persistable CRUD commands
            (command.AlleleCrudCommand, PermissionTypeSet.CRUD),
            (command.AlleleAlignmentCrudCommand, PermissionTypeSet.CRUD),
            (command.SampleCrudCommand, PermissionTypeSet.CRUD),
            (command.ReadSetCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqCrudCommand, PermissionTypeSet.CRUD),
            (command.AlleleProfileCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqAlignmentCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqTaxonomyCrudCommand, PermissionTypeSet.CRUD),
            (command.PcrMeasurementCrudCommand, PermissionTypeSet.CRUD),
            (command.AstMeasurementCrudCommand, PermissionTypeSet.CRUD),
            (command.AstPredictionCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqDistanceCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqClassificationCrudCommand, PermissionTypeSet.CRUD),
            (command.SnpProfileCrudCommand, PermissionTypeSet.CRUD),
            # seq.metadata CRUD commands
            (command.AlignmentProtocolCrudCommand, PermissionTypeSet.R),
            (command.AssemblyProtocolCrudCommand, PermissionTypeSet.R),
            (command.AstProtocolCrudCommand, PermissionTypeSet.R),
            (command.RefSnpCrudCommand, PermissionTypeSet.R),
            (command.SnpDetectionProtocolCrudCommand, PermissionTypeSet.R),
            (command.RefSnpSetCrudCommand, PermissionTypeSet.R),
            (command.RefSnpSetMemberCrudCommand, PermissionTypeSet.R),
            (command.LibraryPrepProtocolCrudCommand, PermissionTypeSet.R),
            (command.LocusCrudCommand, PermissionTypeSet.R),
            (command.LocusDetectionProtocolCrudCommand, PermissionTypeSet.R),
            (command.LocusSetCrudCommand, PermissionTypeSet.R),
            (command.LocusSetMemberCrudCommand, PermissionTypeSet.R),
            (command.PcrProtocolCrudCommand, PermissionTypeSet.R),
            (command.RefSeqCrudCommand, PermissionTypeSet.R),
            (command.SeqCategoryCrudCommand, PermissionTypeSet.R),
            (command.SeqCategorySetCrudCommand, PermissionTypeSet.R),
            (command.SeqClassificationProtocolCrudCommand, PermissionTypeSet.R),
            (command.SeqDistanceProtocolCrudCommand, PermissionTypeSet.R),
            (command.SubtypingSchemeCrudCommand, PermissionTypeSet.R),
            (command.TaxonCrudCommand, PermissionTypeSet.R),
            (command.TaxonLocusLinkCrudCommand, PermissionTypeSet.R),
            (command.TaxonSetCrudCommand, PermissionTypeSet.R),
            (command.TaxonSetMemberCrudCommand, PermissionTypeSet.R),
            (command.TreeAlgorithmClassCrudCommand, PermissionTypeSet.R),
            (command.TreeAlgorithmCrudCommand, PermissionTypeSet.R),
            (command.TaxonomyProtocolCrudCommand, PermissionTypeSet.R),
            # seq non-CRUD commands
            (command.RetrievePhylogeneticTreeCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteAlleleProfileCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteSnpProfileCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteContigCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteSampleCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteSeqCommand, PermissionTypeSet.E),
        },
        Role.GUEST: set(),
    }

    # Tree hierarchy of roles: each role can do everything the roles below it can do.
    # Hierarchy described here per role with union of all roles below it.
    ROLE_HIERARCHY: dict[Role, set[Role]] = {
        Role.ROOT: {
            Role.APP_ADMIN,
            Role.METADATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        },
        Role.APP_ADMIN: {
            Role.METADATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        },
        Role.METADATA_ADMIN: {Role.GUEST},
        Role.ORG_USER: {Role.GUEST},
        Role.GUEST: set(),
    }

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS
    )
