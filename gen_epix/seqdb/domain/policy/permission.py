from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.policy import RoleGenerator as CommonRoleGenerator
from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.enum import Role


class RoleGenerator(CommonRoleGenerator):

    COMMON_ROLE_ENUM_MAP = {x: Role[x.name] for x in CommonRole}

    EXTRA_ROLE_SET_MAP = {}

    COMMON_ROLE_PERMISSION_SETS = (
        CommonRoleGenerator.map_from_common_role_permission_sets(
            COMMON_ROLE_ENUM_MAP, command.COMMON_COMMAND_MAP
        )
    )

    ROLE_PERMISSION_SETS = {
        Role.APP_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.APP_ADMIN] | set(),
        Role.REFDATA_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.REFDATA_ADMIN]
        | {
            (command.AlignmentProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.AssemblyProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.AstProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.KmerDetectionProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.LocusCrudCommand, PermissionTypeSet.CRU),
            (command.LocusCodeMapCrudCommand, PermissionTypeSet.CRUD),
            (command.LocusDetectionProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.LocusSetCrudCommand, PermissionTypeSet.CRU),
            (command.MlvaDetectionProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.PcrProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.RefAlleleCrudCommand, PermissionTypeSet.CR),
            (command.RefSeqCrudCommand, PermissionTypeSet.CR),
            (command.RefSnpCrudCommand, PermissionTypeSet.CRU),
            (command.RefSnpSetCrudCommand, PermissionTypeSet.CRU),
            (command.RefSnpSetMemberCrudCommand, PermissionTypeSet.CRU),
            (command.SeqCategoryCrudCommand, PermissionTypeSet.CRU),
            (command.SeqCategorySetCrudCommand, PermissionTypeSet.CRU),
            (command.SeqClassificationProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.SeqDistanceProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.SequencingProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.SnpDetectionProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonomyProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonSetCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonSetMemberCrudCommand, PermissionTypeSet.CRU),
            (command.TreeAlgorithmClassCrudCommand, PermissionTypeSet.CRU),
            (command.TreeAlgorithmCrudCommand, PermissionTypeSet.CRU),
        },
        Role.ORG_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.ORG_ADMIN] | set(),
        Role.ORG_USER: COMMON_ROLE_PERMISSION_SETS[Role.ORG_USER]
        | {
            (command.AlignmentProtocolCrudCommand, PermissionTypeSet.R),
            (command.AlleleAlignmentCrudCommand, PermissionTypeSet.CRUD),
            (command.AlleleCrudCommand, PermissionTypeSet.CRUD),
            (command.AlleleProfileCrudCommand, PermissionTypeSet.CRUD),
            (command.AssemblyProtocolCrudCommand, PermissionTypeSet.R),
            (command.AstMeasurementCrudCommand, PermissionTypeSet.CRUD),
            (command.AstPredictionCrudCommand, PermissionTypeSet.CRUD),
            (command.AstProtocolCrudCommand, PermissionTypeSet.R),
            (command.CreateFileCommand, PermissionTypeSet.E),
            (command.FileCrudCommand, PermissionTypeSet.CRD),
            (command.KmerProfileCrudCommand, PermissionTypeSet.CRUD),
            (command.LocusCrudCommand, PermissionTypeSet.R),
            (command.LocusDetectionProtocolCrudCommand, PermissionTypeSet.R),
            (command.LocusProfileCrudCommand, PermissionTypeSet.CRUD),
            (command.LocusSetCrudCommand, PermissionTypeSet.R),
            (command.MlvaProfileCrudCommand, PermissionTypeSet.CRUD),
            (command.PcrMeasurementCrudCommand, PermissionTypeSet.CRUD),
            (command.PcrProtocolCrudCommand, PermissionTypeSet.R),
            (command.ReadSetCrudCommand, PermissionTypeSet.CRUD),
            (command.RefSeqCrudCommand, PermissionTypeSet.R),
            (command.RefSnpCrudCommand, PermissionTypeSet.R),
            (command.RefSnpSetCrudCommand, PermissionTypeSet.R),
            (command.RefSnpSetMemberCrudCommand, PermissionTypeSet.R),
            (command.RetrievePhylogeneticTreeCommand, PermissionTypeSet.E),
            (command.RetrieveSeqFastaCommand, PermissionTypeSet.E),
            (command.SampleCrudCommand, PermissionTypeSet.CRUD),
            (command.SampleDataCollectionLinkCrudCommand, PermissionTypeSet.CRUD),
            (command.SampleIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqAlignmentCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqCategoryCrudCommand, PermissionTypeSet.R),
            (command.SeqCategorySetCrudCommand, PermissionTypeSet.R),
            (command.SeqClassificationCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqClassificationProtocolCrudCommand, PermissionTypeSet.R),
            (command.SeqCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqDistanceCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqDistanceProtocolCrudCommand, PermissionTypeSet.R),
            (command.SeqTaxonomyCrudCommand, PermissionTypeSet.CRUD),
            (command.SequencingProtocolCrudCommand, PermissionTypeSet.R),
            (command.SnpDetectionProtocolCrudCommand, PermissionTypeSet.R),
            (command.SnpProfileCrudCommand, PermissionTypeSet.CRUD),
            (command.TaxonCrudCommand, PermissionTypeSet.R),
            (command.TaxonomyProtocolCrudCommand, PermissionTypeSet.R),
            (command.TaxonSetCrudCommand, PermissionTypeSet.R),
            (command.TaxonSetMemberCrudCommand, PermissionTypeSet.R),
            (command.TreeAlgorithmClassCrudCommand, PermissionTypeSet.R),
            (command.TreeAlgorithmCrudCommand, PermissionTypeSet.R),
            (command.UploadSamplesCommand, PermissionTypeSet.E),
        },
        Role.GUEST: COMMON_ROLE_PERMISSION_SETS[Role.GUEST] | set(),
    }

    ROLE_HIERARCHY = CommonRoleGenerator.map_from_common_role_hierarchy(
        COMMON_ROLE_ENUM_MAP
    )

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS
    )
