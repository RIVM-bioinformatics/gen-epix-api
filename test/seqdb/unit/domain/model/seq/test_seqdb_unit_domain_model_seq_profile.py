"""Tests for parsing NextClade profile substitutions."""

import pytest

from gen_epix.seqdb.domain.model.seq.profile import (
    _get_nextclade_non_acgtn_snps,
    _get_nextclade_substitution_snps,
)


def test_nextclade_substitutions_extract_positions_and_normalize_nucleotides() -> None:
    """Extract changed positions and lowercase substituted nucleotides."""
    assert _get_nextclade_substitution_snps({"substitutions": "A12C,G20T"}) == [
        (12, "c"),
        (20, "t"),
    ]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, []),
        ("", []),
        ("N:10-12", [(10, "n"), (11, "n"), (12, "n")]),
        ("X:15", [(15, "x")]),
        ("N:10-11,X:15", [(10, "n"), (11, "n"), (15, "x")]),
    ],
)
def test_nextclade_non_acgtn_positions_expand_inclusive_ranges(
    value: str | None, expected: list[tuple[int, str]]
) -> None:
    """Expand inclusive non-ACGTN ranges and accept singleton positions."""
    assert _get_nextclade_non_acgtn_snps({"nonACGTNs": value}) == expected
