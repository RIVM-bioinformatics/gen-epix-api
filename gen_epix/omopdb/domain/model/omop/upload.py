from typing import ClassVar
from uuid import UUID

from pydantic import Field, computed_field

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload,
    BaseBatchUploadResult,
    DataIssue,
    IdentifiersMixin,
    ParentForUpload,
    ParentUploadResult,
    UploadResult,
)
from gen_epix.omopdb.domain.model.omop import clinical_data as model
from gen_epix.util import copy_model_field


class MeasurementForUpload(model.Measurement, IdentifiersMixin):
    """
    An measurement record intended for upload. Equal to a Measurement, with
    additional variables.
    """

    ENTITY: ClassVar = model.Measurement.model_entity().clone(
        update={"persistable": False}
    )
    NAME: ClassVar = "MeasurementForUpload"
    IDENTIFIER_CLASS: ClassVar = model.MeasurementIdentifier

    person_id: UUID = Field(
        default=NULL_ID,
        description="The id of the person associated with the measurement. If not available, it must be filled with the null ID.",
    )
    measurement_id: UUID = Field(
        default=NULL_ID,
        description="The id of the measurement.",
    )


class ObservationForUpload(model.Observation, IdentifiersMixin):
    """
    An observation record intended for upload. Equal to an Observation, with
    additional variables.
    """

    ENTITY: ClassVar = model.Observation.model_entity().clone(
        update={"persistable": False}
    )
    NAME: ClassVar = "ObservationForUpload"
    IDENTIFIER_CLASS: ClassVar = model.ObservationIdentifier

    person_id: UUID = Field(
        default=NULL_ID,
        description="The id of the person associated with the observation. If not available, it must be filled with the null ID.",
    )
    observation_id: UUID = Field(
        default=NULL_ID,
        description="The id of the observation.",
    )


class SpecimenForUpload(model.Specimen, IdentifiersMixin):
    """
    A specimen record intended for upload. Equal to a Specimen, with
    additional variables.
    """

    ENTITY: ClassVar = model.Specimen.model_entity().clone(
        update={"persistable": False}
    )
    NAME: ClassVar = "SpecimenForUpload"
    IDENTIFIER_CLASS: ClassVar = model.SpecimenIdentifier

    person_id: UUID = Field(
        default=NULL_ID,
        description="The id of the person associated with the specimen. If not available, it must be filled with the null ID.",
    )
    specimen_id: UUID = Field(
        default=NULL_ID,
        description="The id of the specimen.",
    )


class MeasurementRelationForUpload(model.MeasurementRelation, IdentifiersMixin):
    """
    A measurement relation record intended for upload. Equal to a MeasurementRelation, with
    additional variables.
    """

    ENTITY: ClassVar = model.MeasurementRelation.model_entity().clone(
        update={"persistable": False}
    )
    NAME: ClassVar = "MeasurementRelationForUpload"
    IDENTIFIER_CLASS: ClassVar = model.MeasurementRelationIdentifier

    measurement_relation_id: UUID = Field(
        default=NULL_ID,
        description="The id of the measurement relation. If not available, it must be filled with the null ID.",
    )


class PersonForUpload(ParentForUpload):
    """
    A person, together with any relevant associated data, intended for upload.
    """

    ENTITY: ClassVar = ParentForUpload.model_entity().clone(
        update={"persistable": False}
    )
    NAME: ClassVar = "PersonForUpload"
    IDENTIFIER_CLASS: ClassVar = model.PersonIdentifier
    PARENT_CLASS: ClassVar = model.Person
    PARENT_FIELD_NAME: ClassVar = "person"
    CHILDREN_FIELD_NAME_MAP: ClassVar = {
        model.Measurement: "measurements",
        model.Observation: "observations",
        model.Specimen: "specimens",
        model.MeasurementRelation: "measurement_relations",
    }
    CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar = {
        model.Measurement: MeasurementForUpload,
        model.Observation: ObservationForUpload,
        model.Specimen: SpecimenForUpload,
        model.MeasurementRelation: MeasurementRelationForUpload,
    }
    CHILD_PARENT_ID_FIELD_NAME_MAP: ClassVar = {
        x: "person_id" for x in CHILD_FOR_UPLOAD_CLASS_MAP.keys()
    }

    # Parent
    person: model.Person | None = Field(
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

    ENTITY: ClassVar = ParentUploadResult.model_entity().clone()
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

    ENTITY: ClassVar = BaseBatchForUpload.model_entity().clone()
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


class PersonBatchUploadResult(BaseBatchUploadResult):
    """
    The result of uploading a batch of persons.
    """

    ENTITY: ClassVar = BaseBatchForUpload.model_entity().clone()
    NAME: ClassVar = "PersonBatchUploadResult"

    BATCH_FOR_UPLOAD_CLASS: ClassVar = PersonBatchForUpload  # type: ignore[assignment]
    PARENT_RESULT_CLASS: ClassVar = PersonUploadResult  # type: ignore[assignment]

    persons: list[PersonUploadResult] = Field(
        description="The results of uploading the individual persons, in the same order as provided."
    )
