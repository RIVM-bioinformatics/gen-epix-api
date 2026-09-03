"""Non-persistable OMOP models for retrieval requests and assembled results."""

from datetime import datetime
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model.base import ModelNoId
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.omopdb.domain.model.base import Model
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    ConditionOccurrence,
    ConditionOccurrenceIdentifier,
    Death,
    DeathIdentifier,
    DeviceExposure,
    DeviceExposureIdentifier,
    DrugExposure,
    DrugExposureIdentifier,
    Measurement,
    MeasurementIdentifier,
    MeasurementRelation,
    MeasurementRelationIdentifier,
    Note,
    NoteIdentifier,
    Observation,
    ObservationIdentifier,
    ObservationPeriod,
    ObservationPeriodIdentifier,
    Person,
    PersonIdentifier,
    ProcedureOccurrence,
    ProcedureOccurrenceIdentifier,
    Specimen,
    SpecimenIdentifier,
    VisitDetail,
    VisitDetailIdentifier,
    VisitOccurrence,
    VisitOccurrenceIdentifier,
)


class SpecimenIdsByCohortResult(Model):
    """Represents a mapping from each requested cohort identifier to its matching specimen identifiers."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="specimen_ids_by_cohort_results",
        persistable=False,
    )
    specimen_ids_by_cohort_id: dict[UUID, list[UUID]] = Field(
        description=(
            "Map from cohort_id to the specimen_ids of the person in that cohort."
        )
    )


class PersonQuery(Model):
    """
    Represents a query for retrieving persons based on their demographic information. All
    constraints are optional, but at least some must be provided, and the query will
    match any person that matches all of the provided criteria.

    Model validation: At least one modification-time bound must be provided to
    prevent an unbounded person retrieval.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="person_queries",
        persistable=False,
    )
    label: str | None = Field(default=None, description="The label for the query.")
    modified_since: datetime | None = Field(
        default=None,
        description="The lower bound of the last modified datetime range to filter by. Inclusive. Not applied if not provided.",
    )
    modified_until: datetime | None = Field(
        default=None,
        description="The upper bound of the last modified datetime range to filter by. Exclusive. Not applied if not provided.",
    )

    @model_validator(mode="after")
    def _validate_some_criteria(self) -> Self:
        """
        Validate that at least some criteria are provided, to avoid accidentally
        retrieving all persons.
        """
        if self.modified_since is None and self.modified_until is None:
            raise ValueError("At least one criterion must be provided")
        return self


class PersonQueryResult(Model):
    """Represents the person identifiers matching an executed person query."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="person_query_results",
        persistable=False,
    )
    person_query: PersonQuery = Field(
        description="The person query that was executed, provided back."
    )
    person_ids: list[UUID] = Field(
        description="The IDs of the persons matching the query, possibly limited by CaseSettings.read_max_n_cases. If limited, the most recent persons are returned"
    )
    is_max_results_exceeded: bool = Field(
        description="Whether the number of results was limited."
    )


class FullPerson(Model):
    """
    Represents a comprehensive view of a person in the OMOP CDM, including
    their demographic information as well as associated clinical data. It is designed to
    facilitate access to all relevant data for a person in a single structure.
    """

    NAME: ClassVar = "FullPerson"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="full_persons",
        persistable=False,
    )
    DATA_CLASSES: ClassVar[list[type[ModelNoId]]] = [
        Observation,
        Measurement,
        Specimen,
        MeasurementRelation,
        ObservationPeriod,
        Death,
        VisitOccurrence,
        VisitDetail,
        ConditionOccurrence,
        DrugExposure,
        ProcedureOccurrence,
        DeviceExposure,
        Note,
    ]
    DATA_CLASS_FIELD_MAP: ClassVar[dict[type[ModelNoId], str]] = {
        Observation: "observations",
        Measurement: "measurements",
        Specimen: "specimens",
        MeasurementRelation: "measurement_relations",
        ObservationPeriod: "observation_periods",
        Death: "deaths",
        VisitOccurrence: "visit_occurrences",
        VisitDetail: "visit_details",
        ConditionOccurrence: "condition_occurrences",
        DrugExposure: "drug_exposures",
        ProcedureOccurrence: "procedure_occurrences",
        DeviceExposure: "device_exposures",
        Note: "notes",
    }
    IDENTIFIER_CLASSES: ClassVar[list[type[ModelNoId]]] = [
        ObservationIdentifier,
        MeasurementIdentifier,
        SpecimenIdentifier,
        MeasurementRelationIdentifier,
        ObservationPeriodIdentifier,
        DeathIdentifier,
        VisitOccurrenceIdentifier,
        VisitDetailIdentifier,
        ConditionOccurrenceIdentifier,
        DrugExposureIdentifier,
        ProcedureOccurrenceIdentifier,
        DeviceExposureIdentifier,
        NoteIdentifier,
    ]
    DATA_IDENTIFIER_CLASS_MAP: ClassVar[dict[type[ModelNoId], type[ModelNoId]]] = {
        Observation: ObservationIdentifier,
        Measurement: MeasurementIdentifier,
        Specimen: SpecimenIdentifier,
        MeasurementRelation: MeasurementRelationIdentifier,
        ObservationPeriod: ObservationPeriodIdentifier,
        Death: DeathIdentifier,
        VisitOccurrence: VisitOccurrenceIdentifier,
        VisitDetail: VisitDetailIdentifier,
        ConditionOccurrence: ConditionOccurrenceIdentifier,
        DrugExposure: DrugExposureIdentifier,
        ProcedureOccurrence: ProcedureOccurrenceIdentifier,
        DeviceExposure: DeviceExposureIdentifier,
        Note: NoteIdentifier,
    }
    IDENTIFIER_FIELD_MAP: ClassVar[dict[type[ModelNoId], str]] = {
        ObservationIdentifier: "observation_identifiers",
        MeasurementIdentifier: "measurement_identifiers",
        SpecimenIdentifier: "specimen_identifiers",
        MeasurementRelationIdentifier: "measurement_relation_identifiers",
        ObservationPeriodIdentifier: "observation_period_identifiers",
        DeathIdentifier: "death_identifiers",
        VisitOccurrenceIdentifier: "visit_occurrence_identifiers",
        VisitDetailIdentifier: "visit_detail_identifiers",
        ConditionOccurrenceIdentifier: "condition_occurrence_identifiers",
        DrugExposureIdentifier: "drug_exposure_identifiers",
        ProcedureOccurrenceIdentifier: "procedure_occurrence_identifiers",
        DeviceExposureIdentifier: "device_exposure_identifiers",
        NoteIdentifier: "note_identifiers",
    }

    person: Person = Field(
        description="The person's demographic information. This is the same information as in the Person table in the OMOP CDM."
    )
    person_identifiers: list[PersonIdentifier] = Field(
        default_factory=list,
        description="List of person identifiers associated with the person. There can be multiple if the same person is represented by multiple Person records in the database, e.g. due to merging of records or different source systems.",
    )
    observations: list[Observation] = Field(
        default_factory=list,
        description="List of observations associated with the person.",
    )
    observation_identifiers: list[ObservationIdentifier] = Field(
        default_factory=list,
        description="List of observation identifiers associated with the person.",
    )
    measurements: list[Measurement] = Field(
        default_factory=list,
        description="List of measurements associated with the person.",
    )
    measurement_identifiers: list[MeasurementIdentifier] = Field(
        default_factory=list,
        description="List of measurement identifiers associated with the person.",
    )
    specimens: list[Specimen] = Field(
        default_factory=list,
        description="List of specimens associated with the person.",
    )
    specimen_identifiers: list[SpecimenIdentifier] = Field(
        default_factory=list,
        description="List of specimen identifiers associated with the person.",
    )
    measurement_relations: list[MeasurementRelation] = Field(
        default_factory=list,
        description="List of measurement relations associated with the person.",
    )
    measurement_relation_identifiers: list[MeasurementRelationIdentifier] = Field(
        default_factory=list,
        description="List of measurement relation identifiers associated with the person.",
    )
    observation_periods: list[ObservationPeriod] = Field(
        default_factory=list,
        description="List of observation periods associated with the person.",
    )
    observation_period_identifiers: list[ObservationPeriodIdentifier] = Field(
        default_factory=list,
        description="List of observation period identifiers associated with the person.",
    )
    deaths: list[Death] = Field(
        default_factory=list,
        description="List of death records associated with the person.",
    )
    death_identifiers: list[DeathIdentifier] = Field(
        default_factory=list,
        description="List of death identifiers associated with the person.",
    )
    visit_occurrences: list[VisitOccurrence] = Field(
        default_factory=list,
        description="List of visit occurrences associated with the person.",
    )
    visit_occurrence_identifiers: list[VisitOccurrenceIdentifier] = Field(
        default_factory=list,
        description="List of visit occurrence identifiers associated with the person.",
    )
    visit_details: list[VisitDetail] = Field(
        default_factory=list,
        description="List of visit details associated with the person.",
    )
    visit_detail_identifiers: list[VisitDetailIdentifier] = Field(
        default_factory=list,
        description="List of visit detail identifiers associated with the person.",
    )
    condition_occurrences: list[ConditionOccurrence] = Field(
        default_factory=list,
        description="List of condition occurrences associated with the person.",
    )
    condition_occurrence_identifiers: list[ConditionOccurrenceIdentifier] = Field(
        default_factory=list,
        description="List of condition occurrence identifiers associated with the person.",
    )
    drug_exposures: list[DrugExposure] = Field(
        default_factory=list,
        description="List of drug exposures associated with the person.",
    )
    drug_exposure_identifiers: list[DrugExposureIdentifier] = Field(
        default_factory=list,
        description="List of drug exposure identifiers associated with the person.",
    )
    procedure_occurrences: list[ProcedureOccurrence] = Field(
        default_factory=list,
        description="List of procedure occurrences associated with the person.",
    )
    procedure_occurrence_identifiers: list[ProcedureOccurrenceIdentifier] = Field(
        default_factory=list,
        description="List of procedure occurrence identifiers associated with the person.",
    )
    device_exposures: list[DeviceExposure] = Field(
        default_factory=list,
        description="List of device exposures associated with the person.",
    )
    device_exposure_identifiers: list[DeviceExposureIdentifier] = Field(
        default_factory=list,
        description="List of device exposure identifiers associated with the person.",
    )
    notes: list[Note] = Field(
        default_factory=list,
        description="List of notes associated with the person.",
    )
    note_identifiers: list[NoteIdentifier] = Field(
        default_factory=list,
        description="List of note identifiers associated with the person.",
    )
