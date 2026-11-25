"""Verify retry transformer attempt limits."""

import pytest

from gen_epix.transform.pipeline import RetryTransformer
from gen_epix.transform.transformer import Transformer


class FailingTransformer(Transformer):
    """Raise a stable error and count attempted transformations."""

    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def transform(self, obj: object) -> object:
        self.calls += 1
        raise ValueError("transform failed")


def test_retry_transformer_rejects_negative_attempt_limit() -> None:
    """Reject negative retry counts instead of failing after zero attempts."""
    with pytest.raises(ValueError, match="max_retries must be non-negative"):
        RetryTransformer(FailingTransformer(), max_retries=-1)


def test_zero_retries_performs_one_initial_attempt() -> None:
    """Run the initial transform once when no retries are configured."""
    transformer = FailingTransformer()
    retry_transformer = RetryTransformer(transformer, max_retries=0)

    with pytest.raises(ValueError, match="transform failed"):
        retry_transformer.transform(object())

    assert transformer.calls == 1
