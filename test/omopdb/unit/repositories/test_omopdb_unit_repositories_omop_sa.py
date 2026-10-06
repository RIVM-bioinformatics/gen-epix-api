"""Tests for SQLAlchemy OMOP repository result assembly."""

from uuid import UUID

from gen_epix.omopdb.domain import model
from gen_epix.omopdb.repositories.omop_sa import OmopSARepository

_PERSON_ID = UUID("00000000-0000-0000-0000-000000000001")
_MISSING_PERSON_ID = UUID("00000000-0000-0000-0000-000000000002")


def test_full_person_assembly_skips_missing_people_and_preserves_order() -> None:
    """Assemble requested people in order and omit IDs without person records."""
    model_classes = (
        [model.Person, model.PersonIdentifier]
        + model.FullPerson.DATA_CLASSES
        + model.FullPerson.IDENTIFIER_CLASSES
    )
    db = {
        model_class: {person_id: [] for person_id in (_PERSON_ID, _MISSING_PERSON_ID)}
        for model_class in model_classes
    }
    db[model.Person][_PERSON_ID].append(
        model.Person.model_construct(person_id=_PERSON_ID)
    )

    persons = OmopSARepository._create_full_persons(
        [_MISSING_PERSON_ID, _PERSON_ID], db
    )

    assert [person.id for person in persons] == [_PERSON_ID]
    assert persons[0].person.person_id == _PERSON_ID
    assert persons[0].specimens == []
    assert persons[0].specimen_identifiers == []
