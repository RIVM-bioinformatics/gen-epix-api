"""Test in-place field transformation behavior."""

from test.util.mock_compat import Mock

import pytest

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformers.field import FieldTransformer


def test_transform_updates_present_field_in_place() -> None:
    """Transform an existing value and return the same adapter."""
    data = {("field", 1): 4}
    adapter = ObjectAdapter(data)
    transformer = FieldTransformer(("field", 1), lambda value: value * 3)

    result = transformer.transform(adapter)

    assert result is adapter
    assert data == {("field", 1): 12}


def test_transform_skips_missing_field() -> None:
    """Leave the object unchanged without calling the transform function."""
    data = {"present": 4}
    adapter = ObjectAdapter(data)
    transform_fn = Mock()

    result = FieldTransformer("missing", transform_fn).transform(adapter)

    assert result is adapter
    assert data == {"present": 4}
    transform_fn.assert_not_called()


def test_transform_propagates_callback_error_without_mutating_field() -> None:
    """Propagate callback failures before replacing the original field value."""
    data = {"value": 4}
    adapter = ObjectAdapter(data)
    transform_fn = Mock(side_effect=ValueError("invalid value"))

    with pytest.raises(ValueError, match="invalid value"):
        FieldTransformer("value", transform_fn).transform(adapter)

    assert data == {"value": 4}
    transform_fn.assert_called_once_with(4)
