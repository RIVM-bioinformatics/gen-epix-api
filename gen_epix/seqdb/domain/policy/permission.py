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
            (command.LocusCrudCommand, PermissionTypeSet.CRU),
            (command.LocusCodeMapCrudCommand, PermissionTypeSet.CRUD),
            (command.LocusSetCrudCommand, PermissionTypeSet.CRU),
            (command.ProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.ProtocolSetCrudCommand, PermissionTypeSet.CRU),
            (command.ProtocolSetMemberCrudCommand, PermissionTypeSet.CRU),
            (command.RefAlleleCrudCommand, PermissionTypeSet.CR),
            (command.RefSeqCrudCommand, PermissionTypeSet.CR),
            (command.SeqCategoryCrudCommand, PermissionTypeSet.CRU),
            (command.SeqCategorySetCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonSetCrudCommand, PermissionTypeSet.CRU),
            (command.TaxonSetMemberCrudCommand, PermissionTypeSet.CRU),
            (command.TreeAlgorithmClassCrudCommand, PermissionTypeSet.CRU),
            (command.TreeAlgorithmCrudCommand, PermissionTypeSet.CRU),
        },
        Role.ORG_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.ORG_ADMIN] | set(),
        Role.ORG_USER: COMMON_ROLE_PERMISSION_SETS[Role.ORG_USER]
        | {
            (command.AlleleCrudCommand, PermissionTypeSet.CRUD),
            (command.AstMeasurementCrudCommand, PermissionTypeSet.CRUD),
            (command.AstPredictionCrudCommand, PermissionTypeSet.CRUD),
            (command.CalculateSeqDistancesForNewProfilesCommand, PermissionTypeSet.E),
            (command.UpdateSeqDistancesCommand, PermissionTypeSet.E),
            (command.CreateFileCommand, PermissionTypeSet.E),
            (command.FileCrudCommand, PermissionTypeSet.CRD),
            (command.LocusCrudCommand, PermissionTypeSet.R),
            (command.SeqProfileCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqProfileIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.LocusSetCrudCommand, PermissionTypeSet.R),
            (command.PcrMeasurementCrudCommand, PermissionTypeSet.CRUD),
            (command.ProtocolCrudCommand, PermissionTypeSet.R),
            (command.ReadSetCrudCommand, PermissionTypeSet.CRUD),
            (command.ReadSetIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.RefSeqCrudCommand, PermissionTypeSet.R),
            (command.CalculatePhylogeneticTreeCommand, PermissionTypeSet.E),
            (command.RetrieveBestSeqPerSampleCommand, PermissionTypeSet.E),
            (command.RetrieveBestSeqProfilePerSampleCommand, PermissionTypeSet.E),
            (command.RetrieveSampleIdentifiersByIdCommand, PermissionTypeSet.E),
            (command.RetrieveSamplesByIdCommand, PermissionTypeSet.E),
            (command.RetrieveSamplesByQueryCommand, PermissionTypeSet.E),
            (command.RetrieveSeqDistanceLastModifiedCommand, PermissionTypeSet.E),
            (command.RetrieveSeqFastaCommand, PermissionTypeSet.E),
            (command.RetrieveSimilarProfilesCommand, PermissionTypeSet.E),
            (command.SampleCrudCommand, PermissionTypeSet.CRUD),
            (command.SampleDataCollectionLinkCrudCommand, PermissionTypeSet.CRUD),
            (command.SampleIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqCategoryCrudCommand, PermissionTypeSet.R),
            (command.SeqCategorySetCrudCommand, PermissionTypeSet.R),
            (command.SeqClassificationCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqDistanceCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqTaxonomyCrudCommand, PermissionTypeSet.CRUD),
            (command.TaxonCrudCommand, PermissionTypeSet.R),
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
