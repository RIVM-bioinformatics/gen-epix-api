import datetime
import uuid
from functools import cached_property
from typing import Callable, ClassVar, Self
from uuid import UUID

from pydantic import Field, computed_field, field_serializer, model_validator

from gen_epix import fastapp
from gen_epix.commondb.domain.enum import UploadStatus
from gen_epix.fastapp.domain import Entity
from gen_epix.fastapp.domain.entity import Entity


class Model(fastapp.Model):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the object.",
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


class UploadResult(Model):
    """
    Represents the result of an upload operation, capturing success/failure status,
    error information, performance metrics, and hierarchical sub-results.

    This class serves as the base for all upload result types and supports
    automatic status calculation based on sub-results for complex upload operations.
    """

    ENTITY: ClassVar = Entity(persistable=False)

    # List of field names in subclasses that contain single sub-results for generic model validation
    SUB_RESULT_FIELD_NAMES: ClassVar[list[str]] = []
    # List of field names in subclasses that each contains each a list of sub-results for generic model validation
    SUB_RESULT_LIST_FIELD_NAMES: ClassVar[list[str]] = []

    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the specific object instance that this result pertains to, if applicable. E.g. the object that was created or updated as part of the upload.",
    )
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="The UTC timestamp when the upload result was created.",
    )
    status: UploadStatus = Field(
        default=UploadStatus.PENDING,
        description="The status of the upload operation. In case sub-results are present, this status is calculated from that of the sub-results: success if all sub-results are successful, failed if any sub-result failed, and skipped if all sub-results are skipped.",
    )
    is_update: bool = Field(
        default=False,
        description="Indicates whether the upload operation resulted in an update of at least one existing object. If no objects were updated, i.e. all were newly created or skipped, this will be False.",
    )
    error_codes: list[str | None] | None = Field(
        default=None,
        description="Error codes generated during the upload operation, describing the causes for upload failure, if applicable and available. Must be same length as error_messages if both are provided.",
    )
    error_messages: list[str | None] | None = Field(
        default=None,
        description="Error messages generated during the upload operation, describing the causes for upload failure, if applicable and available. Must be same length as error_codes if both are provided.",
    )
    warning_codes: list[str | None] | None = Field(
        default=None,
        description="Warning codes generated during the upload operation, if applicable and available. If both warning_messages and warning_code are provided, they must be the same length.",
    )
    warning_messages: list[str | None] | None = Field(
        default=None,
        description="Warning messages generated during the upload operation, if applicable and available. If both warning_messages and warning_code are provided, they must be the same length.",
    )
    duration_ms: int | None = Field(
        default=None,
        description="Duration of the upload operation in milliseconds, if available.",
    )

    @computed_field
    @cached_property
    def n_items_processed(self) -> int:
        """The number of records processed during the upload operation."""
        n = bool(self.status != UploadStatus.PENDING)  # Count self if not pending
        for field_name in self.SUB_RESULT_FIELD_NAMES:
            sub_result: UploadResult | None = getattr(self, field_name, None)
            if sub_result is not None:
                n += sub_result.n_items_processed
        for field_name in self.SUB_RESULT_LIST_FIELD_NAMES:
            sub_results: list[UploadResult] = getattr(self, field_name, None) or []
            for sub_result in sub_results:
                n += sub_result.n_items_processed
        return n

    @model_validator(mode="after")
    def _validate_upload_result(self) -> Self:
        """Validate upload result consistency."""
        # Validate error/warning message and code length consistency
        if self.error_messages and self.error_codes:
            if len(self.error_messages) != len(self.error_codes):
                raise ValueError(
                    "error_messages and error_codes must be the same length"
                )
            if any(
                x is None and y is None
                for x, y in zip(self.error_messages, self.error_codes)
            ):
                raise ValueError(
                    "At least one of error_message or error_code must be provided for each error"
                )
        if self.warning_messages and self.warning_codes:
            if len(self.warning_messages) != len(self.warning_codes):
                raise ValueError(
                    "warning_messages and warning_codes must be the same length"
                )
            if any(
                x is None and y is None
                for x, y in zip(self.warning_messages, self.warning_codes)
            ):
                raise ValueError(
                    "At least one of warning_message or warning_code must be provided for each warning"
                )
        # Validate error/status consistency
        has_errors = bool(self.error_messages or self.error_codes)
        if self.status == UploadStatus.SUCCESS and has_errors:
            raise ValueError("Successful results cannot have error information")
        if self.status == UploadStatus.FAILED and not has_errors:
            raise ValueError("Failed results must include error information")

        # Calculate status from sub-results if applicable
        if self.SUB_RESULT_FIELD_NAMES or self.SUB_RESULT_LIST_FIELD_NAMES:
            self._calculate_status_from_sub_results()

        return self

    def _calculate_status_from_sub_results(self) -> None:
        """Calculate status based on sub-results with proper type checking."""
        n_total = 0
        n_pending = 0
        n_skipped = 0
        n_updated = 0

        # Check single sub-results
        self.status = UploadStatus.FAILED
        self.is_update = False
        for field_name in self.SUB_RESULT_FIELD_NAMES:
            sub_result: UploadResult | None = getattr(self, field_name, None)
            if sub_result is None:
                continue
            n_total += 1
            if sub_result.status == UploadStatus.FAILED:
                return
            n_pending += sub_result.status == UploadStatus.PENDING
            n_skipped += sub_result.status == UploadStatus.SKIPPED
            n_updated += sub_result.is_update

        # Check list sub-results
        for field_name in self.SUB_RESULT_LIST_FIELD_NAMES:
            sub_results: list[UploadResult] = getattr(self, field_name, None) or []
            for sub_result in sub_results:
                n_total += 1
                if sub_result.status == UploadStatus.FAILED:
                    self.status = UploadStatus.FAILED
                    return
                n_pending += sub_result.status == UploadStatus.PENDING
                n_skipped += sub_result.status == UploadStatus.SKIPPED
                n_updated += sub_result.is_update

        self.is_update = n_updated > 0
        if n_pending > 0:
            self.status = UploadStatus.PENDING
            return
        self.status = (
            UploadStatus.SUCCESS if n_skipped < n_total else UploadStatus.SKIPPED
        )

    def add_error(
        self,
        message: str | None,
        code: str | None,
    ) -> None:
        """Add an error message and optional code to the upload result."""
        if message is None and code is None:
            raise ValueError("At least one of message or code must be provided")
        if self.error_messages is None:
            self.error_messages = []
        if self.error_codes is None:
            self.error_codes = []
        self.error_messages.append(message)
        self.error_codes.append(code)
        self.status = UploadStatus.FAILED

    def add_warning(
        self,
        message: str | None,
        code: str | None,
    ) -> None:
        """Add a warning message and optional code to the upload result."""
        if message is None and code is None:
            raise ValueError("At least one of message or code must be provided")
        if self.warning_messages is None:
            self.warning_messages = []
        if self.warning_codes is None:
            self.warning_codes = []
        self.warning_messages.append(message)
        self.warning_codes.append(code)


class BaseBatchUploadResult(UploadResult):
    """
    Base class for upload results corresponding to a complete batch of objects uploaded.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "BaseBatchUploadResult"

    batch_id: UUID = Field(
        description="The unique identifier for the upload batch that this result belongs to.",
    )
