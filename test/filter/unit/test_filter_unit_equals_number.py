from decimal import Decimal

import pytest
from pydantic import ValidationError

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals_number import EqualsNumberFilter


@pytest.mark.parametrize(
    "value",
    [0, -7, 1.25, Decimal("1234567890.123456789")],
    ids=["zero", "negative-integer", "fractional-float", "precise-decimal"],
)
def test_equals_number_preserves_numeric_value(value: int | float | Decimal) -> None:
    """Keep supported numeric values intact and set the numeric discriminator."""
    filter_obj = EqualsNumberFilter(value=value)

    assert filter_obj.value == value
    assert type(filter_obj.value) is type(value)
    assert filter_obj.type == FilterType.EQUALS_NUMBER.value


def test_equals_number_requires_value() -> None:
    """Require a value when constructing a numeric equality filter."""
    with pytest.raises(ValidationError):
        EqualsNumberFilter.model_validate({})


def test_equals_number_value_is_frozen() -> None:
    """Prevent changing a numeric equality filter's configured value."""
    filter_obj = EqualsNumberFilter(value=3)

    with pytest.raises(ValidationError):
        filter_obj.value = 4
