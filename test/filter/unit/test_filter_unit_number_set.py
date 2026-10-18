"""Verify numeric set member normalization and model constraints."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from gen_epix.filter.enum import FilterType
from gen_epix.filter.number_set import NumberSetFilter


@pytest.mark.parametrize(
    "member",
    [0, -7, 1.25, Decimal("1234567890.123456789")],
    ids=["zero", "negative-integer", "fractional-float", "precise-decimal"],
)
def test_number_set_preserves_numeric_member_types(
    member: int | float | Decimal,
) -> None:
    """Preserve supported numeric values and set the numeric-set discriminator."""
    filter_obj = NumberSetFilter(members=[member])

    stored_member = next(iter(filter_obj.members))
    assert type(filter_obj.members) is frozenset
    assert stored_member == member
    assert isinstance(stored_member, type(member))
    assert filter_obj.type == FilterType.NUMBER_SET.value


def test_number_set_normalizes_members_without_mutating_input() -> None:
    """Normalize member collections to distinct immutable values."""
    source_members = [1, 1, 2.5, Decimal("3.5")]

    filter_obj = NumberSetFilter(members=source_members)
    source_members.append(4)

    assert filter_obj.members == frozenset({1, 2.5, Decimal("3.5")})
    assert filter_obj.members == frozenset(filter_obj.members)


def test_number_set_accepts_empty_members() -> None:
    """Allow an empty set of numeric members."""
    filter_obj = NumberSetFilter(members=[])

    assert filter_obj.members == frozenset()


@pytest.mark.parametrize(
    "members",
    [None, [None], [object()], ["not-a-number"]],
    ids=["none", "null-member", "object-member", "nonnumeric-text"],
)
def test_number_set_rejects_missing_or_nonnumeric_members(members: object) -> None:
    """Reject absent or incompatible member values."""
    with pytest.raises(ValidationError):
        NumberSetFilter(members=members)


def test_number_set_requires_members() -> None:
    """Require the members field when constructing a numeric-set filter."""
    with pytest.raises(ValidationError):
        NumberSetFilter.model_validate({})


def test_number_set_rejects_another_filter_discriminator() -> None:
    """Keep the discriminator fixed to the numeric-set filter type."""
    with pytest.raises(ValidationError):
        NumberSetFilter(type=FilterType.STRING_SET.value, members=[1])


def test_number_set_members_field_is_frozen() -> None:
    """Prevent replacing the configured numeric members."""
    filter_obj = NumberSetFilter(members=[3])

    with pytest.raises(ValidationError):
        filter_obj.members = frozenset({4})
