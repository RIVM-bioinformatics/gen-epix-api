from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, computed_field, field_serializer, model_validator

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
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
    ENTITY: ClassVar = Entity(persistable=False)

    id: UUID | None = Field(default=None, description="The ID of the subject.")
    person: Person | None = Field(
        default=None, description="The person associated with the subject."
    )
    specimen_records: list[Specimen] = Field(
        description="The specimen records associated with the subject."
    )
    observation_records: list[Observation] = Field(
        description="The observations records associated with the subject."
    )
    measurement_records: list[Measurement] = Field(
        description="The measurements records associated with the subject."
    )
    drug_exposure_records: list[DrugExposure] = Field(
        description="The drug exposure records associated with the subject."
    )
    location_history_records: list[LocationHistory] = Field(
        description="The location history records associated with the subject."
    )


class ConceptFieldsForUploadMixin:
    CONCEPT_FIELD_PAIRS: ClassVar[list[tuple[str, str]]] = []

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        for id_field, int_id_field in self.CONCEPT_FIELD_PAIRS:
            id_value = getattr(self, id_field)
            int_id_value = getattr(self, int_id_field)
            if id_value in {None, NULL_ID} and int_id_value is None:
                raise ValueError(
                    f"Either {id_field} or {int_id_field} must be provided."
                )
        return self


class MeasurementForUpload(Measurement, ConceptFieldsForUploadMixin):
    """
    An measurement record intended for upload. Equal to a Measurement, with
    additional variables. The different concepts can be given either as their UUID
    or integer ID to facilitate the upload operation where applicable.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "MeasurementForUpload"
    CONCEPT_FIELD_PAIRS: ClassVar[list[tuple[str, str]]] = [
        ("measurement_concept_id", "measurement_concept_int_id"),
        ("measurement_type_concept_id", "measurement_type_concept_int_id"),
        ("operator_concept_id", "operator_concept_int_id"),
        ("value_as_concept_id", "value_as_concept_int_id"),
        ("unit_concept_id", "unit_concept_int_id"),
        ("measurement_source_concept_id", "measurement_source_concept_int_id"),
    ]

    person_id: UUID = Field(
        default=NULL_ID,
        description="The id of the person associated with the measurement. If not available, it must be filled with the null ID.",
    )
    measurement_id: UUID = Field(
        default=NULL_ID,
        description="The id of the measurement.",
    )
    measurement_concept_id: UUID = Field(
        default=NULL_ID,
        description="The concept ID of the measurement. If not available, it must be filled with the null ID.",
    )
    measurement_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the measurement_concept_id. Must be provided if the latter is not provided.",
    )
    measurement_type_concept_id: UUID = Field(
        default=NULL_ID,
        description="The type concept ID of the measurement. If not available, it must be filled with the null ID.",
    )
    measurement_type_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the measurement_type_concept_id. Must be provided if the latter is not provided.",
    )
    operator_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the operator_concept_id.",
    )
    value_as_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the value_as_concept_id.",
    )
    unit_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the unit_concept_id.",
    )
    measurement_source_concept_id: UUID = Field(
        default=NULL_ID,
        description="The source concept ID of the measurement. If not available, it must be filled with the null ID.",
    )
    measurement_source_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the measurement_source_concept_id.",
    )
    derived_from_specimen_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. The specimen from which this measurement was derived.\nETL conventions:\nNone",
    )

    @field_serializer(*[x[0] for x in CONCEPT_FIELD_PAIRS])
    def _serialize_null_id(self, value: UUID | None) -> UUID | None:
        """Serialize NULL_ID as None for concept ID fields."""
        return None if value == NULL_ID else value


class ObervationForUpload(Observation, ConceptFieldsForUploadMixin):
    """
    An observation record intended for upload. Equal to an Observation, with
    additional variables. The different concepts can be given either as their UUID
    or integer ID to facilitate the upload operation where applicable.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "ObservationForUpload"
    CONCEPT_FIELD_PAIRS: ClassVar[list[tuple[str, str]]] = [
        ("observation_concept_id", "observation_concept_int_id"),
        ("observation_type_concept_id", "observation_type_concept_int_id"),
        ("value_as_concept_id", "value_as_concept_int_id"),
        ("qualifier_concept_id", "qualifier_concept_int_id"),
        ("unit_concept_id", "unit_concept_int_id"),
        ("observation_source_concept_id", "observation_source_concept_int_id"),
        ("obs_event_field_concept_id", "obs_event_field_concept_int_id"),
    ]

    person_id: UUID = Field(
        default=NULL_ID,
        description="The id of the person associated with the observation. If not available, it must be filled with the null ID.",
    )
    observation_id: UUID = Field(
        default=NULL_ID,
        description="The id of the observation.",
    )
    observation_concept_id: UUID = Field(
        default=NULL_ID,
        description="The concept ID of the observation. If not available, it must be filled with the null ID.",
    )
    observation_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the observation_concept_id. Must be provided if the latter is not provided.",
    )
    observation_type_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the observation_type_concept_id. Must be provided if the latter is not provided.",
    )
    value_as_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the value_as_concept_id.",
    )
    qualifier_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the qualifier_concept_id.",
    )
    unit_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the unit_concept_id.",
    )
    observation_source_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the observation_source_concept_id.",
    )
    obs_event_field_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the obs_event_field_concept_id.",
    )

    @field_serializer(*[x[0] for x in CONCEPT_FIELD_PAIRS])
    def _serialize_null_id(self, value: UUID | None) -> UUID | None:
        """Serialize NULL_ID as None for concept ID fields."""
        return None if value == NULL_ID else value


class SpecimenForUpload(Specimen, ConceptFieldsForUploadMixin):
    """
    A specimen record intended for upload. Equal to a Specimen, with
    additional variables. The different concepts can be given either as their UUID
    or integer ID to facilitate the upload operation where applicable.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "SpecimenForUpload"
    CONCEPT_FIELD_PAIRS: ClassVar[list[tuple[str, str]]] = [
        ("specimen_concept_id", "specimen_concept_int_id"),
        ("specimen_type_concept_id", "specimen_type_concept_int_id"),
        ("unit_concept_id", "unit_concept_int_id"),
        ("anatomic_site_concept_id", "anatomic_site_concept_int_id"),
        ("disease_status_concept_id", "disease_status_concept_int_id"),
        ("derived_from_specimen_concept_id", "derived_from_specimen_concept_int_id"),
    ]

    person_id: UUID = Field(
        default=NULL_ID,
        description="The id of the person associated with the specimen. If not available, it must be filled with the null ID.",
    )
    specimen_id: UUID = Field(
        default=NULL_ID,
        description="The id of the specimen.",
    )
    specimen_concept_id: UUID = Field(
        default=NULL_ID,
        description="The concept ID of the specimen. If not available, it must be filled with the null ID.",
    )
    specimen_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the specimen_concept_id. Must be provided if the latter is not provided.",
    )
    specimen_type_concept_id: UUID = Field(
        default=NULL_ID,
        description="The type concept ID of the specimen. If not available, it must be filled with the null ID.",
    )
    specimen_type_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the specimen_type_concept_id. Must be provided if the latter is not provided.",
    )
    unit_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the unit_concept_id.",
    )
    anatomic_site_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the anatomic_site_concept_id.",
    )
    disease_status_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the disease_status_concept_id.",
    )
    derived_from_specimen_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the derived_from_specimen_concept_id.",
    )

    @field_serializer(*[x[0] for x in CONCEPT_FIELD_PAIRS])
    def _serialize_null_id(self, value: UUID | None) -> UUID | None:
        """Serialize NULL_ID as None for concept ID fields."""
        return None if value == NULL_ID else value


class PersonForUpload(Person):
    """
    A person, together with any relevant associated data, intended for upload.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "PersonForUpload"
    RESULT_FIELD_NAMES: ClassVar[list[str]] = [
        "measurements",
        "observations",
        "specimens",
    ]

    # Person identification
    person_id: UUID = Field(
        default=NULL_ID,
        description="The id of the person, if available. If not, it must be filled with the null ID. Must be present if external_person_ids are not provided.",
    )
    external_ids: list[ExternalIdentifierForUpload] | None = Field(
        default=None,
        description="List of external person identifiers. Must have at least one element if person_id is not provided.",
    )
    data_collection_ids: list[UUID] | None = Field(
        default=None,
        description="The data collection IDs that the person should be put in.",
    )

    # Associated data
    measurements: list[MeasurementForUpload] | None = Field(
        description="The measurements.",
    )
    observations: list[ObervationForUpload] | None = Field(
        description="The observations.",
    )
    specimens: list[SpecimenForUpload] | None = Field(
        description="The specimens.",
    )
    # TODO: add other associated data types when needed

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        if self.person_id is None or self.person_id == NULL_ID:
            return self
        for field_name in self.RESULT_FIELD_NAMES:
            items = getattr(self, field_name)
            for item in items or []:
                if item.person_id in (None, NULL_ID):
                    continue
                raise ValueError(
                    f"person_id of {field_name} is not None or the null ID, while the person_id variable is not provided."
                )
        return self


class PersonSetForUpload(Model):
    """
    A set of persons intended for upload, together with any new reference data required
    for the storage of these data.
    """

    ENTITY: ClassVar = Entity(persistable=False)

    persons: list[PersonForUpload] = Field(
        description="The persons intended for upload.",
    )

    # New reference data required to enable storage of the person data

    @computed_field
    @property
    def has_measurements(self) -> bool:
        """Indicates whether there are any measurements in the person set."""
        return any(len(x.measurements or []) > 0 for x in self.persons)

    @computed_field
    @property
    def has_observations(self) -> bool:
        """Indicates whether there are any observations in the person set."""
        return any(len(x.observations or []) > 0 for x in self.persons)

    @computed_field
    @property
    def has_specimens(self) -> bool:
        """Indicates whether there are any specimens in the person set."""
        return any(len(x.specimens or []) > 0 for x in self.persons)

    # TODO: add model validator to make sure person are unique
