import datetime
import uuid
from typing import Callable, ClassVar, Self
from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_serializer, field_validator, model_validator

from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.enum import DataIssueTypeSet, EtlStatus, UploadStatusSet
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.base import BaseEtlResult, EtlLogItem
from gen_epix.commondb.domain.model.organization import (
    BaseIdentifier,
    IdentifierForUpload,
)
from gen_epix.fastapp import Model
from gen_epix.fastapp.domain import Entity
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import LogLevel, LogLevelSet

# Backward-compatible alias: UploadLogItem is now ResultLogItem.
UploadLogItem = EtlLogItem


class IdentifiersMixin:
    """
    Mixin that adds identifiers fields and validation. Assumes that the
    inheriting model also has an 'identifiers' field.

    Additional validation:
    - All identifiers must have the same identifier type.
    - All identifiers must have unique values.
    """

    # Must be set in child class
    IDENTIFIER_CLASS: ClassVar[type[BaseIdentifier]] = None  # type: ignore[assignment]

    identifiers: list[IdentifierForUpload] | None = Field(
        default=None,
        description="Identifiers for the model, if any. Must be a unique values.",
    )

    @field_validator("identifiers", mode="after")
    @classmethod
    def _validate_identifiers(
        cls, identifiers: list[IdentifierForUpload] | None
    ) -> list[IdentifierForUpload] | None:
        """
        Validate identifiers consistency. Assumes that the inheriting model
        also has an 'identifiers' field.
        """
        if identifiers is None:
            return identifiers
        if len(identifiers) == 1:
            # Nothing to check
            return identifiers
        identifier_issuer_code_id_map = {}
        seen_ids = set()
        seen_codes = set()
        for identifier in identifiers:
            identifier_issuer_id = identifier.identifier_issuer_id
            identifier_issuer_code = identifier.identifier_issuer_code
            if identifier_issuer_id is not None:
                if identifier_issuer_id in seen_ids:
                    raise ValueError(
                        f"Duplicate identifier issuer ID found: {identifier_issuer_id}"
                    )
                if identifier_issuer_code is not None:
                    if (
                        identifier_issuer_code in identifier_issuer_code_id_map
                        and identifier_issuer_code_id_map[identifier_issuer_code]
                        != identifier_issuer_id
                    ):
                        raise ValueError(
                            f"Inconsistent identifier issuer ID for code {identifier_issuer_code}: expected {identifier_issuer_code_id_map[identifier_issuer_code]}, got {identifier_issuer_id}."
                        )
                    identifier_issuer_code_id_map[identifier_issuer_code] = (
                        identifier_issuer_id
                    )
            if identifier_issuer_code is not None:
                if identifier_issuer_code in seen_codes:
                    raise ValueError(
                        f"Duplicate identifier issuer code found: {identifier_issuer_code}"
                    )
                seen_codes.add(identifier_issuer_code)
        return identifiers


class DataIssue(PydanticBaseModel):
    original_value: str | None = Field(description="The original value")
    updated_value: str | None = Field(
        description="The new value after potential resolution of the issue. If not resolved, this will be None.",
    )
    data_issue_type: enum.DataIssueType = Field(
        description="The type of validation issue"
    )
    code: str = Field(description="The code of the data issue")
    message: str | None = Field(description="The details of the data issue")


class UploadResult(BaseEtlResult, Model):
    """
    Represents the result of an upload operation for a particular object, including
    upload status and logs.

    Additional validation:
    - If the status is successful (NOT_FAILED), there must be no error log items.
    - If the status is failed, there must be at least one error log item.
    """

    ENTITY: ClassVar = Entity(persistable=False)

    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the specific object instance that this result pertains to, if applicable. E.g. the object that was created or updated as part of the upload.",
    )
    status: EtlStatus = Field(
        default=EtlStatus.PENDING,
        description="The status of the upload operation. If not successful, error information must be provided in the logs.",
    )
    is_new: bool = Field(
        default=False,
        description="Indicates whether the object did not exist before start of the upload. False in case upload failed before this could be determined.",
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

    def set_error_status(self) -> None:
        self.status = EtlStatus.FAILED

    def add_logs(self, upload_log_items: list[UploadLogItem] | UploadLogItem) -> None:
        """
        Add log items to the upload result. If any of the added log items has severity
        ERROR, the upload status is set to FAILED.
        """
        if isinstance(upload_log_items, list):
            self.logs.extend(upload_log_items)
            if any(log.severity == LogLevel.ERROR for log in upload_log_items):
                self.status = EtlStatus.FAILED
        else:
            self.logs.append(upload_log_items)
            if upload_log_items.severity == LogLevel.ERROR:
                self.status = EtlStatus.FAILED

    def get_identifier_upload_results(self) -> list["UploadResult"] | None:
        """
        Get the upload results for the identifiers associated with the model, if any.
        """
        return None


class UploadResultWithIdentifiers(UploadResult):
    """
    Represents an upload result that also includes upload results for
    identifiers, mirroring a for upload class that has identifiers.
    """

    ENTITY: ClassVar = UploadResult.model_entity().clone()
    NAME: ClassVar = "UploadResultWithIdentifiers"

    identifiers: list[UploadResult] | None = Field(
        default=None,
        description="The upload results for the identifiers associated with the model, if any.",
    )

    def get_identifier_upload_results(self) -> list["UploadResult"] | None:
        """
        Get the upload results for the identifiers associated with the model, if any.
        """
        return self.identifiers


class ParentForUpload(Model, IdentifiersMixin):
    """
    Represents a parent model for upload, where the term "parent" refers to a model
    that can have child models associated with it through a link. Other identifiers
    can also be added here, in the "identifiers" field.

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

    ENTITY: ClassVar = Entity(persistable=False, id_field_name="id")

    # Must be set in child class
    # The type of identifier for identifiers (inherited from mixin)
    IDENTIFIER_CLASS: ClassVar = None  # type: ignore[assignment]

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
    # Mapping from child model classes to their corresponding ForUpload classes
    CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar[dict[type[Model], type[Model]]] = {}

    # Must be set in child class
    # Mapping from child model classes to the names of the fields in the child models that refer back to the parent ID
    CHILD_PARENT_ID_FIELD_NAME_MAP: ClassVar[dict[type[Model], str]] = {}

    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the Parent object. If NULL_ID is provided, it will be set to None. The id must match that of the contained Parent model, if provided, and be consistent with the parent ID in the child models, if provided. The contained Parent model may have a different ID field than 'id', but this class uses 'id' instead.",
    )

    @field_validator("id", mode="before")
    @classmethod
    def _validate_id_field(cls, id: UUID | None) -> UUID | None:
        """Validate the id field, converting NULL_ID to None."""
        if id == NULL_ID:
            return None
        return id

    @model_validator(mode="after")
    def validate_parent_id(self) -> Self:
        """
        Validate consistency of IDs with the parent (self) field, if provided.
        """
        parent: Model | None = getattr(self, self.PARENT_FIELD_NAME)
        if parent is None:
            return self
        id_field_name = self.PARENT_CLASS.ENTITY.get_id_field_name()
        parent_id = getattr(parent, id_field_name)
        if parent_id == NULL_ID:
            setattr(parent, id_field_name, None)
            parent_id = None
        has_for_upload_id = self.id is not None
        has_id = parent_id is not None
        if has_for_upload_id:
            if has_id:
                if parent_id != self.id:
                    raise ValueError(
                        f"ParentForUpload.id={self.id} does not match Parent.{id_field_name}={parent_id} of the contained Parent model."
                    )
            else:
                # Set the parent id to match the ForUpload id
                setattr(parent, id_field_name, self.id)
        elif has_id:
            # Set the ForUpload id to match the parent id
            self.id = parent_id
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
            child_id_field_name = self.CHILD_FOR_UPLOAD_CLASS_MAP[
                child_model_class
            ].ENTITY.get_id_field_name()
            parent_id_field_name = self.CHILD_PARENT_ID_FIELD_NAME_MAP[
                child_model_class
            ]
            children: list[Model] | None = getattr(self, children_field_name, None)
            if children is None:
                continue
            seen_child_ids = set()
            has_identifiers = issubclass(child_model_class, IdentifiersMixin)
            seen_child_identifiers = set()
            for i, child in enumerate(children):
                # Check for duplicate child IDs
                child_id = getattr(child, child_id_field_name)
                if child_id and child_id != NULL_ID:
                    if child_id in seen_child_ids:
                        raise ValueError(
                            f"Duplicate ID {child_id_field_name}={child_id} found in {children_field_name}."
                        )
                    seen_child_ids.add(child_id)
                # Check child parent ID consistency
                if has_id:
                    child_parent_id = getattr(child, parent_id_field_name)
                    if child_parent_id is None or child_parent_id == NULL_ID:
                        pass
                    elif child_parent_id != self.id:
                        raise ValueError(
                            f"{children_field_name}[{i}].{parent_id_field_name}={child_parent_id} does not match parent.id={self.id}."
                        )
                # Check for duplicate child identifiers
                if has_identifiers:
                    assert isinstance(child, IdentifiersMixin)
                    if not child.identifiers:
                        continue
                    if len(child.identifiers) != len(set(child.identifiers)):
                        raise ValueError(
                            f"Duplicate identifiers found in {children_field_name}[{i}]."
                        )
                    for identifier in child.identifiers:
                        if identifier in seen_child_identifiers:
                            raise ValueError(
                                f"Duplicate identifier {identifier} found in {children_field_name}."
                            )
                        seen_child_identifiers.add(identifier)
        return self

    def get_parent(self) -> Model | None:
        """
        Get the actual model contained in this for-upload model, if set.
        """
        parent: Model | None = getattr(self, self.PARENT_FIELD_NAME)
        return parent

    def get_identifiers(self) -> list[IdentifierForUpload] | None:
        """
        Get the list of identifiers for upload, or an empty list if none are set.
        """
        return self.identifiers


class ParentUploadResult(UploadResultWithIdentifiers):
    """
    Represents the upload result for a Parent model upload. This class must be
    subclassed analogous to the ParentForUpload model it corresponds to.
    """

    ENTITY: ClassVar = UploadResultWithIdentifiers.model_entity().clone()
    NAME: ClassVar = "ParentUploadResult"

    # Must be set in child class
    # The ParentForUpload child class corresponding to this result class
    PARENT_FOR_UPLOAD_CLASS: ClassVar[type[ParentForUpload]] = None  # type: ignore[assignment]

    data_issues: list[DataIssue] = Field(
        default_factory=list,
        description="The data issues found for the original content and potential corresponding updates made to it.",
    )

    def get_status_count(self, include_self: bool = True) -> dict[EtlStatus, int]:
        """
        Count the number of occurrences of each EtlStatus in this result (if
        include_self) and that of its child results.
        """
        status_count_map: dict[EtlStatus, int] = {x: 0 for x in EtlStatus}
        if include_self:
            status_count_map[self.status] += 1
        for field_name in self.get_child_results_field_names():
            child_results: list[UploadResult] = getattr(self, field_name, None) or []
            for child_result in child_results:
                status_count_map[child_result.status] += 1
                # Any child identifiers
                for identifier_result in (
                    child_result.get_identifier_upload_results() or []
                ):
                    status_count_map[identifier_result.status] += 1
        # Parent identifiers
        for identifier_result in self.identifiers or []:
            status_count_map[identifier_result.status] += 1
        return status_count_map

    def update_status_with_data_issues(self) -> None:
        """
        Update the upload status of this result based on the data issues found, adding
        corresponding log items.
        """
        data_issues = self.data_issues
        # Errors
        error_codes = {
            x.code
            for x in data_issues
            if x.data_issue_type in DataIssueTypeSet.ERROR.value
        }
        if error_codes:
            error_codes_str = ", ".join(sorted(error_codes))
            self.add_error(
                "d3f5c1a2",
                f"Data has errors: {error_codes_str}",
            )
        # Warnings
        warning_codes = {
            x.code
            for x in data_issues
            if x.data_issue_type in DataIssueTypeSet.WARNING.value
        }
        if warning_codes:
            warning_codes_str = ", ".join(sorted(warning_codes))
            self.add_warning(
                "b4e6d2c3",
                f"Data has warnings: {warning_codes_str}",
            )
        # Info
        info_codes = {
            x.code
            for x in data_issues
            if x.data_issue_type in DataIssueTypeSet.INFO.value
        }
        if info_codes:
            info_codes_str = ", ".join(sorted(info_codes))
            self.add_info(
                "c5d7e8f9",
                f"Data has info: {info_codes_str}",
            )

    def convert_status(self, from_status: EtlStatus, to_status: EtlStatus) -> None:
        """
        Convert all occurrences of from_status to to_status in this result and all
        its child and identifier results.
        """
        if self.status == from_status:
            self.status = to_status
        for field_name in self.get_child_results_field_names():
            for child_result in getattr(self, field_name) or []:
                if child_result.status == from_status:
                    child_result.status = to_status
                for identifier_result in (
                    child_result.get_identifier_upload_results() or []
                ):
                    if identifier_result.status == from_status:
                        identifier_result.status = to_status
        for identifier_result in self.identifiers or []:
            if identifier_result.status == from_status:
                identifier_result.status = to_status

    @classmethod
    def get_child_results_field_names(cls) -> list[str]:
        """
        Get the list of field names in this result class that contain lists of child results.
        """
        return list(cls.PARENT_FOR_UPLOAD_CLASS.CHILDREN_FIELD_NAME_MAP.values())


class BaseBatchForUpload(Model):
    """
    Base class for batches of ParentForUpload objects to be uploaded. A batch is
    intended as a single unit of work for an upload operation and as such to be
    processed atomically.

    Additional validation:
    - All ParentForUpload objects must have unique IDs (if provided)
    - All ParentForUpload objects must have unique other identifiers
    """

    ENTITY: ClassVar = Entity(persistable=False, id_field_name="id")

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
        Validate that all parents for upload in the batch have unique IDs and other
        identifiers.
        """
        # Verify duplicate parent IDs
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
        # Verify duplicate parent identifiers
        seen_parent_identifiers = set()
        for parent_for_upload in parents_for_upload:
            if not parent_for_upload.identifiers:
                continue
            parent_identifiers = set(parent_for_upload.identifiers or [])
            if parent_identifiers.isdisjoint(seen_parent_identifiers):
                seen_parent_identifiers.update(parent_identifiers)
            else:
                raise ValueError("Duplicate parent identifiers found in batch.")
        # Verify duplicate child IDs and identifiers across all types of children
        seen_child_ids = set()
        for (
            child_model_class,
            children_field_name,
        ) in self.PARENT_FOR_UPLOAD_CLASS.CHILDREN_FIELD_NAME_MAP.items():
            # Get all children
            child_id_field_name = child_model_class.ENTITY.get_id_field_name()
            children_for_upload: list[Model] = [
                y
                for x in parents_for_upload
                for y in (getattr(x, children_field_name) or [])
            ]
            # Add all IDs and identifiers
            seen_child_identifiers = set()
            has_identifiers = issubclass(child_model_class, IdentifiersMixin)
            for child_for_upload in children_for_upload:
                child_id = getattr(child_for_upload, child_id_field_name)
                if child_id is not None and child_id != NULL_ID:
                    if child_id in seen_child_ids:
                        raise ValueError(
                            f"Duplicate child ID {child_id} found in batch in field {children_field_name}."
                        )
                    seen_child_ids.add(child_id)
                if not has_identifiers:
                    continue
                assert isinstance(child_for_upload, IdentifiersMixin)
                if not child_for_upload.identifiers:
                    continue
                child_identifiers = set(child_for_upload.identifiers or [])
                if child_identifiers.isdisjoint(seen_child_identifiers):
                    seen_child_identifiers.update(child_identifiers)
                else:
                    duplicate_identifiers = child_identifiers.intersection(
                        seen_child_identifiers
                    )
                    duplicate_identifiers_str = ", ".join(
                        str(x) for x in duplicate_identifiers
                    )
                    raise ValueError(
                        f"Duplicate child identifiers found in batch in field {children_field_name}: {duplicate_identifiers_str}"
                    )
        return self

    def get_parents_for_upload(self) -> list[ParentForUpload]:
        """
        Get the list of objects to be uploaded in this batch.
        """
        parents_for_upload: list[ParentForUpload] = getattr(
            self, self.PARENTS_FOR_UPLOAD_FIELD_NAME
        )
        return parents_for_upload

    def get_n_parents(self) -> int:
        return len(self.get_parents_for_upload())

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

    ENTITY: ClassVar = UploadResult.model_entity().clone()
    NAME: ClassVar = "BaseBatchUploadResult"

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

    def get_status_count(self, include_self: bool = True) -> dict[EtlStatus, int]:
        """
        Count the number of occurrences of each EtlStatus in this result (if
        include_self) and that of its child results.
        """
        status_count_map: dict[EtlStatus, int] = {x: 0 for x in EtlStatus}
        if include_self:
            status_count_map[self.status] += 1
        for parent_result in self.get_parent_results():
            parent_status_count = parent_result.get_status_count(include_self=True)
            for status, count in parent_status_count.items():
                status_count_map[status] += count
        return status_count_map

    def resolve_status(self) -> None:
        """
        Set this batch result's status based on the aggregate of its children.
        Only has effect when status is still PENDING.
        """
        if self.status != EtlStatus.PENDING:
            return
        status_count = self.get_status_count(include_self=False)
        n_results = sum(status_count.values())
        if n_results == 0 or status_count[EtlStatus.SKIPPED] == n_results:
            self.status = EtlStatus.SKIPPED
        elif status_count[EtlStatus.CREATED] == n_results:
            self.status = EtlStatus.CREATED
        elif status_count[EtlStatus.UPDATED] == n_results:
            self.status = EtlStatus.UPDATED
        else:
            self.status = EtlStatus.PROCESSED
