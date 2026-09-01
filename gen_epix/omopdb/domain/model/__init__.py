"""Expose shared and OMOP model types plus their domain registration metadata.

The facade re-exports commondb identity, organization, authorization, and
system models alongside OMOP clinical, ontology, metadata, and upload models.
`SORTED_MODELS_BY_SERVICE_TYPE`, `SORTED_SERVICE_TYPES`, and
`STORED_MODEL_FIELD_PROPS` describe their application composition.
"""

# pylint: disable=useless-import-alias
from gen_epix import fastapp
from gen_epix.commondb.domain import enum as common_enum
from gen_epix.commondb.domain.model import (
    SORTED_MODELS_BY_SERVICE_TYPE as _COMMON_SORTED_MODELS_BY_SERVICE_TYPE,
)
from gen_epix.commondb.domain.model import BaseIdentifier as BaseIdentifier
from gen_epix.commondb.domain.model import Contact as Contact
from gen_epix.commondb.domain.model import DataCollection as DataCollection
from gen_epix.commondb.domain.model import DataCollectionSet as DataCollectionSet
from gen_epix.commondb.domain.model import (
    DataCollectionSetMember as DataCollectionSetMember,
)
from gen_epix.commondb.domain.model import IdentifierIssuer as IdentifierIssuer
from gen_epix.commondb.domain.model import ModelNoId as Model
from gen_epix.commondb.domain.model import Organization as Organization
from gen_epix.commondb.domain.model import (
    OrganizationAdminPolicy as OrganizationAdminPolicy,
)
from gen_epix.commondb.domain.model import (
    OrganizationIdentifierIssuerLink as OrganizationIdentifierIssuerLink,
)
from gen_epix.commondb.domain.model import OrganizationSet as OrganizationSet
from gen_epix.commondb.domain.model import (
    OrganizationSetMember as OrganizationSetMember,
)
from gen_epix.commondb.domain.model import Outage as Outage
from gen_epix.commondb.domain.model import Site as Site
from gen_epix.commondb.domain.model import User as User
from gen_epix.commondb.domain.model import UserInvitation as UserInvitation
from gen_epix.commondb.domain.model import (
    UserInvitationConstraints as UserInvitationConstraints,
)
from gen_epix.commondb.domain.model import UserNameEmail as UserNameEmail
from gen_epix.commondb.domain.model.upload import UploadResult as UploadResult
from gen_epix.commondb.domain.util import complete_stored_model_field_props
from gen_epix.fastapp.model import ModelFieldProps
from gen_epix.fastapp.services.auth import IdentityProvider as IdentityProvider
from gen_epix.fastapp.services.auth import IDPUser as IDPUser
from gen_epix.omopdb.domain import enum
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
from gen_epix.omopdb.domain.model.omop import (
    ConditionOccurrenceIdentifier as ConditionOccurrenceIdentifier,
)
from gen_epix.omopdb.domain.model.omop import Cost as Cost
from gen_epix.omopdb.domain.model.omop import DataLineageMixin as DataLineageMixin
from gen_epix.omopdb.domain.model.omop import Death as Death
from gen_epix.omopdb.domain.model.omop import DeathIdentifier as DeathIdentifier
from gen_epix.omopdb.domain.model.omop import DeviceExposure as DeviceExposure
from gen_epix.omopdb.domain.model.omop import (
    DeviceExposureIdentifier as DeviceExposureIdentifier,
)
from gen_epix.omopdb.domain.model.omop import Domain as Domain
from gen_epix.omopdb.domain.model.omop import DoseEra as DoseEra
from gen_epix.omopdb.domain.model.omop import DrugEra as DrugEra
from gen_epix.omopdb.domain.model.omop import DrugExposure as DrugExposure
from gen_epix.omopdb.domain.model.omop import (
    DrugExposureIdentifier as DrugExposureIdentifier,
)
from gen_epix.omopdb.domain.model.omop import DrugStrength as DrugStrength
from gen_epix.omopdb.domain.model.omop import Episode as Episode
from gen_epix.omopdb.domain.model.omop import EpisodeEvent as EpisodeEvent
from gen_epix.omopdb.domain.model.omop import FactRelationship as FactRelationship
from gen_epix.omopdb.domain.model.omop import FullPerson as FullPerson
from gen_epix.omopdb.domain.model.omop import Location as Location
from gen_epix.omopdb.domain.model.omop import Measurement as Measurement
from gen_epix.omopdb.domain.model.omop import (
    MeasurementForUpload as MeasurementForUpload,
)
from gen_epix.omopdb.domain.model.omop import (
    MeasurementIdentifier as MeasurementIdentifier,
)
from gen_epix.omopdb.domain.model.omop import MeasurementRelation as MeasurementRelation
from gen_epix.omopdb.domain.model.omop import (
    MeasurementRelationForUpload as MeasurementRelationForUpload,
)
from gen_epix.omopdb.domain.model.omop import (
    MeasurementRelationIdentifier as MeasurementRelationIdentifier,
)
from gen_epix.omopdb.domain.model.omop import Metadata as Metadata
from gen_epix.omopdb.domain.model.omop import Note as Note
from gen_epix.omopdb.domain.model.omop import NoteIdentifier as NoteIdentifier
from gen_epix.omopdb.domain.model.omop import NoteNlp as NoteNlp
from gen_epix.omopdb.domain.model.omop import NoteNlpIdentifier as NoteNlpIdentifier
from gen_epix.omopdb.domain.model.omop import Observation as Observation
from gen_epix.omopdb.domain.model.omop import (
    ObservationForUpload as ObservationForUpload,
)
from gen_epix.omopdb.domain.model.omop import (
    ObservationIdentifier as ObservationIdentifier,
)
from gen_epix.omopdb.domain.model.omop import ObservationPeriod as ObservationPeriod
from gen_epix.omopdb.domain.model.omop import (
    ObservationPeriodIdentifier as ObservationPeriodIdentifier,
)
from gen_epix.omopdb.domain.model.omop import PayerPlanPeriod as PayerPlanPeriod
from gen_epix.omopdb.domain.model.omop import Person as Person
from gen_epix.omopdb.domain.model.omop import (
    PersonBatchForUpload as PersonBatchForUpload,
)
from gen_epix.omopdb.domain.model.omop import (
    PersonBatchUploadResult as PersonBatchUploadResult,
)
from gen_epix.omopdb.domain.model.omop import PersonDataIssue as PersonDataIssue
from gen_epix.omopdb.domain.model.omop import PersonForUpload as PersonForUpload
from gen_epix.omopdb.domain.model.omop import PersonIdentifier as PersonIdentifier
from gen_epix.omopdb.domain.model.omop import PersonQuery as PersonQuery
from gen_epix.omopdb.domain.model.omop import PersonQueryResult as PersonQueryResult
from gen_epix.omopdb.domain.model.omop import PersonUploadResult as PersonUploadResult
from gen_epix.omopdb.domain.model.omop import ProcedureOccurrence as ProcedureOccurrence
from gen_epix.omopdb.domain.model.omop import (
    ProcedureOccurrenceIdentifier as ProcedureOccurrenceIdentifier,
)
from gen_epix.omopdb.domain.model.omop import Provider as Provider
from gen_epix.omopdb.domain.model.omop import Relationship as Relationship
from gen_epix.omopdb.domain.model.omop import SourceToConceptMap as SourceToConceptMap
from gen_epix.omopdb.domain.model.omop import Specimen as Specimen
from gen_epix.omopdb.domain.model.omop import SpecimenForUpload as SpecimenForUpload
from gen_epix.omopdb.domain.model.omop import SpecimenIdentifier as SpecimenIdentifier
from gen_epix.omopdb.domain.model.omop import (
    SpecimenIdsByCohortResult as SpecimenIdsByCohortResult,
)
from gen_epix.omopdb.domain.model.omop import VisitDetail as VisitDetail
from gen_epix.omopdb.domain.model.omop import (
    VisitDetailIdentifier as VisitDetailIdentifier,
)
from gen_epix.omopdb.domain.model.omop import VisitOccurrence as VisitOccurrence
from gen_epix.omopdb.domain.model.omop import (
    VisitOccurrenceIdentifier as VisitOccurrenceIdentifier,
)
from gen_epix.omopdb.domain.model.omop import Vocabulary as Vocabulary
from gen_epix.util import add_parent_class_docs

# List up model classes per service and sorted according to links topology
SORTED_MODELS_BY_SERVICE_TYPE: dict[enum.ServiceType, list[type[fastapp.Model]]] = (
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
            # Ontology
            Vocabulary,
            Domain,
            ConceptClass,
            Concept,
            Relationship,
            ConceptRelationship,
            ConceptAncestor,
            ConceptSynonym,
            SourceToConceptMap,
            DrugStrength,
            # Health system
            Location,
            CareSite,
            Provider,
            # Metadata
            CdmSource,
            Metadata,
            # Clinical data
            Person,
            PersonIdentifier,
            ObservationPeriod,
            ObservationPeriodIdentifier,
            VisitOccurrence,
            VisitOccurrenceIdentifier,
            VisitDetail,
            VisitDetailIdentifier,
            ConditionOccurrence,
            ConditionOccurrenceIdentifier,
            ProcedureOccurrence,
            ProcedureOccurrenceIdentifier,
            DrugExposure,
            DrugExposureIdentifier,
            DeviceExposure,
            DeviceExposureIdentifier,
            Specimen,
            SpecimenIdentifier,
            Measurement,
            MeasurementIdentifier,
            Observation,
            ObservationIdentifier,
            Note,
            NoteIdentifier,
            NoteNlp,
            NoteNlpIdentifier,
            FactRelationship,
            Death,
            DeathIdentifier,
            MeasurementRelation,
            MeasurementRelationIdentifier,
            # Health economics
            PayerPlanPeriod,
            Cost,
            # Derived
            ConditionEra,
            DrugEra,
            DoseEra,
            CohortDefinition,
            Cohort,
            Episode,
            EpisodeEvent,
            # Non-persistent models including upload
            PersonQuery,
            PersonQueryResult,
            FullPerson,
            SpecimenForUpload,
            MeasurementForUpload,
            MeasurementRelationForUpload,
            ObservationForUpload,
            PersonForUpload,
            PersonUploadResult,
            PersonBatchForUpload,
            PersonBatchUploadResult,
            SpecimenIdsByCohortResult,
        ],
    }
)

SORTED_SERVICE_TYPES = tuple(SORTED_MODELS_BY_SERVICE_TYPE.keys())

COMMON_MODEL_MAP: dict[type[fastapp.Model], type[fastapp.Model]] = {}

# Additional field properties for models that have already been stored (persisted)
STORED_MODEL_FIELD_PROPS: dict[type[fastapp.Model], dict[str, ModelFieldProps]] = {
    Person: {
        # All fields except the PK are mutable to allow correction of Person records
        # after creation. Without this, mandatory fields (year_of_birth, gender_concept_id,
        # etc.) would be permanently immutable once set, blocking on_exists=UPDATE.
        field_name: ModelFieldProps(is_mutable_always=True)
        for field_name in Person.model_fields
        if field_name != "person_id"
    },
}
complete_stored_model_field_props(
    STORED_MODEL_FIELD_PROPS, SORTED_MODELS_BY_SERVICE_TYPE
)
add_parent_class_docs(
    set.union(
        *[
            set(y)  # type: ignore[arg-type]
            for x, y in SORTED_MODELS_BY_SERVICE_TYPE.items()
            if x
            not in {
                enum.ServiceType.AUTH,
                enum.ServiceType.SYSTEM,
                enum.ServiceType.RBAC,
                enum.ServiceType.ORGANIZATION,
            }
        ]
    ),
    exclude=(Model,),
)
