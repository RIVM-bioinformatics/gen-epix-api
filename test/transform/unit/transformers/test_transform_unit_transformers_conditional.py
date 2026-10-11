"""Test predicate-controlled transformer delegation."""

from test.util.mock_compat import Mock

import pytest

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformers.conditional import ConditionalTransformer


def test_transform_delegates_and_returns_transformed_adapter() -> None:
    """Pass the original adapter to the child transformer when condition matches."""
    adapter = ObjectAdapter({"value": 1})
    transformed = ObjectAdapter({"value": 2})
    condition = Mock(return_value=True)
    transformer = Mock(transform=Mock(return_value=transformed))
    conditional = ConditionalTransformer(condition, transformer, name="conditional")

    result = conditional.transform(adapter)

    condition.assert_called_once_with(adapter)
    transformer.transform.assert_called_once_with(adapter)
    assert result is transformed
    assert conditional.name == "conditional"


def test_transform_returns_original_adapter_when_condition_is_false() -> None:
    """Return the same adapter without invoking the child transformer."""
    adapter = ObjectAdapter({"value": 1})
    condition = Mock(return_value=False)
    transformer = Mock()
    conditional = ConditionalTransformer(condition, transformer)

    result = conditional.transform(adapter)

    condition.assert_called_once_with(adapter)
    transformer.transform.assert_not_called()
    assert result is adapter
    assert conditional.name == "ConditionalTransformer"


@pytest.mark.parametrize("failure_source", ["condition", "transformer"])
def test_transform_propagates_callback_errors(failure_source: str) -> None:
    """Propagate failures from the predicate or delegated transformer."""
    adapter = ObjectAdapter({"value": 1})
    error = ValueError(f"{failure_source} failed")
    condition = Mock(return_value=True)
    transformer = Mock(transform=Mock())
    if failure_source == "condition":
        condition.side_effect = error
    else:
        transformer.transform.side_effect = error
    conditional = ConditionalTransformer(condition, transformer)

    with pytest.raises(ValueError, match=f"{failure_source} failed"):
        conditional.transform(adapter)
