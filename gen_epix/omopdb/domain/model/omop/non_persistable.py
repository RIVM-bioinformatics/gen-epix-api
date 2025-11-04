from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model import Model
from gen_epix.fastapp.domain import Entity
from gen_epix.omopdb.domain.model.omop.omop import (
    DrugExposure,
    LocationHistory,
    Measurement,
    Observation,
    Person,
    Specimen,
)


class Subject(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="subjects",
        persistable=False,
    )

    id: UUID | None = Field(default=None, description="The ID of the subject.")
    person: Person | None = Field(
        default=None, description="The person associated with the subject."
    )
    specimen_records: list[Specimen] = Field(
        description="The list of specimen records associated with the subject."
    )
    observation_records: list[Observation] = Field(
        description="The list of observations records associated with the subject."
    )
    measurement_records: list[Measurement] = Field(
        description="The list of measurements records associated with the subject."
    )
    drug_exposure_records: list[DrugExposure] = Field(
        description="The list of drug exposure records associated with the subject."
    )
    location_history_records: list[LocationHistory] = Field(
        description="The list of location history records associated with the subject."
    )
