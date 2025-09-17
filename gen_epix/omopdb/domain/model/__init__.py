from typing import Type

from gen_epix import fastapp
from gen_epix.commondb.domain import enum as common_enum
from gen_epix.commondb.domain import model as common_model
from gen_epix.commondb.domain.model import (
    SORTED_MODELS_BY_SERVICE_TYPE as _COMMON_SORTED_MODELS_BY_SERVICE_TYPE,
)
from gen_epix.commondb.domain.model import Contact as Contact
from gen_epix.commondb.domain.model import DataCollection as DataCollection
from gen_epix.commondb.domain.model import DataCollectionSet as DataCollectionSet
from gen_epix.commondb.domain.model import (
    DataCollectionSetMember as DataCollectionSetMember,
)
from gen_epix.commondb.domain.model import IdentifierIssuer as IdentifierIssuer
from gen_epix.commondb.domain.model import Model as Model
from gen_epix.commondb.domain.model import Organization as Organization
from gen_epix.commondb.domain.model import OrganizationSet as OrganizationSet
from gen_epix.commondb.domain.model import (
    OrganizationSetMember as OrganizationSetMember,
)
from gen_epix.commondb.domain.model import Outage as Outage
from gen_epix.commondb.domain.model import Site as Site
from gen_epix.commondb.domain.model import UserNameEmail as UserNameEmail
from gen_epix.fastapp.services.auth import IdentityProvider as IdentityProvider
from gen_epix.fastapp.services.auth import IDPUser as IDPUser
from gen_epix.omopdb.domain import enum
from gen_epix.omopdb.domain.model.abac import (
    OrganizationAdminPolicy as OrganizationAdminPolicy,
)
from gen_epix.omopdb.domain.model.omop import CareSite as CareSite
from gen_epix.omopdb.domain.model.omop import CdmSource as CdmSource
from gen_epix.omopdb.domain.model.omop import Cohort as Cohort
from gen_epix.omopdb.domain.model.omop import CohortDefinition as CohortDefinition
from gen_epix.omopdb.domain.model.omop import Concept as Concept
from gen_epix.omopdb.domain.model.omop import ConceptAncestor as ConceptAncestor
from gen_epix.omopdb.domain.model.omop import ConceptClass as ConceptClass
from gen_epix.omopdb.domain.model.omop import ConceptRelationship as ConceptRelationship
from gen_epix.omopdb.domain.model.omop import ConceptSynonym as ConceptSynonym
from gen_epix.omopdb.domain.model.omop import ConditionEra as ConditionEra
from gen_epix.omopdb.domain.model.omop import ConditionOccurrence as ConditionOccurrence
from gen_epix.omopdb.domain.model.omop import Cost as Cost
from gen_epix.omopdb.domain.model.omop import DataLineageMixin as DataLineageMixin
from gen_epix.omopdb.domain.model.omop import DeviceExposure as DeviceExposure
from gen_epix.omopdb.domain.model.omop import Domain as Domain
from gen_epix.omopdb.domain.model.omop import DoseEra as DoseEra
from gen_epix.omopdb.domain.model.omop import DrugEra as DrugEra
from gen_epix.omopdb.domain.model.omop import DrugExposure as DrugExposure
from gen_epix.omopdb.domain.model.omop import DrugStrength as DrugStrength
from gen_epix.omopdb.domain.model.omop import FactRelationship as FactRelationship
from gen_epix.omopdb.domain.model.omop import Location as Location
from gen_epix.omopdb.domain.model.omop import LocationHistory as LocationHistory
from gen_epix.omopdb.domain.model.omop import Measurement as Measurement
from gen_epix.omopdb.domain.model.omop import MeasurementRelation as MeasurementRelation
from gen_epix.omopdb.domain.model.omop import Metadata as Metadata
from gen_epix.omopdb.domain.model.omop import Note as Note
from gen_epix.omopdb.domain.model.omop import NoteNlp as NoteNlp
from gen_epix.omopdb.domain.model.omop import Observation as Observation
from gen_epix.omopdb.domain.model.omop import ObservationPeriod as ObservationPeriod
from gen_epix.omopdb.domain.model.omop import PayerPlanPeriod as PayerPlanPeriod
from gen_epix.omopdb.domain.model.omop import Person as Person
from gen_epix.omopdb.domain.model.omop import ProcedureOccurrence as ProcedureOccurrence
from gen_epix.omopdb.domain.model.omop import Provider as Provider
from gen_epix.omopdb.domain.model.omop import Relationship as Relationship
from gen_epix.omopdb.domain.model.omop import SourceToConceptMap as SourceToConceptMap
from gen_epix.omopdb.domain.model.omop import Specimen as Specimen
from gen_epix.omopdb.domain.model.omop import SurveyConduct as SurveyConduct
from gen_epix.omopdb.domain.model.omop import VisitDetail as VisitDetail
from gen_epix.omopdb.domain.model.omop import VisitOccurrence as VisitOccurrence
from gen_epix.omopdb.domain.model.omop import Vocabulary as Vocabulary
from gen_epix.omopdb.domain.model.omop.non_persistable import Subject as Subject
from gen_epix.omopdb.domain.model.organization import User as User
from gen_epix.omopdb.domain.model.organization import UserInvitation as UserInvitation

# List up model classes per service and sorted according to links topology
SORTED_MODELS_BY_SERVICE_TYPE: dict[enum.ServiceType, list[Type[fastapp.Model]]] = (
    {  # pyright: ignore[reportAssignmentType]
        # Common models
        enum.ServiceType.AUTH: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.AUTH]
        ),
        enum.ServiceType.SYSTEM: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.SYSTEM]
        ),
        enum.ServiceType.RBAC: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.RBAC]
        ),
        enum.ServiceType.ORGANIZATION: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.ORGANIZATION]
        ),
        # Specific models
        enum.ServiceType.ABAC: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.ABAC]
        )
        + [],
        enum.ServiceType.OMOP: [
            # Ordered topologically based on foreign key dependencies
            # Foundation tables (no dependencies)
            Location,
            CohortDefinition,
            Cohort,
            CdmSource,
            # Vocabulary system (circular dependencies resolved logically)
            Vocabulary,
            Domain,
            ConceptClass,
            Concept,
            Relationship,
            # Concept relationships (depend on concept and relationship)
            ConceptRelationship,
            ConceptAncestor,
            ConceptSynonym,
            # Reference/mapping tables
            DrugStrength,
            SourceToConceptMap,
            Metadata,
            # Care infrastructure
            CareSite,
            Provider,
            # Person and observations
            Person,
            ObservationPeriod,
            PayerPlanPeriod,
            # Visits (depend on person, care_site, provider, concept)
            VisitOccurrence,
            VisitDetail,
            # Clinical events (depend on person, visits, providers, concepts)
            ConditionOccurrence,
            ProcedureOccurrence,
            DrugExposure,
            DeviceExposure,
            Measurement,
            Observation,
            Specimen,
            Note,
            # Other tables depending at least on person
            ConditionEra,
            DrugEra,
            DoseEra,
            NoteNlp,
            Cost,
            LocationHistory,
            SurveyConduct,
            # General relationships
            FactRelationship,
            MeasurementRelation,
        ],
    }
)

SORTED_SERVICE_TYPES = tuple(SORTED_MODELS_BY_SERVICE_TYPE.keys())

COMMON_MODEL_IMPL: dict[Type[fastapp.Model], Type[fastapp.Model]] = {
    common_model.User: User,
    common_model.UserInvitation: UserInvitation,
    common_model.OrganizationAdminPolicy: OrganizationAdminPolicy,
}
