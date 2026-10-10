"""Exercise UUID parsing, matching, and immutability for the UUID-set filter."""

from test.filter.unit import util
from uuid import UUID

import pytest
from pydantic import ValidationError

from gen_epix.filter.enum import FilterType
from gen_epix.filter.uuid_set import UuidSetFilter

MATCHED_UUID = UUID("12345678-1234-5678-1234-567812345678")
OTHER_UUID = UUID("87654321-4321-8765-4321-876543218765")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(MATCHED_UUID, MATCHED_UUID, id="uuid-instance"),
        pytest.param(str(MATCHED_UUID), MATCHED_UUID, id="uuid-string"),
    ],
)
def test_members_are_validated_as_uuids(value: UUID | str, expected: UUID) -> None:
    """Accept UUID objects and parse valid UUID strings in member collections."""
    filter_model = UuidSetFilter.model_validate({"members": [value, value]})

    assert filter_model.members == frozenset({expected})
    assert filter_model.type == FilterType.UUID_SET.value


def test_uuid_set_matches_values_and_rows() -> None:
    """Match configured UUIDs and reject absent, null, or other row values."""
    filter_model = UuidSetFilter(key="id", members=frozenset({MATCHED_UUID}))
    rows: list[dict[str, UUID | None]] = [
        {"id": MATCHED_UUID},
        {"id": OTHER_UUID},
        {"id": None},
        {},
    ]

    util.validate_filter_behavior(filter_model, rows, [True, False, False, False])


def test_empty_member_set_does_not_match() -> None:
    """Return false for every UUID when the configured membership set is empty."""
    filter_model = UuidSetFilter(members=frozenset())

    assert not filter_model.match_value(MATCHED_UUID)


def test_members_are_immutable_and_copied() -> None:
    """Store a frozen copy and reject replacing the configured members."""
    source_members = {MATCHED_UUID}
    filter_model = UuidSetFilter.model_validate({"members": source_members})
    source_members.add(OTHER_UUID)

    assert filter_model.members == frozenset({MATCHED_UUID})
    with pytest.raises(ValidationError):
        filter_model.members = frozenset({OTHER_UUID})


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({}, id="missing-members"),
        pytest.param({"members": ["not-a-uuid"]}, id="malformed-member"),
        pytest.param({"members": [None]}, id="null-member"),
        pytest.param({"members": [123]}, id="integer-member"),
    ],
)
def test_invalid_members_are_rejected(data: dict[str, object]) -> None:
    """Require members and reject values that cannot be parsed as UUIDs."""
    with pytest.raises(ValidationError):
        UuidSetFilter.model_validate(data)
