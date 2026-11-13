import pytest

from gen_epix.casedb.domain.enum import ColType
from gen_epix.casedb.services.case.base import BaseCaseService


@pytest.mark.parametrize(
    ("col_type", "expected_zero"),
    [
        pytest.param(ColType.DECIMAL_0, "0", id="decimal-0"),
        pytest.param(ColType.DECIMAL_1, "0.0", id="decimal-1"),
        pytest.param(ColType.DECIMAL_2, "0.00", id="decimal-2"),
        pytest.param(ColType.DECIMAL_3, "0.000", id="decimal-3"),
        pytest.param(ColType.DECIMAL_4, "0.0000", id="decimal-4"),
        pytest.param(ColType.DECIMAL_5, "0.00000", id="decimal-5"),
        pytest.param(ColType.DECIMAL_6, "0.000000", id="decimal-6"),
    ],
)
def test_decimal_value_conversion_distinguishes_zero_from_missing(
    col_type: ColType, expected_zero: str
) -> None:
    convert = BaseCaseService._VALUE_TO_STR[col_type]

    assert convert(0) == expected_zero
    assert convert(None) is None
    assert convert("0") == "0"
