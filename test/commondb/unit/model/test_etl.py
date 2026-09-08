"""Unit tests for the shared ETL-run result accumulators in commondb.

Covers status roll-up on EtlBatchResult / EtlResult, the etl_command_id coercion,
and — most importantly — that polymorphic transform / extract / upload results
survive a JSON round-trip through EtlBatchResult as their concrete subclasses,
including subclasses defined outside the module and legacy payloads written before
the ``result_type`` discriminator existed.
"""

import pytest

from gen_epix import casedb_model, omopdb_model, seqdb_model
from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.commondb.domain.model.etl import (
    EtlBatchResult,
    EtlResult,
    ExtractResult,
    TransformResult,
)
from gen_epix.commondb.domain.model.upload import (
    BaseBatchUploadResult,
    UploadResult,
)

# ---------------------------------------------------------------------------
# Local subclasses defined *outside* gen_epix.commondb.domain.model.etl, to prove
# the registries reconstruct consumer-defined types.
# ---------------------------------------------------------------------------


class _FooTransformResult(TransformResult):
    _COMPLETED_CODE = "foo00001"
    _COMPLETED_MESSAGE = "foo done"
    foo_note: str = ""


class _FooExtractResult(ExtractResult):
    _COMPLETED_CODE = "foo00002"
    _COMPLETED_MESSAGE = "foo extracted"


# ---------------------------------------------------------------------------
# Status roll-up
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestEtlBatchResultStatus:
    def test_all_transforms_success_gives_success(self) -> None:
        batch = EtlBatchResult()
        for _ in range(3):
            t = batch.start_transform(source_id="s")
            t.mark_completed()
        batch.update_status_from_transforms()
        assert batch.status == EtlStatus.SUCCESS

    def test_partial_transform_failure_gives_mixed(self) -> None:
        batch = EtlBatchResult()
        batch.start_transform(source_id="ok").mark_completed()
        batch.start_transform(source_id="bad").add_error("e", "boom")
        batch.update_status_from_transforms()
        assert batch.status == EtlStatus.MIXED

    def test_all_transform_failure_gives_error(self) -> None:
        batch = EtlBatchResult()
        batch.start_transform(source_id="bad").add_error("e", "boom")
        batch.update_status_from_transforms()
        assert batch.status == EtlStatus.ERROR

    def test_for_subject_filters_by_source_id(self) -> None:
        batch = EtlBatchResult()
        batch.start_transform(source_id="a")
        batch.start_transform(source_id="b")
        batch.start_extract(source_id="a")
        only_a = batch.for_subject("a")
        assert len(only_a.transform_results) == 1
        assert len(only_a.extract_results) == 1


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestEtlResult:
    def test_coerce_command_id_fills_missing(self) -> None:
        result = EtlResult.model_validate({"etl_name": "flow", "etl_command_id": None})
        assert result.etl_command_id is not None

    def test_update_status_from_batches_excludes_initialized(self) -> None:
        result = EtlResult(etl_name="flow")
        good = result.start_batch()
        good.start_transform(source_id="s").mark_completed()
        good.update_status_from_transforms()
        result.start_batch()  # left INITIALIZED, must be ignored
        result.update_status_from_batches()
        assert result.status == EtlStatus.SUCCESS

    def test_summary_fields_counts(self) -> None:
        result = EtlResult(etl_name="flow", batch_type="bt")
        batch = result.start_batch()
        batch.start_transform(source_id="s").mark_completed()
        batch.start_extract(source_id="s").mark_completed()
        batch.update_status_from_transforms()
        fields = result.summary_fields()
        assert fields["flow"] == "flow"
        assert fields["n_transformed_ok"] == 1
        assert fields["n_extracted_ok"] == 1


# ---------------------------------------------------------------------------
# Polymorphic round-trip
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestPolymorphicRoundTrip:
    def test_transform_and_extract_subclasses_restored(self) -> None:
        batch = EtlBatchResult()
        t = batch.start_transform(source_id="s", result_type=_FooTransformResult)
        t.foo_note = "hello"
        batch.start_extract(source_id="s", result_type=_FooExtractResult)

        restored = EtlBatchResult.model_validate_json(batch.model_dump_json())

        assert isinstance(restored.transform_results[0], _FooTransformResult)
        assert restored.transform_results[0].foo_note == "hello"
        assert isinstance(restored.extract_results[0], _FooExtractResult)

    def test_upload_results_restored_by_result_type(self) -> None:
        batch = EtlBatchResult()
        batch.add_load_result(seqdb_model.SampleBatchUploadResult(samples=[]))
        batch.add_load_result(casedb_model.CaseBatchUploadResult(cases=[]))
        batch.add_load_result(omopdb_model.PersonBatchUploadResult(persons=[]))

        restored = EtlBatchResult.model_validate_json(batch.model_dump_json())

        types = {type(x) for x in restored.load_results}
        assert types == {
            seqdb_model.SampleBatchUploadResult,
            casedb_model.CaseBatchUploadResult,
            omopdb_model.PersonBatchUploadResult,
        }

    def test_upload_result_restored_from_legacy_payload(self) -> None:
        """A load_results dict without result_type still resolves via field name."""
        payload = {
            "batch_id": None,
            "transform_results": [],
            "extract_results": [],
            "load_results": [{"cases": [], "status": "PROCESSED"}],
        }
        restored = EtlBatchResult.model_validate(payload)
        assert isinstance(restored.load_results[0], casedb_model.CaseBatchUploadResult)

    def test_unknown_upload_dict_falls_back_to_base(self) -> None:
        payload = {
            "load_results": [{"status": "PROCESSED", "is_new": False}],
        }
        restored = EtlBatchResult.model_validate(payload)
        assert type(restored.load_results[0]) is UploadResult


# ---------------------------------------------------------------------------
# BaseBatchUploadResult.resolve_subclass
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestResolveSubclass:
    def test_registry_hit(self) -> None:
        assert (
            BaseBatchUploadResult.resolve_subclass(
                {"result_type": "SampleBatchUploadResult"}
            )
            is seqdb_model.SampleBatchUploadResult
        )

    def test_legacy_key_hit(self) -> None:
        assert (
            BaseBatchUploadResult.resolve_subclass({"persons": []})
            is omopdb_model.PersonBatchUploadResult
        )

    def test_miss_returns_none(self) -> None:
        assert BaseBatchUploadResult.resolve_subclass({"id": None}) is None

    def test_result_type_auto_populated(self) -> None:
        result = casedb_model.CaseBatchUploadResult(cases=[])
        assert result.result_type == "CaseBatchUploadResult"
        assert result.model_dump()["result_type"] == "CaseBatchUploadResult"
