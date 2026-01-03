from collections.abc import Hashable
from typing import ClassVar, Self
from uuid import UUID

from pydantic import (
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from gen_epix.commondb.domain.model.upload import (
    BaseBatchUploadResult,
    ForUploadMixin,
    UploadResult,
)
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
    def _validate_concept_fields_for_upload(self) -> Self:
        for id_field, int_id_field in self.CONCEPT_FIELD_PAIRS:
            id_value = getattr(self, id_field)
            int_id_value = getattr(self, int_id_field)
            if id_value in {None, NULL_ID} and int_id_value is None:
                raise ValueError(
                    f"Either {id_field} or {int_id_field} must be provided."
                )
        return self


class MeasurementForUpload(Measurement, ForUploadMixin, ConceptFieldsForUploadMixin):
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


class ObservationForUpload(Observation, ForUploadMixin, ConceptFieldsForUploadMixin):
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


class SpecimenForUpload(Specimen, ForUploadMixin, ConceptFieldsForUploadMixin):
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


class PersonForUpload(Person, ForUploadMixin):
    """
    A person, together with any relevant associated data, intended for upload.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "PersonForUpload"

    FOR_UPLOAD_MODEL_CLASS_MAP: ClassVar[dict[type[Model], type[Model]]] = {
        Measurement: MeasurementForUpload,
        Observation: ObservationForUpload,
        Specimen: SpecimenForUpload,
    }

    MODEL_RESULT_FIELD_NAME_MAP: ClassVar[dict[type[Model], str]] = {
        MeasurementForUpload: "measurements",
        ObservationForUpload: "observations",
        SpecimenForUpload: "specimens",
    }

    # Person identification
    person_id: UUID = Field(
        default=NULL_ID,
        description="The id of the person, if available. If not, it must be filled with the null ID. Must be present if external_person_ids are not provided.",
    )
    external_ids: list[ExternalIdentifierForUpload] | None = Field(
        default=None,
        description="List of external person identifiers. Must have at least one element if person_id is not provided.",
    )

    # Associated data
    measurements: list[MeasurementForUpload] | None = Field(
        description="The measurements. If None, this element is not taken into consideration during the upload.",
    )
    observations: list[ObservationForUpload] | None = Field(
        description="The observations. If None, this element is not taken into consideration during the upload.",
    )
    specimens: list[SpecimenForUpload] | None = Field(
        description="The specimens. If None, this element is not taken into consideration during the upload.",
    )
    # TODO: add other associated data types when needed

    @field_validator("external_ids", mode="after")
    def _validate_associated_ids(
        cls, value: list[Hashable] | None
    ) -> list[Hashable] | None:
        if value is None:
            return None
        if len(set(value)) != len(value):
            raise ValueError("Associated IDs must be unique.")
        return value

    @model_validator(mode="after")
    def _validate_person_for_upload(self) -> Self:
        # Verify that external_ids contains no duplicates
        if self.external_ids is not None and len(self.external_ids) != len(
            set(self.external_ids)
        ):
            raise ValueError("external_ids must not contain duplicates.")
        # TODO: verify that each list of results is unique, e.g. no identical measurements
        # Verify that result person_ids are consistent with person id
        person_id = NULL_ID if self.id is None else self.id
        for field_name in self.MODEL_RESULT_FIELD_NAME_MAP:
            items = getattr(self, field_name)
            for item in items or []:
                if item.person_id == NULL_ID or item.person_id == person_id:
                    continue
                raise ValueError(
                    f"person_id of {field_name} is not the null ID, while the person id variable is not provided."
                )
        return self


class PersonUploadResult(UploadResult):
    """
    The result of uploading a single person.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "PersonUploadResult"

    CHILD_RESULT_FIELD_NAMES: ClassVar = []
    CHILD_RESULT_LIST_FIELD_NAMES: ClassVar = [
        "external_id_results",
    ] + list(PersonForUpload.MODEL_RESULT_FIELD_NAME_MAP.values())

    external_ids: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the external identifiers associated with the person, if any were provided, in the same order as provided.",
    )
    measurements: list[UploadResult] | None = Field(
        description="The results of uploading the individual measurements, if any were provided, in the same order as provided."
    )
    observations: list[UploadResult] | None = Field(
        description="The results of uploading the individual observations, if any were provided, in the same order as provided."
    )
    specimens: list[UploadResult] | None = Field(
        description="The results of uploading the individual specimens, if any were provided, in the same order as provided."
    )


class PersonBatchForUpload(Model):
    """
    A set of persons intended for upload, together with any new reference data required
    for the storage of these data.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "PersonBatchForUpload"

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

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        # Verify that persons contain no duplicate person_ids
        person_ids = [x.id for x in self.persons if x.id is not None]
        if len(person_ids) != len(set(person_ids)):
            raise ValueError("Persons must not contain duplicate person IDs.")
        # Verify that persons contains no duplicate external_ids
        all_external_ids = []
        for person in self.persons:
            if person.external_ids is not None:
                all_external_ids.extend(person.external_ids)
        if len(all_external_ids) != len(set(all_external_ids)):
            raise ValueError("Persons must not contain duplicate external_ids.")
        return self


class PersonBatchUploadResult(BaseBatchUploadResult):
    """
    The result of uploading a batch of persons.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "PersonBatchUploadResult"

    CHILD_RESULT_LIST_FIELD_NAMES: ClassVar = ["persons"]

    persons: list[PersonUploadResult] = Field(
        description="The results of uploading the individual persons, in the same order as provided."
    )
