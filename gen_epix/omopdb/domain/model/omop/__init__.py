# pylint: disable=useless-import-alias
from gen_epix.omopdb.domain.model.omop.base import DataLineageMixin as DataLineageMixin

# Clinical data domain imports
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    ConditionOccurrence as ConditionOccurrence,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    ConditionOccurrenceIdentifier as ConditionOccurrenceIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import Death as Death
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    DeathIdentifier as DeathIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    DeviceExposure as DeviceExposure,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    DeviceExposureIdentifier as DeviceExposureIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import DrugExposure as DrugExposure
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    DrugExposureIdentifier as DrugExposureIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    FactRelationship as FactRelationship,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import Measurement as Measurement
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    MeasurementIdentifier as MeasurementIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    MeasurementRelation as MeasurementRelation,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    MeasurementRelationIdentifier as MeasurementRelationIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import Note as Note
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    NoteIdentifier as NoteIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import NoteNlp as NoteNlp
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    NoteNlpIdentifier as NoteNlpIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import Observation as Observation
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    ObservationIdentifier as ObservationIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    ObservationPeriod as ObservationPeriod,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    ObservationPeriodIdentifier as ObservationPeriodIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import Person as Person
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    PersonIdentifier as PersonIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    ProcedureOccurrence as ProcedureOccurrence,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    ProcedureOccurrenceIdentifier as ProcedureOccurrenceIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import Specimen as Specimen
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    SpecimenIdentifier as SpecimenIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import VisitDetail as VisitDetail
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    VisitDetailIdentifier as VisitDetailIdentifier,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    VisitOccurrence as VisitOccurrence,
)
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    VisitOccurrenceIdentifier as VisitOccurrenceIdentifier,
)

# Results domain imports
# Derived domain imports
from gen_epix.omopdb.domain.model.omop.derived import Cohort as Cohort
from gen_epix.omopdb.domain.model.omop.derived import (
    CohortDefinition as CohortDefinition,
)
from gen_epix.omopdb.domain.model.omop.derived import ConditionEra as ConditionEra
from gen_epix.omopdb.domain.model.omop.derived import DoseEra as DoseEra
from gen_epix.omopdb.domain.model.omop.derived import DrugEra as DrugEra
from gen_epix.omopdb.domain.model.omop.derived import Episode as Episode
from gen_epix.omopdb.domain.model.omop.derived import EpisodeEvent as EpisodeEvent

# Health economics domain imports
from gen_epix.omopdb.domain.model.omop.health_economics import Cost as Cost
from gen_epix.omopdb.domain.model.omop.health_economics import (
    PayerPlanPeriod as PayerPlanPeriod,
)

# Health system domain imports
from gen_epix.omopdb.domain.model.omop.health_system import CareSite as CareSite
from gen_epix.omopdb.domain.model.omop.health_system import Location as Location
from gen_epix.omopdb.domain.model.omop.health_system import Provider as Provider

# Metadata domain imports
from gen_epix.omopdb.domain.model.omop.metadata import CdmSource as CdmSource
from gen_epix.omopdb.domain.model.omop.metadata import Metadata as Metadata

# Ontology domain imports
from gen_epix.omopdb.domain.model.omop.ontology import Concept as Concept
from gen_epix.omopdb.domain.model.omop.ontology import (
    ConceptAncestor as ConceptAncestor,
)
from gen_epix.omopdb.domain.model.omop.ontology import ConceptClass as ConceptClass
from gen_epix.omopdb.domain.model.omop.ontology import (
    ConceptRelationship as ConceptRelationship,
)
from gen_epix.omopdb.domain.model.omop.ontology import ConceptSynonym as ConceptSynonym
from gen_epix.omopdb.domain.model.omop.ontology import Domain as Domain
from gen_epix.omopdb.domain.model.omop.ontology import DrugStrength as DrugStrength
from gen_epix.omopdb.domain.model.omop.ontology import Relationship as Relationship
from gen_epix.omopdb.domain.model.omop.ontology import (
    SourceToConceptMap as SourceToConceptMap,
)
from gen_epix.omopdb.domain.model.omop.ontology import Vocabulary as Vocabulary

# Upload models
from gen_epix.omopdb.domain.model.omop.upload import (
    MeasurementForUpload as MeasurementForUpload,
)
from gen_epix.omopdb.domain.model.omop.upload import (
    MeasurementRelationForUpload as MeasurementRelationForUpload,
)
from gen_epix.omopdb.domain.model.omop.upload import (
    ObservationForUpload as ObservationForUpload,
)
from gen_epix.omopdb.domain.model.omop.upload import (
    PersonBatchForUpload as PersonBatchForUpload,
)
from gen_epix.omopdb.domain.model.omop.upload import (
    PersonBatchUploadResult as PersonBatchUploadResult,
)
from gen_epix.omopdb.domain.model.omop.upload import PersonDataIssue as PersonDataIssue
from gen_epix.omopdb.domain.model.omop.upload import PersonForUpload as PersonForUpload
from gen_epix.omopdb.domain.model.omop.upload import (
    PersonUploadResult as PersonUploadResult,
)
from gen_epix.omopdb.domain.model.omop.upload import (
    SpecimenForUpload as SpecimenForUpload,
)
