"""Tests for the streaming callback and error-threshold wrapper."""

from collections.abc import Iterator
from test.util.mock_compat import Mock

import pytest

from gen_epix.transform.pipeline import Pipeline
from gen_epix.transform.streaming import StreamingPipeline
from gen_epix.transform.transform_result import TransformResult


def _pipeline_with_results() -> Mock:
    pipeline = Mock(spec=Pipeline)

    def process_stream(values: Iterator[int]) -> Iterator[TransformResult]:
        for value in values:
            success = value >= 0
            yield TransformResult(
                success=success,
                original_object=value,
                transformed_object=value * 2 if success else None,
                error=None if success else ValueError("negative value"),
            )

    pipeline.process_stream.side_effect = process_stream
    return pipeline


def test_stream_results_in_order_and_invokes_callbacks() -> None:
    """Yield outcomes in input order and call the matching callback once."""
    successes: list[int] = []
    errors: list[int] = []
    processor = StreamingPipeline(_pipeline_with_results(), error_threshold=0.5)

    results = list(
        processor.process_stream_async(
            iter([2, -1]),
            on_success=lambda result: successes.append(result.original_object),
            on_error=lambda result: errors.append(result.original_object),
        )
    )

    assert [result.success for result in results] == [True, False]
    assert successes == [2]
    assert errors == [-1]
    assert (processor.total_count, processor.error_count) == (2, 1)


def test_stream_raises_only_when_error_rate_exceeds_threshold() -> None:
    """Allow equality with the threshold and raise once it is exceeded."""
    processor = StreamingPipeline(_pipeline_with_results(), error_threshold=0.5)

    with pytest.raises(RuntimeError, match="exceeds threshold"):
        list(processor.process_stream_async(iter([1, -1, -2])))


def test_collect_errors_separates_successes_and_failure_results() -> None:
    """Collect transformed success values separately from failed outcomes."""
    processor = StreamingPipeline(_pipeline_with_results(), error_threshold=1.0)

    successes, errors = processor.collect_errors(iter([1, -1, 2]))

    assert successes == [2, 4]
    assert len(errors) == 1
    assert errors[0].original_object == -1
