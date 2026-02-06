from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.enum import Role
from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.policy import RoleGenerator as CommonRoleGenerator
from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService


class RoleGenerator(CommonRoleGenerator):

    COMMON_ROLE_ENUM_MAP = {x: Role[x.name] for x in CommonRole}

    EXTRA_ROLE_SET_MAP = {}

    COMMON_ROLE_PERMISSION_SETS = (
        CommonRoleGenerator.map_from_common_role_permission_sets(
            COMMON_ROLE_ENUM_MAP, command.COMMON_COMMAND_MAP
        )
    )

    ROLE_PERMISSION_SETS = {
        # TODO: remove UPDATE from association objects that do not have properties of their own such as CaseTypeSetMember
        Role.APP_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.APP_ADMIN]
        | {
            # case
            (command.CaseSetCrudCommand, PermissionTypeSet.C),
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
            # case with impact on abac
            # Create/update has no impact on abac
            (command.CaseTypeSetMemberCrudCommand, PermissionTypeSet.CUD),
            (command.CaseTypeSetCaseTypeUpdateAssociationCommand, PermissionTypeSet.E),
            (
                command.CaseTypeColSetCrudCommand,
                PermissionTypeSet.D,
            ),  # Create/update has no impact on abac
            (command.CaseTypeColSetMemberCrudCommand, PermissionTypeSet.CUD),
            (
                command.CaseTypeColSetCaseTypeColUpdateAssociationCommand,
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
            (command.CaseSetCategoryCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeColCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeDimCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeSetCategoryCrudCommand, PermissionTypeSet.CRU),
            (
                command.CaseTypeSetCrudCommand,
                PermissionTypeSet.CRU,
            ),  # Create/update has no impact on abac
            (command.CaseTypeColSetMemberCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeSetMemberCrudCommand, PermissionTypeSet.R),
            (
                command.CaseTypeColSetCrudCommand,
                PermissionTypeSet.CRU,
            ),  # Create/update has no impact on abac
            (command.ColCrudCommand, PermissionTypeSet.CRU),
            (command.DimCrudCommand, PermissionTypeSet.CRU),
            # ontology
            (command.ConceptCrudCommand, PermissionTypeSet.CRU),
            (command.ConceptSetCrudCommand, PermissionTypeSet.CRU),
            (command.ConceptRelationCrudCommand, PermissionTypeSet.CRU),
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
            (command.CaseDataCollectionLinkCrudCommand, PermissionTypeSet.CRUD),
            (command.CaseSetCategoryCrudCommand, PermissionTypeSet.R),
            (command.CaseSetCrudCommand, PermissionTypeSet.RUD),
            (command.CaseSetDataCollectionLinkCrudCommand, PermissionTypeSet.CRUD),
            (command.CaseSetMemberCrudCommand, PermissionTypeSet.CRUD),
            (command.CaseSetStatusCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeColCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeColSetCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeColSetMemberCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeDimCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeSetCategoryCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeSetCrudCommand, PermissionTypeSet.R),
            (command.CaseTypeSetMemberCrudCommand, PermissionTypeSet.R),
            (command.ColCrudCommand, PermissionTypeSet.R),
            (command.CreateCaseSetCommand, PermissionTypeSet.E),
            (command.CreateFileForReadSetCommand, PermissionTypeSet.E),
            (command.CreateFileForSeqCommand, PermissionTypeSet.E),
            (command.DimCrudCommand, PermissionTypeSet.R),
            (command.GeneticDistanceProtocolCrudCommand, PermissionTypeSet.R),
            (command.RetrieveAssemblyProtocolsCommand, PermissionTypeSet.E),
            (command.RetrieveCaseRightsCommand, PermissionTypeSet.E),
            (command.RetrieveCaseSetRightsCommand, PermissionTypeSet.E),
            (command.RetrieveCaseStatsCommand, PermissionTypeSet.E),
            (command.RetrieveCasesByIdCommand, PermissionTypeSet.E),
            (command.RetrieveCasesByQueryCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteCaseTypeCommand, PermissionTypeSet.E),
            (command.RetrieveSequencingProtocolsCommand, PermissionTypeSet.E),
            (command.TreeAlgorithmClassCrudCommand, PermissionTypeSet.R),
            (command.TreeAlgorithmCrudCommand, PermissionTypeSet.R),
            (command.UploadCasesCommand, PermissionTypeSet.E),
            # ontology
            (command.ConceptCrudCommand, PermissionTypeSet.R),
            (command.ConceptSetCrudCommand, PermissionTypeSet.R),
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
            (command.RetrieveGeneticSequenceFastaByCaseCommand, PermissionTypeSet.E),
            (command.RetrievePhylogeneticTreeByCasesCommand, PermissionTypeSet.E),
            (command.RetrievePhylogeneticTreeBySequencesCommand, PermissionTypeSet.E),
        },
        Role.GUEST: COMMON_ROLE_PERMISSION_SETS[Role.GUEST] | set(),
    }

    ROLE_HIERARCHY = CommonRoleGenerator.map_from_common_role_hierarchy(
        COMMON_ROLE_ENUM_MAP
    )

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS  # type: ignore[arg-type]
    )
