"""Test FASTA retrieval for all supported DNA storage representations."""

from typing import Any
from uuid import UUID, uuid4

from gen_epix.fastapp.repositories.sa import SAUnitOfWork
from gen_epix.seqdb.domain import enum, model
from gen_epix.seqdb.domain.model.seq.base import encode_gzip_base64
from gen_epix.seqdb.repositories.seq_dict import SeqDictRepository
from gen_epix.seqdb.repositories.seq_sa import SeqSARepository


def create_seq(sequence: str, seq_format: enum.SeqFormat) -> model.Seq:
    """Create an identified sequence with one contig in the requested format."""
    stored_sequence = (
        encode_gzip_base64(sequence)
        if seq_format
        in {
            enum.SeqFormat.STR_DNA_GZB64,
            enum.SeqFormat.STR_DNA_INCL_GAP_GZB64,
        }
        else sequence
    )
    return model.Seq(  # type: ignore[call-arg]
        id=uuid4(),
        sample_id=uuid4(),
        code=f"seq-{uuid4()}",
        contigs=[model.Contig(seq=stored_sequence, seq_format=seq_format)],
    )


def expected_fasta(
    seq: model.Seq, sequence: str
) -> list[tuple[UUID, list[tuple[UUID, str]]]]:
    """Return the repository FASTA payload expected for one sequence."""
    assert seq.id is not None
    assert seq.contigs[0].id is not None
    return [(seq.id, [(seq.contigs[0].id, sequence.lower())])]


def test_dict_repository_retrieves_decoded_fasta_for_compressed_contig() -> None:
    """Decode compressed contigs in the dictionary repository FASTA path."""
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


class FakeSession:
    """Return one SQL row for the SQL repository FASTA test."""

    def execute(self, statement: Any) -> list[tuple[object]]:
        """Return the preconfigured sequence row."""
        del statement
        return [(object(),)]


class FakeMapper:
    """Load the test sequence from a SQLAlchemy row placeholder."""

    def __init__(self, seq: model.Seq) -> None:
        self.seq = seq

    def load(self, row: object) -> model.Seq:
        """Return the sequence represented by the row."""
        del row
        return self.seq


def test_sa_repository_retrieves_decoded_fasta_for_compressed_contig() -> None:
    """Decode compressed contigs in the SQLAlchemy repository FASTA path."""
    sequence = "ATCGATCG"
    seq = create_seq(sequence, enum.SeqFormat.STR_DNA_GZB64)
    repository = SeqSARepository.__new__(SeqSARepository)
    repository.get_mapper = lambda model_class: FakeMapper(seq)  # type: ignore[method-assign,return-value,assignment]
    uow = SAUnitOfWork(FakeSession())  # type: ignore[arg-type]

    result = list(repository.retrieve_seq_fasta(uow, [seq.id]))  # type: ignore[list-item]

    assert result == expected_fasta(seq, sequence)
