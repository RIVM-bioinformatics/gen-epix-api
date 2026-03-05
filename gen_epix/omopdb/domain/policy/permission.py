from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.policy import \
    RoleGenerator as CommonRoleGenerator
from gen_epix.fastapp.enum import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService
from gen_epix.omopdb.domain import command
from gen_epix.omopdb.domain.enum import Role


class RoleGenerator(CommonRoleGenerator):

    COMMON_ROLE_ENUM_MAP = {x: Role[x.name] for x in CommonRole}

    EXTRA_ROLE_SET_MAP = {}

    COMMON_ROLE_PERMISSION_SETS = (
        CommonRoleGenerator.map_from_common_role_permission_sets(
            COMMON_ROLE_ENUM_MAP, command.COMMON_COMMAND_MAP
        )
    )

    ROLE_PERMISSION_SETS = {
        # TODO: fill in permissions
        Role.APP_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.APP_ADMIN]
        | {
            (command.ConceptClassCrudCommand, PermissionTypeSet.CRU),
            (command.DomainCrudCommand, PermissionTypeSet.CRU),
            (command.VocabularyCrudCommand, PermissionTypeSet.CRU),
        },
        Role.REFDATA_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.REFDATA_ADMIN]
        | {
            (command.ConceptAncestorCrudCommand, PermissionTypeSet.CRU),
            (command.ConceptCrudCommand, PermissionTypeSet.CRU),
            (command.ConceptRelationshipCrudCommand, PermissionTypeSet.CRU),
            (command.ConceptSynonymCrudCommand, PermissionTypeSet.CRU),
            (command.DrugStrengthCrudCommand, PermissionTypeSet.CRU),
        },
        Role.ORG_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.ORG_ADMIN] | set(),
        Role.ORG_USER: COMMON_ROLE_PERMISSION_SETS[Role.ORG_USER]
        | {
            (command.CareSiteCrudCommand, PermissionTypeSet.CRUD),
            (command.CdmSourceCrudCommand, PermissionTypeSet.CRUD),
            (command.CohortCrudCommand, PermissionTypeSet.CRUD),
            (command.CohortDefinitionCrudCommand, PermissionTypeSet.CRUD),
            (command.ConditionEraCrudCommand, PermissionTypeSet.CRUD),
            (command.ConditionOccurrenceCrudCommand, PermissionTypeSet.CRUD),
            (command.CostCrudCommand, PermissionTypeSet.CRUD),
            (command.DeathCrudCommand, PermissionTypeSet.CRUD),
            (command.DeviceExposureCrudCommand, PermissionTypeSet.CRUD),
            (command.DoseEraCrudCommand, PermissionTypeSet.CRUD),
            (command.DrugEraCrudCommand, PermissionTypeSet.CRUD),
            (command.DrugExposureCrudCommand, PermissionTypeSet.CRUD),
            (command.EpisodeCrudCommand, PermissionTypeSet.CRUD),
            (command.EpisodeEventCrudCommand, PermissionTypeSet.CRUD),
            (command.FactRelationshipCrudCommand, PermissionTypeSet.CRUD),
            (command.LocationCrudCommand, PermissionTypeSet.CRUD),
            (command.MeasurementCrudCommand, PermissionTypeSet.CRUD),
            (command.MeasurementRelationCrudCommand, PermissionTypeSet.CRUD),
            (command.MetadataCrudCommand, PermissionTypeSet.CRUD),
            (command.NoteCrudCommand, PermissionTypeSet.CRUD),
            (command.NoteNlpCrudCommand, PermissionTypeSet.CRUD),
            (command.ObservationCrudCommand, PermissionTypeSet.CRUD),
            (command.ObservationPeriodCrudCommand, PermissionTypeSet.CRUD),
            (command.PayerPlanPeriodCrudCommand, PermissionTypeSet.CRUD),
            (command.PersonCrudCommand, PermissionTypeSet.CRUD),
            (command.ProcedureOccurrenceCrudCommand, PermissionTypeSet.CRUD),
            (command.ProviderCrudCommand, PermissionTypeSet.CRUD),
            (command.RelationshipCrudCommand, PermissionTypeSet.CRUD),
            (command.SourceToConceptMapCrudCommand, PermissionTypeSet.CRUD),
            (command.SpecimenCrudCommand, PermissionTypeSet.CRUD),
            (command.VisitDetailCrudCommand, PermissionTypeSet.CRUD),
            (command.VisitOccurrenceCrudCommand, PermissionTypeSet.CRUD),
        },
        Role.GUEST: COMMON_ROLE_PERMISSION_SETS[Role.GUEST] | set(),
    }

    ROLE_HIERARCHY = CommonRoleGenerator.map_from_common_role_hierarchy(
        COMMON_ROLE_ENUM_MAP
    )

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS
    )
