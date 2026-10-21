from uuid import UUID, uuid4

from gen_epix.seqdb.domain import enum, model
from gen_epix.seqdb.domain.model.seq.base import encode_ascii_as_gzip_base64


def create_seq(sequence: str, seq_format: enum.SeqFormat) -> model.Seq:
    stored_sequence = (
        encode_ascii_as_gzip_base64(sequence)
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
    assert seq.id is not None
    assert seq.contigs[0].id is not None
    return [(seq.id, [(seq.contigs[0].id, sequence.lower())])]
