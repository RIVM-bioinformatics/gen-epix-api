"""Tests for sequence retrieval in the SQLAlchemy repository."""

from test.seqdb.unit.repositories.seq_fasta_test_support import (
    create_seq,
    expected_fasta,
)
from typing import Any

from gen_epix.fastapp.repositories.sa import SAUnitOfWork
from gen_epix.seqdb.domain import enum, model
from gen_epix.seqdb.repositories.seq_sa import SeqSARepository


class FakeSession:
    def execute(self, statement: Any) -> list[tuple[object]]:
        del statement
        return [(object(),)]


class FakeMapper:
    def __init__(self, seq: model.Seq) -> None:
        self.seq = seq

    def load(self, row: object) -> model.Seq:
        del row
        return self.seq


def test_retrieve_seq_fasta_decodes_compressed_contig() -> None:
    sequence = "ATCGATCG"
    seq = create_seq(sequence, enum.SeqFormat.STR_DNA_GZB64)
    repository = SeqSARepository.__new__(SeqSARepository)
    repository.get_mapper = lambda model_class: FakeMapper(  # type: ignore[method-assign,return-value,assignment]
        seq
    )
    uow = SAUnitOfWork(FakeSession())  # type: ignore[arg-type]

    result = list(repository.retrieve_seq_fasta(uow, [seq.id]))  # type: ignore[list-item]

    assert result == expected_fasta(seq, sequence)
