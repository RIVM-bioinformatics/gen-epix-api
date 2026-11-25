"""Verify hashable set filter behavior for arbitrary candidates."""

import pytest

from gen_epix.filter.hashable_set import HashableSetFilter


@pytest.mark.parametrize("invert", [False, True], ids=["normal", "inverted"])
def test_hashable_set_non_hashable_candidate_is_a_non_match(invert: bool) -> None:
    """Treat unhashable candidates as non-members while preserving inversion."""
    filter_obj = HashableSetFilter(members=frozenset({"member"}), invert=invert)

    assert filter_obj.match_value(["member"]) is invert


def test_hashable_set_matches_hashable_member() -> None:
    """Continue matching configured hashable members."""
    filter_obj = HashableSetFilter(members=frozenset({"member"}))

    assert filter_obj.match_value("member") is True
    assert filter_obj.match_value("other") is False
