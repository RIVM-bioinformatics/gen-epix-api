"""Tests for the in-memory OMOP repository query helpers."""

from datetime import date
from uuid import UUID

from gen_epix.omopdb.domain import model
from gen_epix.omopdb.repositories.omop_dict import OmopDictRepository

_PERSON_ID = UUID("00000000-0000-0000-0000-000000000001")
_COHORT_ID = UUID("00000000-0000-0000-0000-000000000002")
_DEFINITION_ID = UUID("00000000-0000-0000-0000-000000000003")
_CONCEPT_ID = UUID("00000000-0000-0000-0000-000000000004")
_SPECIMEN_START_ID = UUID("00000000-0000-0000-0000-000000000005")
_SPECIMEN_END_ID = UUID("00000000-0000-0000-0000-000000000006")
_SPECIMEN_OUTSIDE_ID = UUID("00000000-0000-0000-0000-000000000007")


def test_specimen_ids_include_both_cohort_date_boundaries() -> None:
    """Return same-person specimens dated inclusively within the cohort range."""
    repo = OmopDictRepository.__new__(OmopDictRepository)
    cohort = model.Cohort(
        cohort_id=_COHORT_ID,
        cohort_definition_id=_DEFINITION_ID,
        subject_id=_PERSON_ID,
        cohort_start_date=date(2023, 1, 1),
        cohort_end_date=date(2023, 1, 31),
    )
    specimens = {
        _SPECIMEN_START_ID: model.Specimen(
            specimen_id=_SPECIMEN_START_ID,
            person_id=_PERSON_ID,
            specimen_concept_id=_CONCEPT_ID,
            specimen_type_concept_id=_CONCEPT_ID,
            specimen_date=date(2023, 1, 1),
        ),
        _SPECIMEN_END_ID: model.Specimen(
            specimen_id=_SPECIMEN_END_ID,
            person_id=_PERSON_ID,
            specimen_concept_id=_CONCEPT_ID,
            specimen_type_concept_id=_CONCEPT_ID,
            specimen_date=date(2023, 1, 31),
        ),
        _SPECIMEN_OUTSIDE_ID: model.Specimen(
            specimen_id=_SPECIMEN_OUTSIDE_ID,
            person_id=_PERSON_ID,
            specimen_concept_id=_CONCEPT_ID,
            specimen_type_concept_id=_CONCEPT_ID,
            specimen_date=date(2023, 2, 1),
        ),
    }
    repo._db = {model.Cohort: {_COHORT_ID: cohort}, model.Specimen: specimens}

    assert repo.get_specimen_ids_by_cohort_ids(_DEFINITION_ID, [_COHORT_ID]) == {
        _COHORT_ID: [_SPECIMEN_START_ID, _SPECIMEN_END_ID]
    }
