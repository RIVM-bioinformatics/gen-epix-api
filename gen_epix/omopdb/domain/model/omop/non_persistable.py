from datetime import datetime
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model.base import ModelNoId
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.omopdb.domain.model.base import Model
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    ConditionOccurrence,
    Death,
    DeviceExposure,
    DrugExposure,
    Measurement,
    MeasurementRelation,
    Note,
    Observation,
    ObservationPeriod,
    Person,
    ProcedureOccurrence,
    Specimen,
    VisitDetail,
    VisitOccurrence,
)


class PersonQuery(Model):
    """
    A query for retrieving persons based on their demographic information. All
    constraints are optional, but at least some must be provided, and the query will
    match any person that matches all of the provided criteria.
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


class FullPerson(Person):
    """
    This class represents a comprehensive view of a person in the OMOP CDM, including
    their demographic information as well as associated clinical data. It is designed to
    facilitate access to all relevant data for a person in a single structure.
    """

    NAME: ClassVar = "FullPerson"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="full_persons",
        persistable=False,
    )
    LINKED_DATA_CLASSES: ClassVar[list[type[ModelNoId]]] = [
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
    LINKED_DATA_CLASS_FIELD_MAP: ClassVar[dict[type[ModelNoId], str]] = {
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

    observations: list[Observation] = Field(
        default_factory=list,
        description="List of observations associated with the person.",
    )
    measurements: list[Measurement] = Field(
        default_factory=list,
        description="List of measurements associated with the person.",
    )
    specimens: list[Specimen] = Field(
        default_factory=list,
        description="List of specimens associated with the person.",
    )
    measurement_relations: list[MeasurementRelation] = Field(
        default_factory=list,
        description="List of measurement relations associated with the person.",
    )
    observation_periods: list[ObservationPeriod] = Field(
        default_factory=list,
        description="List of observation periods associated with the person.",
    )
    deaths: list[Death] = Field(
        default_factory=list,
        description="List of death records associated with the person.",
    )
    visit_occurrences: list[VisitOccurrence] = Field(
        default_factory=list,
        description="List of visit occurrences associated with the person.",
    )
    visit_details: list[VisitDetail] = Field(
        default_factory=list,
        description="List of visit details associated with the person.",
    )
    condition_occurrences: list[ConditionOccurrence] = Field(
        default_factory=list,
        description="List of condition occurrences associated with the person.",
    )
    drug_exposures: list[DrugExposure] = Field(
        default_factory=list,
        description="List of drug exposures associated with the person.",
    )
    procedure_occurrences: list[ProcedureOccurrence] = Field(
        default_factory=list,
        description="List of procedure occurrences associated with the person.",
    )
    device_exposures: list[DeviceExposure] = Field(
        default_factory=list,
        description="List of device exposures associated with the person.",
    )
    notes: list[Note] = Field(
        default_factory=list,
        description="List of notes associated with the person.",
    )
