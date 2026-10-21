"""Tests for sequence retrieval in the Dict-backed repository."""

from test.seqdb.unit.repositories.seq_fasta_test_support import (
    create_seq,
    expected_fasta,
)

from gen_epix.seqdb.domain import enum, model
from gen_epix.seqdb.repositories.seq_dict import SeqDictRepository


def test_retrieve_seq_fasta_decodes_compressed_contig() -> None:
    sequence = "AT-CGATCG"
    seq = create_seq(sequence, enum.SeqFormat.STR_DNA_INCL_GAP_GZB64)
    repository = SeqDictRepository(
        entities=[model.Seq.ENTITY],
        db={model.Seq: {seq.id: seq}},
        missing_data="ignore",
    )

    with repository.uow() as uow:
        result = list(repository.retrieve_seq_fasta(uow, [seq.id]))  # type: ignore[list-item]

    assert result == expected_fasta(seq, sequence)
