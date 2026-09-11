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


class LogItem(BaseModel):
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


class Result(BaseModel):
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
    _SUBCLASS_REGISTRY: ClassVar[dict[str, type["Result"]]] = {}

    type: str = Field(
        default="",
        description="The class ID representing the specific ETL result subclass. This allows polymorphic deserialization of ETL results. The value is set equal to the ID class variable.",
    )
    status: EtlStatus = Field(
        default=EtlStatus.PENDING,
        description="The current status of the ETL operation.",
    )
    source_id: str | None = Field(
        default=None,
        description="The source-system identifier relevant for the concrete subclass.",
    )
    logs: list[LogItem] = Field(
        default_factory=list,
        description="Log items capturing messages and events that occurred during the operation.",
    )

    def add_logs(self, upload_log_items: list[LogItem] | LogItem) -> None:
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
            LogItem(
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
            LogItem(
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
            LogItem(
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

    def get_errors(self) -> list[LogItem]:
        """Return a list of log items with ERROR severity."""
        return [x for x in self.logs if x.severity == LogLevel.ERROR]

    def get_warnings(self) -> list[LogItem]:
        """Return a list of log items with WARN severity."""
        return [x for x in self.logs if x.severity == LogLevel.WARN]

    def get_infos(self) -> list[LogItem]:
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

    def set_mixed(self) -> None:
        """Set status to MIXED."""
        self.status = EtlStatus.MIXED

    def set_success(self) -> None:
        """Set status to SUCCESS."""
        self.status = EtlStatus.SUCCESS

    def is_success(self) -> bool:
        """Return True if status is SUCCESS."""
        return self.status == EtlStatus.SUCCESS

    def is_failed(self) -> bool:
        """Return True if status is FAILED."""
        return self.status == EtlStatus.FAILED

    def is_pending(self) -> bool:
        """Return True if status is PENDING."""
        return self.status == EtlStatus.PENDING

    def is_mixed(self) -> bool:
        """Return True if status is MIXED."""
        return self.status == EtlStatus.MIXED

    @deprecated(reason="Use set_completed() instead.")  # type: ignore[misc]
    def mark_completed(self) -> None:
        """Set the status to completed (deprecated)."""
        return self.set_completed()

    def set_completed(self) -> None:
        """Write the completion log entry and set status to SUCCESS if still PENDING.

        Uses ``== PENDING`` rather than ``!= ERROR`` so that subclasses can call
        their own status-propagation logic before calling super(), without the base
        method overwriting an already-set MIXED or ERROR status.
        """
        self.add_info(self.COMPLETED_CODE, self.COMPLETED_MESSAGE)
        if self.status == EtlStatus.PENDING:
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
        if isinstance(data, Result):
            return data
        if not isinstance(data, dict):
            return data
        class_id = data["type"]
        if class_id not in Result._SUBCLASS_REGISTRY:
            raise ValueError(f"Unknown subclass ID: {class_id}")
        cls = Result._SUBCLASS_REGISTRY[class_id]
        return cls.model_validate(data)

    @model_validator(mode="after")
    def _validate_type(self) -> Self:
        self.type = self.ID
        return self

    def __new__(cls, **data: Any) -> Any:
        if cls is Result and "type" in data:
            class_id = data["type"]
            subclass = cls._SUBCLASS_REGISTRY.get(class_id)
            if subclass is None:
                raise ValueError(f"Unknown subclass ID: {class_id}")
            return subclass.__new__(subclass, **data)
        return super().__new__(cls)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        if cls.ID in Result._SUBCLASS_REGISTRY:
            raise ValueError(
                f"Duplicate {Result.__name__} subclass ID: {cls.ID} - possibly the subclass ID was not set for class with name {cls.__name__}"
            )
        Result._SUBCLASS_REGISTRY[cls.ID] = cls


class LoadResult(Result):
    """Represents a load ETL result."""

    ID: ClassVar[str] = "7c2e9a5f"
    COMPLETED_CODE: ClassVar[str] = "a5b6c7d8"
    COMPLETED_MESSAGE: ClassVar[str] = "Load completed."


def _require_own_completed_code(cls: type) -> None:
    """Raise if a subclass doesn't declare its own COMPLETED_CODE/COMPLETED_MESSAGE.

    Without this, a subclass that misspells or forgets to override these
    silently inherits the parent's generic completion code/message instead
    of erroring — the bug found in idsdb's and lsp-data's own subclasses
    after the ClassVar names were changed out from under them.
    """
    missing = [
        name
        for name in ("COMPLETED_CODE", "COMPLETED_MESSAGE")
        if name not in cls.__dict__
    ]
    if missing:
        raise TypeError(
            f"{cls.__name__} must define its own {' and '.join(missing)} "
            f"(inherited from {cls.__mro__[1].__name__} is not enough)."
        )


class TransformResult(Result):
    """Represents a transform ETL result."""

    ID: ClassVar[str] = "a1f6b3c9"
    COMPLETED_CODE: ClassVar[str] = "3c4f5e6f"
    COMPLETED_MESSAGE: ClassVar[str] = "Transform completed."
    TARGET_ID_FIELD: ClassVar[str] = ""

    target_id: UUID | None = Field(
        default=None, description="Target ID for the transform result"
    )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _require_own_completed_code(cls)


class ExtractResult(Result):
    """Represents an extract ETL result."""

    ID: ClassVar[str] = "e5d2f8a6"
    COMPLETED_CODE: ClassVar[str] = "a5b6c7d8"
    COMPLETED_MESSAGE: ClassVar[str] = "Extract completed."

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _require_own_completed_code(cls)


_T_Extract = TypeVar("_T_Extract", bound=ExtractResult)
_T_Transform = TypeVar("_T_Transform", bound=TransformResult)
_T_Load = TypeVar("_T_Load", bound=LoadResult)

AnyExtractResult = Annotated[
    SerializeAsAny[ExtractResult], BeforeValidator(Result._deserialize)
]
AnyTransformResult = Annotated[
    SerializeAsAny[TransformResult], BeforeValidator(Result._deserialize)
]
AnyLoadResult = Annotated[
    SerializeAsAny[LoadResult], BeforeValidator(Result._deserialize)
]


class BatchResult(Result):
    """Represents a single ETL batch result, consisting of extract, transform, and load
    results.
    """

    ID: ClassVar[str] = "b9c3e7d1"
    COMPLETED_CODE: ClassVar[str] = "4d5e6f7a"
    COMPLETED_MESSAGE: ClassVar[str] = "Batch completed."
    SOURCE_ID_FIELD: ClassVar[str] = "BatchResult.batch_id"

    batch_id: str | None = Field(
        default=None,
        description="Identifier of the stored batch, if this result was persisted",
    )
    extract_results: list[AnyExtractResult] = Field(
        default_factory=list, description="List of extract results for the batch"
    )
    transform_results: list[AnyTransformResult] = Field(
        default_factory=list, description="List of transform results for the batch"
    )
    load_results: list[AnyLoadResult] = Field(
        default_factory=list, description="List of load results for the batch"
    )

    @field_validator("batch_id", mode="before")
    def _validate_batch_id(cls, value):
        if value is not None and not isinstance(value, str):
            return str(value)
        return value

    def set_completed(self) -> None:
        """Propagate child statuses, then write the completion log entry.

        Calls update_status_from_extractions(), update_status_from_transforms(), and
        update_status_from_loads() first so that the final status reflects the actual
        outcomes before the base class sets SUCCESS for any still-PENDING batch
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
        n_errors = sum(1 for x in self.extract_results if not x.is_success())
        if n_errors == 0:
            self.set_success()
        elif n_errors == len(self.extract_results):
            self.set_failed()
        else:
            self.set_mixed()

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
            if not (self.is_mixed() or self.is_failed()):
                self.set_success()
        elif n_errors == len(self.load_results):
            self.set_failed()
        else:
            self.set_mixed()

    def update_status_from_transforms(self) -> None:
        """Propagate TransformResult statuses: SUCCESS / MIXED / ERROR.

        Will not upgrade the status to SUCCESS if it was already set to MIXED or ERROR
        by a prior call to update_status_from_extractions().
        """
        if not self.transform_results:
            return
        # Note that transforms that were started but never completed are assumed to have failed.
        n_errors = sum(1 for x in self.transform_results if not x.is_success())
        if n_errors == 0:
            if not (self.is_mixed() or self.is_failed()):
                self.set_success()
        elif n_errors == len(self.transform_results):
            self.set_failed()
        else:
            self.set_mixed()

    def add_results(
        self,
        results: (
            list[ExtractResult | TransformResult | LoadResult]
            | ExtractResult
            | TransformResult
            | LoadResult
        ),
    ) -> None:
        """Add one or more ETL results (extract, transform, or load) to this batch."""
        if not isinstance(results, list):
            results = [results]
        for result in results:
            if isinstance(result, ExtractResult):
                self.extract_results.append(result)
            elif isinstance(result, TransformResult):
                self.transform_results.append(result)
            elif isinstance(result, LoadResult):
                self.load_results.append(result)

    @deprecated("Use for_source() instead")  # type: ignore[misc]
    def for_subject(self, source_id: str) -> "BatchResult":
        return self.for_source(source_id)

    def for_source(self, source_id: str) -> "BatchResult":
        """Return a copy of this batch filtered to results for a single source."""
        retval: BatchResult = self.model_copy(
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


class JobResult(Result):
    """Represents a top-level ETL job result consisting of multiple batches."""

    ID: ClassVar[str] = "7c1c2cce"
    COMPLETED_CODE: ClassVar[str] = "fd6d5984"
    COMPLETED_MESSAGE: ClassVar[str] = "Job completed."

    job_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the job",
    )
    etl_name: str = Field(description="Name of the ETL process")
    batch_type: str | None = Field(default=None, description="Type of the batch")
    batches: list[BatchResult] = Field(
        default_factory=list, description="List of batches in this job"
    )

    @field_validator("job_id", mode="before")
    def _validate_job_id(cls, value):
        if value is None:
            return str(uuid.uuid4())
        elif not isinstance(value, str):
            return str(value)
        return value

    @property
    def batch_ids(self) -> list[str]:
        """IDs of all successfully stored batches produced in this run, in order."""
        return [x.batch_id for x in self.batches if x.batch_id is not None]

    def start_batch(self) -> BatchResult:
        """Create and register a new BatchEtlResult, then return it.

        Registering up-front ensures that any logs written to the batch are
        preserved in etl_result.batches even if an exception aborts the loop
        iteration before the batch reaches storage.
        """
        batch = BatchResult()
        self.batches.append(batch)
        return batch

    def update_status_from_batches(self) -> None:
        """Set status based on ``BatchEtlResult`` statuses.

        Call this once the batching loop has completed normally. If status is
        already FAILED (set via ``add_error()``), this is a no-op. PENDING
        batches (started but containing no subjects, e.g. the terminal empty
        batch) are excluded from propagation and do not affect the outcome.
        """
        if self.is_failed():
            return
        processed = [x for x in self.batches if not x.is_pending()]
        if not processed:
            self.set_success()
            return
        n_error_or_mixed = sum(1 for x in processed if x.is_failed() or x.is_mixed())
        if n_error_or_mixed == 0:
            self.set_success()
        elif n_error_or_mixed == len(processed):
            self.set_failed()
        else:
            self.set_mixed()

    def get_summary(self) -> dict[str, str | int]:
        """Flatten this result into the key/value fields of a one-line run summary.

        Pure derived state: counts of extract / transform / load outcomes across
        all non-PENDING batches, plus the overall status and stored-batch
        count. Intended for a uniform, machine-parseable ``run-summary`` log line
        that any ETL flow can emit regardless of its source or target system.

        PENDING batches (started but never given a subject, e.g. the terminal
        empty batch that ends a paging loop) are excluded.
        """
        batches = [x for x in self.batches if not x.is_pending()]
        not_failed_load = EtlStatusSet.NOT_FAILED.value
        n_extracted_ok = n_extracted_failed = 0
        n_transformed_ok = n_transformed_failed = 0
        n_loaded_ok = n_loaded_failed = 0
        for batch in batches:
            for extract in batch.extract_results:
                if extract.is_success():
                    n_extracted_ok += 1
                else:
                    n_extracted_failed += 1
            for transform in batch.transform_results:
                if transform.is_success():
                    n_transformed_ok += 1
                else:
                    n_transformed_failed += 1
            for load in batch.load_results:
                if load.status in not_failed_load:
                    n_loaded_ok += 1
                else:
                    n_loaded_failed += 1
        return {
            "etl_name": self.etl_name,
            "job_id": self.job_id,
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
