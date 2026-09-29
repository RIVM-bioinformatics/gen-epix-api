"""Test conversion of stored sequence representations."""

from collections.abc import Iterable
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.model.seq.base import encode_ascii_as_gzip_base64
from gen_epix.seqdb.services.seq.convert_seq_format import (
    seq_service_convert_seq_format,
)


class TrackingUnitOfWork(BaseUnitOfWork):
    """Track the transaction outcome for the conversion service test."""

    def __init__(self) -> None:
        super().__init__()
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


class SequenceRepository:
    """Provide the generic CRUD operations used by the conversion service."""

    def __init__(self, seqs: Iterable[model.Seq]) -> None:
        self.seqs = {seq.id: seq for seq in seqs}
        self.uow_instance = TrackingUnitOfWork()
        self.update_called = False

    def uow(self) -> TrackingUnitOfWork:
        return self.uow_instance

    def crud(
        self,
        uow: BaseUnitOfWork,
        user_id: Any,
        model_class: type[model.Model],
        operation: CrudOperation,
        objs: Iterable[model.Model] | None = None,
        obj_ids: Iterable[UUID] | None = None,
        return_id: bool = False,
        **kwargs: Any,
    ) -> Any:
        assert model_class is model.Seq
        if operation == CrudOperation.READ_SOME:
            assert obj_ids is not None
            return [self.seqs[seq_id].model_copy(deep=True) for seq_id in obj_ids]
        if operation == CrudOperation.UPDATE_SOME:
            assert objs is not None
            self.update_called = True
            updated = list(objs)
            for seq in updated:
                assert seq.id is not None
                self.seqs[seq.id] = seq  # type: ignore[assignment]
            return [seq.id for seq in updated] if return_id else updated
        raise AssertionError(f"Unexpected operation: {operation}")


def create_seq(sequence: str, seq_format: enum.SeqFormat) -> model.Seq:
    """Create a sequence aggregate containing one contig."""
    return model.Seq(  # type: ignore[call-arg]
        id=uuid4(),
        sample_id=uuid4(),
        code=f"seq-{uuid4()}",
        contigs=[
            model.Contig(
                seq=(
                    encode_ascii_as_gzip_base64(sequence)
                    if seq_format
                    in {
                        enum.SeqFormat.STR_DNA_GZB64,
                        enum.SeqFormat.STR_DNA_INCL_GAP_GZB64,
                    }
                    else sequence
                ),
                seq_format=seq_format,
            )
        ],
    )


@pytest.mark.parametrize(
    ("from_format", "to_format"),
    [
        (enum.SeqFormat.STR_DNA, enum.SeqFormat.STR_DNA_GZB64),
        (enum.SeqFormat.STR_DNA_GZB64, enum.SeqFormat.STR_DNA),
        (enum.SeqFormat.STR_DNA_INCL_GAP, enum.SeqFormat.STR_DNA_INCL_GAP_GZB64),
        (enum.SeqFormat.STR_DNA_INCL_GAP_GZB64, enum.SeqFormat.STR_DNA_INCL_GAP),
    ],
)
def test_convert_seq_format_all_supported_directions(
    from_format: enum.SeqFormat, to_format: enum.SeqFormat
) -> None:
    """Convert each supported direction without changing sequence identity."""
    sequence = "ATCGATCG"
    if from_format in {
        enum.SeqFormat.STR_DNA_INCL_GAP,
        enum.SeqFormat.STR_DNA_INCL_GAP_GZB64,
    }:
        sequence = "AT-CGATCG"
    seq = create_seq(sequence, from_format)
    assert seq.id is not None
    repository = SequenceRepository([seq])
    command_ = command.ConvertSeqFormatCommand(
        seq_ids=[seq.id], from_format=from_format, to_format=to_format
    )

    result = seq_service_convert_seq_format(
        SimpleNamespace(repository=repository), command_  # type: ignore[arg-type]
    )

    assert result == [seq.id]
    converted = repository.seqs[seq.id]
    assert converted.contigs[0].seq_format == to_format
    assert converted.contigs[0].get_nucleotide_seq() == sequence.lower()
    assert converted.contigs[0].id == seq.contigs[0].id
    assert repository.uow_instance.commits == 1
    assert repository.uow_instance.rollbacks == 0


@pytest.mark.parametrize(
    ("from_format", "to_format"),
    [
        (enum.SeqFormat.STR_DNA, enum.SeqFormat.STR_DNA_INCL_GAP),
        (enum.SeqFormat.HASH_ONLY, enum.SeqFormat.STR_DNA),
    ],
)
def test_convert_seq_format_rejects_invalid_format_pairs(
    from_format: enum.SeqFormat, to_format: enum.SeqFormat
) -> None:
    """Reject cross-family and non-DNA conversions at command level."""
    with pytest.raises(ValidationError):
        command.ConvertSeqFormatCommand(
            seq_ids=[uuid4()], from_format=from_format, to_format=to_format
        )


def test_convert_seq_format_same_format_no_op() -> None:
    """Same format conversion returns seq_ids without modification."""
    sequence = "ATCGATCG"
    seq = create_seq(sequence, enum.SeqFormat.STR_DNA)
    assert seq.id is not None
    original_seq = seq.model_copy(deep=True)
    repository = SequenceRepository([seq])
    command_ = command.ConvertSeqFormatCommand(
        seq_ids=[seq.id],
        from_format=enum.SeqFormat.STR_DNA,
        to_format=enum.SeqFormat.STR_DNA,
    )

    result = seq_service_convert_seq_format(
        SimpleNamespace(repository=repository), command_  # type: ignore[arg-type]
    )

    assert result == [seq.id]
    assert repository.seqs[seq.id] == original_seq  # Unchanged
    assert repository.uow_instance.commits == 0  # No database write


def test_convert_seq_format_empty_ids_no_op() -> None:
    """Empty seq_ids list returns empty list without database access."""
    command_ = command.ConvertSeqFormatCommand(
        seq_ids=[],
        from_format=enum.SeqFormat.STR_DNA,
        to_format=enum.SeqFormat.STR_DNA_GZB64,
    )
    repository = SequenceRepository([])

    result = seq_service_convert_seq_format(
        SimpleNamespace(repository=repository), command_  # type: ignore[arg-type]
    )

    assert result == []
    assert repository.uow_instance.commits == 0


def test_convert_seq_format_rejects_duplicate_ids() -> None:
    """Require unique identifiers."""
    seq_id = uuid4()
    with pytest.raises(ValidationError, match="seq_ids must be unique"):
        command.ConvertSeqFormatCommand(
            seq_ids=[seq_id, seq_id],
            from_format=enum.SeqFormat.STR_DNA,
            to_format=enum.SeqFormat.STR_DNA_GZB64,
        )


def test_convert_seq_format_validates_batch_before_updating() -> None:
    """Leave all records unchanged when one requested contig has the wrong format."""
    first = create_seq("ATCG", enum.SeqFormat.STR_DNA)
    second = create_seq("ATCG", enum.SeqFormat.STR_DNA_GZB64)
    repository = SequenceRepository([first, second])
    command_ = command.ConvertSeqFormatCommand(
        seq_ids=[first.id, second.id],  # type: ignore[list-item]
        from_format=enum.SeqFormat.STR_DNA,
        to_format=enum.SeqFormat.STR_DNA_GZB64,
    )

    with pytest.raises(ValueError, match="expected 2"):
        seq_service_convert_seq_format(
            SimpleNamespace(repository=repository), command_  # type: ignore[arg-type]
        )  # type: ignore[arg-type]

    assert not repository.update_called
    assert first.id is not None
    assert second.id is not None
    assert repository.seqs[first.id].contigs[0].seq_format == enum.SeqFormat.STR_DNA
    assert (
        repository.seqs[second.id].contigs[0].seq_format == enum.SeqFormat.STR_DNA_GZB64
    )
    assert repository.uow_instance.commits == 0
    assert repository.uow_instance.rollbacks == 1


def test_convert_seq_format_multiple_sequences() -> None:
    """Convert multiple sequences in a single batch operation."""
    seqs = [
        create_seq("ATCG", enum.SeqFormat.STR_DNA),
        create_seq("GCTA", enum.SeqFormat.STR_DNA),
        create_seq("TTAA", enum.SeqFormat.STR_DNA),
    ]
    seq_ids = [seq.id for seq in seqs]
    repository = SequenceRepository(seqs)
    command_ = command.ConvertSeqFormatCommand(
        seq_ids=seq_ids,  # type: ignore[arg-type]
        from_format=enum.SeqFormat.STR_DNA,
        to_format=enum.SeqFormat.STR_DNA_GZB64,
    )

    result = seq_service_convert_seq_format(
        SimpleNamespace(repository=repository), command_  # type: ignore[arg-type]
    )

    assert result == seq_ids
    for seq_id in seq_ids:
        assert (
            repository.seqs[seq_id].contigs[0].seq_format
            == enum.SeqFormat.STR_DNA_GZB64
        )
    assert repository.uow_instance.commits == 1


def test_convert_seq_format_preserves_contig_identity() -> None:
    """Conversion preserves contig ID and other metadata."""
    seq = create_seq("ATCGATCG", enum.SeqFormat.STR_DNA)
    original_contig_id = seq.contigs[0].id
    assert seq.id is not None
    repository = SequenceRepository([seq])
    command_ = command.ConvertSeqFormatCommand(
        seq_ids=[seq.id],
        from_format=enum.SeqFormat.STR_DNA,
        to_format=enum.SeqFormat.STR_DNA_GZB64,
    )

    seq_service_convert_seq_format(
        SimpleNamespace(repository=repository), command_  # type: ignore[arg-type]
    )

    converted = repository.seqs[seq.id]
    assert converted.contigs[0].id == original_contig_id
    assert converted.id == seq.id


def test_convert_seq_format_case_normalization() -> None:
    """Conversion normalizes case to lowercase during compression."""
    # Create with uppercase sequence
    seq = create_seq("ATCGATCG", enum.SeqFormat.STR_DNA)
    assert seq.id is not None
    repository = SequenceRepository([seq])
    command_ = command.ConvertSeqFormatCommand(
        seq_ids=[seq.id],
        from_format=enum.SeqFormat.STR_DNA,
        to_format=enum.SeqFormat.STR_DNA_GZB64,
    )

    seq_service_convert_seq_format(
        SimpleNamespace(repository=repository), command_  # type: ignore[arg-type]
    )

    converted = repository.seqs[seq.id]
    # Verify the nucleotide sequence is lowercase
    assert converted.contigs[0].get_nucleotide_seq() == "atcgatcg"


def test_convert_seq_format_with_gaps() -> None:
    """Conversion works with gap-inclusive formats."""
    sequence = "AT-CGATCG"
    seq = create_seq(sequence, enum.SeqFormat.STR_DNA_INCL_GAP)
    assert seq.id is not None
    repository = SequenceRepository([seq])
    command_ = command.ConvertSeqFormatCommand(
        seq_ids=[seq.id],
        from_format=enum.SeqFormat.STR_DNA_INCL_GAP,
        to_format=enum.SeqFormat.STR_DNA_INCL_GAP_GZB64,
    )

    result = seq_service_convert_seq_format(
        SimpleNamespace(repository=repository), command_  # type: ignore[arg-type]
    )

    assert result == [seq.id]
    converted = repository.seqs[seq.id]
    assert converted.contigs[0].seq_format == enum.SeqFormat.STR_DNA_INCL_GAP_GZB64
    assert converted.contigs[0].get_nucleotide_seq() == sequence.lower()


def test_convert_seq_format_bidirectional_gzb64_to_plain() -> None:
    """Convert from compressed back to plain format."""
    sequence = "ATCGATCG"
    seq = create_seq(sequence, enum.SeqFormat.STR_DNA_GZB64)
    assert seq.id is not None
    repository = SequenceRepository([seq])
    command_ = command.ConvertSeqFormatCommand(
        seq_ids=[seq.id],
        from_format=enum.SeqFormat.STR_DNA_GZB64,
        to_format=enum.SeqFormat.STR_DNA,
    )

    result = seq_service_convert_seq_format(
        SimpleNamespace(repository=repository), command_  # type: ignore[arg-type]
    )

    assert result == [seq.id]
    converted = repository.seqs[seq.id]
    assert converted.contigs[0].seq_format == enum.SeqFormat.STR_DNA
    # Plain format stores lowercase directly
    assert converted.contigs[0].seq == sequence.lower()
    assert converted.contigs[0].get_nucleotide_seq() == sequence.lower()
