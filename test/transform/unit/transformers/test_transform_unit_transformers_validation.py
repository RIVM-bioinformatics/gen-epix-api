"""Test predicate-based validation of adapted objects."""

import pytest

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformers.validation import ValidationTransformer


def test_constructor_uses_class_name_when_name_is_omitted() -> None:
    """Use the concrete transformer class name by default."""
    transformer = ValidationTransformer(lambda obj: True)

    assert transformer.name == "ValidationTransformer"


def test_constructor_preserves_custom_name() -> None:
    """Retain a caller-provided name for transformation results."""
    transformer = ValidationTransformer(lambda obj: True, name="required-fields")

    assert transformer.name == "required-fields"


def test_transform_returns_the_same_adapter_when_validator_accepts() -> None:
    """Return the supplied adapter unchanged when validation succeeds."""
    adapter = ObjectAdapter({"value": 1})
    received_objects = []

    def validator(obj: ObjectAdapter) -> bool:
        received_objects.append(obj)
        return True

    result = ValidationTransformer(validator).transform(adapter)

    assert received_objects == [adapter]
    assert result is adapter


def test_transform_raises_value_error_when_validator_rejects() -> None:
    """Reject an adapted object when the validator returns false."""
    adapter = ObjectAdapter({"value": 1})

    with pytest.raises(ValueError, match="Validation failed for object"):
        ValidationTransformer(lambda obj: False).transform(adapter)


def test_transform_propagates_validator_exception() -> None:
    """Propagate exceptions raised while evaluating the validation predicate."""

    def validator(obj: ObjectAdapter) -> bool:
        raise RuntimeError("validator unavailable")

    with pytest.raises(RuntimeError, match="validator unavailable"):
        ValidationTransformer(validator).transform(ObjectAdapter({"value": 1}))
