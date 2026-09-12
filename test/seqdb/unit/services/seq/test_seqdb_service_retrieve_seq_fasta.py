"""Test FASTA formatting in the sequence service."""

from collections.abc import Iterable
from typing import Self, cast
from uuid import UUID, uuid4

from gen_epix.seqdb.domain import command
from gen_epix.seqdb.services.seq.service import SeqService


class _RepositoryStub:
    def __init__(self, records: list[tuple[UUID, list[tuple[UUID, str]]]]) -> None:
        self.records = records

    def uow(self) -> Self:
        return self

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def retrieve_seq_fasta(
        self,
        _uow: object,
        _seq_ids: list[UUID],
    ) -> Iterable[tuple[UUID, list[tuple[UUID, str]]]]:
        return iter(self.records)


class _ServiceStub:
    def __init__(self, records: list[tuple[UUID, list[tuple[UUID, str]]]]) -> None:
        self.repository = _RepositoryStub(records)


def test_retrieve_seq_fasta_separates_wrapped_records() -> None:
    """Terminate each wrapped FASTA record before yielding the next header."""
    seq_id_one, contig_id_one = uuid4(), uuid4()
    seq_id_two, contig_id_two = uuid4(), uuid4()
    service = _ServiceStub(
        [
            (seq_id_one, [(contig_id_one, "acgt")]),
            (seq_id_two, [(contig_id_two, "tgca")]),
        ]
    )
    cmd = command.RetrieveSeqFastaCommand(seq_ids=[seq_id_one, seq_id_two])

    result = "".join(SeqService.retrieve_seq_fasta(cast(SeqService, service), cmd))

    assert result == (
        f">{seq_id_one}:{contig_id_one}\n"
        "acgt\n"
        f">{seq_id_two}:{contig_id_two}\n"
        "tgca\n"
    )
