"""Validate SeqDB request-field descriptions in command schemas."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain.command.seq import (
    CalculateSeqDistancesForNewProfilesCommand,
    ConvertSeqFormatCommand,
    RetrieveBestSeqClassificationPerSampleCommand,
    RetrieveBestSeqPerSampleCommand,
    RetrieveBestSeqProfilePerSampleCommand,
    RetrieveSeqFastaCommand,
    UpdateSeqDistancesCommand,
    UploadSamplesCommand,
)
from gen_epix.seqdb.domain.enum import SeqFormat

NUMPY_DISTANCE_DESCRIPTION = (
    "If True, use numpy-vectorised ALLELE Hamming with an automatic "
    "variant gate: numpy_batch for n_new < 200, int32_vocab for "
    "n_new >= 200. No effect on non-ALLELE profile types."
)
SAMPLE_IDS_DESCRIPTION = (
    "The IDs of the samples to search among. If None, search among all samples."
)


@pytest.mark.parametrize(
    "command_class",
    [
        CalculateSeqDistancesForNewProfilesCommand,
        UpdateSeqDistancesCommand,
        UploadSamplesCommand,
    ],
)
def test_numpy_distance_schema_description(command_class: type) -> None:
    """Explain the selected NumPy distance strategy to API clients."""
    assert (
        command_class.model_fields["use_numpy_allele_distance"].description
        == NUMPY_DISTANCE_DESCRIPTION
    )


@pytest.mark.parametrize(
    "command_class",
    [
        RetrieveBestSeqClassificationPerSampleCommand,
        RetrieveBestSeqPerSampleCommand,
        RetrieveBestSeqProfilePerSampleCommand,
    ],
)
def test_sample_ids_schema_description(command_class: type) -> None:
    """Explain how optional sample IDs constrain the search."""
    assert (
        command_class.model_fields["sample_ids"].description == SAMPLE_IDS_DESCRIPTION
    )


@pytest.mark.parametrize(
    ("from_format", "to_format"),
    [
        (SeqFormat.STR_DNA, SeqFormat.STR_DNA_INCL_GAP),
        (SeqFormat.HASH_ONLY, SeqFormat.STR_DNA),
    ],
)
def test_convert_seq_format_rejects_invalid_format_pairs(
    from_format: SeqFormat, to_format: SeqFormat
) -> None:
    """Reject cross-family and non-DNA conversions at command level."""
    with pytest.raises(ValidationError):
        ConvertSeqFormatCommand(
            seq_ids=[uuid4()], from_format=from_format, to_format=to_format
        )


def test_convert_seq_format_rejects_duplicate_ids() -> None:
    """Require unique sequence identifiers."""
    seq_id = uuid4()
    with pytest.raises(ValidationError, match="seq_ids must be unique"):
        ConvertSeqFormatCommand(
            seq_ids=[seq_id, seq_id],
            from_format=SeqFormat.STR_DNA,
            to_format=SeqFormat.STR_DNA_GZB64,
        )


def test_retrieve_seq_fasta_wrap_defaults_to_80() -> None:
    command = RetrieveSeqFastaCommand(seq_ids=[uuid4()])
    assert command.wrap == 80


@pytest.mark.parametrize("wrap", [0, 1, 80])
def test_retrieve_seq_fasta_accepts_nonnegative_wrap(wrap: int) -> None:
    command = RetrieveSeqFastaCommand(seq_ids=[uuid4()], wrap=wrap)
    assert command.wrap == wrap


def test_retrieve_seq_fasta_rejects_negative_wrap() -> None:
    with pytest.raises(ValidationError):
        RetrieveSeqFastaCommand(seq_ids=[uuid4()], wrap=-1)
