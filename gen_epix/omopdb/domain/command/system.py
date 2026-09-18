"""Define omopdb commands for system operations."""

from typing import ClassVar

from gen_epix.commondb.domain.command import (
    DeleteAllOperationalDataCommand as CommonDeleteAllOperationalDataCommand,
)
from gen_epix.commondb.domain.command import (
    DeleteAllRefDataCommand as CommonDeleteAllRefDataCommand,
)
from gen_epix.omopdb.domain import model


class DeleteAllOperationalDataCommand(CommonDeleteAllOperationalDataCommand):
    SORTED_OPERATIONAL_DATA_MODEL_CLASSES: ClassVar = [
        model.Cohort,
        model.ConditionEra,
        model.ConditionOccurrenceIdentifier,
        model.Cost,
        model.DeathIdentifier,
        model.DeviceExposureIdentifier,
        model.DoseEra,
        model.DrugEra,
        model.DrugExposureIdentifier,
        model.EpisodeEvent,
        model.FactRelationship,
        model.MeasurementIdentifier,
        model.MeasurementRelationIdentifier,
        model.NoteNlpIdentifier,
        model.NoteNlp,
        model.NoteIdentifier,
        model.ObservationIdentifier,
        model.ObservationPeriodIdentifier,
        model.PayerPlanPeriod,
        model.PersonIdentifier,
        model.ProcedureOccurrenceIdentifier,
        model.SpecimenIdentifier,
        model.VisitDetailIdentifier,
        model.VisitOccurrenceIdentifier,
        model.ConditionOccurrence,
        model.Death,
        model.DeviceExposure,
        model.DrugExposure,
        model.Episode,
        model.MeasurementRelation,
        model.Note,
        model.Observation,
        model.ObservationPeriod,
        model.ProcedureOccurrence,
        model.Measurement,
        model.Specimen,
        model.VisitDetail,
        model.VisitOccurrence,
        model.Person,
    ]


class DeleteAllRefDataCommand(CommonDeleteAllRefDataCommand):
    """Request deletion of all persisted OMOP reference data."""

    REF_DATA_SERVICE_TYPE_VALUES: ClassVar[frozenset[str]] = frozenset({"OMOP"})
    SORTED_REF_DATA_MODEL_CLASSES: ClassVar[list[type[model.Model]]] = [
        model.Provider,
        model.ConceptRelationship,
        model.Metadata,
        model.CareSite,
        model.DrugStrength,
        model.SourceToConceptMap,
        model.ConceptSynonym,
        model.ConceptAncestor,
        model.Relationship,
        model.Concept,
        model.CohortDefinition,
        model.CdmSource,
        model.Location,
        model.ConceptClass,
        model.Domain,
        model.Vocabulary,
    ]
