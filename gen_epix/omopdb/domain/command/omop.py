# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar

from pydantic import Field

from gen_epix.commondb.domain.command import Command, CrudCommand
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.omopdb.domain import model


# Non-CRUD commands
class UploadPersonsCommand(Command, UploadBatchCommandMixin):
    """
    Upload a batch of persons along with their associated data.
    The data are uploaded as a single atomic unit of work, so that
    either all data are successfully uploaded or none are.
    """

    BATCH_FOR_UPLOAD_CLASS: ClassVar = model.PersonBatchForUpload
    BATCH_FOR_UPLOAD_FIELD_NAME: ClassVar = "person_batch"
    BATCH_UPLOAD_RESULT_CLASS: ClassVar = model.PersonBatchUploadResult

    person_batch: model.PersonBatchForUpload = Field(
        description="Persons to upload, along with any associated data.",
    )


# CRUD commands
class CareSiteCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CareSite


class CdmSourceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CdmSource


class CohortCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Cohort


class CohortDefinitionCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CohortDefinition


class ConceptAncestorCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptAncestor


class ConceptClassCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptClass


class ConceptCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Concept


class ConceptRelationshipCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptRelationship


class ConceptSynonymCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptSynonym


class ConditionEraCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConditionEra


class ConditionOccurrenceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConditionOccurrence


class ConditionOccurrenceIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConditionOccurrenceIdentifier


class CostCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Cost


class DeviceExposureCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DeviceExposure


class DeviceExposureIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DeviceExposureIdentifier


class DeathCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Death


class DeathIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DeathIdentifier


class DomainCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Domain


class DoseEraCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DoseEra


class DrugEraCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DrugEra


class DrugExposureCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DrugExposure


class DrugExposureIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DrugExposureIdentifier


class DrugStrengthCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DrugStrength


class EpisodeCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Episode


class EpisodeEventCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.EpisodeEvent


class FactRelationshipCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.FactRelationship


class LocationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Location


class MeasurementCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Measurement


class MeasurementIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.MeasurementIdentifier


class MeasurementRelationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.MeasurementRelation


class MeasurementRelationIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.MeasurementRelationIdentifier


class MetadataCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Metadata


class NoteCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Note


class NoteIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.NoteIdentifier


class NoteNlpCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.NoteNlp


class NoteNlpIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.NoteNlpIdentifier


class ObservationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Observation


class ObservationIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ObservationIdentifier


class ObservationPeriodCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ObservationPeriod


class ObservationPeriodIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ObservationPeriodIdentifier


class PayerPlanPeriodCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.PayerPlanPeriod


class PersonCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Person


class PersonIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.PersonIdentifier


class ProcedureOccurrenceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ProcedureOccurrence


class ProcedureOccurrenceIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ProcedureOccurrenceIdentifier


class ProviderCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Provider


class RelationshipCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Relationship


class SourceToConceptMapCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SourceToConceptMap


class SpecimenCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Specimen


class SpecimenIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SpecimenIdentifier


class VisitDetailCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.VisitDetail


class VisitDetailIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.VisitDetailIdentifier


class VisitOccurrenceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.VisitOccurrence


class VisitOccurrenceIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.VisitOccurrenceIdentifier


class VocabularyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Vocabulary
