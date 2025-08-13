from typing import Type

from gen_epix import fastapp
from gen_epix.common.domain.model import Contact as Contact
from gen_epix.common.domain.model import DataCollection as DataCollection
from gen_epix.common.domain.model import DataCollectionSet as DataCollectionSet
from gen_epix.common.domain.model import (
    DataCollectionSetMember as DataCollectionSetMember,
)
from gen_epix.common.domain.model import IdentifierIssuer as IdentifierIssuer
from gen_epix.common.domain.model import Model as Model
from gen_epix.common.domain.model import Organization as Organization
from gen_epix.common.domain.model import OrganizationSet as OrganizationSet
from gen_epix.common.domain.model import OrganizationSetMember as OrganizationSetMember
from gen_epix.common.domain.model import Outage as Outage
from gen_epix.common.domain.model import Site as Site
from gen_epix.common.domain.model import UserNameEmail as UserNameEmail
from gen_epix.fastapp.services.auth import IdentityProvider as IdentityProvider
from gen_epix.fastapp.services.auth import IDPUser as IDPUser
from gen_epix.omopdb.domain import DOMAIN, enum
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
from gen_epix.omopdb.domain.model.omop import DeviceExposure as DeviceExposure
from gen_epix.omopdb.domain.model.omop import Domain as Domain
from gen_epix.omopdb.domain.model.omop import DoseEra as DoseEra
from gen_epix.omopdb.domain.model.omop import DrugEra as DrugEra
from gen_epix.omopdb.domain.model.omop import DrugExposure as DrugExposure
from gen_epix.omopdb.domain.model.omop import DrugStrength as DrugStrength
from gen_epix.omopdb.domain.model.omop import Etl as Etl
from gen_epix.omopdb.domain.model.omop import FactRelationship as FactRelationship
from gen_epix.omopdb.domain.model.omop import Location as Location
from gen_epix.omopdb.domain.model.omop import LocationHistory as LocationHistory
from gen_epix.omopdb.domain.model.omop import Measurement as Measurement
from gen_epix.omopdb.domain.model.omop import Metadata as Metadata
from gen_epix.omopdb.domain.model.omop import Note as Note
from gen_epix.omopdb.domain.model.omop import NoteNlp as NoteNlp
from gen_epix.omopdb.domain.model.omop import Observation as Observation
from gen_epix.omopdb.domain.model.omop import ObservationPeriod as ObservationPeriod
from gen_epix.omopdb.domain.model.omop import PayerPlanPeriod as PayerPlanPeriod
from gen_epix.omopdb.domain.model.omop import Person as Person
from gen_epix.omopdb.domain.model.omop import ProcedureOccurrence as ProcedureOccurrence
from gen_epix.omopdb.domain.model.omop import Provenance as Provenance
from gen_epix.omopdb.domain.model.omop import Provider as Provider
from gen_epix.omopdb.domain.model.omop import Relationship as Relationship
from gen_epix.omopdb.domain.model.omop import Source as Source
from gen_epix.omopdb.domain.model.omop import SourceToConceptMap as SourceToConceptMap
from gen_epix.omopdb.domain.model.omop import Specimen as Specimen
from gen_epix.omopdb.domain.model.omop import Subject as Subject
from gen_epix.omopdb.domain.model.omop import SurveyConduct as SurveyConduct
from gen_epix.omopdb.domain.model.omop import VisitDetail as VisitDetail
from gen_epix.omopdb.domain.model.omop import VisitOccurrence as VisitOccurrence
from gen_epix.omopdb.domain.model.omop import Vocabulary as Vocabulary
from gen_epix.omopdb.domain.model.organization import User as User
from gen_epix.omopdb.domain.model.organization import UserInvitation as UserInvitation

# List up model classes per service and sorted according to links topology
SORTED_MODELS_BY_SERVICE: dict[enum.ServiceType, list[Type[fastapp.Model]]] = (
    {  # pyright: ignore[reportAssignmentType]
        enum.ServiceType.AUTH: [
            IdentityProvider,
            IDPUser,
        ],
        enum.ServiceType.SYSTEM: [
            Outage,
        ],
        enum.ServiceType.ORGANIZATION: [
            Organization,
            OrganizationSet,
            OrganizationSetMember,
            DataCollection,
            DataCollectionSet,
            DataCollectionSetMember,
            IdentifierIssuer,
            Site,
            Contact,
            UserNameEmail,
            User,
            UserInvitation,
        ],
        enum.ServiceType.OMOP: [
            # Core vocabulary and reference tables
            Vocabulary,
            Domain,
            ConceptClass,
            Relationship,
            Concept,
            ConceptAncestor,
            ConceptRelationship,
            ConceptSynonym,
            # Source and mapping tables
            CdmSource,
            Source,
            SourceToConceptMap,
            # Geographic and organizational tables
            Location,
            CareSite,
            Provider,
            # Person and observation period
            Subject,
            Person,
            ObservationPeriod,
            # Visit tables
            VisitOccurrence,
            VisitDetail,
            LocationHistory,
            PayerPlanPeriod,
            # Clinical event tables
            ConditionOccurrence,
            DrugStrength,
            DrugExposure,
            DeviceExposure,
            ProcedureOccurrence,
            Observation,
            Measurement,
            Note,
            NoteNlp,
            Specimen,
            # Era tables (depend on clinical events)
            ConditionEra,
            DrugEra,
            DoseEra,
            # Cost and relationship tables
            Cost,
            FactRelationship,
            # Cohort tables
            Cohort,
            CohortDefinition,
            SurveyConduct,
            # Metadata tables
            Metadata,
            Etl,
            Provenance,
        ],
    }
)

for service_type, model_classes in SORTED_MODELS_BY_SERVICE.items():
    for model_class in model_classes:
        assert model_class.ENTITY is not None
        DOMAIN.register_entity(
            model_class.ENTITY, model_class=model_class, service_type=service_type
        )
