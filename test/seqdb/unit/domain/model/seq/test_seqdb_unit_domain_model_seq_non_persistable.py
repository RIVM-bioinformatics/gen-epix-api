"""Exercise retrieval query, result, and assembled sample model contracts."""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain.model.seq.non_persistable import (
    FullSample,
    SampleQuery,
    SampleQueryResult,
)
from gen_epix.seqdb.domain.model.seq.sample import Sample


@pytest.mark.parametrize(
    ("criteria", "expected_valid"),
    [
        pytest.param({}, False, id="no-criteria"),
        pytest.param({"label": "recent"}, False, id="label-only"),
        pytest.param(
            {"modified_since": datetime(2026, 1, 1)},
            True,
            id="since-only",
        ),
        pytest.param(
            {"modified_until": datetime(2026, 2, 1)},
            True,
            id="until-only",
        ),
        pytest.param(
            {
                "label": "recent",
                "modified_since": datetime(2026, 1, 1),
                "modified_until": datetime(2026, 2, 1),
            },
            True,
            id="both-boundaries",
        ),
    ],
)
def test_sample_query_requires_a_datetime_boundary(
    criteria: dict[str, object], expected_valid: bool
) -> None:
    """Require a datetime boundary while accepting either boundary alone."""
    if expected_valid:
        query = SampleQuery(**criteria)
        assert query.model_dump(exclude_unset=True) == criteria
    else:
        with pytest.raises(ValidationError, match="At least one criterion"):
            SampleQuery(**criteria)


@pytest.mark.parametrize("is_max_results_exceeded", [False, True])
def test_sample_query_result_preserves_query_and_result_state(
    is_max_results_exceeded: bool,
) -> None:
    """Preserve the executed query, matching identifiers, and truncation state."""
    query = SampleQuery(modified_since=datetime(2026, 1, 1))
    sample_ids = [uuid4(), uuid4()]

    result = SampleQueryResult(
        sample_query=query,
        sample_ids=sample_ids,
        is_max_results_exceeded=is_max_results_exceeded,
    )

    assert result.sample_query is query
    assert result.sample_ids == sample_ids
    assert result.is_max_results_exceeded is is_max_results_exceeded


def test_full_sample_has_independent_empty_collections_and_identifier_maps() -> None:
    """Initialize each related-data collection independently and map identifiers."""
    sample = Sample(created_in_data_collection_id=uuid4())

    first = FullSample(sample=sample)
    second = FullSample(sample=sample)

    collection_fields = (
        "sample_identifiers",
        "read_sets",
        "read_set_identifiers",
        "seqs",
        "seq_identifiers",
        "seq_taxonomies",
        "seq_classifications",
        "seq_profiles",
        "seq_profile_identifiers",
        "pcr_measurements",
        "ast_measurements",
    )
    for field_name in collection_fields:
        first_values = getattr(first, field_name)
        second_values = getattr(second, field_name)
        assert not first_values
        assert first_values is not second_values

    assert FullSample.DATA_CLASS_FIELD_MAP[FullSample.DATA_CLASSES[0]] == "read_sets"
    assert (
        FullSample.IDENTIFIER_FIELD_MAP[FullSample.IDENTIFIER_CLASSES[0]]
        == "read_set_identifiers"
    )
