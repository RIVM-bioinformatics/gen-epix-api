"""Generate OmopDB role permissions from shared and OMOP-specific commands."""

from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.policy import RoleGenerator as CommonRoleGenerator
from gen_epix.fastapp.enum import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService
from gen_epix.omopdb.domain import command
from gen_epix.omopdb.domain.enum import Role


class RoleGenerator(CommonRoleGenerator):
    """Build hierarchical OmopDB role permissions for shared and local commands."""

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
            (command.ConditionOccurrenceIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.CostCrudCommand, PermissionTypeSet.CRUD),
            (command.DeathCrudCommand, PermissionTypeSet.CRUD),
            (command.DeathIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.DeviceExposureCrudCommand, PermissionTypeSet.CRUD),
            (command.DeviceExposureIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.DoseEraCrudCommand, PermissionTypeSet.CRUD),
            (command.DrugEraCrudCommand, PermissionTypeSet.CRUD),
            (command.DrugExposureCrudCommand, PermissionTypeSet.CRUD),
            (command.DrugExposureIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.EpisodeCrudCommand, PermissionTypeSet.CRUD),
            (command.EpisodeEventCrudCommand, PermissionTypeSet.CRUD),
            (command.FactRelationshipCrudCommand, PermissionTypeSet.CRUD),
            (command.LocationCrudCommand, PermissionTypeSet.CRUD),
            (command.MeasurementCrudCommand, PermissionTypeSet.CRUD),
            (command.MeasurementIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.MeasurementRelationCrudCommand, PermissionTypeSet.CRUD),
            (command.MeasurementRelationIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.MetadataCrudCommand, PermissionTypeSet.CRUD),
            (command.NoteCrudCommand, PermissionTypeSet.CRUD),
            (command.NoteIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.NoteNlpCrudCommand, PermissionTypeSet.CRUD),
            (command.NoteNlpIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.ObservationCrudCommand, PermissionTypeSet.CRUD),
            (command.ObservationIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.ObservationPeriodCrudCommand, PermissionTypeSet.CRUD),
            (command.ObservationPeriodIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.PayerPlanPeriodCrudCommand, PermissionTypeSet.CRUD),
            (command.PersonCrudCommand, PermissionTypeSet.CRUD),
            (command.PersonIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.ProcedureOccurrenceCrudCommand, PermissionTypeSet.CRUD),
            (command.ProcedureOccurrenceIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.ProviderCrudCommand, PermissionTypeSet.CRUD),
            (command.RelationshipCrudCommand, PermissionTypeSet.CRUD),
            (command.RetrievePersonsByIdCommand, PermissionTypeSet.E),
            (command.RetrievePersonsByQueryCommand, PermissionTypeSet.E),
            (command.RetrieveSpecimenIdsByCohortIdsCommand, PermissionTypeSet.E),
            (command.UploadPersonsCommand, PermissionTypeSet.E),
            (command.SourceToConceptMapCrudCommand, PermissionTypeSet.CRUD),
            (command.SpecimenCrudCommand, PermissionTypeSet.CRUD),
            (command.SpecimenIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.VisitDetailCrudCommand, PermissionTypeSet.CRUD),
            (command.VisitDetailIdentifierCrudCommand, PermissionTypeSet.CRUD),
            (command.VisitOccurrenceCrudCommand, PermissionTypeSet.CRUD),
            (command.VisitOccurrenceIdentifierCrudCommand, PermissionTypeSet.CRUD),
        },
        Role.GUEST: COMMON_ROLE_PERMISSION_SETS[Role.GUEST] | set(),
    }

    ROLE_HIERARCHY = CommonRoleGenerator.map_from_common_role_hierarchy(
        COMMON_ROLE_ENUM_MAP
    )

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS
    )
