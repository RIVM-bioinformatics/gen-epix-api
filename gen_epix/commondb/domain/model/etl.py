"""Shared ETL-run result accumulators.

These models track the outcome of a multi-stage ETL run (extract -> transform ->
load): per-run (:class:`EtlResult`), per-stored-batch (:class:`EtlBatchResult`)
and per-subject (:class:`ExtractResult`, :class:`TransformResult`) accumulators,
each carrying structured logs and a roll-up status.

Naming notes:

* :class:`BaseEtlResult` here is the accumulator base and is distinct from
  :class:`gen_epix.commondb.domain.model.base.BaseResult` (its parent, formerly
  ``BaseEtlResult``).
* :class:`TransformResult` here is unrelated to
  :class:`gen_epix.transform.TransformResult` (a stream-processing helper).

Concrete ``TransformResult`` / ``ExtractResult`` subclasses are defined by the ETL
services that consume this module. They register themselves through
``__init_subclass__`` and are only reconstructed as their concrete type by
``model_validate`` once their defining module has been imported; otherwise they
round-trip as the base class.
"""

import uuid
from typing import Annotated, Any, ClassVar, TypeVar
from uuid import UUID

from pydantic import BeforeValidator, Field, SerializeAsAny, model_validator

from gen_epix.commondb.domain import enum as commondb_enum
from gen_epix.commondb.domain.model.base import BaseResult
from gen_epix.commondb.domain.model.upload import BaseBatchUploadResult, UploadResult

# Registries populated automatically via TransformResult/__init_subclass__ and
# ExtractResult/__init_subclass__.  Dispatch functions and Annotated aliases
# (AnyTransformResult, AnyExtractResult) are defined after the classes.
_TRANSFORM_REGISTRY: dict[str, type[Any]] = {}
_EXTRACT_REGISTRY: dict[str, type[Any]] = {}


class BaseEtlResult(BaseResult):
    """
    Base class for ETL result accumulators.

    Inherits ``logs`` from ``BaseResult``; adds ``status``, ``source_id``,
    ``_SOURCE_ID_FIELD``, and the ``mark_completed`` / ``has_completed`` pattern
    driven by per-subclass ``_COMPLETED_CODE`` / ``_COMPLETED_MESSAGE`` class variables.

    ``source_id`` stores whichever source-system identifier is most relevant for
    the concrete subclass as a string; ``_SOURCE_ID_FIELD`` records its origin as
    ``"ClassName.field_name"`` so the value is always traceable.
    """

    status: commondb_enum.EtlStatus = commondb_enum.EtlStatus.INITIALIZED
    source_id: str | None = None
    _COMPLETED_CODE: ClassVar[str] = ""
    _COMPLETED_MESSAGE: ClassVar[str] = ""
    _SOURCE_ID_FIELD: ClassVar[str] = ""

    def set_error_status(self) -> None:
        self.status = commondb_enum.EtlStatus.ERROR

    def mark_completed(self) -> None:
        """Write the completion log entry and set status to SUCCESS if still INITIALIZED.

        Uses ``== INITIALIZED`` rather than ``!= ERROR`` so that subclasses can call
        their own status-propagation logic before calling super(), without the base
        method overwriting an already-set MIXED or ERROR status.
        """
        self.add_info(self._COMPLETED_CODE, self._COMPLETED_MESSAGE)
        if self.status == commondb_enum.EtlStatus.INITIALIZED:
            self.status = commondb_enum.EtlStatus.SUCCESS

    def has_completed(self) -> bool:
        """Return True if the completion log code is present."""
        return self.has_log_code(self._COMPLETED_CODE)


class TransformResult(BaseEtlResult):
    """
    Generic transform-result accumulator.

    Concrete subclasses should declare ``_SOURCE_ID_FIELD``, ``_TARGET_ID_FIELD``,
    ``_COMPLETED_CODE``, and ``_COMPLETED_MESSAGE``; ``source_id`` is inherited from
    ``BaseEtlResult``.
    Status is set to ERROR automatically when add_error() is called.
    ``result_type`` is set automatically to the concrete class name on every
    instantiation and is used by ``AnyTransformResult`` to restore the correct
    subclass when deserialising from a stored dict.
    """

    _COMPLETED_CODE: ClassVar[str] = "3c4f5e6f"
    _COMPLETED_MESSAGE: ClassVar[str] = "TransformResult completed."
    _TARGET_ID_FIELD: ClassVar[str] = ""

    target_id: UUID | None = None
    result_type: str = Field(default="")

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _TRANSFORM_REGISTRY[cls.__name__] = cls

    @model_validator(mode="after")
    def _ensure_result_type(self) -> "TransformResult":
        if not self.result_type:
            self.result_type = type(self).__name__
        return self


class ExtractResult(BaseEtlResult):
    """
    Generic extract-result accumulator.

    Concrete subclasses should declare ``_SOURCE_ID_FIELD``, ``_COMPLETED_CODE``, and
    ``_COMPLETED_MESSAGE``; ``source_id`` is inherited from ``BaseEtlResult``.
    Status is set to ERROR automatically when add_error() is called.
    ``result_type`` is set automatically to the concrete class name on every
    instantiation and is used by ``AnyExtractResult`` to restore the correct
    subclass when deserialising from a stored dict.
    """

    _COMPLETED_CODE: ClassVar[str] = "a5b6c7d8"
    _COMPLETED_MESSAGE: ClassVar[str] = "ExtractResult completed successfully."

    result_type: str = Field(default="")

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _EXTRACT_REGISTRY[cls.__name__] = cls

    @model_validator(mode="after")
    def _ensure_result_type(self) -> "ExtractResult":
        if not self.result_type:
            self.result_type = type(self).__name__
        return self


_T_Extract = TypeVar("_T_Extract", bound=ExtractResult)
_T_Transform = TypeVar("_T_Transform", bound=TransformResult)


class EtlBatchResult(BaseEtlResult):
    """
    Result of a single stored batch: tracks the stored batch ID and the
    per-subject extract, transform, and load results that produced it.

    batch_id is None until the batch has been persisted by the repository.
    Call update_status_from_transforms() once all TransformResults are added.
    """

    _COMPLETED_CODE: ClassVar[str] = "4d5e6f7a"
    _COMPLETED_MESSAGE: ClassVar[str] = "EtlBatchResult completed."
    _SOURCE_ID_FIELD: ClassVar[str] = "EtlBatchResult.batch_id"

    batch_id: UUID | None = None
    extract_results: list["AnyExtractResult"] = Field(default_factory=list)
    transform_results: list["AnyTransformResult"] = Field(default_factory=list)
    load_results: list["AnyUploadResult"] = Field(default_factory=list)

    def mark_completed(self) -> None:
        """Propagate child statuses, then write the completion log entry.

        Calls update_status_from_extractions(), update_status_from_transforms(), and
        update_status_from_loads() first so that the final status reflects the actual
        outcomes before the base class sets SUCCESS for any still-INITIALIZED batch
        (i.e. one with no subjects).
        """
        self.update_status_from_extractions()
        self.update_status_from_transforms()
        self.update_status_from_loads()
        super().mark_completed()

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
        extract_result.add_info("b6c7d8e9", "ExtractResult started.")
        return extract_result

    def completed_extract_source_values(self) -> frozenset[str]:
        """Return the source_ids of all successfully completed ExtractResults."""
        return frozenset(
            x.source_id
            for x in self.extract_results
            if x.has_completed() and x.source_id is not None
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
        transform_result.add_info("1a2b3c4d", "TransformResult started.")
        return transform_result

    def get_completed_source_values(self) -> frozenset[str]:
        """Return the source_ids of all successfully completed TransformResults."""
        return frozenset(
            x.source_id
            for x in self.transform_results
            if x.has_completed() and x.source_id is not None
        )

    def get_completed_target_values(self) -> frozenset[UUID]:
        """Return the target_ids of all successfully completed TransformResults.

        Unlike ``get_completed_source_values``, this keys on the generated target
        identifier (e.g. the OMOP person_id), which is always present for a
        completed transform even when the source system has no stable id for the
        subject (e.g. non-human samples with a NULL patient_id).
        """
        return frozenset(
            x.target_id
            for x in self.transform_results
            if x.has_completed() and x.target_id is not None
        )

    def update_status_from_extractions(self) -> None:
        """Propagate ExtractResult statuses to batch status: SUCCESS / MIXED / ERROR.

        Once this method has set the status to MIXED or ERROR, subsequent calls to
        update_status_from_transforms() cannot improve the status back to SUCCESS.
        """
        if not self.extract_results:
            return
        # Extractions that were initialized but never completed are assumed to have failed.
        n_errors = sum(
            1
            for x in self.extract_results
            if x.status != commondb_enum.EtlStatus.SUCCESS
        )
        if n_errors == 0:
            self.status = commondb_enum.EtlStatus.SUCCESS
        elif n_errors == len(self.extract_results):
            self.status = commondb_enum.EtlStatus.ERROR
        else:
            self.status = commondb_enum.EtlStatus.MIXED

    def add_load_result(self, result: UploadResult) -> None:
        """Register a load result returned by the remote app."""
        self.load_results.append(result)

    def update_status_from_loads(self) -> None:
        """Propagate UploadResult statuses to batch status: SUCCESS / MIXED / ERROR.

        Will not upgrade the status to SUCCESS if it was already MIXED or ERROR
        from a prior extract/transform phase.
        """
        if not self.load_results:
            return
        n_errors = sum(
            1
            for x in self.load_results
            if x.status not in commondb_enum.UploadStatusSet.NOT_FAILED.value
        )
        if n_errors == 0:
            if self.status not in (
                commondb_enum.EtlStatus.MIXED,
                commondb_enum.EtlStatus.ERROR,
            ):
                self.status = commondb_enum.EtlStatus.SUCCESS
        elif n_errors == len(self.load_results):
            self.status = commondb_enum.EtlStatus.ERROR
        else:
            self.status = commondb_enum.EtlStatus.MIXED

    # TODO: rename to for_source()
    def for_subject(self, source_id: str) -> "EtlBatchResult":
        """Return a copy of this EtlBatchResult filtered to results for a single subject."""
        retval: EtlBatchResult = self.model_copy(
            update={
                "extract_results": [
                    x for x in self.extract_results if x.source_id == source_id
                ],
                "transform_results": [
                    x for x in self.transform_results if x.source_id == source_id
                ],
                "load_results": list(
                    self.load_results
                ),  # UploadResult has no source_id to filter by
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
        # Note that transforms that were initialized but never completed are assumed to have failed.
        n_errors = sum(
            1
            for x in self.transform_results
            if x.status != commondb_enum.EtlStatus.SUCCESS
        )
        if n_errors == 0:
            if self.status not in (
                commondb_enum.EtlStatus.MIXED,
                commondb_enum.EtlStatus.ERROR,
            ):
                self.status = commondb_enum.EtlStatus.SUCCESS
        elif n_errors == len(self.transform_results):
            self.status = commondb_enum.EtlStatus.ERROR
        else:
            self.status = commondb_enum.EtlStatus.MIXED


class SeqDistanceUpdateResult(BaseEtlResult):
    """Result accumulator for one deferred seq-distance update run (one protocol).

    Holds one INFO log per processed batch and a final completion entry.
    n_profiles_processed counts newly created SeqDistance records (CREATED status);
    n_batches counts non-empty calls made.
    """

    _COMPLETED_CODE: ClassVar[str] = "e3f1a2b4"
    _COMPLETED_MESSAGE: ClassVar[str] = "Seq distance update completed."

    protocol_id: UUID
    n_profiles_processed: int = 0
    n_batches: int = 0


class EtlResult(BaseEtlResult):
    """
    Top-level ETL run accumulator. Collects EtlBatchResults as batches are stored.
    """

    etl_command_id: UUID = Field(default_factory=uuid.uuid4)
    etl_name: str
    batch_type: str | None = None
    batches: list[EtlBatchResult] = Field(default_factory=list)

    def set_error_status(self) -> None:
        self.status = commondb_enum.EtlStatus.FAILED

    @model_validator(mode="before")
    @classmethod
    def _coerce_command_id(cls, data: Any) -> Any:
        if isinstance(data, dict) and data.get("etl_command_id") is None:
            data = {**data, "etl_command_id": uuid.uuid4()}
        return data

    @property
    def batch_ids(self) -> list[UUID]:
        """UUIDs of all successfully stored batches produced in this run, in order."""
        return [x.batch_id for x in self.batches if x.batch_id is not None]

    def start_batch(self) -> EtlBatchResult:
        """Create and register a new EtlBatchResult, then return it.

        Registering up-front ensures that any logs written to the batch are
        preserved in etl_result.batches even if an exception aborts the loop
        iteration before the batch reaches storage.
        """
        batch = EtlBatchResult()
        self.batches.append(batch)
        return batch

    def update_status_from_batches(self) -> None:
        """
        Set EtlResult status based on EtlBatchResult statuses.
        Call this once the batching loop has completed normally.
        If status is already FAILURE (set via add_error), this is a no-op.

        INITIALIZED batches (started but containing no subjects, e.g. the
        terminal empty batch) are excluded from propagation and do not affect
        the outcome.
        """
        if self.status == commondb_enum.EtlStatus.FAILED:
            return
        processed = [
            x for x in self.batches if x.status != commondb_enum.EtlStatus.INITIALIZED
        ]
        if not processed:
            self.status = commondb_enum.EtlStatus.SUCCESS
            return
        n_error_or_mixed = sum(
            1
            for x in processed
            if x.status
            in (commondb_enum.EtlStatus.ERROR, commondb_enum.EtlStatus.MIXED)
        )
        if n_error_or_mixed == 0:
            self.status = commondb_enum.EtlStatus.SUCCESS
        elif n_error_or_mixed == len(processed):
            self.status = commondb_enum.EtlStatus.ERROR
        else:
            self.status = commondb_enum.EtlStatus.MIXED

    def summary_fields(self) -> dict[str, str | int]:
        """Flatten this result into the key/value fields of a one-line run summary.

        Pure derived state: counts of extract / transform / load outcomes across
        all non-INITIALIZED batches, plus the overall status and stored-batch
        count. Intended for a uniform, machine-parseable ``run-summary`` log line
        that any ETL flow can emit regardless of its source or target system.

        INITIALIZED batches (started but never given a subject, e.g. the terminal
        empty batch that ends a paging loop) are excluded.
        """
        batches = [
            x for x in self.batches if x.status != commondb_enum.EtlStatus.INITIALIZED
        ]
        not_failed_load = commondb_enum.UploadStatusSet.NOT_FAILED.value
        n_extracted_ok = n_extracted_failed = 0
        n_transformed_ok = n_transformed_failed = 0
        n_loaded_ok = n_loaded_failed = 0
        for batch in batches:
            for extract in batch.extract_results:
                if extract.status == commondb_enum.EtlStatus.SUCCESS:
                    n_extracted_ok += 1
                else:
                    n_extracted_failed += 1
            for transform in batch.transform_results:
                if transform.status == commondb_enum.EtlStatus.SUCCESS:
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


# ---------------------------------------------------------------------------
# Polymorphic field helpers
# ---------------------------------------------------------------------------
# These annotated aliases are used by EtlBatchResult.extract_results /
# transform_results / load_results so that:
#   • Serialisation  – SerializeAsAny ensures the *runtime* type is used,
#     preserving subclass-specific fields.
#   • Deserialisation – BeforeValidator dispatches to the correct subclass
#     via the _TRANSFORM_REGISTRY / _EXTRACT_REGISTRY (populated by
#     __init_subclass__) or the upload-result registry, using a "result_type"
#     discriminator field.
# The registries are populated lazily as subclass modules are imported, so
# every concrete subclass that has been imported before model_validate is
# called will be restorable correctly.


def _dispatch_transform(data: Any) -> Any:
    if isinstance(data, TransformResult):
        return data
    if isinstance(data, dict):
        cls = _TRANSFORM_REGISTRY.get(data.get("result_type", ""))
        if cls is not None:
            return cls.model_validate(data)
    return data


def _dispatch_extract(data: Any) -> Any:
    if isinstance(data, ExtractResult):
        return data
    if isinstance(data, dict):
        cls = _EXTRACT_REGISTRY.get(data.get("result_type", ""))
        if cls is not None:
            return cls.model_validate(data)
    return data


def _dispatch_upload(data: Any) -> Any:
    """Restore the concrete UploadResult subclass when deserialising from a dict.

    Delegates the type resolution to ``BaseBatchUploadResult.resolve_subclass``
    (registry lookup on the ``result_type`` discriminator, with a legacy fallback
    on parent-results field names). Falls back to a plain ``UploadResult`` for
    individual-item results.
    """
    if isinstance(data, UploadResult):
        return data
    if not isinstance(data, dict):
        return data
    cls = BaseBatchUploadResult.resolve_subclass(data)
    if cls is not None:
        return cls.model_validate(data)
    return UploadResult.model_validate(data)


AnyTransformResult = Annotated[
    SerializeAsAny[TransformResult], BeforeValidator(_dispatch_transform)
]
AnyExtractResult = Annotated[
    SerializeAsAny[ExtractResult], BeforeValidator(_dispatch_extract)
]

AnyUploadResult = Annotated[
    SerializeAsAny[UploadResult], BeforeValidator(_dispatch_upload)
]

# Resolve forward references now that AnyTransformResult / AnyExtractResult
# / AnyUploadResult are defined.
EtlBatchResult.model_rebuild()
