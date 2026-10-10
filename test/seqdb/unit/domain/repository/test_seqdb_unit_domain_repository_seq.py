"""Verify the SeqDB sequence repository domain contract."""

import json
from inspect import isabstract
from uuid import UUID

import pytest

from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.repository.seq import BaseSeqRepository

match_profiles = getattr(
    BaseSeqRepository, "_get_matching_profiles_for_distance_dict_format"
)

LOWER_PROFILE_ID = UUID("11111111-1111-1111-1111-111111111111")
EQUAL_PROFILE_ID = UUID("22222222-2222-2222-2222-222222222222")
UPPER_PROFILE_ID = UUID("33333333-3333-3333-3333-333333333333")
EXISTING_PROFILE_ID = UUID("44444444-4444-4444-4444-444444444444")
DISTANCES = {
    LOWER_PROFILE_ID: 0.25,
    EQUAL_PROFILE_ID: 0.5,
    UPPER_PROFILE_ID: 0.75,
}


def test_base_seq_repository_is_abstract():
    """Require persistence implementations to provide the repository contract."""
    assert isabstract(BaseSeqRepository)


@pytest.mark.parametrize(
    ("max_distance", "expected_profile_ids"),
    [
        pytest.param(0.25, {LOWER_PROFILE_ID}, id="inclusive-lower-bound"),
        pytest.param(
            0.5,
            {LOWER_PROFILE_ID, EQUAL_PROFILE_ID},
            id="inclusive-equal-distance",
        ),
        pytest.param(
            0.75,
            {LOWER_PROFILE_ID, EQUAL_PROFILE_ID, UPPER_PROFILE_ID},
            id="inclusive-upper-bound",
        ),
    ],
)
def test_matching_profiles_includes_distances_at_or_below_threshold(
    max_distance, expected_profile_ids
):
    """Add map entries at or below the threshold without clearing prior matches."""
    matching_profile_ids = {EXISTING_PROFILE_ID}

    result = match_profiles(
        max_distance,
        matching_profile_ids,
        enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
        json.dumps(
            {str(profile_id): distance for profile_id, distance in DISTANCES.items()}
        ),
    )

    assert result is None
    assert matching_profile_ids == expected_profile_ids | {EXISTING_PROFILE_ID}


def test_matching_profiles_propagates_malformed_distance_json():
    """Expose malformed persisted JSON instead of silently ignoring it."""
    with pytest.raises(json.JSONDecodeError):
        match_profiles(
            1.0,
            set(),
            enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
            "{invalid",
        )
