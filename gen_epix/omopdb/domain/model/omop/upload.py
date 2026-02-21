from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, computed_field, field_serializer, model_validator

from gen_epix.commondb.domain.enum import IdentifierType
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload,
    BaseBatchUploadResult,
    DataIssue,
    ExternalIdentifiersMixin,
    IsNewIdMixin,
    ParentForUpload,
    ParentUploadResult,
    UploadResult,
)
from gen_epix.fastapp.domain import Entity
from gen_epix.omopdb.domain.model.omop.clinical_data import (
    Measurement,
    MeasurementRelation,
    Observation,
    Person,
    Specimen,
)
from gen_epix.util import copy_model_field


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


class MeasurementForUpload(Measurement, IsNewIdMixin, ConceptFieldsForUploadMixin):
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


class ObservationForUpload(Observation, IsNewIdMixin, ConceptFieldsForUploadMixin):
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


class SpecimenForUpload(
    Specimen, IsNewIdMixin, ExternalIdentifiersMixin, ConceptFieldsForUploadMixin
):
    """
    A specimen record intended for upload. Equal to a Specimen, with
    additional variables. The different concepts can be given either as their UUID
    or integer ID to facilitate the upload operation where applicable.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "SpecimenForUpload"
    EXTERNAL_IDENTIFIER_TYPE: ClassVar = IdentifierType.SAMPLE
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


class MeasurementRelationForUpload(
    MeasurementRelation, IsNewIdMixin, ConceptFieldsForUploadMixin
):
    """
    A measurement relation record intended for upload. Equal to a MeasurementRelation, with
    additional variables.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "MeasurementRelationForUpload"
    CONCEPT_FIELD_PAIRS: ClassVar[list[tuple[str, str]]] = [
        (
            "measurement_relation_concept_id",
            "measurement_relation_concept_int_id",
        ),
    ]

    measurement_relation_id: UUID = Field(
        default=NULL_ID,
        description="The id of the measurement relation. If not available, it must be filled with the null ID.",
    )
    from_measurement_id: UUID = Field(
        default=NULL_ID,
        description="The measurement from which the to measurement was derived. If not available, it must be filled with the null ID.",
    )
    to_measurement_id: UUID = Field(
        default=NULL_ID,
        description="The measurement that was derived. If not available, it must be filled with the null ID.",
    )
    measurement_relation_concept_id: UUID = Field(
        default=NULL_ID,
        description="The Concept Id that represents the relationship between the from and to measurement. If not available, it must be filled with the null ID.",
    )
    measurement_relation_concept_int_id: int | None = Field(
        default=None,
        description="The corresponding integer concept ID of the measurement_relation_concept_id. Must be provided if the latter is not provided.",
    )


class PersonForUpload(ParentForUpload):
    """
    A person, together with any relevant associated data, intended for upload.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "PersonForUpload"

    EXTERNAL_IDENTIFIER_TYPE: ClassVar = IdentifierType.PERSON
    PARENT_CLASS: ClassVar = Person
    PARENT_FIELD_NAME: ClassVar = "person"
    CHILDREN_FIELD_NAME_MAP: ClassVar = {
        Measurement: "measurements",
        Observation: "observations",
        Specimen: "specimens",
        MeasurementRelation: "measurement_relations",
    }
    CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar = {
        Measurement: MeasurementForUpload,
        Observation: ObservationForUpload,
        Specimen: SpecimenForUpload,
        MeasurementRelation: MeasurementRelationForUpload,
    }
    CHILD_PARENT_ID_FIELD_NAME_MAP: ClassVar = {
        x: "person_id" for x in CHILD_FOR_UPLOAD_CLASS_MAP.keys()
    }

    # Parent
    person: Person | None = Field(
        default=None,
        description="The person model itself, if to be created or updated as a whole.",
    )

    # Children
    measurements: list[MeasurementForUpload] | None = Field(
        default=None,
        description="The measurements. If None, this element is not taken into consideration during the upload.",
    )
    observations: list[ObservationForUpload] | None = Field(
        default=None,
        description="The observations. If None, this element is not taken into consideration during the upload.",
    )
    specimens: list[SpecimenForUpload] | None = Field(
        default=None,
        description="The specimens. If None, this element is not taken into consideration during the upload.",
    )
    measurement_relations: list[MeasurementRelationForUpload] | None = Field(
        default=None,
        description="The measurement relations. If None, this element is not taken into consideration during the upload.",
    )
    # TODO: add other associated data types when needed


class PersonDataIssue(DataIssue):
    pass


class PersonUploadResult(ParentUploadResult):
    """
    The result of uploading a single person.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "PersonUploadResult"

    PARENT_FOR_UPLOAD_CLASS: ClassVar = PersonForUpload

    data_issues: list[PersonDataIssue] = copy_model_field(
        ParentUploadResult, "data_issues"
    )

    measurements: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the individual measurements, if any were provided, in the same order as provided.",
    )
    observations: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the individual observations, if any were provided, in the same order as provided.",
    )
    specimens: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the individual specimens, if any were provided, in the same order as provided.",
    )
    measurement_relations: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the individual measurement relations, if any were provided, in the same order as provided.",
    )


class PersonBatchForUpload(BaseBatchForUpload):
    """
    A set of persons intended for upload, together with any new reference data required
    for the storage of these data.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "PersonBatchForUpload"

    PARENT_FOR_UPLOAD_CLASS: ClassVar = PersonForUpload  # type: ignore[assignment]
    PARENTS_FOR_UPLOAD_FIELD_NAME: ClassVar = "persons"

    persons: list[PersonForUpload] = Field(
        description="The persons intended for upload.",
    )

    # New reference data required to enable storage of the person data

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_measurements(self) -> bool:
        """Indicates whether there are any measurements in the person set."""
        return any(len(x.measurements or []) > 0 for x in self.persons)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_observations(self) -> bool:
        """Indicates whether there are any observations in the person set."""
        return any(len(x.observations or []) > 0 for x in self.persons)

    @computed_field  # type: ignore[prop-decorator]
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
        # Verify that persons contains no duplicate external_identifiers
        all_external_identifiers = []
        for person in self.persons:
            if person.external_identifiers is not None:
                all_external_identifiers.extend(person.external_identifiers)
        if len(all_external_identifiers) != len(set(all_external_identifiers)):
            raise ValueError("Persons must not contain duplicate external_identifiers.")
        return self


class PersonBatchUploadResult(BaseBatchUploadResult):
    """
    The result of uploading a batch of persons.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "PersonBatchUploadResult"

    BATCH_FOR_UPLOAD_CLASS: ClassVar = PersonBatchForUpload  # type: ignore[assignment]
    PARENT_RESULT_CLASS: ClassVar = PersonUploadResult  # type: ignore[assignment]

    persons: list[PersonUploadResult] = Field(
        description="The results of uploading the individual persons, in the same order as provided."
    )
