import datetime
import uuid
from typing import Callable, ClassVar, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from gen_epix.commondb.domain.enum import IdentifierType, UploadStatus, UploadStatusSet
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import (
    ExternalIdentifier,
    ExternalIdentifierForUpload,
)
from gen_epix.fastapp.domain import Entity
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import LogLevel, LogLevelSet


class IsNewIdMixin:
    """
    Mixin that adds an is_new_id field to indicate whether the model instance is new
    and has an externally assigned ID rather than one assigned by the system.
    Assumes that the inheriting model also has an 'id' field.

    Additional validation:
    - If is_new_id is True, the model id field field may not be None or NULL_ID.
    """

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
        id_value = getattr(self, "id")
        if self.is_new_id and (id_value is None or id_value == NULL_ID):
            raise ValueError("is_new_id cannot be True when id is None or NULL_ID.")
        return self


class UploadLogItem(BaseModel):
    """
    Represents a log item for an upload result, contain a timestamp, code, message
    and severity.
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
    Represents the result of an upload operation, including upload status and logs.

    Additional validation:
    - If the status is successful (NOT_FAILED), there must be no error log items.
    - If the status is failed, there must be at least one error log item.
    """

    ENTITY: ClassVar = Entity(persistable=False)

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
        """Add an error log item. Sets the upload status to FAILED."""
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

    def add_logs(self, upload_log_items: list[UploadLogItem] | UploadLogItem) -> None:
        """
        Add log items to the upload result. If any of the added log items has severity
        ERROR, the upload status is set to FAILED.
        """
        if isinstance(upload_log_items, list):
            self.logs.extend(upload_log_items)
            if any(log.severity == LogLevel.ERROR for log in upload_log_items):
                self.status = UploadStatus.FAILED
        else:
            self.logs.append(upload_log_items)
            if upload_log_items.severity == LogLevel.ERROR:
                self.status = UploadStatus.FAILED

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


class ParentForUpload(Model, IsNewIdMixin):
    """
    Represents a parent model for upload, where the term "parent" refers to a model
    that can have child models associated with it through a link. External identifiers
    can also be added here.

    This class must be subclassed for specific parent models, adding the following
    fields:
    - A parent Parent|None field where the parent model that needs to be uploaded, if
      any, will be put
    - For each child model type that can be associated with the parent, a "children"
      list|None field that will contain the actual child models to be uploaded along with
      the parent model.
    Metadata on the parent and child models, allowing introspection, must be provided
    through the class variables.

    Additional validation:
    - NULL_ID in the id field is converted to None.
    - If both the ParentForUpload id and the contained Parent model id are provided,
      they must match.
    - For each child model type, if the ParentForUpload id is provided, the parent ID
      field in each child model must either be None/NULL_ID or match the ParentForUpload
      id.
    """

    # Must be set in child class
    # The type of identifier for external identifiers
    PARENT_IDENTIFIER_TYPE: ClassVar[IdentifierType] = None  # type: ignore[assignment]

    # Must be set in child class
    # The actual Parent model child class
    PARENT_CLASS: ClassVar[type[Model]] = None  # type: ignore[assignment]

    # Must be set in child class
    # The name of the field in the child class that contains the actual Parent model
    PARENT_FIELD_NAME: ClassVar[str] = None  # type: ignore[assignment]

    # Must be set in child class
    # Mapping from child model classes to the names of the fields in the ParentForUpload model that contain lists of those child models
    CHILDREN_FIELD_NAME_MAP: ClassVar[dict[type[Model], str]] = {}

    # Must be set in child class
    # Mapping from child model classes to their corresponding ForUploadMixin classes
    CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar[dict[type[Model], type[IsNewIdMixin]]] = {}

    # Must be set in child class
    # Mapping from child model classes to the names of the fields in the child models that refer back to the parent ID
    CHILD_PARENT_ID_FIELD_NAME_MAP: ClassVar[dict[type[Model], str]] = {}

    # The name of the field in the ParentForUpload model that contains the external identifiers
    EXTERNAL_IDENTIFIER_FOR_UPLOAD_CLASS: ClassVar[
        type[ExternalIdentifierForUpload]
    ] = ExternalIdentifierForUpload
    EXTERNAL_IDENTIFIER_CLASS: ClassVar[type[Model]] = ExternalIdentifier
    EXTERNAL_IDENTIFIERS_FIELD_NAME: ClassVar[str] = "external_identifiers"

    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the Parent object. If NULL_ID is provided, it will be set to None.",
    )
    external_identifiers: list[ExternalIdentifierForUpload] | None = Field(
        default=None,
        description="External identifiers for the parent model, if any. Must be a unique values.",
    )

    @field_validator("id", mode="before")
    def _validate_id_field(cls, id: UUID | None) -> UUID | None:
        """Validate the id field, converting NULL_ID to None."""
        if id == NULL_ID:
            return None
        return id

    @field_validator("external_identifiers", mode="after")
    def _validate_external_identifiers(
        cls, external_identifiers: list[ExternalIdentifierForUpload] | None
    ) -> list[ExternalIdentifierForUpload] | None:
        if external_identifiers is None:
            return external_identifiers
        seen = set()
        for ext_id in external_identifiers:
            if ext_id in seen:
                raise ValueError("Duplicate external identifiers are not allowed.")
            seen.add(ext_id)
        return external_identifiers

    @model_validator(mode="after")
    def validate_parent_id(self) -> Self:
        """
        Validate consistency of IDs with the parent (self) field, if provided.
        """
        parent: Model | None = getattr(self, self.PARENT_FIELD_NAME)
        if parent is None:
            return self
        if parent.id == NULL_ID:
            parent.id = None
        has_for_upload_id = self.id is not None
        has_id = parent.id is not None
        if has_for_upload_id:
            if has_id:
                if parent.id != self.id:
                    raise ValueError(
                        "The id of ParentForUpload must match the id of the contained Parent model."
                    )
            else:
                # Set the parent id to match the ForUpload id
                parent.id = self.id
        elif has_id:
            # Set the ForUpload id to match the parent id
            self.id = parent.id
        return self

    @model_validator(mode="after")
    def validate_child_parent_id(self) -> Self:
        """
        Validate consistency of child parent ID their actual parent ID.
        Validate unicity of child IDs.
        """
        has_id = self.id is not None and self.id != NULL_ID
        for (
            child_model_class,
            children_field_name,
        ) in self.CHILDREN_FIELD_NAME_MAP.items():
            parent_id_field_name = self.CHILD_PARENT_ID_FIELD_NAME_MAP[
                child_model_class
            ]
            children: list[Model] | None = getattr(self, children_field_name, None)
            if children is None:
                continue
            seen_child_ids = set()
            for i, child in enumerate(children):
                # Check for duplicate child IDs
                if child.id and child.id != NULL_ID:
                    if child.id in seen_child_ids:
                        raise ValueError(
                            f"Duplicate ID {child.id} found in {children_field_name}."
                        )
                    seen_child_ids.add(child.id)
                # Check child parent ID consistency
                if not has_id:
                    continue
                child_parent_id = getattr(child, parent_id_field_name)
                if child_parent_id is None or child_parent_id == NULL_ID:
                    continue
                if child_parent_id != self.id:
                    raise ValueError(
                        f"{children_field_name}[{i}].{parent_id_field_name}={child_parent_id} does not match parent.id={self.id}."
                    )
        return self

    def get_parent(self) -> Model | None:
        """
        Get the actual model contained in this for-upload model, if set.
        """
        parent: Model | None = getattr(self, self.PARENT_FIELD_NAME)
        return parent

    def get_external_identifiers(self) -> list[ExternalIdentifierForUpload] | None:
        """
        Get the list of external identifiers for upload, or an empty list if none are set.
        """
        return self.external_identifiers


class ParentUploadResult(UploadResult):
    """
    Represents the upload result for a Parent model upload. This class must be
    subclassed analogous to the ParentForUpload model it corresponds to.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "ParentUploadResult"

    # Must be set in child class
    # The ParentForUpload child class corresponding to this result class
    PARENT_FOR_UPLOAD_CLASS: ClassVar[type[ParentForUpload]] = None  # type: ignore[assignment]

    external_identifiers: list[UploadResult] | None = Field(
        default=None,
        description="The upload results for the external identifiers associated with the parent model, if any.",
    )

    def get_status_count(self, include_self: bool = True) -> dict[UploadStatus, int]:
        """
        Count the number of occurrences of each UploadStatus in this result (if
        include_self) and that of its child results.
        """
        retval: dict[UploadStatus, int] = {x: 0 for x in UploadStatus}
        if include_self:
            retval[self.status] += 1
        for field_name in self.get_child_results_field_names():
            child_results: list[UploadResult] = getattr(self, field_name, None) or []
            for child_result in child_results:
                retval[child_result.status] += 1
        return retval

    @classmethod
    def get_child_results_field_names(cls) -> list[str]:
        """
        Get the list of field names in this result class that contain lists of child results.
        """
        return [cls.PARENT_FOR_UPLOAD_CLASS.EXTERNAL_IDENTIFIERS_FIELD_NAME] + list(
            cls.PARENT_FOR_UPLOAD_CLASS.CHILDREN_FIELD_NAME_MAP.values()
        )


class BaseBatchForUpload(Model):
    """
    Base class for batches of ParentForUpload objects to be uploaded. A batch is
    intended as a single unit of work for an upload operation and as such to be
    processed atomically.

    Additional validation:
    - All ParentForUpload objects must have unique IDs (if provided)
    - All ParentForUpload objects must have unique external identifiers
    """

    # Must be set in child class
    # The ParentForUpload model class contained in this batch
    PARENT_FOR_UPLOAD_CLASS: ClassVar[type[ParentForUpload]] = None  # type: ignore[assignment]

    # Must be set in child class
    # The name of the field in the child class that contains the list of
    # ParentForUpload models to be uploaded
    PARENTS_FOR_UPLOAD_FIELD_NAME: ClassVar[str] = None  # type: ignore[assignment]

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

    @model_validator(mode="after")
    def _validate_parent_ids(self) -> Self:
        """
        Validate that all parents for upload in the batch have unique IDs and external
        identifiers.
        """
        # Verify duplicate IDs
        parents_for_upload = self.get_parents_for_upload()
        parent_ids = [
            x.id for x in parents_for_upload if x.id is not None and x.id != NULL_ID
        ]
        if len(parent_ids) != len(set(parent_ids)):
            duplicate_ids = sorted(
                set(x for x in parent_ids if parent_ids.count(x) > 1)
            )
            duplicate_ids_str = ", ".join(str(x) for x in duplicate_ids)
            raise ValueError(
                f"Duplicate parent IDs found in batch: {duplicate_ids_str}"
            )
        # Verify duplicate external identifiers
        all_external_identifiers = []
        for parent_for_upload in parents_for_upload:
            if parent_for_upload.external_identifiers is not None:
                all_external_identifiers.extend(parent_for_upload.external_identifiers)
        if len(all_external_identifiers) != len(set(all_external_identifiers)):
            raise ValueError("Duplicate parent external identifiers found in batch.")
        return self

    def get_parents_for_upload(self) -> list[ParentForUpload]:
        """
        Get the list of objects to be uploaded in this batch.
        """
        parents_for_upload: list[ParentForUpload] = getattr(
            self, self.PARENTS_FOR_UPLOAD_FIELD_NAME
        )
        return parents_for_upload

    @classmethod
    def get_parent_class(cls) -> type[ParentForUpload]:
        """
        Get the ParentForUpload class corresponding to this batch class.
        """
        return cls.PARENT_FOR_UPLOAD_CLASS


class BaseBatchUploadResult(UploadResult):
    """
    Base class for upload results corresponding to a complete batch of objects
    uploaded. The names of the fields in any child class must be exactly identical to
    those in the corresponding BaseBatchForUpload child class.
    """

    # Must be overridden in child class
    # The BaseBatchForUpload child class corresponding to this result class
    BATCH_FOR_UPLOAD_CLASS: ClassVar[type[BaseBatchForUpload]] = None  # type: ignore[assignment]

    # Must be overridden in child class
    # The ParentUploadResult child class that will contain the results of the parent uploads
    PARENT_RESULT_CLASS: ClassVar[type[ParentUploadResult]] = None  # type: ignore[assignment]

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "BaseBatchUploadResult"

    batch_id: UUID = Field(
        default_factory=uuid.uuid4,
        description="The unique identifier for the upload batch that this result belongs to.",
    )

    def get_parent_results(self) -> list[ParentUploadResult]:
        """
        Get the list of parent upload results in this batch upload result.
        """
        parent_results: list[ParentUploadResult] = getattr(
            self, self.BATCH_FOR_UPLOAD_CLASS.PARENTS_FOR_UPLOAD_FIELD_NAME
        )
        return parent_results

    def get_status_count(self, include_self: bool = True) -> dict[UploadStatus, int]:
        """
        Count the number of occurrences of each UploadStatus in this result (if
        include_self) and that of its child results.
        """
        retval: dict[UploadStatus, int] = {x: 0 for x in UploadStatus}
        if include_self:
            retval[self.status] += 1
        for parent_result in self.get_parent_results():
            parent_status_count = parent_result.get_status_count(include_self=True)
            for status, count in parent_status_count.items():
                retval[status] += count
        return retval
