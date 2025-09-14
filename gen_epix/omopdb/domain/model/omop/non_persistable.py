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

    id: UUID | None
    person: Person | None = Field(
        default=None,
    )
    specimen_records: list[Specimen]
    observation_records: list[Observation]
    measurement_records: list[Measurement]
    drug_exposure_records: list[DrugExposure]
    location_history_records: list[LocationHistory]
