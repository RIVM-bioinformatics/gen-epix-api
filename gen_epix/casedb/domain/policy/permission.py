from typing import Type

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.enum import Role
from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.policy import (
    map_common_role_hierarchy,
    map_common_role_permission_sets,
)
from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService

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
        # TODO: remove UPDATE from association objects that do not have properties of their own such as CaseTypeSetMember
        Role.APP_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.APP_ADMIN]
        | {
            # case
            (
                command.CaseSetCrudCommand,
                PermissionTypeSet.C,
            ),  # Other users can only use dedicated command
            (
                command.CaseCrudCommand,
                PermissionTypeSet.C,
            ),  # Other users can only use dedicated command
            (command.CaseTypeCrudCommand, PermissionTypeSet.D),
            (command.CaseSetCategoryCrudCommand, PermissionTypeSet.CU),
            (command.CaseSetStatusCrudCommand, PermissionTypeSet.CU),
            (command.CaseTypeSetCategoryCrudCommand, PermissionTypeSet.D),
            (command.CaseTypeSetCrudCommand, PermissionTypeSet.D),
            (
                command.DataCollectionSetDataCollectionUpdateAssociationCommand,
                PermissionTypeSet.E,
            ),
            # abac
            (command.OrganizationAccessCasePolicyCrudCommand, PermissionTypeSet.CUD),
            (
                command.OrganizationShareCasePolicyCrudCommand,
                PermissionTypeSet.CUD,
            ),
        },
        Role.REFDATA_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.REFDATA_ADMIN]
        | {
            # case
            (command.GeneticDistanceProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeColCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeColSetCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeColSetMemberCrudCommand, PermissionTypeSet.CRUD),
            (command.CaseTypeCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeSetCaseTypeUpdateAssociationCommand, PermissionTypeSet.E),
            (
                command.CaseTypeColSetCaseTypeColUpdateAssociationCommand,
                PermissionTypeSet.E,
            ),
            (command.CaseTypeSetCategoryCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeSetCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeSetMemberCrudCommand, PermissionTypeSet.CRUD),
            (command.ColCrudCommand, PermissionTypeSet.CRU),
            (command.DimCrudCommand, PermissionTypeSet.CRU),
            # ontology
            (command.ConceptCrudCommand, PermissionTypeSet.CRU),
            (command.ConceptSetConceptUpdateAssociationCommand, PermissionTypeSet.E),
            (command.ConceptSetCrudCommand, PermissionTypeSet.CRU),
            (command.ConceptSetMemberCrudCommand, PermissionTypeSet.CRUD),
            (command.DiseaseCrudCommand, PermissionTypeSet.CRU),
            (
                command.DiseaseEtiologicalAgentUpdateAssociationCommand,
                PermissionTypeSet.E,
            ),
            (command.EtiologicalAgentCrudCommand, PermissionTypeSet.CRU),
            (command.EtiologyCrudCommand, PermissionTypeSet.CRU),
            (command.RegionCrudCommand, PermissionTypeSet.CRU),
            (command.RegionSetCrudCommand, PermissionTypeSet.CRU),
            (command.RegionSetShapeCrudCommand, PermissionTypeSet.CRUD),
        },
        Role.ORG_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.ORG_ADMIN]
        | {
            # abac
            (command.UserAccessCasePolicyCrudCommand, PermissionTypeSet.CUD),
            (command.UserShareCasePolicyCrudCommand, PermissionTypeSet.CUD),
        },
        Role.ORG_USER: COMMON_ROLE_PERMISSION_SETS[Role.ORG_USER]
        | {
            # case
            (command.CaseTypeColCrudCommand, PermissionTypeSet.R),
            (command.ColCrudCommand, PermissionTypeSet.R),
            (command.GeneticDistanceProtocolCrudCommand, PermissionTypeSet.R),
            (command.TreeAlgorithmClassCrudCommand, PermissionTypeSet.R),
            (command.TreeAlgorithmCrudCommand, PermissionTypeSet.R),
            (command.CaseSetCategoryCrudCommand, PermissionTypeSet.R),
            (command.CaseSetDataCollectionLinkCrudCommand, PermissionTypeSet.CRUD),
            (command.CaseSetStatusCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeColSetCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeSetCategoryCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeSetCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeColSetMemberCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeSetMemberCrudCommand, PermissionTypeSet.R),
            (
                command.CaseDataCollectionLinkCrudCommand,
                PermissionTypeSet.CRUD,
            ),
            (command.CreateCaseSetCommand, PermissionTypeSet.E),
            (command.CreateCasesCommand, PermissionTypeSet.E),
            (command.CaseSetCrudCommand, PermissionTypeSet.RUD),
            (command.CaseSetMemberCrudCommand, PermissionTypeSet.CRUD),
            (command.RetrieveCaseSetStatsCommand, PermissionTypeSet.E),
            (command.RetrieveCaseTypeStatsCommand, PermissionTypeSet.E),
            (command.RetrieveCasesByIdCommand, PermissionTypeSet.E),
            (command.RetrieveCasesByQueryCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteCaseTypeCommand, PermissionTypeSet.E),
            (command.RetrieveCaseSetRightsCommand, PermissionTypeSet.E),
            (command.RetrieveCaseRightsCommand, PermissionTypeSet.E),
            (command.ValidateCasesCommand, PermissionTypeSet.E),
            # ontology
            (command.ConceptCrudCommand, PermissionTypeSet.R),
            (command.ConceptSetCrudCommand, PermissionTypeSet.R),
            (command.ConceptSetMemberCrudCommand, PermissionTypeSet.R),
            (command.DiseaseCrudCommand, PermissionTypeSet.R),
            (command.EtiologicalAgentCrudCommand, PermissionTypeSet.R),
            (command.EtiologyCrudCommand, PermissionTypeSet.R),
            (command.RegionSetCrudCommand, PermissionTypeSet.R),
            (command.RegionSetShapeCrudCommand, PermissionTypeSet.R),
            (command.RegionCrudCommand, PermissionTypeSet.R),
            # abac
            (command.OrganizationAccessCasePolicyCrudCommand, PermissionTypeSet.R),
            (command.OrganizationShareCasePolicyCrudCommand, PermissionTypeSet.R),
            (command.UserAccessCasePolicyCrudCommand, PermissionTypeSet.R),
            (command.UserShareCasePolicyCrudCommand, PermissionTypeSet.R),
            # seq
            (command.RetrieveAlleleProfileCommand, PermissionTypeSet.E),
            (command.RetrieveGeneticSequenceByCaseCommand, PermissionTypeSet.E),
            (command.RetrieveGeneticSequenceFastaByCaseCommand, PermissionTypeSet.E),
            (command.RetrievePhylogeneticTreeByCasesCommand, PermissionTypeSet.E),
            (command.RetrievePhylogeneticTreeBySequencesCommand, PermissionTypeSet.E),
        },
        Role.GUEST: COMMON_ROLE_PERMISSION_SETS[Role.GUEST] | set(),
    }

    ROLE_HIERARCHY: dict[Role, set[Role]] = map_common_role_hierarchy(COMMON_ROLE_MAP)  # type: ignore[assignment,arg-type]

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS  # type: ignore[arg-type]
    )
