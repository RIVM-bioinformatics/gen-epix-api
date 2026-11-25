"""Test OMOP domain command validation."""

from uuid import uuid4

import pytest

from gen_epix.omopdb.domain.command.omop import (
    RetrieveSpecimenIdsByCohortIdsCommand,
)


def test_retrieve_specimen_ids_by_cohort_ids_preserves_unique_ids() -> None:
    cohort_definition_id = uuid4()
    cohort_ids = [uuid4(), uuid4()]

    cmd = RetrieveSpecimenIdsByCohortIdsCommand(
        cohort_definition_id=cohort_definition_id,
        cohort_ids=cohort_ids,
    )

    assert cmd.cohort_ids == cohort_ids


def test_retrieve_specimen_ids_by_cohort_ids_rejects_duplicate_ids() -> None:
    cohort_id = uuid4()

    with pytest.raises(ValueError, match="cohort_ids must be unique"):
        RetrieveSpecimenIdsByCohortIdsCommand(
            cohort_definition_id=uuid4(),
            cohort_ids=[cohort_id, cohort_id],
        )
