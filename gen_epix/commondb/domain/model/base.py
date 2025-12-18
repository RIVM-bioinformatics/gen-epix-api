import datetime
import uuid
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix import fastapp
from gen_epix.fastapp.domain.entity import Entity


class Model(fastapp.Model):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the object.",
    )


class BatchForUpload(Model):
    """
    Base class for batches of objects to be uploaded. A batch is intended as a single
    unit of work for an upload operation and as such to be processed atomically.
    """

    ENTITY: ClassVar = Entity(persistable=False)

    id: UUID = Field(
        default_factory=uuid.uuid4,
        description="The unique identifier for the upload batch.",
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="The timestamp when the upload batch was created.",
    )


class UploadResult(Model):
    """Base class for upload results."""

    ENTITY: ClassVar = Entity(persistable=False)

    # List of field names that are single sub-results for generic model validation
    SUB_RESULT_FIELD_NAMES: ClassVar[list[str]] = []
    # List of field names that are each a list of sub-results for generic model validation
    SUB_RESULT_LIST_FIELD_NAMES: ClassVar[list[str]] = []

    id: UUID = Field(
        default_factory=uuid.uuid4,
        description="The unique identifier for the upload batch result.",
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="The timestamp when the upload result was created.",
    )
    batch_id: UUID = Field(
        description="The unique identifier for the upload batch that this result belongs to.",
    )
    instance_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the specific object instance that this result pertains to, if applicable. E.g. the object that was created or updated as part of the upload.",
    )
    success: bool = Field(
        default=False,
        description="Whether the upload was successful for the scope that the result covers.",
    )
    error_message: str | None = Field(
        default=None,
        description="An message providing additional information about the upload result, if applicable and available.",
    )
    error_codes: list[str] | None = Field(
        description="A set of error codes indicating reasons for upload failure, if applicable and available.",
    )

    @model_validator(mode="after")
    def _validate_upload_result(self) -> Self:
        """
        Generic validation for upload results with sub-results.
        """
        if not self.SUB_RESULT_FIELD_NAMES and not self.SUB_RESULT_LIST_FIELD_NAMES:
            return self
        # Calculate success based on sub-results
        self.success = all(
            getattr(getattr(self, x), "success", True)
            for x in self.SUB_RESULT_FIELD_NAMES
        ) and all(
            all(y.success for y in getattr(self, x) or [])
            for x in self.SUB_RESULT_LIST_FIELD_NAMES
        )
        return self
