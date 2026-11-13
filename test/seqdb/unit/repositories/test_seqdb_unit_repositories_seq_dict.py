"""Tests for sequence retrieval in the Dict-backed repository."""

from test.seqdb.unit.repositories.seq_fasta_test_support import (
    create_seq,
    expected_fasta,
)
from uuid import uuid4

import pytest

from gen_epix.fastapp import exc
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


def test_get_full_samples_by_sample_ids_raises_for_missing_ids() -> None:
    sample_id = uuid4()
    missing_id = uuid4()
    sample = model.Sample(
        id=sample_id,
        created_in_data_collection_id=uuid4(),
    )
    repository = SeqDictRepository(
        entities=[model.Sample.ENTITY],
        db={model.Sample: {sample_id: sample}},
        missing_data="ignore",
    )

    with pytest.raises(exc.InvalidIdsError, match="e6de62b3") as error:
        repository.get_full_samples_by_sample_ids([sample_id, missing_id])

    assert error.value.ids == [missing_id]
