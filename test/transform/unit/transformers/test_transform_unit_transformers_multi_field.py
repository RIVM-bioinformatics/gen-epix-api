"""Exercise ordered field updates, skipped fields, and callback failures."""

from typing import Any

import pytest

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformers.multi_field import MultiFieldTransformer


def test_transform_applies_callables_in_mapping_order() -> None:
    """Apply present fields in order and return the same adapter."""
    calls: list[str] = []

    def increment(value: Any) -> Any:
        calls.append("first")
        return value + 1

    def double(value: Any) -> Any:
        calls.append("second")
        return value * 2

    data = {"first": 2, "second": 3, "unchanged": 4}
    adapter = ObjectAdapter(data)
    transformer = MultiFieldTransformer({"first": increment, "second": double})

    result = transformer.transform(adapter)

    assert result is adapter
    assert calls == ["first", "second"]
    assert data == {"first": 3, "second": 6, "unchanged": 4}


def test_transform_skips_missing_fields() -> None:
    """Do not call a transformation configured for an absent field."""
    data = {"present": 1}
    adapter = ObjectAdapter(data)

    def fail_if_called(value: Any) -> Any:
        pytest.fail(f"transformer received missing-field value: {value}")

    transformer = MultiFieldTransformer({"missing": fail_if_called})

    result = transformer.transform(adapter)

    assert result is adapter
    assert data == {"present": 1}


def test_transform_with_empty_mapping_is_a_noop() -> None:
    """Leave the object unchanged when no fields are configured."""
    data = {"value": 1}
    adapter = ObjectAdapter(data)

    result = MultiFieldTransformer({}).transform(adapter)

    assert result is adapter
    assert data == {"value": 1}


def test_transform_propagates_callable_error_after_prior_updates() -> None:
    """Propagate callback errors while retaining earlier in-place updates."""
    data = {"first": 1, "second": 2}
    adapter = ObjectAdapter(data)

    def fail(value: Any) -> Any:
        raise ValueError("cannot transform second field")

    transformer = MultiFieldTransformer(
        {"first": lambda value: value + 1, "second": fail}
    )

    with pytest.raises(ValueError, match="cannot transform second field"):
        transformer.transform(adapter)

    assert data == {"first": 2, "second": 2}
