from typing import ClassVar

from pydantic import Field

from gen_epix.fastapp.domain.entity import Entity
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    Measurement,
    MeasurementRelation,
    Observation,
    Person,
    Specimen,
)


class FullPerson(Person):
    """
    This class represents a comprehensive view of a person in the OMOP CDM, including
    their demographic information as well as associated clinical data such as
    observations, measurements, specimens, and measurement relations. It is designed to
    facilitate access to all relevant data for a person in a single structure.
    """

    NAME: ClassVar = "FullPerson"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="full_persons",
        persistable=False,
    )

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
