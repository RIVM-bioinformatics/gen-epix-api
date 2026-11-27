"""Verify transform result status classification."""

from gen_epix.transform.enum import TransformResultType
from gen_epix.transform.transform_result import TransformResult


class FalseyError(Exception):
    """An exception whose truth value differs from its presence."""

    def __bool__(self) -> bool:
        return False


def test_falsey_exception_is_an_error() -> None:
    """Classify a present exception as an error even when it is falsey."""
    result = TransformResult(success=False, original_object=None, error=FalseyError())

    assert result.result_type is TransformResultType.ERROR


def test_missing_exception_is_skipped() -> None:
    """Classify an unsuccessful result without an exception as skipped."""
    result = TransformResult(success=False, original_object=None)

    assert result.result_type is TransformResultType.SKIPPED


def test_success_takes_precedence_over_exception() -> None:
    """Keep successful results successful even if error context is present."""
    result = TransformResult(
        success=True, original_object=None, error=RuntimeError("context")
    )

    assert result.result_type is TransformResultType.SUCCESS
