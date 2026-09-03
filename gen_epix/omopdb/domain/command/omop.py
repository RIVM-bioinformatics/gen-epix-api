"""Commands for OMOP CRUD operations, person upload, and retrieval."""

from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_validator

from gen_epix.commondb.domain.command import Command, CrudCommand
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.omopdb.domain import model


# Non-CRUD commands
class UploadPersonsCommand(Command, UploadBatchCommandMixin):
    """
    Represents an upload of a batch of persons along with their associated data.
    The data are uploaded as a single atomic unit of work, so that
    either all data are successfully uploaded or none are.
    """

    BATCH_FOR_UPLOAD_CLASS: ClassVar = model.PersonBatchForUpload
    BATCH_FOR_UPLOAD_FIELD_NAME: ClassVar = "person_batch"
    BATCH_UPLOAD_RESULT_CLASS: ClassVar = model.PersonBatchUploadResult

    person_batch: model.PersonBatchForUpload = Field(
        description="Persons to upload, along with any associated data.",
    )


class RetrievePersonsByQueryCommand(Command):
    """
    Represents a request to retrieve person IDs based on a query. These IDs can then be used to retrieve the
    actual data for these persons.
    """

    person_query: model.PersonQuery = Field(
        description="The query to filter persons by."
    )


class RetrievePersonsByIdCommand(Command):
    """
    Represents a request to retrieve all data for a list of person IDs, as a list of FullPerson objects in the
    same order.
    """

    person_ids: list[UUID] = Field(
        description="IDs of the persons to retrieve. Must be unique.",
    )

    @field_validator("person_ids", mode="after")
    def _validate_person_ids(cls, person_ids: list[UUID]) -> list[UUID]:
        """Validate that requested person identifiers are unique."""
        if len(set(person_ids)) != len(person_ids):
            raise ValueError("person_ids must be unique")
        return person_ids


class RetrieveSpecimenIdsByCohortIdsCommand(Command):
    """
    Represents a request to retrieve specimen IDs (equivalent to SEQDB sample IDs)
    for persons belonging to a set of cohort IDs (equivalent to CASEDB case IDs)
    and a cohort definition ID.
    """

    cohort_definition_id: UUID = Field(description="The cohort definition ID.")
    cohort_ids: list[UUID] = Field(description="The cohort IDs to look up. UNIQUE")


# CRUD commands
class CareSiteCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP care-site records."""

    MODEL_CLASS: ClassVar = model.CareSite


class CdmSourceCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP CDM-source records."""

    MODEL_CLASS: ClassVar = model.CdmSource


class CohortCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP cohort records."""

    MODEL_CLASS: ClassVar = model.Cohort


class CohortDefinitionCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP cohort-definition records."""

    MODEL_CLASS: ClassVar = model.CohortDefinition


class ConceptAncestorCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP concept-ancestor records."""

    MODEL_CLASS: ClassVar = model.ConceptAncestor


class ConceptClassCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP concept-class records."""

    MODEL_CLASS: ClassVar = model.ConceptClass


class ConceptCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP concept records."""

    MODEL_CLASS: ClassVar = model.Concept


class ConceptRelationshipCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP concept-relationship records."""

    MODEL_CLASS: ClassVar = model.ConceptRelationship


class ConceptSynonymCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP concept-synonym records."""

    MODEL_CLASS: ClassVar = model.ConceptSynonym


class ConditionEraCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP condition-era records."""

    MODEL_CLASS: ClassVar = model.ConditionEra


class ConditionOccurrenceCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP condition-occurrence records."""

    MODEL_CLASS: ClassVar = model.ConditionOccurrence


class ConditionOccurrenceIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for condition-occurrence identifiers."""

    MODEL_CLASS: ClassVar = model.ConditionOccurrenceIdentifier


class CostCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP cost records."""

    MODEL_CLASS: ClassVar = model.Cost


class DeviceExposureCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP device-exposure records."""

    MODEL_CLASS: ClassVar = model.DeviceExposure


class DeviceExposureIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for device-exposure identifiers."""

    MODEL_CLASS: ClassVar = model.DeviceExposureIdentifier


class DeathCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP death records."""

    MODEL_CLASS: ClassVar = model.Death


class DeathIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for death identifiers."""

    MODEL_CLASS: ClassVar = model.DeathIdentifier


class DomainCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP domain records."""

    MODEL_CLASS: ClassVar = model.Domain


class DoseEraCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP dose-era records."""

    MODEL_CLASS: ClassVar = model.DoseEra


class DrugEraCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP drug-era records."""

    MODEL_CLASS: ClassVar = model.DrugEra


class DrugExposureCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP drug-exposure records."""

    MODEL_CLASS: ClassVar = model.DrugExposure


class DrugExposureIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for drug-exposure identifiers."""

    MODEL_CLASS: ClassVar = model.DrugExposureIdentifier


class DrugStrengthCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP drug-strength records."""

    MODEL_CLASS: ClassVar = model.DrugStrength


class EpisodeCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP episode records."""

    MODEL_CLASS: ClassVar = model.Episode


class EpisodeEventCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP episode-event records."""

    MODEL_CLASS: ClassVar = model.EpisodeEvent


class FactRelationshipCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP fact-relationship records."""

    MODEL_CLASS: ClassVar = model.FactRelationship


class LocationCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP location records."""

    MODEL_CLASS: ClassVar = model.Location


class MeasurementCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP measurement records."""

    MODEL_CLASS: ClassVar = model.Measurement


class MeasurementIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for measurement identifiers."""

    MODEL_CLASS: ClassVar = model.MeasurementIdentifier


class MeasurementRelationCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP measurement-relation records."""

    MODEL_CLASS: ClassVar = model.MeasurementRelation


class MeasurementRelationIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for measurement-relation identifiers."""

    MODEL_CLASS: ClassVar = model.MeasurementRelationIdentifier


class MetadataCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP metadata records."""

    MODEL_CLASS: ClassVar = model.Metadata


class NoteCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP note records."""

    MODEL_CLASS: ClassVar = model.Note


class NoteIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for note identifiers."""

    MODEL_CLASS: ClassVar = model.NoteIdentifier


class NoteNlpCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP note-NLP records."""

    MODEL_CLASS: ClassVar = model.NoteNlp


class NoteNlpIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for note-NLP identifiers."""

    MODEL_CLASS: ClassVar = model.NoteNlpIdentifier


class ObservationCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP observation records."""

    MODEL_CLASS: ClassVar = model.Observation


class ObservationIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for observation identifiers."""

    MODEL_CLASS: ClassVar = model.ObservationIdentifier


class ObservationPeriodCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP observation-period records."""

    MODEL_CLASS: ClassVar = model.ObservationPeriod


class ObservationPeriodIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for observation-period identifiers."""

    MODEL_CLASS: ClassVar = model.ObservationPeriodIdentifier


class PayerPlanPeriodCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP payer-plan-period records."""

    MODEL_CLASS: ClassVar = model.PayerPlanPeriod


class PersonCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP person records."""

    MODEL_CLASS: ClassVar = model.Person


class PersonIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for person identifiers."""

    MODEL_CLASS: ClassVar = model.PersonIdentifier


class ProcedureOccurrenceCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP procedure-occurrence records."""

    MODEL_CLASS: ClassVar = model.ProcedureOccurrence


class ProcedureOccurrenceIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for procedure-occurrence identifiers."""

    MODEL_CLASS: ClassVar = model.ProcedureOccurrenceIdentifier


class ProviderCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP provider records."""

    MODEL_CLASS: ClassVar = model.Provider


class RelationshipCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP relationship records."""

    MODEL_CLASS: ClassVar = model.Relationship


class SourceToConceptMapCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP source-to-concept mappings."""

    MODEL_CLASS: ClassVar = model.SourceToConceptMap


class SpecimenCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP specimen records."""

    MODEL_CLASS: ClassVar = model.Specimen


class SpecimenIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for specimen identifiers."""

    MODEL_CLASS: ClassVar = model.SpecimenIdentifier


class VisitDetailCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP visit-detail records."""

    MODEL_CLASS: ClassVar = model.VisitDetail


class VisitDetailIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for visit-detail identifiers."""

    MODEL_CLASS: ClassVar = model.VisitDetailIdentifier


class VisitOccurrenceCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP visit-occurrence records."""

    MODEL_CLASS: ClassVar = model.VisitOccurrence


class VisitOccurrenceIdentifierCrudCommand(CrudCommand):
    """Represents CRUD operations for visit-occurrence identifiers."""

    MODEL_CLASS: ClassVar = model.VisitOccurrenceIdentifier


class VocabularyCrudCommand(CrudCommand):
    """Represents CRUD operations for OMOP vocabulary records."""

    MODEL_CLASS: ClassVar = model.Vocabulary
