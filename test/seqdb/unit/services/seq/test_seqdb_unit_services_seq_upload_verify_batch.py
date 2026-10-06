"""Tests for sequence upload natural-key matching."""

from uuid import UUID

import pytest

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.services.seq.upload_verify_batch import _get_existing_seq_match

_PROTOCOL_ID = UUID("00000000-0000-0000-0000-000000000001")
_READ_SET_ID = UUID("00000000-0000-0000-0000-000000000002")
_CONTENT_HASH = UUID("00000000-0000-0000-0000-000000000003")
_SEQ_ID = UUID("00000000-0000-0000-0000-000000000004")


def test_sequence_match_prefers_exact_read_set_natural_key() -> None:
    """Prefer a sequence with matching protocol and both read-set links."""
    seq = model.SeqForUpload.model_construct(
        protocol_id=_PROTOCOL_ID,
        read_set_id=_READ_SET_ID,
        read_set2_id=None,
    )
    exact_match = (_CONTENT_HASH, _SEQ_ID)
    fallback_match = (UUID(int=5), UUID(int=6))

    assert (
        _get_existing_seq_match(
            seq,
            {
                (_PROTOCOL_ID, _READ_SET_ID, None): exact_match,
                (_PROTOCOL_ID, None, None): fallback_match,
            },
        )
        == exact_match
    )


def test_sequence_match_falls_back_to_existing_record_without_read_sets() -> None:
    """Resolve a known read-set link against an existing no-read-set record."""
    seq = model.SeqForUpload.model_construct(
        protocol_id=_PROTOCOL_ID,
        read_set_id=_READ_SET_ID,
        read_set2_id=None,
    )
    expected = (_CONTENT_HASH, _SEQ_ID)

    assert (
        _get_existing_seq_match(seq, {(_PROTOCOL_ID, None, None): expected}) == expected
    )


@pytest.mark.parametrize(
    ("read_set_id", "expected"),
    [(None, (_CONTENT_HASH, _SEQ_ID)), (NULL_ID, (None, None))],
)
def test_missing_and_unknown_read_set_links_are_distinct(
    read_set_id: UUID | None, expected: tuple[UUID | None, UUID | None]
) -> None:
    """Treat absent read-set links as exact keys and NULL_ID as unknown."""
    seq = model.SeqForUpload.model_construct(
        protocol_id=_PROTOCOL_ID,
        read_set_id=read_set_id,
        read_set2_id=None,
    )

    assert (
        _get_existing_seq_match(
            seq, {(_PROTOCOL_ID, None, None): (_CONTENT_HASH, _SEQ_ID)}
        )
        == expected
    )
