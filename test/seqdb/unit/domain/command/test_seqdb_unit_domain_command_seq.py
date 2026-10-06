"""Validate SeqDB request-field descriptions in command schemas."""

import pytest

from gen_epix.seqdb.domain.command.seq import (
    CalculateSeqDistancesForNewProfilesCommand,
    RetrieveBestSeqClassificationPerSampleCommand,
    RetrieveBestSeqPerSampleCommand,
    RetrieveBestSeqProfilePerSampleCommand,
    UpdateSeqDistancesCommand,
    UploadSamplesCommand,
)

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
