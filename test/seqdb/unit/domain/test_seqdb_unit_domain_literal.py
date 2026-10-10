"""Check SeqDB domain sentinels and Nextclade literal syntax."""

import pytest

from gen_epix.seqdb.domain import literal


@pytest.mark.parametrize(
    ("pattern", "value", "matches"),
    [
        (literal.NCBI_TAXID_PATTERN, "NCBI:txid123", True),
        (literal.NCBI_TAXID_PATTERN, "ncbi:txid123", False),
        (literal.NCBI_TAXID_PATTERN, "NCBI:txid", False),
        (literal.NEXTCLADE_SUBSTITUTION_PATTERN, "A12G", True),
        (literal.NEXTCLADE_SUBSTITUTION_PATTERN, "a12-", True),
        (literal.NEXTCLADE_SUBSTITUTION_PATTERN, "A12GG", False),
        (literal.NEXTCLADE_INSERTION_PATTERN, "12:AC-", True),
        (literal.NEXTCLADE_INSERTION_PATTERN, "12:", False),
        (literal.NEXTCLADE_NON_ACGTN_PATTERN, "N:12-14", True),
        (literal.NEXTCLADE_NON_ACGTN_PATTERN, "N:14-12", True),
        (literal.NEXTCLADE_POSITION_RANGE_PATTERN, "12", True),
        (literal.NEXTCLADE_POSITION_RANGE_PATTERN, "12-14", True),
        (literal.NEXTCLADE_POSITION_RANGE_PATTERN, "12-", False),
    ],
    ids=[
        "taxid",
        "taxid-case-sensitive",
        "taxid-requires-digits",
        "substitution",
        "substitution-hyphen",
        "substitution-extra-base",
        "insertion",
        "insertion-requires-bases",
        "non-acgtn-range",
        "non-acgtn-range-order-validated-by-consumer",
        "single-position",
        "position-range",
        "incomplete-range",
    ],
)
def test_literal_patterns_match_supported_token_syntax(pattern, value, matches):
    """Match complete tokens while rejecting malformed syntax."""
    assert (pattern.fullmatch(value) is not None) is matches


def test_required_nextclade_key_collections():
    """Keep common required fields as the prefix of sequence-required fields."""
    expected_keys = "substitutions deletions insertions missings non_acgtns".split()
    assert literal.REQUIRED_NEXTCLADE_KEYS == expected_keys
    assert literal.REQUIRED_NEXTCLADE_SEQ_KEYS == [
        *expected_keys,
        "alignment_start",
        "alignment_end",
    ]
    assert literal.MLVA_NO_LOCUS_REPEAT_NUMBER == -1
