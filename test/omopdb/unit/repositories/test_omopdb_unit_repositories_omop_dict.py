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
_COHORT2_ID = UUID("00000000-0000-0000-0000-000000000008")
_SPECIMEN_WINDOW2_START_ID = UUID("00000000-0000-0000-0000-000000000009")
_SPECIMEN_WINDOW2_INSIDE_ID = UUID("00000000-0000-0000-0000-00000000000a")
_SPECIMEN_NULL_DATE_ID = UUID("00000000-0000-0000-0000-00000000000b")
_FULL_PERSON_ID = UUID("00000000-0000-0000-0000-000000000010")
_FULL_SPECIMEN_ID = UUID("00000000-0000-0000-0000-000000000011")
_ISSUER_ID = UUID("00000000-0000-0000-0000-000000000012")
_FULL_CONCEPT_ID = UUID("00000000-0000-0000-0000-000000000013")


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


def test_specimen_ids_are_grouped_into_distinct_cohort_date_windows() -> None:
    repo = OmopDictRepository.__new__(OmopDictRepository)
    first_cohort = model.Cohort(
        cohort_id=_COHORT_ID,
        cohort_definition_id=_DEFINITION_ID,
        subject_id=_PERSON_ID,
        cohort_start_date=date(2023, 1, 1),
        cohort_end_date=date(2023, 1, 15),
    )
    second_cohort = model.Cohort(
        cohort_id=_COHORT2_ID,
        cohort_definition_id=_DEFINITION_ID,
        subject_id=_PERSON_ID,
        cohort_start_date=date(2023, 3, 2),
        cohort_end_date=date(2023, 3, 16),
    )
    specimens = {
        specimen_id: model.Specimen(
            specimen_id=specimen_id,
            person_id=_PERSON_ID,
            specimen_concept_id=_CONCEPT_ID,
            specimen_type_concept_id=_CONCEPT_ID,
            specimen_date=specimen_date,
        )
        for specimen_id, specimen_date in [
            (_SPECIMEN_START_ID, date(2023, 1, 1)),
            (_SPECIMEN_END_ID, date(2023, 1, 3)),
            (_SPECIMEN_WINDOW2_START_ID, date(2023, 3, 2)),
            (_SPECIMEN_WINDOW2_INSIDE_ID, date(2023, 3, 4)),
        ]
    }
    repo._db = {
        model.Cohort: {_COHORT_ID: first_cohort, _COHORT2_ID: second_cohort},
        model.Specimen: specimens,
    }

    result = repo.get_specimen_ids_by_cohort_ids(
        _DEFINITION_ID, [_COHORT_ID, _COHORT2_ID]
    )

    assert set(result[_COHORT_ID]) == {_SPECIMEN_START_ID, _SPECIMEN_END_ID}
    assert set(result[_COHORT2_ID]) == {
        _SPECIMEN_WINDOW2_START_ID,
        _SPECIMEN_WINDOW2_INSIDE_ID,
    }
    assert not set(result[_COHORT_ID]) & set(result[_COHORT2_ID])


def test_specimen_ids_skip_null_specimen_dates() -> None:
    repo = OmopDictRepository.__new__(OmopDictRepository)
    cohort = model.Cohort(
        cohort_id=_COHORT_ID,
        cohort_definition_id=_DEFINITION_ID,
        subject_id=_PERSON_ID,
        cohort_start_date=date(2023, 1, 1),
        cohort_end_date=date(2023, 1, 31),
    )
    specimen = model.Specimen.model_construct(
        specimen_id=_SPECIMEN_NULL_DATE_ID,
        person_id=_PERSON_ID,
        specimen_concept_id=_CONCEPT_ID,
        specimen_type_concept_id=_CONCEPT_ID,
        specimen_date=None,
    )
    repo._db = {
        model.Cohort: {_COHORT_ID: cohort},
        model.Specimen: {_SPECIMEN_NULL_DATE_ID: specimen},
    }

    assert repo.get_specimen_ids_by_cohort_ids(_DEFINITION_ID, [_COHORT_ID]) == {}


def _make_full_person_repo(with_specimen: bool) -> OmopDictRepository:
    repo = OmopDictRepository.__new__(OmopDictRepository)
    person = model.Person(
        person_id=_FULL_PERSON_ID,
        gender_concept_id=_CONCEPT_ID,
        year_of_birth=1990,
        race_concept_id=_CONCEPT_ID,
        ethnicity_concept_id=_CONCEPT_ID,
        person_type_concept_id=_CONCEPT_ID,
    )
    specimen = model.Specimen(
        specimen_id=_FULL_SPECIMEN_ID,
        person_id=_FULL_PERSON_ID,
        specimen_concept_id=_FULL_CONCEPT_ID,
        specimen_type_concept_id=_FULL_CONCEPT_ID,
        specimen_date=date(2023, 6, 1),
    )
    specimen_identifier = model.SpecimenIdentifier(
        identifier_issuer_id=_ISSUER_ID,
        external_id="SPECIMEN-1",
        internal_id=_FULL_SPECIMEN_ID,
    )
    all_classes = (
        [model.Person, model.PersonIdentifier]
        + model.FullPerson.DATA_CLASSES
        + list(model.FullPerson.IDENTIFIER_CLASSES)
    )
    db = {model_class: {} for model_class in all_classes}
    db[model.Person] = {_FULL_PERSON_ID: person}
    if with_specimen:
        db[model.Specimen] = {_FULL_SPECIMEN_ID: specimen}
        db[model.SpecimenIdentifier] = {specimen_identifier.id: specimen_identifier}
    repo._db = db
    return repo


def test_full_person_retrieval_populates_specimen_identifiers() -> None:
    repo = _make_full_person_repo(with_specimen=True)

    result = repo.get_full_persons_by_person_ids([_FULL_PERSON_ID])

    assert len(result) == 1
    assert len(result[0].specimen_identifiers) == 1
    assert result[0].specimen_identifiers[0].internal_id == _FULL_SPECIMEN_ID
    assert result[0].specimen_identifiers[0].external_id == "SPECIMEN-1"


def test_full_person_without_specimen_has_no_specimen_identifiers() -> None:
    repo = _make_full_person_repo(with_specimen=False)

    result = repo.get_full_persons_by_person_ids([_FULL_PERSON_ID])

    assert len(result) == 1
    assert result[0].specimen_identifiers == []
