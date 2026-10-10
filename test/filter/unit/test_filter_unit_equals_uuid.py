"""Exercise UUID parsing, matching, and immutability for the UUID filter."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals_uuid import EqualsUuidFilter

MATCHED_UUID = UUID("12345678-1234-5678-1234-567812345678")
OTHER_UUID = UUID("87654321-4321-8765-4321-876543218765")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(MATCHED_UUID, MATCHED_UUID, id="uuid-instance"),
        pytest.param(str(MATCHED_UUID), MATCHED_UUID, id="uuid-string"),
    ],
)
def test_value_is_validated_as_uuid(value: UUID | str, expected: UUID) -> None:
    """Accept UUID objects and parse valid UUID strings."""
    filter_model = EqualsUuidFilter(value=value)

    assert filter_model.value == expected
    assert filter_model.type == FilterType.EQUALS_UUID.value


def test_match_value_compares_uuid_values() -> None:
    """Match an equal UUID and reject a different UUID."""
    filter_model = EqualsUuidFilter(value=MATCHED_UUID)

    assert filter_model.match_value(MATCHED_UUID)
    assert not filter_model.match_value(OTHER_UUID)


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({}, id="missing-value"),
        pytest.param({"value": "not-a-uuid"}, id="malformed-value"),
    ],
)
def test_invalid_value_is_rejected(data: dict[str, object]) -> None:
    """Require a valid UUID value during model construction."""
    with pytest.raises(ValidationError):
        EqualsUuidFilter.model_validate(data)


def test_value_is_immutable() -> None:
    """Reject changes to the configured UUID after construction."""
    filter_model = EqualsUuidFilter(value=MATCHED_UUID)

    with pytest.raises(ValidationError):
        filter_model.value = OTHER_UUID
