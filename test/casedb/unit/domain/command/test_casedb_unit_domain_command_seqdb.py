"""Validate the Casedb command for retrieving genetic sequences as FASTA."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.casedb.domain.command.seqdb import RetrieveGeneticSequenceFastaByIdCommand

WRAP_DESCRIPTION = "The line length to wrap sequences at, or 0 for no wrapping."


def test_retrieve_genetic_sequence_fasta_wrap_defaults_to_80() -> None:
    command = RetrieveGeneticSequenceFastaByIdCommand(seq_ids=[uuid4()])
    assert command.wrap == 80


@pytest.mark.parametrize("wrap", [0, 1, 80])
def test_retrieve_genetic_sequence_fasta_accepts_nonnegative_wrap(wrap: int) -> None:
    command = RetrieveGeneticSequenceFastaByIdCommand(seq_ids=[uuid4()], wrap=wrap)
    assert command.wrap == wrap


def test_retrieve_genetic_sequence_fasta_rejects_negative_wrap() -> None:
    with pytest.raises(ValidationError):
        RetrieveGeneticSequenceFastaByIdCommand(seq_ids=[uuid4()], wrap=-1)


def test_retrieve_genetic_sequence_fasta_describes_zero_wrap() -> None:
    assert (
        RetrieveGeneticSequenceFastaByIdCommand.model_fields["wrap"].description
        == WRAP_DESCRIPTION
    )
