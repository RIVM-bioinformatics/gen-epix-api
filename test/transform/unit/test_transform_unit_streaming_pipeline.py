"""Tests for the exported streaming pipeline's executor-backed processing."""

from test.util.mock_compat import Mock

import pytest

from gen_epix.transform.pipeline import Pipeline
from gen_epix.transform.streaming_pipeline import StreamingPipeline


@pytest.mark.asyncio
async def test_coroutine_processes_full_and_partial_batches_in_order(
    pipeline_with_results: Pipeline,
) -> None:
    """Process complete and trailing partial batches without reordering inputs."""
    processor = StreamingPipeline(pipeline_with_results)

    results = await processor.process_stream_async_coroutine(
        iter([1, -1, 2]), batch_size=2
    )

    assert [result.original_object for result in results] == [1, -1, 2]
    assert [result.success for result in results] == [True, False, True]
    assert results[0].transformed_object == 2


@pytest.mark.asyncio
async def test_coroutine_reports_when_pipeline_returns_no_result() -> None:
    """Convert an empty per-object pipeline output into a failed result."""
    pipeline = Mock(spec=Pipeline)
    pipeline.process_stream.return_value = iter(())
    processor = StreamingPipeline(pipeline)

    results = await processor.process_stream_async_coroutine(iter(["input"]))

    assert len(results) == 1
    assert not results[0].success
    assert results[0].original_object == "input"
    assert str(results[0].error) == "No results returned"
