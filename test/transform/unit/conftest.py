"""Shared fixtures for transform unit tests."""

from collections.abc import Iterator
from test.util.mock_compat import Mock
from typing import cast

import pytest

from gen_epix.transform.pipeline import Pipeline
from gen_epix.transform.transform_result import TransformResult


@pytest.fixture
def pipeline_with_results() -> Pipeline:
    """Return a pipeline that doubles nonnegative integers and rejects negatives."""
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
    return cast(Pipeline, pipeline)
