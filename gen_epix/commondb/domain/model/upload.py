import datetime
import uuid
from functools import cached_property
from typing import Callable, ClassVar, Self
from uuid import UUID

from pydantic import BaseModel, Field, computed_field, field_serializer, model_validator

from gen_epix.commondb.domain.enum import UploadStatus, UploadStatusSet
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import LogLevel, LogLevelSet


class UploadLogItem(BaseModel):
    """
    Represents a log item for an upload result, capturing timestamped messages
    with optional codes and severity levels.
    """

    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="The UTC timestamp when the log item was created.",
    )
    code: str = Field(
        description="A code categorizing the log item.",
    )
    message: str = Field(
        description="The log message describing the event or information.",
    )
    severity: LogLevel = Field(
        description="The severity level of the log item.",
    )


class UploadResult(Model):
    """
    Represents the result of an upload operation, including status and logs.
    """

    ENTITY: ClassVar = Entity(persistable=False)

    # List of field names in child classes that contain single results for generic model validation
    CHILD_RESULT_FIELD_NAMES: ClassVar[list[str]] = []
    # List of field names in child classes that each contains each a list of results for generic model validation
    CHILD_RESULT_LIST_FIELD_NAMES: ClassVar[list[str]] = []

    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the specific object instance that this result pertains to, if applicable. E.g. the object that was created or updated as part of the upload.",
    )
    status: UploadStatus = Field(
        default=UploadStatus.PENDING,
        description="The status of the upload operation. If not successful, error information must be provided in the logs.",
    )
    logs: list[UploadLogItem] = Field(
        default_factory=list,
        description="A list of log items capturing messages and events that occurred during the upload operation.",
    )

    @computed_field
    @cached_property
    def n_items_processed(self) -> int:
        """The number of records processed during the upload operation."""
        n = int(self.status != UploadStatus.PENDING)  # Count self if not pending
        for field_name in self.CHILD_RESULT_FIELD_NAMES:
            child_result: UploadResult | None = getattr(self, field_name, None)
            if child_result is not None:
                n += child_result.n_items_processed
        for field_name in self.CHILD_RESULT_LIST_FIELD_NAMES:
            child_results: list[UploadResult] = getattr(self, field_name, None) or []
            for child_result in child_results:
                n += child_result.n_items_processed
        return n

    @computed_field
    @cached_property
    def n_created(self) -> int:
        """Number of results, including self, with status CREATED."""
        return self.get_n_results_with_status(UploadStatus.CREATED)

    @computed_field
    @cached_property
    def n_updated(self) -> int:
        """Number of results, including self, with status UPDATED."""
        return self.get_n_results_with_status(UploadStatus.UPDATED)

    @computed_field
    @cached_property
    def n_skipped(self) -> int:
        """Number of results, including self, with status SKIPPED."""
        return self.get_n_results_with_status(UploadStatus.SKIPPED)

    @computed_field
    @cached_property
    def n_failed(self) -> int:
        """Number of results, including self, with status FAILED."""
        return self.get_n_results_with_status(UploadStatus.FAILED)

    @computed_field
    @cached_property
    def n_pending(self) -> int:
        """Number of results, including self, with status PENDING."""
        return self.get_n_results_with_status(UploadStatus.PENDING)

    def get_n_results_with_status(
        self, status: UploadStatus, include_self: bool = True
    ) -> int:
        """Check if any sub-results have the specified status."""
        n = int(include_self and self.status == status)
        for field_name in self.CHILD_RESULT_FIELD_NAMES:
            child_result: UploadResult | None = getattr(self, field_name, None)
            if child_result is not None and child_result.status == status:
                n += 1
        for field_name in self.CHILD_RESULT_LIST_FIELD_NAMES:
            child_results: list[UploadResult] = getattr(self, field_name, None) or []
            for child_result in child_results:
                if child_result.status == status:
                    n += 1
        return n

    @model_validator(mode="after")
    def _validate_upload_result(self) -> Self:
        """Validate upload result consistency."""
        has_errors = any(
            x.severity in LogLevelSet.ERROR_OR_WORSE.value for x in self.logs
        )
        if self.status in UploadStatusSet.NOT_FAILED.value:
            if has_errors:
                raise ValueError("Successful results cannot have error information")
        elif not has_errors:
            raise ValueError("Failed results must include error information")
        return self

    def add_error(
        self,
        code: str,
        message: str,
    ) -> None:
        """Add an error log item."""
        self.logs.append(
            UploadLogItem(code=code, message=message, severity=LogLevel.ERROR)
        )
        self.status = UploadStatus.FAILED

    def add_warning(
        self,
        code: str,
        message: str,
    ) -> None:
        """Add a warning log item."""
        self.logs.append(
            UploadLogItem(code=code, message=message, severity=LogLevel.WARN)
        )

    def add_info(
        self,
        code: str,
        message: str,
    ) -> None:
        """Add an info log item."""
        self.logs.append(
            UploadLogItem(code=code, message=message, severity=LogLevel.INFO)
        )

    def has_errors(self) -> bool:
        """Check if there are any error log items."""
        return any(log.severity == LogLevel.ERROR for log in self.logs)

    def has_warnings(self) -> bool:
        """Check if there are any warning log items."""
        return any(log.severity == LogLevel.WARN for log in self.logs)

    def has_infos(self) -> bool:
        """Check if there are any info log items."""
        return any(log.severity == LogLevel.INFO for log in self.logs)

    def has_log_code(self, code: str) -> bool:
        """Check if any log item has the specified code."""
        return any(log.code == code for log in self.logs)


class BaseBatchUploadResult(UploadResult):
    """
    Base class for upload results corresponding to a complete batch of objects uploaded.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "BaseBatchUploadResult"

    batch_id: UUID = Field(
        description="The unique identifier for the upload batch that this result belongs to.",
    )


class BaseBatchForUpload(Model):
    """
    Base class for batches of objects to be uploaded. A batch is intended as a single
    unit of work for an upload operation and as such to be processed atomically.
    """

    id: UUID = Field(
        default_factory=uuid.uuid4,
        description="The unique identifier for the upload batch.",
    )
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="The UTC timestamp when the upload batch was created.",
    )

    @field_serializer("*_id", "id", mode="wrap", check_fields=False)
    def _serialize_id_fields(self, value: UUID, serializer: Callable) -> str:
        """Generic UUID field serializer for the id field and all *_id fields."""
        if isinstance(value, UUID):
            return str(value)
        return serializer(value)


class ForUploadMixin:
    """Mixin for models representing objects to be uploaded."""

    is_new_id: bool = Field(
        default=False,
        description="Indicates whether the model instance is both new (not yet stored) and its ID is assigned outside the system, e.g. for having the same IDs between different environments.",
    )

    @model_validator(mode="after")
    def _validate_for_upload(self) -> Self:
        """
        Validate ForUploadMixin consistency. Assumes that the inheriting model also has an 'id' field.
        """
        if not hasattr(self, "id"):
            return self
        if self.is_new_id and getattr(self, "id") is None:
            raise ValueError("is_new_id cannot be True when id is None")
        return self
