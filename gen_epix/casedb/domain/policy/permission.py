from typing import Type

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.enum import Role
from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService


class RoleGenerator:

    ROLE_PERMISSION_SETS: dict[
        Role, set[tuple[Type[command.Command], PermissionTypeSet]]
    ] = {
        # TODO: remove UPDATE from association objects that do not have properties of their own such as CaseTypeSetMember
        Role.APP_ADMIN: {
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
                command.DataCollectionSetDataCollectionUpdateAssociationCommand,  # type: ignore[arg-type]
                PermissionTypeSet.E,
            ),
            # abac
            (command.OrganizationAdminPolicyCrudCommand, PermissionTypeSet.CUD),
            (command.OrganizationAccessCasePolicyCrudCommand, PermissionTypeSet.CUD),
            (
                command.OrganizationShareCasePolicyCrudCommand,
                PermissionTypeSet.CUD,
            ),
            # organization
            (command.OrganizationCrudCommand, PermissionTypeSet.CU),
            (
                command.OrganizationSetOrganizationUpdateAssociationCommand,  # type: ignore[arg-type]
                PermissionTypeSet.E,
            ),
            (command.DataCollectionCrudCommand, PermissionTypeSet.CU),
            (
                command.DataCollectionSetCrudCommand,
                PermissionTypeSet.CRUD,
            ),  # TODO: READ permission can be set broader once this entity is actually used
            (
                command.DataCollectionSetMemberCrudCommand,
                PermissionTypeSet.CRUD,
            ),  # TODO: READ permission can be set broader once this entity is actually used
            # system
            (command.OutageCrudCommand, PermissionTypeSet.CRUD),
        },
        Role.METADATA_ADMIN: {
            # case
            (command.GeneticDistanceProtocolCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeColCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeColSetCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeColSetMemberCrudCommand, PermissionTypeSet.CRUD),
            (command.CaseTypeCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeSetCaseTypeUpdateAssociationCommand, PermissionTypeSet.E),  # type: ignore[arg-type]
            (
                command.CaseTypeColSetCaseTypeColUpdateAssociationCommand,  # type: ignore[arg-type]
                PermissionTypeSet.E,
            ),
            (command.CaseTypeSetCategoryCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeSetCrudCommand, PermissionTypeSet.CRU),
            (command.CaseTypeSetMemberCrudCommand, PermissionTypeSet.CRUD),
            (command.ColCrudCommand, PermissionTypeSet.CRU),
            (command.DimCrudCommand, PermissionTypeSet.CRU),
            # ontology
            (command.ConceptCrudCommand, PermissionTypeSet.CRU),
            (command.ConceptSetConceptUpdateAssociationCommand, PermissionTypeSet.E),  # type: ignore[arg-type]
            (command.ConceptSetCrudCommand, PermissionTypeSet.CRU),
            (command.ConceptSetMemberCrudCommand, PermissionTypeSet.CRUD),
            (command.DiseaseCrudCommand, PermissionTypeSet.CRU),
            (
                command.DiseaseEtiologicalAgentUpdateAssociationCommand,  # type: ignore[arg-type]
                PermissionTypeSet.E,
            ),
            (command.EtiologicalAgentCrudCommand, PermissionTypeSet.CRU),
            (command.EtiologyCrudCommand, PermissionTypeSet.CRU),
            (command.RegionCrudCommand, PermissionTypeSet.CRU),
            (command.RegionSetCrudCommand, PermissionTypeSet.CRU),
            (command.RegionSetShapeCrudCommand, PermissionTypeSet.CRUD),
            # organization
            (command.UserCrudCommand, PermissionTypeSet.R),
            (command.DataCollectionCrudCommand, PermissionTypeSet.R),
        },
        Role.ORG_ADMIN: {
            # organization
            (command.InviteUserCommand, PermissionTypeSet.E),
            (command.UpdateUserCommand, PermissionTypeSet.E),
            (command.UserInvitationCrudCommand, PermissionTypeSet.CRD),
            # abac
            (command.UserAccessCasePolicyCrudCommand, PermissionTypeSet.CUD),
            (command.UserShareCasePolicyCrudCommand, PermissionTypeSet.CUD),
        },
        Role.ORG_USER: {
            # case
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
            (command.CaseSetCreateCommand, PermissionTypeSet.E),
            (command.CasesCreateCommand, PermissionTypeSet.E),
            (command.CaseSetCrudCommand, PermissionTypeSet.RUD),
            (command.CaseSetMemberCrudCommand, PermissionTypeSet.CRUD),
            (command.RetrieveCaseSetStatsCommand, PermissionTypeSet.E),
            (command.RetrieveCaseTypeStatsCommand, PermissionTypeSet.E),
            (command.RetrieveCasesByIdCommand, PermissionTypeSet.E),
            (command.RetrieveCasesByQueryCommand, PermissionTypeSet.E),
            (command.RetrieveCompleteCaseTypeCommand, PermissionTypeSet.E),
            (command.RetrieveCaseSetRightsCommand, PermissionTypeSet.E),
            (command.RetrieveCaseRightsCommand, PermissionTypeSet.E),
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
            # organization
            (command.UserCrudCommand, PermissionTypeSet.R),
            (command.DataCollectionCrudCommand, PermissionTypeSet.R),
            (command.OrganizationCrudCommand, PermissionTypeSet.R),
            (command.RetrieveOrganizationAdminNameEmailsCommand, PermissionTypeSet.E),
            (command.RetrieveOrganizationContactCommand, PermissionTypeSet.E),
            (command.UpdateUserOwnOrganizationCommand, PermissionTypeSet.E),
            # abac
            (command.OrganizationAdminPolicyCrudCommand, PermissionTypeSet.R),
            (command.OrganizationAccessCasePolicyCrudCommand, PermissionTypeSet.R),
            (command.OrganizationShareCasePolicyCrudCommand, PermissionTypeSet.R),
            (command.UserAccessCasePolicyCrudCommand, PermissionTypeSet.R),
            (command.UserShareCasePolicyCrudCommand, PermissionTypeSet.R),
            # seq
            (command.RetrieveAlleleProfileCommand, PermissionTypeSet.E),
            (command.RetrieveGeneticSequenceByCaseCommand, PermissionTypeSet.E),
            (command.RetrievePhylogeneticTreeByCasesCommand, PermissionTypeSet.E),
            (command.RetrievePhylogeneticTreeBySequencesCommand, PermissionTypeSet.E),
        },
        Role.GUEST: {
            # organization
            (command.RetrieveOwnPermissionsCommand, PermissionTypeSet.E),
            # system
            (command.RetrieveOutagesCommand, PermissionTypeSet.E),
        },
    }

    # Tree hierarchy of roles: each role can do everything the roles below it can do.
    # Hierarchy described here per role with union of all roles below it.
    ROLE_HIERARCHY: dict[Role, set[Role]] = {
        Role.ROOT: {
            Role.APP_ADMIN,
            Role.ORG_ADMIN,
            Role.METADATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        },
        Role.APP_ADMIN: {
            Role.ORG_ADMIN,
            Role.METADATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        },
        Role.ORG_ADMIN: {
            Role.ORG_USER,
            Role.GUEST,
        },
        Role.METADATA_ADMIN: {Role.GUEST},
        Role.ORG_USER: {Role.GUEST},
        Role.GUEST: set(),
    }

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS  # type: ignore[arg-type]
    )
