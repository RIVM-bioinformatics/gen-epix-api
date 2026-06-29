"""
Unit tests for get_full_persons_by_person_ids in OmopDictRepository and
OmopSARepository.

Regression: the SA implementation queried IDENTIFIER_CLASSES (e.g.
SpecimenIdentifier) with WHERE internal_id IN (person_ids), but
internal_id on those classes is the entity id (specimen_id), not the
person_id.  Fix: two-phase lookup — Phase 1 fetches DATA_CLASSES by
person_id; Phase 2 builds entity_id→person_id reverse map and queries
IDENTIFIER_CLASSES by entity ids.
"""

from datetime import date
from unittest.mock import Mock
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.omopdb.domain import model
from gen_epix.omopdb.domain.enum import ServiceType
from gen_epix.omopdb.repositories import sa_model as omop_sa
from gen_epix.omopdb.repositories.omop_dict import OmopDictRepository
from gen_epix.omopdb.repositories.omop_sa import OmopSARepository

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

_PERSON_ID = UUID("00000000-0000-0000-0000-000000000001")
_SPECIMEN_ID = UUID("00000000-0000-0000-0000-000000000002")
_ISSUER_ID = UUID("00000000-0000-0000-0000-000000000003")
_CONCEPT_ID = UUID("00000000-0000-0000-0000-000000000004")
_GENDER_ID = UUID("00000000-0000-0000-0000-000000000010")
_RACE_ID = UUID("00000000-0000-0000-0000-000000000011")
_ETHNICITY_ID = UUID("00000000-0000-0000-0000-000000000012")
_PERSON_TYPE_ID = UUID("00000000-0000-0000-0000-000000000013")
_EXTERNAL_ID = "LSP-12345"
_DATE = date(2023, 6, 1)

# SA table classes required in Phase 1 (queried by person_id / internal_id)
_PHASE1_SA_CLASSES = [omop_sa.Person, omop_sa.PersonIdentifier] + [
    omop_sa.SA_MODELS_BY_SERVICE_TYPE[ServiceType.OMOP][cls]
    for cls in model.FullPerson.DATA_CLASSES
]


# ---------------------------------------------------------------------------
# Dict repository tests
# ---------------------------------------------------------------------------


def _make_dict_repo() -> OmopDictRepository:
    """Bypass __init__: person → specimen → specimen_identifier."""
    repo = OmopDictRepository.__new__(OmopDictRepository)
    person = model.Person(
        person_id=_PERSON_ID,
        gender_concept_id=_GENDER_ID,
        year_of_birth=1990,
        race_concept_id=_RACE_ID,
        ethnicity_concept_id=_ETHNICITY_ID,
        person_type_concept_id=_PERSON_TYPE_ID,
    )
    specimen = model.Specimen(
        specimen_id=_SPECIMEN_ID,
        person_id=_PERSON_ID,
        specimen_concept_id=_CONCEPT_ID,
        specimen_type_concept_id=_CONCEPT_ID,
        specimen_date=_DATE,
    )
    spec_id = model.SpecimenIdentifier(
        identifier_issuer_id=_ISSUER_ID,
        external_id=_EXTERNAL_ID,
        internal_id=_SPECIMEN_ID,
    )
    all_classes = (
        [model.Person, model.PersonIdentifier]
        + model.FullPerson.DATA_CLASSES
        + list(model.FullPerson.IDENTIFIER_CLASSES)
    )
    db: dict = {cls: {} for cls in all_classes}
    db[model.Person] = {_PERSON_ID: person}
    db[model.Specimen] = {_SPECIMEN_ID: specimen}
    db[model.SpecimenIdentifier] = {spec_id.id: spec_id}
    repo._db = db  # type: ignore[attr-defined]
    return repo


class TestDictRepositoryGetFullPersonsByPersonIds:
    def test_specimen_identifiers_populated(self) -> None:
        repo = _make_dict_repo()
        result = repo.get_full_persons_by_person_ids([_PERSON_ID])
        assert len(result) == 1
        si_list = result[0].specimen_identifiers
        assert len(si_list) == 1
        assert si_list[0].internal_id == _SPECIMEN_ID
        assert si_list[0].external_id == _EXTERNAL_ID

    def test_no_specimen_yields_empty_identifiers(self) -> None:
        repo = _make_dict_repo()
        repo._db[model.Specimen] = {}  # type: ignore[index]
        result = repo.get_full_persons_by_person_ids([_PERSON_ID])
        assert result[0].specimen_identifiers == []


# ---------------------------------------------------------------------------
# SA repository tests — SQLite in-memory
# ---------------------------------------------------------------------------


def _col_mapper(model_class: type) -> Mock:
    """Mock mapper that loads domain objects from SA row column values.

    Only copies column names that appear in both the SA table and the
    domain model's fields, avoiding relationship attributes and row-metadata
    fields that have no domain-model counterpart.
    """
    sa_cls = omop_sa.SA_MODELS_BY_SERVICE_TYPE[ServiceType.OMOP][model_class]
    col_names = {c.name for c in sa_cls.__table__.columns}
    field_names = col_names & set(model_class.model_fields.keys())
    m = Mock()
    m.load = lambda row: model_class.model_construct(
        **{f: getattr(row, f) for f in field_names}
    )
    return m


@pytest.fixture(scope="module")
def _sa_session() -> Session:  # type: ignore[misc]
    """In-memory SQLite DB with Person, Specimen, SpecimenIdentifier, and
    all other Phase-1 class tables (empty).

    The SA models use schema "omop"; attach a second in-memory database
    under that name so table creation succeeds.  SQLite does not enforce
    FK constraints by default, so tables with FK references to missing
    tables are created without error.
    """
    engine = sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as conn:
        conn.execute(sa.text("ATTACH DATABASE ':memory:' AS omop"))
        conn.commit()

    # Create all tables needed for phase-1 queries and SpecimenIdentifier
    for sa_cls in _PHASE1_SA_CLASSES + [omop_sa.SpecimenIdentifier]:
        sa_cls.__table__.create(engine)

    # Compute the SA row id for the SpecimenIdentifier (SHA-256 derived)
    _domain_si = model.SpecimenIdentifier(
        identifier_issuer_id=_ISSUER_ID,
        external_id=_EXTERNAL_ID,
        internal_id=_SPECIMEN_ID,
    )

    SessionFactory = sessionmaker(bind=engine)
    session: Session = SessionFactory()
    session.add(
        omop_sa.Person(
            person_id=_PERSON_ID,
            gender_concept_id=_GENDER_ID,
            year_of_birth=1990,
            race_concept_id=_RACE_ID,
            ethnicity_concept_id=_ETHNICITY_ID,
            person_type_concept_id=_PERSON_TYPE_ID,
        )
    )
    session.add(
        omop_sa.Specimen(
            specimen_id=_SPECIMEN_ID,
            person_id=_PERSON_ID,
            specimen_concept_id=_CONCEPT_ID,
            specimen_type_concept_id=_CONCEPT_ID,
            specimen_date=_DATE,
        )
    )
    session.add(
        omop_sa.SpecimenIdentifier(
            id=_domain_si.id,
            internal_id=_SPECIMEN_ID,
            identifier_issuer_id=_ISSUER_ID,
            external_id=_EXTERNAL_ID,
        )
    )
    session.commit()
    yield session  # type: ignore[misc]
    session.close()
    engine.dispose()


def _make_sa_repo(session: Session) -> OmopSARepository:
    """Bypass SARepository.__init__ and wire uow() to the provided session."""
    repo = OmopSARepository.__new__(OmopSARepository)
    repo._uow_context_stack = []  # type: ignore[attr-defined]
    repo.uow = lambda **kwargs: SAUnitOfWork(  # type: ignore[method-assign]
        session, context_stack=repo._uow_context_stack
    )
    # Register mock mappers for all phase-1 and identifier classes
    all_classes = (
        [model.Person, model.PersonIdentifier]
        + model.FullPerson.DATA_CLASSES
        + list(model.FullPerson.IDENTIFIER_CLASSES)
    )
    repo._mapper_by_model = {cls: _col_mapper(cls) for cls in all_classes}  # type: ignore[attr-defined]
    return repo


class TestSARepositoryGetFullPersonsByPersonIds:
    def test_specimen_identifiers_populated(self, _sa_session: Session) -> None:
        # Pre-fix: SA queried SpecimenIdentifier by person_id, always returning
        # empty results because internal_id stores specimen_id, not person_id.
        repo = _make_sa_repo(_sa_session)
        result = repo.get_full_persons_by_person_ids([_PERSON_ID])
        assert len(result) == 1
        si_list = result[0].specimen_identifiers
        assert len(si_list) == 1
        assert si_list[0].internal_id == _SPECIMEN_ID
        assert si_list[0].external_id == _EXTERNAL_ID

    def test_no_person_returns_empty_list(self, _sa_session: Session) -> None:
        repo = _make_sa_repo(_sa_session)
        result = repo.get_full_persons_by_person_ids([])
        assert result == []
