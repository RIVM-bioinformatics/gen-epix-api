"""Shared ETL-run result accumulators.

These models track the outcome of a multi-stage ETL run (extract -> transform ->
load): per-run (:class:`EtlResult`), per-stored-batch (:class:`EtlBatchResult`)
and per-subject (:class:`ExtractResult`, :class:`TransformResult`) accumulators,
each carrying structured logs and a roll-up status.

Naming notes:

* :class:`TransformResult` here is unrelated to
  :class:`gen_epix.transform.TransformResult` (a stream-processing helper).

Concrete ``TransformResult`` / ``ExtractResult`` subclasses are defined by the ETL
services that consume this module. They register themselves through
``__init_subclass__`` and are only reconstructed as their concrete type by
``model_validate`` once their defining module has been imported; otherwise they
round-trip as the base class.
"""

import uuid
from datetime import UTC, datetime
from typing import Annotated, Any, ClassVar, Self, TypeVar
from uuid import UUID

from deprecated import deprecated
from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    SerializeAsAny,
    field_serializer,
    field_validator,
    model_validator,
)

from gen_epix.etl.enum import EtlStatus, EtlStatusSet
from gen_epix.fastapp.enum import LogLevel


class EtlLogItem(BaseModel):
    """Represents a single log item for inclusion in an ETL result."""

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="The UTC timestamp when the log item was created.",
    )
    code: str = Field(
        description="A code categorizing the log item.",
    )
    message: str = Field(
        description="The log message describing the event or information.",
    )
    severity: LogLevel = Field(
        description="Log severity, accepting a LogLevel or member name and serializing to its string value.",
    )
    source: str | None = Field(
        default=None,
        description="Optional field to capture source trace information, e.g. relevant source record ids.",
    )
    target: str | None = Field(
        default=None,
        description="Optional field to capture target trace information, e.g. relevant target record ids created or updated as a result of the logged event.",
    )

    @field_validator("severity", mode="before")
    @classmethod
    def _validate_severity(cls, severity: LogLevel | str) -> LogLevel:
        """Normalize a severity member name to a LogLevel."""
        if isinstance(severity, str):
            return LogLevel[severity]
        return severity

    @field_serializer("severity")
    def _serialize_severity(self, value: LogLevel) -> str:
        """Serialize a log level as its configured value."""
        return value.value


class EtlResult(BaseModel):
    """Represents an ETL result, storing logs and status information for ETL operations.

    Intended as the base class for specialized ETL results.

    Includes severity-specific methods and status setting and tracking.

    ``source_id`` stores whichever source-system identifier is most
    relevant for the concrete subclass as a string; ``SOURCE_ID_FIELD`` records
    its origin as ``"ClassName.field_name"`` so the value is always traceable.
    """

    ID: ClassVar[str] = "f2b8e4a1"
    COMPLETED_CODE: ClassVar[str] = ""
    COMPLETED_MESSAGE: ClassVar[str] = ""
    SOURCE_ID_FIELD: ClassVar[str] = ""
    _SUBCLASS_REGISTRY: ClassVar[dict[str, type["EtlResult"]]] = {}

    type: str = Field(
        default="",
        description="The class ID representing the specific ETL result subclass. This allows polymorphic deserialization of ETL results. The value is set to ID.",
    )
    status: EtlStatus = Field(
        default=EtlStatus.INITIALIZED,
        description="The current status of the ETL operation.",
    )
    source_id: str | None = Field(
        default=None,
        description="The source-system identifier relevant for the concrete subclass.",
    )
    logs: list[EtlLogItem] = Field(
        default_factory=list,
        description="Log items capturing messages and events that occurred during the operation.",
    )

    def add_logs(self, upload_log_items: list[EtlLogItem] | EtlLogItem) -> None:
        """Add log items to the upload result.

        If any of the added log items has severity ERROR, the upload status is set to
        FAILED.
        """
        if isinstance(upload_log_items, list):
            self.logs.extend(upload_log_items)
            if any(x.severity == LogLevel.ERROR for x in upload_log_items):
                self.status = EtlStatus.FAILED
        else:
            self.logs.append(upload_log_items)
            if upload_log_items.severity == LogLevel.ERROR:
                self.status = EtlStatus.FAILED

    def add_error(
        self,
        code: str,
        message: str,
        source: str | None = None,
        target: str | None = None,
    ) -> None:
        """Append an ERROR-severity log item and update the status."""
        self.logs.append(
            EtlLogItem(
                code=code,
                message=message,
                severity=LogLevel.ERROR,
                source=source,
                target=target,
            )
        )
        self.set_failed()

    def add_warning(
        self,
        code: str,
        message: str,
        source: str | None = None,
        target: str | None = None,
    ) -> None:
        """Append a WARN-severity log item."""
        self.logs.append(
            EtlLogItem(
                code=code,
                message=message,
                severity=LogLevel.WARN,
                source=source,
                target=target,
            )
        )

    def add_info(
        self,
        code: str,
        message: str,
        source: str | None = None,
        target: str | None = None,
    ) -> None:
        """Append an INFO-severity log item."""
        self.logs.append(
            EtlLogItem(
                code=code,
                message=message,
                severity=LogLevel.INFO,
                source=source,
                target=target,
            )
        )

    def has_errors(self) -> bool:
        """Return True if any log item has ERROR severity."""
        return any(x.severity == LogLevel.ERROR for x in self.logs)

    def has_warnings(self) -> bool:
        """Return True if any log item has WARN severity."""
        return any(x.severity == LogLevel.WARN for x in self.logs)

    def has_infos(self) -> bool:
        """Return True if any log item has INFO severity."""
        return any(x.severity == LogLevel.INFO for x in self.logs)

    def has_log_code(self, code: str) -> bool:
        """Return True if any log item carries the given code."""
        return any(x.code == code for x in self.logs)

    def get_errors(self) -> list[EtlLogItem]:
        """Return a list of log items with ERROR severity."""
        return [x for x in self.logs if x.severity == LogLevel.ERROR]

    def get_warnings(self) -> list[EtlLogItem]:
        """Return a list of log items with WARN severity."""
        return [x for x in self.logs if x.severity == LogLevel.WARN]

    def get_infos(self) -> list[EtlLogItem]:
        """Return a list of log items with INFO severity."""
        return [x for x in self.logs if x.severity == LogLevel.INFO]

    # TODO: method kept for backwards compatibility, remove in future versions
    @deprecated(reason="Use set_failed() instead.")  # type: ignore[misc]
    def set_error_status(self) -> None:
        """Set status to ERROR."""
        return self.set_failed()

    def set_failed(self) -> None:
        """Set status to FAILED."""
        self.status = EtlStatus.FAILED

    @deprecated(reason="Use set_completed() instead.")  # type: ignore[misc]
    def mark_completed(self) -> None:
        """Set the status to completed (deprecated)."""
        return self.set_completed()

    def set_completed(self) -> None:
        """Write the completion log entry and set status to SUCCESS if still INITIALIZED.

        Uses ``== INITIALIZED`` rather than ``!= ERROR`` so that subclasses can call
        their own status-propagation logic before calling super(), without the base
        method overwriting an already-set MIXED or ERROR status.
        """
        self.add_info(self.COMPLETED_CODE, self.COMPLETED_MESSAGE)
        if self.status == EtlStatus.INITIALIZED:
            self.status = EtlStatus.SUCCESS

    @deprecated(reason="Use is_completed() instead.")  # type: ignore[misc]
    def has_completed(self) -> bool:
        """Return True if the completion log code is present (deprecated)."""
        return self.is_completed()

    def is_completed(self) -> bool:
        """Return True if the completion log code is present."""
        return self.has_log_code(self.COMPLETED_CODE)

    @staticmethod
    def _deserialize(data: Any) -> Any:
        """Restore the concrete EtlResult subclass when deserialising from a dict.

        Restores the concrete EtlResult subclass from a dictionary representation.
        If the input is already an instance of BaseEtlResult, it is returned as-is.
        If the input is not a dictionary, it is returned as-is.
        Otherwise, the ``type`` field is used to look up the appropriate subclass
        in the registry and the subclass's ``model_validate`` method is called.
        """
        if isinstance(data, EtlResult):
            return data
        if not isinstance(data, dict):
            return data
        class_id = data["type"]
        if class_id not in EtlResult._SUBCLASS_REGISTRY:
            raise ValueError(f"Unknown subclass ID: {class_id}")
        cls = EtlResult._SUBCLASS_REGISTRY[class_id]
        return cls.model_validate(data)

    @model_validator(mode="after")
    def _validate_type(self) -> Self:
        self.type = self.ID
        return self

    def __new__(cls, **data: Any) -> Any:
        if cls is EtlResult and "type" in data:
            class_id = data["type"]
            subclass = cls._SUBCLASS_REGISTRY.get(class_id)
            if subclass is None:
                raise ValueError(f"Unknown subclass ID: {class_id}")
            return subclass.__new__(subclass, **data)
        return super().__new__(cls)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        if cls.ID in EtlResult._SUBCLASS_REGISTRY:
            raise ValueError(
                f"Duplicate {EtlResult.__name__} subclass ID: {cls.ID} - possibly the subclass ID was not set for class with name {cls.__name__}"
            )
        EtlResult._SUBCLASS_REGISTRY[cls.ID] = cls


class LoadResult(EtlResult):
    """Represents a load ETL result."""

    ID: ClassVar[str] = "7c2e9a5f"
    COMPLETED_CODE: ClassVar[str] = "a5b6c7d8"
    COMPLETED_MESSAGE: ClassVar[str] = "Load completed."


class TransformResult(EtlResult):
    """Represents a transform ETL result."""

    ID: ClassVar[str] = "a1f6b3c9"
    COMPLETED_CODE: ClassVar[str] = "3c4f5e6f"
    COMPLETED_MESSAGE: ClassVar[str] = "Transform completed."
    TARGET_ID_FIELD: ClassVar[str] = ""

    target_id: UUID | None = None


class ExtractResult(EtlResult):
    """Represents an extract ETL result."""

    ID: ClassVar[str] = "e5d2f8a6"
    COMPLETED_CODE: ClassVar[str] = "a5b6c7d8"
    COMPLETED_MESSAGE: ClassVar[str] = "Extract completed."


_T_Extract = TypeVar("_T_Extract", bound=ExtractResult)
_T_Transform = TypeVar("_T_Transform", bound=TransformResult)
_T_Load = TypeVar("_T_Load", bound=LoadResult)

AnyExtractResult = Annotated[
    SerializeAsAny[ExtractResult], BeforeValidator(EtlResult._deserialize)
]
AnyTransformResult = Annotated[
    SerializeAsAny[TransformResult], BeforeValidator(EtlResult._deserialize)
]
AnyLoadResult = Annotated[
    SerializeAsAny[LoadResult], BeforeValidator(EtlResult._deserialize)
]


class BatchEtlResult(EtlResult):
    """Represents a single stored batch result.

    Tracks the stored batch ID and the per-subject extract, transform, and load
    results that produced it. ``batch_id`` is ``None`` until the batch has been
    persisted by the repository. Call ``update_status_from_transforms()`` once
    all ``TransformResult``s are added.
    """

    ID: ClassVar[str] = "b9c3e7d1"
    COMPLETED_CODE: ClassVar[str] = "4d5e6f7a"
    COMPLETED_MESSAGE: ClassVar[str] = "Batch completed."
    SOURCE_ID_FIELD: ClassVar[str] = "BatchEtlResult.batch_id"

    batch_id: UUID | None = None
    extract_results: list[AnyExtractResult] = Field(default_factory=list)
    transform_results: list[AnyTransformResult] = Field(default_factory=list)
    load_results: list[AnyLoadResult] = Field(default_factory=list)

    def set_completed(self) -> None:
        """Propagate child statuses, then write the completion log entry.

        Calls update_status_from_extractions(), update_status_from_transforms(), and
        update_status_from_loads() first so that the final status reflects the actual
        outcomes before the base class sets SUCCESS for any still-INITIALIZED batch
        (i.e. one with no subjects).
        """
        self.update_status_from_extractions()
        self.update_status_from_transforms()
        self.update_status_from_loads()
        super().set_completed()

    def start_extract(
        self,
        source_id: str | None = None,
        result_type: type[_T_Extract] = ExtractResult,  # type: ignore[assignment]  # mypy can't prove the bare class satisfies type[_T] for an unbound TypeVar; callers get correct inference
    ) -> _T_Extract:
        """Create and register a new ExtractResult (or subclass), then return it.

        Registering up-front ensures that any logs written to the result are
        preserved in extract_results even if an exception aborts the
        subject's extraction before it completes.
        """
        extract_result = result_type(source_id=source_id)
        self.extract_results.append(extract_result)
        extract_result.add_info("b6c7d8e9", "Extract started.")
        return extract_result

    @deprecated("Use get_completed_extract_source_ids() instead.")
    def get_completed_extract_source_values(self) -> frozenset[str]:
        return self.get_completed_extract_source_ids()

    def get_completed_extract_source_ids(self) -> frozenset[str]:
        """Return the source_ids of all successfully completed ExtractResults."""
        return frozenset(
            x.source_id
            for x in self.extract_results
            if x.is_completed() and x.source_id is not None
        )

    def start_transform(
        self,
        source_id: str | None = None,
        result_type: type[_T_Transform] = TransformResult,  # type: ignore[assignment]  # mypy can't prove the bare class satisfies type[_T] for an unbound TypeVar; callers get correct inference
    ) -> _T_Transform:
        """Create and register a new TransformResult (or subclass), then return it.

        Registering up-front ensures that any logs written to the result are
        preserved in transform_results even if an exception aborts the
        subject's transformation before it completes.
        """
        transform_result = result_type(source_id=source_id)
        self.transform_results.append(transform_result)
        transform_result.add_info("d7a3f9c2", "Transform started.")
        return transform_result

    @deprecated("Use get_completed_transform_source_ids() instead.")
    def get_completed_source_values(self) -> frozenset[str]:
        return self.get_completed_transform_source_ids()

    def get_completed_transform_source_ids(self) -> frozenset[str]:
        """Return the source_ids of all successfully completed TransformResults."""
        return frozenset(
            x.source_id
            for x in self.transform_results
            if x.is_completed() and x.source_id is not None
        )

    @deprecated("Use get_completed_transform_target_ids() instead.")
    def get_completed_target_values(self) -> frozenset[UUID]:
        return self.get_completed_transform_target_ids()

    def get_completed_transform_target_ids(self) -> frozenset[UUID]:
        """Return the target_ids of all successfully completed TransformResults.

        Unlike ``get_completed_transform_source_ids``, this keys on the generated target
        identifier (e.g. the OMOP person_id), which is always present for a
        completed transform even when the source system has no stable id for the
        subject (e.g. non-human samples with a NULL patient_id).
        """
        return frozenset(
            x.target_id
            for x in self.transform_results
            if x.is_completed() and x.target_id is not None
        )

    def update_status_from_extractions(self) -> None:
        """Propagate ExtractResult statuses to batch status: SUCCESS / MIXED / ERROR.

        Once this method has set the status to MIXED or ERROR, subsequent calls to
        update_status_from_transforms() cannot improve the status back to SUCCESS.
        """
        if not self.extract_results:
            return
        # Extractions that were initialized but never completed are assumed to have failed.
        n_errors = sum(1 for x in self.extract_results if x.status != EtlStatus.SUCCESS)
        if n_errors == 0:
            self.status = EtlStatus.SUCCESS
        elif n_errors == len(self.extract_results):
            self.status = EtlStatus.FAILED
        else:
            self.status = EtlStatus.MIXED

    def add_load_result(self, result: LoadResult) -> None:
        """Register a load result returned by the remote app."""
        self.load_results.append(result)

    def update_status_from_loads(self) -> None:
        """Propagate LoadResult statuses to batch status: SUCCESS / MIXED / ERROR.

        Will not upgrade the status to SUCCESS if it was already MIXED or ERROR
        from a prior extract/transform phase.
        """
        if not self.load_results:
            return
        n_errors = sum(
            1
            for x in self.load_results
            if x.status not in EtlStatusSet.NOT_FAILED.value
        )
        if n_errors == 0:
            if self.status not in (
                EtlStatus.MIXED,
                EtlStatus.FAILED,
            ):
                self.status = EtlStatus.SUCCESS
        elif n_errors == len(self.load_results):
            self.status = EtlStatus.FAILED
        else:
            self.status = EtlStatus.MIXED

    @deprecated("Use for_source() instead")  # type: ignore[misc]
    def for_subject(self, source_id: str) -> "BatchEtlResult":
        return self.for_source(source_id)

    def for_source(self, source_id: str) -> "BatchEtlResult":
        """Return a copy of this batch filtered to results for a single source."""
        retval: BatchEtlResult = self.model_copy(
            update={
                "extract_results": [
                    x for x in self.extract_results if x.source_id == source_id
                ],
                "transform_results": [
                    x for x in self.transform_results if x.source_id == source_id
                ],
                "load_results": list(
                    self.load_results
                ),  # LoadResult has no source_id to filter by
            }
        )
        return retval

    def update_status_from_transforms(self) -> None:
        """Propagate TransformResult statuses: SUCCESS / MIXED / ERROR.

        Will not upgrade the status to SUCCESS if it was already set to MIXED or ERROR
        by a prior call to update_status_from_extractions().
        """
        if not self.transform_results:
            return
        # Note that transforms that were started but never completed are assumed to have failed.
        n_errors = sum(
            1
            for x in self.transform_results
            if x.status not in EtlStatusSet.NOT_FAILED.value
        )
        if n_errors == 0:
            if self.status not in (
                EtlStatus.MIXED,
                EtlStatus.FAILED,
            ):
                self.status = EtlStatus.SUCCESS
        elif n_errors == len(self.transform_results):
            self.status = EtlStatus.FAILED
        else:
            self.status = EtlStatus.MIXED


class JobEtlResult(EtlResult):
    """Represents a top-level ETL job result.

    Collects ``BatchEtlResult``s as batches are stored, tracking the overall run
    status, command ID, and batch type.

    Model validation: Before validation, ``_coerce_command_id`` generates a new
    UUID for ``etl_command_id`` if one is not provided.
    """

    ID: ClassVar[str] = "7c1c2cce"

    etl_command_id: UUID = Field(default_factory=uuid.uuid4)
    etl_name: str
    batch_type: str | None = None
    batches: list[BatchEtlResult] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _coerce_command_id(cls, data: Any) -> Any:  # type: ignore[misc]
        if isinstance(data, dict) and data.get("etl_command_id") is None:
            data = {**data, "etl_command_id": uuid.uuid4()}
        return data

    @property
    def batch_ids(self) -> list[UUID]:
        """UUIDs of all successfully stored batches produced in this run, in order."""
        return [x.batch_id for x in self.batches if x.batch_id is not None]

    def start_batch(self) -> BatchEtlResult:
        """Create and register a new BatchEtlResult, then return it.

        Registering up-front ensures that any logs written to the batch are
        preserved in etl_result.batches even if an exception aborts the loop
        iteration before the batch reaches storage.
        """
        batch = BatchEtlResult()
        self.batches.append(batch)
        return batch

    def update_status_from_batches(self) -> None:
        """Set status based on ``BatchEtlResult`` statuses.

        Call this once the batching loop has completed normally. If status is
        already FAILED (set via ``add_error()``), this is a no-op. INITIALIZED
        batches (started but containing no subjects, e.g. the terminal empty
        batch) are excluded from propagation and do not affect the outcome.
        """
        if self.status == EtlStatus.FAILED:
            return
        processed = [x for x in self.batches if x.status != EtlStatus.INITIALIZED]
        if not processed:
            self.status = EtlStatus.SUCCESS
            return
        n_error_or_mixed = sum(
            1 for x in processed if x.status in (EtlStatus.FAILED, EtlStatus.MIXED)
        )
        if n_error_or_mixed == 0:
            self.status = EtlStatus.SUCCESS
        elif n_error_or_mixed == len(processed):
            self.status = EtlStatus.FAILED
        else:
            self.status = EtlStatus.MIXED

    def summary_fields(self) -> dict[str, str | int]:
        """Flatten this result into the key/value fields of a one-line run summary.

        Pure derived state: counts of extract / transform / load outcomes across
        all non-INITIALIZED batches, plus the overall status and stored-batch
        count. Intended for a uniform, machine-parseable ``run-summary`` log line
        that any ETL flow can emit regardless of its source or target system.

        INITIALIZED batches (started but never given a subject, e.g. the terminal
        empty batch that ends a paging loop) are excluded.
        """
        batches = [x for x in self.batches if x.status != EtlStatus.INITIALIZED]
        not_failed_load = EtlStatusSet.NOT_FAILED.value
        n_extracted_ok = n_extracted_failed = 0
        n_transformed_ok = n_transformed_failed = 0
        n_loaded_ok = n_loaded_failed = 0
        for batch in batches:
            for extract in batch.extract_results:
                if extract.status == EtlStatus.SUCCESS:
                    n_extracted_ok += 1
                else:
                    n_extracted_failed += 1
            for transform in batch.transform_results:
                if transform.status == EtlStatus.SUCCESS:
                    n_transformed_ok += 1
                else:
                    n_transformed_failed += 1
            for load in batch.load_results:
                if load.status in not_failed_load:
                    n_loaded_ok += 1
                else:
                    n_loaded_failed += 1
        return {
            "flow": self.etl_name,
            "batch_type": self.batch_type or "",
            "status": self.status.value,
            "n_batches": len(batches),
            "n_stored_batches": len(self.batch_ids),
            "n_extracted_ok": n_extracted_ok,
            "n_extracted_failed": n_extracted_failed,
            "n_transformed_ok": n_transformed_ok,
            "n_transformed_failed": n_transformed_failed,
            "n_loaded_ok": n_loaded_ok,
            "n_loaded_failed": n_loaded_failed,
        }
