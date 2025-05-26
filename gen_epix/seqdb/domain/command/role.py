from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.enum import Role


class RoleGenerator:

    ROLE_PERMISSIONS = {
        Role.ADMIN: {  # type: ignore
            # organization
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
        Role.REFDATA_ADMIN: {  # type: ignore
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
        Role.DATA_WRITER: {  # type: ignore
            # seq.persistable CRUD commands
            (command.AlleleCrudCommand, PermissionTypeSet.CUD),
            (command.AlleleAlignmentCrudCommand, PermissionTypeSet.CUD),
            (command.SampleCrudCommand, PermissionTypeSet.CUD),
            (command.ReadSetCrudCommand, PermissionTypeSet.CUD),
            (command.SeqCrudCommand, PermissionTypeSet.CUD),
            (command.AlleleProfileCrudCommand, PermissionTypeSet.CUD),
            (command.SeqAlignmentCrudCommand, PermissionTypeSet.CUD),
            (command.SeqTaxonomyCrudCommand, PermissionTypeSet.CUD),
            (command.PcrMeasurementCrudCommand, PermissionTypeSet.CUD),
            (command.AstMeasurementCrudCommand, PermissionTypeSet.CUD),
            (command.AstPredictionCrudCommand, PermissionTypeSet.CUD),
            (command.SeqDistanceCrudCommand, PermissionTypeSet.CUD),
            (command.SeqClassificationCrudCommand, PermissionTypeSet.CUD),
            (command.SnpProfileCrudCommand, PermissionTypeSet.CUD),
        },
        Role.DATA_READER: {  # type: ignore
            # organization
            (command.DataCollectionCrudCommand, PermissionTypeSet.R),
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
            # seq CRUD commands
            (command.AlleleCrudCommand, PermissionTypeSet.R),
            (command.AlleleAlignmentCrudCommand, PermissionTypeSet.R),
            (command.SampleCrudCommand, PermissionTypeSet.R),
            (command.ReadSetCrudCommand, PermissionTypeSet.R),
            (command.SeqCrudCommand, PermissionTypeSet.R),
            (command.AlleleProfileCrudCommand, PermissionTypeSet.R),
            (command.SeqAlignmentCrudCommand, PermissionTypeSet.R),
            (command.SeqTaxonomyCrudCommand, PermissionTypeSet.R),
            (command.PcrMeasurementCrudCommand, PermissionTypeSet.R),
            (command.AstMeasurementCrudCommand, PermissionTypeSet.R),
            (command.AstPredictionCrudCommand, PermissionTypeSet.R),
            (command.SeqDistanceCrudCommand, PermissionTypeSet.R),
            (command.SeqClassificationCrudCommand, PermissionTypeSet.R),
            (command.SnpProfileCrudCommand, PermissionTypeSet.R),
            # seq non-CRUD commands
            (command.RetrievePhylogeneticTreeCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteAlleleProfileCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteSnpProfileCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteContigCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteSampleCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteSeqCommand, PermissionTypeSet.E),
        },
        Role.GUEST: set(),  # type: ignore
    }

    # Tree hierarchy of roles: each role can do everything the roles below it can do.
    # Hierarchy described here per role with union of all roles below it.
    ROLE_HIERARCHY = {
        Role.ROOT: {  # type: ignore
            Role.ADMIN,
            Role.REFDATA_ADMIN,
            Role.DATA_READER,
            Role.DATA_WRITER,
            Role.GUEST,
        },
        Role.ADMIN: {  # type: ignore
            Role.REFDATA_ADMIN,
            Role.DATA_READER,
            Role.DATA_WRITER,
            Role.GUEST,
        },
        Role.REFDATA_ADMIN: {Role.GUEST},  # type: ignore
        Role.DATA_READER: {Role.GUEST},  # type: ignore
        Role.DATA_WRITER: {Role.DATA_READER, Role.GUEST},  # type: ignore
        Role.GUEST: set(),  # type: ignore
    }

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSIONS
    )
