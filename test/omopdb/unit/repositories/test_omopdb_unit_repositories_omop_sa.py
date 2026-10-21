"""Tests for SQLAlchemy OMOP repository result assembly."""

from datetime import date
from test.util.mock_compat import Mock
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.omopdb.domain import model
from gen_epix.omopdb.domain.enum import ServiceType
from gen_epix.omopdb.repositories import sa_model as omop_sa
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


_QUERY_PERSON_ID = UUID("00000000-0000-0000-0000-000000000101")
_QUERY_ISSUER_ID = UUID("00000000-0000-0000-0000-000000000102")
_QUERY_CONCEPT_ID = UUID("00000000-0000-0000-0000-000000000103")
_COHORT_DEFINITION_ID = UUID("00000000-0000-0000-0000-000000000110")
_COHORT1_ID = UUID("00000000-0000-0000-0000-000000000111")
_COHORT2_ID = UUID("00000000-0000-0000-0000-000000000112")
_SPECIMEN_IDS = [
    UUID("00000000-0000-0000-0000-000000000121"),
    UUID("00000000-0000-0000-0000-000000000122"),
    UUID("00000000-0000-0000-0000-000000000123"),
    UUID("00000000-0000-0000-0000-000000000124"),
]
_COHORT_SPECIMEN_DATES = [
    date(2023, 1, 1),
    date(2023, 1, 3),
    date(2023, 3, 2),
    date(2023, 3, 4),
]
_PHASE1_CLASSES = [model.Person, model.PersonIdentifier] + model.FullPerson.DATA_CLASSES


def _column_mapper(model_class: type) -> Mock:
    sa_class = omop_sa.SA_MODELS_BY_SERVICE_TYPE[ServiceType.OMOP][model_class]
    column_names = {column.name for column in sa_class.__table__.columns}
    field_names = column_names & set(model_class.model_fields)
    mapper = Mock()
    mapper.load = lambda row: model_class.model_construct(
        **{field: getattr(row, field) for field in field_names}
    )
    return mapper


@pytest.fixture(scope="module")
def _omop_session() -> Session:  # type: ignore[misc]
    engine = sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as connection:
        connection.execute(sa.text("ATTACH DATABASE ':memory:' AS omop"))
        connection.commit()

    sa_model_by_domain = omop_sa.SA_MODELS_BY_SERVICE_TYPE[ServiceType.OMOP]
    sa_classes = [sa_model_by_domain[domain_class] for domain_class in _PHASE1_CLASSES]
    sa_classes.extend([omop_sa.SpecimenIdentifier, omop_sa.Cohort])
    for sa_class in sa_classes:
        sa_class.__table__.create(engine)

    session = sessionmaker(bind=engine)()
    person = omop_sa.Person(
        person_id=_QUERY_PERSON_ID,
        gender_concept_id=_QUERY_CONCEPT_ID,
        year_of_birth=1990,
        race_concept_id=_QUERY_CONCEPT_ID,
        ethnicity_concept_id=_QUERY_CONCEPT_ID,
        person_type_concept_id=_QUERY_CONCEPT_ID,
    )
    specimens = [
        omop_sa.Specimen(
            specimen_id=specimen_id,
            person_id=_QUERY_PERSON_ID,
            specimen_concept_id=_QUERY_CONCEPT_ID,
            specimen_type_concept_id=_QUERY_CONCEPT_ID,
            specimen_date=specimen_date,
        )
        for specimen_id, specimen_date in zip(_SPECIMEN_IDS, _COHORT_SPECIMEN_DATES)
    ]
    domain_identifier = model.SpecimenIdentifier(
        identifier_issuer_id=_QUERY_ISSUER_ID,
        external_id="SPECIMEN-SA-1",
        internal_id=_SPECIMEN_IDS[0],
    )
    session.add_all(
        [
            person,
            *specimens,
            omop_sa.SpecimenIdentifier(
                id=domain_identifier.id,
                internal_id=_SPECIMEN_IDS[0],
                identifier_issuer_id=_QUERY_ISSUER_ID,
                external_id="SPECIMEN-SA-1",
            ),
            omop_sa.Cohort(
                cohort_id=_COHORT1_ID,
                cohort_definition_id=_COHORT_DEFINITION_ID,
                subject_id=_QUERY_PERSON_ID,
                cohort_start_date=date(2023, 1, 1),
                cohort_end_date=date(2023, 1, 15),
            ),
            omop_sa.Cohort(
                cohort_id=_COHORT2_ID,
                cohort_definition_id=_COHORT_DEFINITION_ID,
                subject_id=_QUERY_PERSON_ID,
                cohort_start_date=date(2023, 3, 2),
                cohort_end_date=date(2023, 3, 16),
            ),
        ]
    )
    session.commit()
    yield session  # type: ignore[misc]
    session.close()
    engine.dispose()


def _make_query_repo(session: Session) -> OmopSARepository:
    repo = OmopSARepository.__new__(OmopSARepository)
    repo._uow_context_stack = []  # type: ignore[attr-defined]
    repo.uow = lambda **kwargs: SAUnitOfWork(  # type: ignore[method-assign]
        session, context_stack=repo._uow_context_stack
    )
    repo._mapper_by_model = {  # type: ignore[attr-defined]
        model_class: _column_mapper(model_class)
        for model_class in (_PHASE1_CLASSES + list(model.FullPerson.IDENTIFIER_CLASSES))
    }
    return repo


def test_full_person_retrieval_populates_specimen_identifiers(
    _omop_session: Session,
) -> None:
    repo = _make_query_repo(_omop_session)

    result = repo.get_full_persons_by_person_ids([_QUERY_PERSON_ID])

    assert len(result) == 1
    assert len(result[0].specimen_identifiers) == 1
    assert result[0].specimen_identifiers[0].internal_id == _SPECIMEN_IDS[0]
    assert result[0].specimen_identifiers[0].external_id == "SPECIMEN-SA-1"


def test_full_person_retrieval_with_empty_ids_returns_empty_list(
    _omop_session: Session,
) -> None:
    repo = _make_query_repo(_omop_session)
    assert repo.get_full_persons_by_person_ids([]) == []


def test_specimen_ids_are_grouped_into_distinct_cohort_date_windows(
    _omop_session: Session,
) -> None:
    repo = _make_query_repo(_omop_session)

    result = repo.get_specimen_ids_by_cohort_ids(
        _COHORT_DEFINITION_ID, [_COHORT1_ID, _COHORT2_ID]
    )

    assert set(result[_COHORT1_ID]) == set(_SPECIMEN_IDS[:2])
    assert set(result[_COHORT2_ID]) == set(_SPECIMEN_IDS[2:])
    assert not set(result[_COHORT1_ID]) & set(result[_COHORT2_ID])
