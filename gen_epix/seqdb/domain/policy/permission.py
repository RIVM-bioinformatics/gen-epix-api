from typing import Type

from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.policy import (
    map_common_role_hierarchy,
    map_common_role_permission_sets,
)
from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.enum import Role

COMMON_ROLE_MAP = {
    CommonRole.ROOT: Role.ROOT,
    CommonRole.APP_ADMIN: Role.APP_ADMIN,
    CommonRole.REFDATA_ADMIN: Role.REFDATA_ADMIN,
    CommonRole.ORG_ADMIN: Role.ORG_ADMIN,
    CommonRole.ORG_USER: Role.ORG_USER,
    CommonRole.GUEST: Role.GUEST,
}


class RoleGenerator:

    COMMON_ROLE_PERMISSION_SETS = map_common_role_permission_sets(
        COMMON_ROLE_MAP, command.COMMON_COMMAND_MAP  # type: ignore[arg-type]
    )

    ROLE_PERMISSION_SETS: dict[
        Role, set[tuple[Type[command.Command], PermissionTypeSet]]
    ] = {
        Role.APP_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.APP_ADMIN] | set(),
        Role.REFDATA_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.REFDATA_ADMIN]
        | {
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
        Role.ORG_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.ORG_ADMIN] | set(),
        Role.ORG_USER: COMMON_ROLE_PERMISSION_SETS[Role.ORG_USER]
        | {
            # seq.persistable CRUD commands
            (command.AlleleCrudCommand, PermissionTypeSet.CRUD),
            (command.AlleleAlignmentCrudCommand, PermissionTypeSet.CRUD),
            (command.SampleCrudCommand, PermissionTypeSet.CRUD),
            (command.ReadSetCrudCommand, PermissionTypeSet.CRUD),
            (command.SeqCrudCommand, PermissionTypeSet.CRUD),
            (command.RawSeqCrudCommand, PermissionTypeSet.CRUD),
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
        Role.GUEST: COMMON_ROLE_PERMISSION_SETS[Role.GUEST] | set(),
    }

    ROLE_HIERARCHY: dict[Role, set[Role]] = map_common_role_hierarchy(COMMON_ROLE_MAP)  # type: ignore[assignment,arg-type]

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS  # type: ignore[arg-type]
    )
