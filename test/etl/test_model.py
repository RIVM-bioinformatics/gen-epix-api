"""Unit tests for the shared ETL result hierarchy."""

from datetime import UTC, datetime
from typing import Any, ClassVar, cast
from uuid import UUID, uuid4

import pytest

from gen_epix.etl.enum import EtlStatus
from gen_epix.etl.model import (
    BatchEtlResult,
    EtlLogItem,
    EtlResult,
    ExtractResult,
    JobEtlResult,
    LoadResult,
    TransformResult,
)
from gen_epix.fastapp.enum import LogLevel


class _FooTransformResult(TransformResult):
    ID: ClassVar[str] = "test-transform"
    COMPLETED_CODE: ClassVar[str] = "foo00001"
    COMPLETED_MESSAGE: ClassVar[str] = "foo done"

    note: str = ""


class _FooExtractResult(ExtractResult):
    ID: ClassVar[str] = "test-extract"
    COMPLETED_CODE: ClassVar[str] = "foo00002"
    COMPLETED_MESSAGE: ClassVar[str] = "foo extracted"


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestEtlLogItem:
    def test_normalizes_and_serializes_severity(self) -> None:
        timestamp = datetime(2026, 1, 2, tzinfo=UTC)
        item = EtlLogItem.model_validate(
            cast(
                Any,
                {
                    "timestamp": timestamp,
                    "code": "code",
                    "message": "message",
                    "severity": "WARN",
                    "source": "source",
                    "target": "target",
                },
            )
        )

        assert item.severity is LogLevel.WARN
        assert item.model_dump() == {
            "timestamp": timestamp,
            "code": "code",
            "message": "message",
            "severity": LogLevel.WARN.value,
            "source": "source",
            "target": "target",
        }

    def test_accepts_log_level_instance(self) -> None:
        item = EtlLogItem(code="code", message="message", severity=LogLevel.INFO)

        assert item.severity is LogLevel.INFO


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestEtlResult:
    def test_log_helpers_add_query_and_filter_logs(self) -> None:
        result = EtlResult()

        result.add_info("info", "information", source="source")
        result.add_warning("warning", "warning", target="target")
        result.add_error("error", "failure", source="source", target="target")

        assert result.status is EtlStatus.FAILED
        assert result.has_infos() and result.has_warnings() and result.has_errors()
        assert result.has_log_code("warning")
        assert [item.code for item in result.get_infos()] == ["info"]
        assert [item.code for item in result.get_warnings()] == ["warning"]
        assert [item.code for item in result.get_errors()] == ["error"]
        assert result.logs[0].source == "source"
        assert result.logs[1].target == "target"

    @pytest.mark.parametrize("as_list", [False, True])
    @pytest.mark.parametrize("severity", [LogLevel.INFO, LogLevel.ERROR])
    def test_add_logs_accepts_one_or_many_and_propagates_errors(
        self, as_list: bool, severity: LogLevel
    ) -> None:
        result = EtlResult()
        item = EtlLogItem(code="code", message="message", severity=severity)

        result.add_logs([item] if as_list else item)

        assert result.logs == [item]
        expected = (
            EtlStatus.FAILED if severity is LogLevel.ERROR else EtlStatus.INITIALIZED
        )
        assert result.status is expected

    def test_completion_marks_initialized_result_and_preserves_failure(self) -> None:
        successful = TransformResult()
        successful.set_completed()
        failed = ExtractResult(status=EtlStatus.FAILED)
        failed.set_completed()

        assert successful.status is EtlStatus.SUCCESS
        assert successful.is_completed()
        assert successful.get_infos()[-1].message == "Transform completed."
        assert failed.status is EtlStatus.FAILED
        assert failed.is_completed()

    def test_deprecated_status_and_completion_aliases(self) -> None:
        result = LoadResult()

        with pytest.warns(DeprecationWarning):
            result.mark_completed()
        with pytest.warns(DeprecationWarning):
            assert result.has_completed()
        with pytest.warns(DeprecationWarning):
            result.set_error_status()

        assert result.status is EtlStatus.FAILED

    def test_each_concrete_result_uses_its_discriminator(self) -> None:
        protocol_id = uuid4()
        results = [
            LoadResult(),
            TransformResult(target_id=uuid4()),
            ExtractResult(),
            BatchEtlResult(),
            SeqDistanceUpdateResult(protocol_id=protocol_id),
            JobEtlResult(etl_name="flow"),
        ]

        assert [result.type for result in results] == [result.ID for result in results]
        distance_result = results[-2]
        assert isinstance(distance_result, SeqDistanceUpdateResult)
        assert distance_result.protocol_id == protocol_id
        assert distance_result.n_profiles_processed == 0
        assert distance_result.n_batches == 0

    def test_deserialize_handles_instances_non_dicts_and_registered_dicts(self) -> None:
        result = _FooExtractResult(source_id="source")

        assert EtlResult._deserialize(result) is result
        assert EtlResult._deserialize("value") == "value"
        restored = EtlResult._deserialize(result.model_dump())
        assert isinstance(restored, _FooExtractResult)
        assert restored.source_id == "source"

    def test_unknown_discriminator_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="Unknown subclass ID: missing"):
            EtlResult._deserialize({"type": "missing"})
        with pytest.raises(ValueError, match="Unknown subclass ID: missing"):
            EtlResult(type="missing")

    def test_duplicate_discriminator_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="Duplicate EtlResult subclass ID"):

            class DuplicateTransformResult(TransformResult):
                ID: ClassVar[str] = _FooTransformResult.ID


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestBatchEtlResult:
    @pytest.mark.parametrize(
        ("statuses", "expected"),
        [
            ([], EtlStatus.INITIALIZED),
            ([EtlStatus.SUCCESS], EtlStatus.SUCCESS),
            ([EtlStatus.INITIALIZED], EtlStatus.FAILED),
            ([EtlStatus.SUCCESS, EtlStatus.FAILED], EtlStatus.MIXED),
        ],
    )
    def test_update_status_from_extractions(
        self, statuses: list[EtlStatus], expected: EtlStatus
    ) -> None:
        batch = BatchEtlResult(
            extract_results=[ExtractResult(status=status) for status in statuses]
        )

        batch.update_status_from_extractions()

        assert batch.status is expected

    @pytest.mark.parametrize(
        ("statuses", "expected"),
        [
            ([], EtlStatus.INITIALIZED),
            ([EtlStatus.SUCCESS], EtlStatus.SUCCESS),
            ([EtlStatus.INITIALIZED], EtlStatus.FAILED),
            ([EtlStatus.SUCCESS, EtlStatus.FAILED], EtlStatus.MIXED),
        ],
    )
    def test_update_status_from_transforms(
        self, statuses: list[EtlStatus], expected: EtlStatus
    ) -> None:
        batch = BatchEtlResult(
            transform_results=[TransformResult(status=status) for status in statuses]
        )

        batch.update_status_from_transforms()

        assert batch.status is expected

    @pytest.mark.parametrize(
        ("statuses", "expected"),
        [
            ([], EtlStatus.INITIALIZED),
            ([EtlStatus.PROCESSED], EtlStatus.SUCCESS),
            ([EtlStatus.SUCCESS], EtlStatus.FAILED),
            ([EtlStatus.PROCESSED, EtlStatus.FAILED], EtlStatus.MIXED),
        ],
    )
    def test_update_status_from_loads(
        self, statuses: list[EtlStatus], expected: EtlStatus
    ) -> None:
        batch = BatchEtlResult(
            load_results=[LoadResult(status=status) for status in statuses]
        )

        batch.update_status_from_loads()

        assert batch.status is expected

    @pytest.mark.parametrize("status", [EtlStatus.MIXED, EtlStatus.FAILED])
    @pytest.mark.parametrize("phase", ["transform", "load"])
    def test_successful_later_phase_does_not_upgrade_failure(
        self, status: EtlStatus, phase: str
    ) -> None:
        batch = BatchEtlResult(status=status)
        if phase == "transform":
            batch.transform_results = [TransformResult(status=EtlStatus.SUCCESS)]
            batch.update_status_from_transforms()
        else:
            batch.load_results = [LoadResult(status=EtlStatus.PROCESSED)]
            batch.update_status_from_loads()

        assert batch.status is status

    def test_set_completed_propagates_all_phases_and_adds_completion_log(self) -> None:
        batch = BatchEtlResult(
            extract_results=[ExtractResult(status=EtlStatus.SUCCESS)],
            transform_results=[TransformResult(status=EtlStatus.SUCCESS)],
            load_results=[LoadResult(status=EtlStatus.FAILED)],
        )

        batch.set_completed()

        assert batch.status is EtlStatus.FAILED
        assert batch.is_completed()

    def test_empty_batch_completes_successfully(self) -> None:
        batch = BatchEtlResult()

        batch.set_completed()

        assert batch.status is EtlStatus.SUCCESS

    def test_start_helpers_register_results_and_completed_ids(self) -> None:
        target_id = uuid4()
        batch = BatchEtlResult()
        completed_extract = batch.start_extract("extract", _FooExtractResult)
        cast(ExtractResult, batch.start_extract(None)).set_completed()
        completed_transform = batch.start_transform("transform", _FooTransformResult)
        batch.start_transform("unfinished")
        completed_extract.set_completed()
        completed_transform.target_id = target_id
        completed_transform.set_completed()

        assert batch.extract_results[0] is completed_extract
        assert batch.transform_results[0] is completed_transform
        assert completed_extract.logs[0].message == "Extract started."
        assert completed_transform.logs[0].message == "Transform started."
        assert batch.get_completed_extract_source_ids() == frozenset({"extract"})
        assert batch.get_completed_transform_source_ids() == frozenset({"transform"})
        assert batch.get_completed_transform_target_ids() == frozenset({target_id})

    def test_deprecated_completed_id_aliases(self) -> None:
        target_id = uuid4()
        batch = BatchEtlResult(
            extract_results=[ExtractResult(source_id="extract")],
            transform_results=[
                TransformResult(source_id="transform", target_id=target_id)
            ],
        )
        batch.extract_results[0].set_completed()
        batch.transform_results[0].set_completed()

        with pytest.warns(DeprecationWarning):
            assert batch.get_completed_extract_source_values() == frozenset({"extract"})
        with pytest.warns(DeprecationWarning):
            assert batch.get_completed_source_values() == frozenset({"transform"})
        with pytest.warns(DeprecationWarning):
            assert batch.get_completed_target_values() == frozenset({target_id})

    def test_for_source_filters_subject_results_and_copies_loads(self) -> None:
        load = LoadResult(status=EtlStatus.PROCESSED)
        batch = BatchEtlResult(load_results=[load])
        batch.start_extract("a")
        batch.start_extract("b")
        batch.start_transform("a")
        batch.start_transform("b")

        filtered = batch.for_source("a")

        assert [result.source_id for result in filtered.extract_results] == ["a"]
        assert [result.source_id for result in filtered.transform_results] == ["a"]
        assert filtered.load_results == [load]
        assert filtered.load_results is not batch.load_results
        with pytest.warns(DeprecationWarning):
            assert batch.for_subject("a").extract_results == filtered.extract_results

    def test_add_load_result_registers_result(self) -> None:
        batch = BatchEtlResult()
        load = LoadResult(status=EtlStatus.PROCESSED)

        batch.add_load_result(load)

        assert batch.load_results == [load]


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestRunEtlResult:
    def test_command_id_defaults_coerces_none_and_preserves_value(self) -> None:
        supplied = uuid4()

        defaulted = JobEtlResult(etl_name="defaulted")
        coerced = JobEtlResult.model_validate(
            {"etl_name": "coerced", "etl_command_id": None}
        )
        preserved = JobEtlResult(etl_name="preserved", etl_command_id=supplied)

        assert isinstance(defaulted.etl_command_id, UUID)
        assert isinstance(coerced.etl_command_id, UUID)
        assert preserved.etl_command_id == supplied

    def test_start_batch_registers_batch_and_batch_ids_skip_unstored(self) -> None:
        stored_id = uuid4()
        result = JobEtlResult(etl_name="flow")
        stored = result.start_batch()
        stored.batch_id = stored_id
        unstored = result.start_batch()

        assert result.batches == [stored, unstored]
        assert result.batch_ids == [stored_id]

    @pytest.mark.parametrize(
        ("statuses", "initial_status", "expected"),
        [
            ([], EtlStatus.INITIALIZED, EtlStatus.SUCCESS),
            ([EtlStatus.INITIALIZED], EtlStatus.INITIALIZED, EtlStatus.SUCCESS),
            ([EtlStatus.SUCCESS], EtlStatus.INITIALIZED, EtlStatus.SUCCESS),
            ([EtlStatus.FAILED], EtlStatus.INITIALIZED, EtlStatus.FAILED),
            ([EtlStatus.MIXED], EtlStatus.INITIALIZED, EtlStatus.FAILED),
            (
                [EtlStatus.SUCCESS, EtlStatus.FAILED],
                EtlStatus.INITIALIZED,
                EtlStatus.MIXED,
            ),
            ([EtlStatus.SUCCESS], EtlStatus.FAILED, EtlStatus.FAILED),
        ],
    )
    def test_update_status_from_batches(
        self,
        statuses: list[EtlStatus],
        initial_status: EtlStatus,
        expected: EtlStatus,
    ) -> None:
        result = JobEtlResult(
            etl_name="flow",
            status=initial_status,
            batches=[BatchEtlResult(status=status) for status in statuses],
        )

        result.update_status_from_batches()

        assert result.status is expected

    def test_summary_fields_counts_all_outcomes_and_excludes_empty_batch(self) -> None:
        stored_id = uuid4()
        processed = BatchEtlResult(
            batch_id=stored_id,
            status=EtlStatus.MIXED,
            extract_results=[
                ExtractResult(status=EtlStatus.SUCCESS),
                ExtractResult(status=EtlStatus.FAILED),
            ],
            transform_results=[
                TransformResult(status=EtlStatus.SUCCESS),
                TransformResult(status=EtlStatus.FAILED),
            ],
            load_results=[
                LoadResult(status=EtlStatus.PROCESSED),
                LoadResult(status=EtlStatus.FAILED),
            ],
        )
        result = JobEtlResult(
            etl_name="flow",
            batch_type="batch-type",
            status=EtlStatus.MIXED,
            batches=[processed, BatchEtlResult()],
        )

        assert result.summary_fields() == {
            "flow": "flow",
            "batch_type": "batch-type",
            "status": "MIXED",
            "n_batches": 1,
            "n_stored_batches": 1,
            "n_extracted_ok": 1,
            "n_extracted_failed": 1,
            "n_transformed_ok": 1,
            "n_transformed_failed": 1,
            "n_loaded_ok": 1,
            "n_loaded_failed": 1,
        }

    def test_summary_fields_uses_empty_batch_type(self) -> None:
        result = JobEtlResult(etl_name="flow")

        assert result.summary_fields()["batch_type"] == ""


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestPolymorphicRoundTrip:
    def test_batch_restores_external_extract_transform_and_load_types(self) -> None:
        batch = BatchEtlResult()
        transform = batch.start_transform("source", _FooTransformResult)
        transform.note = "hello"
        batch.start_extract("source", _FooExtractResult)
        batch.add_load_result(LoadResult(status=EtlStatus.PROCESSED))

        restored = BatchEtlResult.model_validate_json(batch.model_dump_json())

        assert isinstance(restored.transform_results[0], _FooTransformResult)
        assert restored.transform_results[0].note == "hello"
        assert isinstance(restored.extract_results[0], _FooExtractResult)
        assert type(restored.load_results[0]) is LoadResult

    def test_base_constructor_restores_registered_subclass(self) -> None:
        restored = EtlResult(**_FooExtractResult(source_id="source").model_dump())

        assert isinstance(restored, _FooExtractResult)
        assert restored.source_id == "source"

    def test_run_round_trip_restores_nested_results(self) -> None:
        result = JobEtlResult(etl_name="flow")
        batch = result.start_batch()
        batch.start_transform("source", _FooTransformResult)

        restored = JobEtlResult.model_validate_json(result.model_dump_json())

        assert isinstance(restored.batches[0], BatchEtlResult)
        assert isinstance(restored.batches[0].transform_results[0], _FooTransformResult)
