"""Unit tests for the shared ETL result hierarchy."""

from datetime import UTC, datetime
from typing import Any, ClassVar, cast
from uuid import UUID, uuid4

import pytest

from gen_epix.etl.enum import EtlStatus
from gen_epix.etl.model import (
    BatchResult,
    ExtractResult,
    JobResult,
    LoadResult,
    LogItem,
    Result,
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
        item = LogItem.model_validate(
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
        item = LogItem(code="code", message="message", severity=LogLevel.INFO)

        assert item.severity is LogLevel.INFO


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestEtlResult:
    def test_log_helpers_add_query_and_filter_logs(self) -> None:
        result = Result()

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
        result = Result()
        item = LogItem(code="code", message="message", severity=severity)

        result.add_logs([item] if as_list else item)

        assert result.logs == [item]
        expected = EtlStatus.FAILED if severity is LogLevel.ERROR else EtlStatus.PENDING
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

    def test_status_predicates_reflect_current_status(self) -> None:
        result = LoadResult()
        assert result.is_pending()
        assert not result.is_success()
        assert not result.is_failed()
        assert not result.is_mixed()

        result.set_success()
        assert result.is_success()
        assert not result.is_pending()

        result.set_mixed()
        assert result.is_mixed()
        assert not result.is_success()

        result.set_failed()
        assert result.is_failed()
        assert not result.is_mixed()

    def test_extract_transform_subclass_missing_completed_code_raises(self) -> None:
        with pytest.raises(TypeError, match="COMPLETED_CODE and COMPLETED_MESSAGE"):

            class _MissingCompletedCode(TransformResult):
                ID: ClassVar[str] = "missing-completed-code"

        with pytest.raises(TypeError, match="COMPLETED_CODE and COMPLETED_MESSAGE"):

            class _MissingCompletedCode2(ExtractResult):
                ID: ClassVar[str] = "missing-completed-code-2"

    def test_upload_result_hierarchy_still_instantiates_cleanly(self) -> None:
        from gen_epix.commondb.domain.model.upload import UploadResult

        # UploadResult never overrides COMPLETED_CODE/COMPLETED_MESSAGE and never
        # calls set_completed() - the narrow enforcement on ExtractResult/
        # TransformResult must not reach LoadResult's other subclasses.
        result = UploadResult(status=EtlStatus.CREATED)
        assert result.status is EtlStatus.CREATED

    def test_each_concrete_result_uses_its_discriminator(self) -> None:
        results = [
            LoadResult(),
            TransformResult(target_id=uuid4()),
            ExtractResult(),
            BatchResult(),
            JobResult(etl_name="flow"),
        ]

        assert [result.type for result in results] == [result.ID for result in results]

    def test_deserialize_handles_instances_non_dicts_and_registered_dicts(self) -> None:
        result = _FooExtractResult(source_id="source")

        assert Result._deserialize(result) is result
        assert Result._deserialize("value") == "value"
        restored = Result._deserialize(result.model_dump())
        assert isinstance(restored, _FooExtractResult)
        assert restored.source_id == "source"

    def test_unknown_discriminator_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="Unknown subclass ID: missing"):
            Result._deserialize({"type": "missing"})
        with pytest.raises(ValueError, match="Unknown subclass ID: missing"):
            Result(type="missing")

    def test_duplicate_discriminator_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="Duplicate Result subclass ID"):

            class DuplicateTransformResult(TransformResult):
                ID: ClassVar[str] = _FooTransformResult.ID
                COMPLETED_CODE: ClassVar[str] = "dup00001"
                COMPLETED_MESSAGE: ClassVar[str] = "dup done"


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestBatchEtlResult:
    @pytest.mark.parametrize(
        ("statuses", "expected"),
        [
            ([], EtlStatus.PENDING),
            ([EtlStatus.SUCCESS], EtlStatus.SUCCESS),
            ([EtlStatus.PENDING], EtlStatus.FAILED),
            ([EtlStatus.SUCCESS, EtlStatus.FAILED], EtlStatus.MIXED),
        ],
    )
    def test_update_status_from_extractions(
        self, statuses: list[EtlStatus], expected: EtlStatus
    ) -> None:
        batch = BatchResult(
            extract_results=[ExtractResult(status=status) for status in statuses]
        )

        batch.update_status_from_extractions()

        assert batch.status is expected

    @pytest.mark.parametrize(
        ("statuses", "expected"),
        [
            ([], EtlStatus.PENDING),
            ([EtlStatus.SUCCESS], EtlStatus.SUCCESS),
            ([EtlStatus.PENDING], EtlStatus.FAILED),
            ([EtlStatus.SUCCESS, EtlStatus.FAILED], EtlStatus.MIXED),
        ],
    )
    def test_update_status_from_transforms(
        self, statuses: list[EtlStatus], expected: EtlStatus
    ) -> None:
        batch = BatchResult(
            transform_results=[TransformResult(status=status) for status in statuses]
        )

        batch.update_status_from_transforms()

        assert batch.status is expected

    @pytest.mark.parametrize(
        ("statuses", "expected"),
        [
            ([], EtlStatus.PENDING),
            ([EtlStatus.PROCESSED], EtlStatus.SUCCESS),
            ([EtlStatus.FAILED], EtlStatus.FAILED),
            ([EtlStatus.PROCESSED, EtlStatus.FAILED], EtlStatus.MIXED),
        ],
    )
    def test_update_status_from_loads(
        self, statuses: list[EtlStatus], expected: EtlStatus
    ) -> None:
        batch = BatchResult(
            load_results=[LoadResult(status=status) for status in statuses]
        )

        batch.update_status_from_loads()

        assert batch.status is expected

    @pytest.mark.parametrize("status", [EtlStatus.MIXED, EtlStatus.FAILED])
    @pytest.mark.parametrize("phase", ["transform", "load"])
    def test_successful_later_phase_does_not_upgrade_failure(
        self, status: EtlStatus, phase: str
    ) -> None:
        batch = BatchResult(status=status)
        if phase == "transform":
            batch.transform_results = [TransformResult(status=EtlStatus.SUCCESS)]
            batch.update_status_from_transforms()
        else:
            batch.load_results = [LoadResult(status=EtlStatus.PROCESSED)]
            batch.update_status_from_loads()

        assert batch.status is status

    def test_set_completed_propagates_all_phases_and_adds_completion_log(self) -> None:
        batch = BatchResult(
            extract_results=[ExtractResult(status=EtlStatus.SUCCESS)],
            transform_results=[TransformResult(status=EtlStatus.SUCCESS)],
            load_results=[LoadResult(status=EtlStatus.FAILED)],
        )

        batch.set_completed()

        assert batch.status is EtlStatus.FAILED
        assert batch.is_completed()

    def test_empty_batch_completes_successfully(self) -> None:
        batch = BatchResult()

        batch.set_completed()

        assert batch.status is EtlStatus.SUCCESS

    def test_start_helpers_register_results_and_completed_ids(self) -> None:
        target_id = uuid4()
        batch = BatchResult()
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
        batch = BatchResult(
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
        batch = BatchResult(load_results=[load])
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

    def test_add_single_load_result_registers_result(self) -> None:
        batch = BatchResult()
        load = LoadResult(status=EtlStatus.PROCESSED)

        batch.add_results(load)

        assert batch.load_results == [load]
        assert batch.extract_results == []
        assert batch.transform_results == []

    def test_add_list_of_load_results_registers_all(self) -> None:
        batch = BatchResult()
        load1 = LoadResult(status=EtlStatus.PROCESSED)
        load2 = LoadResult(status=EtlStatus.SUCCESS)
        load3 = LoadResult(status=EtlStatus.FAILED)

        batch.add_results([load1, load2, load3])

        assert batch.load_results == [load1, load2, load3]
        assert batch.extract_results == []
        assert batch.transform_results == []

    def test_add_single_extract_result_registers_result(self) -> None:
        batch = BatchResult()
        extract = ExtractResult(source_id="source1", status=EtlStatus.SUCCESS)

        batch.add_results(extract)

        assert batch.extract_results == [extract]
        assert batch.transform_results == []
        assert batch.load_results == []

    def test_add_list_of_extract_results_registers_all(self) -> None:
        batch = BatchResult()
        extract1 = ExtractResult(source_id="source1", status=EtlStatus.SUCCESS)
        extract2 = ExtractResult(source_id="source2", status=EtlStatus.FAILED)
        extract3 = ExtractResult(source_id="source3", status=EtlStatus.PROCESSED)

        batch.add_results([extract1, extract2, extract3])

        assert batch.extract_results == [extract1, extract2, extract3]
        assert batch.transform_results == []
        assert batch.load_results == []

    def test_add_single_transform_result_registers_result(self) -> None:
        batch = BatchResult()
        transform = TransformResult(source_id="source1", status=EtlStatus.SUCCESS)

        batch.add_results(transform)

        assert batch.transform_results == [transform]
        assert batch.extract_results == []
        assert batch.load_results == []

    def test_add_list_of_transform_results_registers_all(self) -> None:
        batch = BatchResult()
        transform1 = TransformResult(source_id="source1", status=EtlStatus.SUCCESS)
        transform2 = TransformResult(source_id="source2", status=EtlStatus.FAILED)
        transform3 = TransformResult(source_id="source3", status=EtlStatus.PROCESSED)

        batch.add_results([transform1, transform2, transform3])

        assert batch.transform_results == [transform1, transform2, transform3]
        assert batch.extract_results == []
        assert batch.load_results == []

    def test_add_mixed_results_registers_each_type(self) -> None:
        batch = BatchResult()
        extract1 = ExtractResult(source_id="source1", status=EtlStatus.SUCCESS)
        extract2 = ExtractResult(source_id="source2", status=EtlStatus.FAILED)
        transform1 = TransformResult(source_id="source1", status=EtlStatus.SUCCESS)
        transform2 = TransformResult(source_id="source2", status=EtlStatus.PROCESSED)
        load1 = LoadResult(status=EtlStatus.SUCCESS)
        load2 = LoadResult(status=EtlStatus.FAILED)

        batch.add_results([extract1, extract2, transform1, transform2, load1, load2])

        assert batch.extract_results == [extract1, extract2]
        assert batch.transform_results == [transform1, transform2]
        assert batch.load_results == [load1, load2]

    def test_add_mixed_results_with_custom_subclasses_registers_correctly(self) -> None:
        batch = BatchResult()
        custom_transform = _FooTransformResult(source_id="source1")
        custom_extract = _FooExtractResult(source_id="source1")
        load = LoadResult(status=EtlStatus.SUCCESS)

        batch.add_results([custom_extract, custom_transform, load])

        assert batch.extract_results == [custom_extract]
        assert isinstance(batch.extract_results[0], _FooExtractResult)
        assert batch.transform_results == [custom_transform]
        assert isinstance(batch.transform_results[0], _FooTransformResult)
        assert batch.load_results == [load]


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestRunEtlResult:
    def test_job_id_defaults_coerces_none_and_preserves_value(self) -> None:
        supplied = uuid4()

        defaulted = JobResult(etl_name="defaulted")
        coerced = JobResult.model_validate({"etl_name": "coerced", "job_id": None})
        preserved = JobResult(etl_name="preserved", job_id=str(supplied))
        non_str = JobResult(etl_name="non-str", job_id=supplied)

        assert isinstance(defaulted.job_id, str)
        assert isinstance(coerced.job_id, str)
        assert preserved.job_id == str(supplied)
        assert non_str.job_id == str(supplied)

    def test_start_batch_registers_batch_and_batch_ids_skip_unstored(self) -> None:
        stored_id = uuid4()
        result = JobResult(etl_name="flow")
        stored = result.start_batch()
        stored.batch_id = stored_id
        unstored = result.start_batch()

        assert result.batches == [stored, unstored]
        assert result.batch_ids == [stored_id]

    @pytest.mark.parametrize(
        ("statuses", "initial_status", "expected"),
        [
            ([], EtlStatus.PENDING, EtlStatus.SUCCESS),
            ([EtlStatus.PENDING], EtlStatus.PENDING, EtlStatus.SUCCESS),
            ([EtlStatus.SUCCESS], EtlStatus.PENDING, EtlStatus.SUCCESS),
            ([EtlStatus.FAILED], EtlStatus.PENDING, EtlStatus.FAILED),
            ([EtlStatus.MIXED], EtlStatus.PENDING, EtlStatus.FAILED),
            (
                [EtlStatus.SUCCESS, EtlStatus.FAILED],
                EtlStatus.PENDING,
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
        result = JobResult(
            etl_name="flow",
            status=initial_status,
            batches=[BatchResult(status=status) for status in statuses],
        )

        result.update_status_from_batches()

        assert result.status is expected

    def test_summary_fields_counts_all_outcomes_and_excludes_empty_batch(self) -> None:
        stored_id = uuid4()
        processed = BatchResult(
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
        result = JobResult(
            etl_name="flow",
            batch_type="batch-type",
            status=EtlStatus.MIXED,
            batches=[processed, BatchResult()],
        )

        assert result.get_summary() == {
            "etl_name": "flow",
            "job_id": result.job_id,
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
        result = JobResult(etl_name="flow")

        assert result.get_summary()["batch_type"] == ""


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestPolymorphicRoundTrip:
    def test_batch_restores_external_extract_transform_and_load_types(self) -> None:
        batch = BatchResult()
        transform = batch.start_transform("source", _FooTransformResult)
        transform.note = "hello"
        batch.start_extract("source", _FooExtractResult)
        batch.add_results(LoadResult(status=EtlStatus.PROCESSED))

        restored = BatchResult.model_validate_json(batch.model_dump_json())

        assert isinstance(restored.transform_results[0], _FooTransformResult)
        assert restored.transform_results[0].note == "hello"
        assert isinstance(restored.extract_results[0], _FooExtractResult)
        assert type(restored.load_results[0]) is LoadResult

    def test_base_constructor_restores_registered_subclass(self) -> None:
        restored = Result(**_FooExtractResult(source_id="source").model_dump())

        assert isinstance(restored, _FooExtractResult)
        assert restored.source_id == "source"

    def test_run_round_trip_restores_nested_results(self) -> None:
        result = JobResult(etl_name="flow")
        batch = result.start_batch()
        batch.start_transform("source", _FooTransformResult)

        restored = JobResult.model_validate_json(result.model_dump_json())

        assert isinstance(restored.batches[0], BatchResult)
        assert isinstance(restored.batches[0].transform_results[0], _FooTransformResult)
