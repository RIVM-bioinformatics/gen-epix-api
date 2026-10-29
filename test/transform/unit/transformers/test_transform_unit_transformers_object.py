"""Test whole-object transformation behavior."""

from test.util.mock_compat import Mock

import pytest

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformers.object import ObjectTransformer


def test_transform_passes_unwrapped_object_and_adapts_replacement() -> None:
    """Call the function with the wrapped value and adapt its replacement."""
    original = {"value": 1}
    replacement = {"value": 2}
    adapter = ObjectAdapter(original)
    transform_fn = Mock(return_value=replacement)

    result = ObjectTransformer(transform_fn).transform(adapter)

    transform_fn.assert_called_once_with(original)
    assert result is not adapter
    assert result.unwrap() is replacement


def test_transform_propagates_callback_error() -> None:
    """Propagate failures raised by the replacement function."""
    original = {"value": 1}
    transform_fn = Mock(side_effect=ValueError("invalid object"))

    with pytest.raises(ValueError, match="invalid object"):
        ObjectTransformer(transform_fn).transform(ObjectAdapter(original))

    transform_fn.assert_called_once_with(original)
