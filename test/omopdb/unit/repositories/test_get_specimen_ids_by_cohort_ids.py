"""
Unit tests for get_specimen_ids_by_cohort_ids.

Scenario: one person with two non-overlapping infection-episode cohorts.
- Person P, specimens A/B in episode 1 and C/D in episode 2.
- Cohort 1: [T, T+14]  — should map to {A, B}
- Cohort 2: [T+60, T+74] — should map to {C, D}
- No specimen ID should appear in both sets.
- A specimen with specimen_date=None must be excluded (Dict repo only; the SA
  schema enforces NOT NULL so that case cannot arise in production).
"""

from datetime import date
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.omopdb.domain import model
from gen_epix.omopdb.repositories import sa_model
from gen_epix.omopdb.repositories.omop_dict import OmopDictRepository
from gen_epix.omopdb.repositories.omop_sa import OmopSARepository
from gen_epix.omopdb.repositories.sa_model.omop import Base

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

_PERSON_ID = UUID("00000000-0000-0000-0000-000000000001")
_COHORT_DEF_ID = UUID("00000000-0000-0000-0000-000000000010")
_COHORT1_ID = UUID("00000000-0000-0000-0000-000000000011")
_COHORT2_ID = UUID("00000000-0000-0000-0000-000000000012")
_CONCEPT_ID = UUID("00000000-0000-0000-0000-000000000020")
_CONCEPT_TYPE_ID = UUID("00000000-0000-0000-0000-000000000021")
_SPECIMEN_A_ID = UUID("00000000-0000-0000-0000-000000000101")
_SPECIMEN_B_ID = UUID("00000000-0000-0000-0000-000000000102")
_SPECIMEN_C_ID = UUID("00000000-0000-0000-0000-000000000103")
_SPECIMEN_D_ID = UUID("00000000-0000-0000-0000-000000000104")
_SPECIMEN_NULL_DATE_ID = UUID("00000000-0000-0000-0000-000000000105")

_T = date(2023, 1, 1)
_T2 = date(2023, 1, 3)  # T + 2 days  — cohort 1 window
_T14 = date(2023, 1, 15)  # T + 14 days — cohort 1 end
_T60 = date(2023, 3, 2)  # T + 60 days — cohort 2 window
_T62 = date(2023, 3, 4)  # T + 62 days — cohort 2 window
_T74 = date(2023, 3, 16)  # T + 74 days — cohort 2 end


# ---------------------------------------------------------------------------
# Dict repository tests
# ---------------------------------------------------------------------------


def _make_dict_repo(include_null_date: bool = False) -> OmopDictRepository:
    """Bypass __init__ and set _db directly."""
    repo = OmopDictRepository.__new__(OmopDictRepository)
    cohorts: dict[UUID, model.Cohort] = {
        _COHORT1_ID: model.Cohort(
            cohort_id=_COHORT1_ID,
            cohort_definition_id=_COHORT_DEF_ID,
            subject_id=_PERSON_ID,
            cohort_start_date=_T,
            cohort_end_date=_T14,
        ),
        _COHORT2_ID: model.Cohort(
            cohort_id=_COHORT2_ID,
            cohort_definition_id=_COHORT_DEF_ID,
            subject_id=_PERSON_ID,
            cohort_start_date=_T60,
            cohort_end_date=_T74,
        ),
    }
    specimens: dict[UUID, model.Specimen] = {
        _SPECIMEN_A_ID: model.Specimen(
            specimen_id=_SPECIMEN_A_ID,
            person_id=_PERSON_ID,
            specimen_concept_id=_CONCEPT_ID,
            specimen_type_concept_id=_CONCEPT_TYPE_ID,
            specimen_date=_T,
        ),
        _SPECIMEN_B_ID: model.Specimen(
            specimen_id=_SPECIMEN_B_ID,
            person_id=_PERSON_ID,
            specimen_concept_id=_CONCEPT_ID,
            specimen_type_concept_id=_CONCEPT_TYPE_ID,
            specimen_date=_T2,
        ),
        _SPECIMEN_C_ID: model.Specimen(
            specimen_id=_SPECIMEN_C_ID,
            person_id=_PERSON_ID,
            specimen_concept_id=_CONCEPT_ID,
            specimen_type_concept_id=_CONCEPT_TYPE_ID,
            specimen_date=_T60,
        ),
        _SPECIMEN_D_ID: model.Specimen(
            specimen_id=_SPECIMEN_D_ID,
            person_id=_PERSON_ID,
            specimen_concept_id=_CONCEPT_ID,
            specimen_type_concept_id=_CONCEPT_TYPE_ID,
            specimen_date=_T62,
        ),
    }
    if include_null_date:
        # model_construct bypasses Pydantic validation so we can set
        # specimen_date=None on a field declared as `date` (not date|None)
        specimens[_SPECIMEN_NULL_DATE_ID] = model.Specimen.model_construct(
            specimen_id=_SPECIMEN_NULL_DATE_ID,
            person_id=_PERSON_ID,
            specimen_date=None,
            specimen_concept_id=_CONCEPT_ID,
            specimen_type_concept_id=_CONCEPT_TYPE_ID,
        )
    repo._db = {model.Cohort: cohorts, model.Specimen: specimens}  # type: ignore[attr-defined]
    return repo


class TestDictRepositoryGetSpecimenIdsByCohortIds:

    def test_two_cohorts_date_windows(self) -> None:
        repo = _make_dict_repo()
        result = repo.get_specimen_ids_by_cohort_ids(
            cohort_definition_id=_COHORT_DEF_ID,
            cohort_ids=[_COHORT1_ID, _COHORT2_ID],
        )
        assert set(result.get(_COHORT1_ID, [])) == {_SPECIMEN_A_ID, _SPECIMEN_B_ID}
        assert set(result.get(_COHORT2_ID, [])) == {_SPECIMEN_C_ID, _SPECIMEN_D_ID}
        assert not set(result.get(_COHORT1_ID, [])) & set(result.get(_COHORT2_ID, []))

    def test_null_specimen_date_excluded(self) -> None:
        repo = _make_dict_repo(include_null_date=True)
        result = repo.get_specimen_ids_by_cohort_ids(
            cohort_definition_id=_COHORT_DEF_ID,
            cohort_ids=[_COHORT1_ID, _COHORT2_ID],
        )
        all_ids = {sid for ids in result.values() for sid in ids}
        assert _SPECIMEN_NULL_DATE_ID not in all_ids


# ---------------------------------------------------------------------------
# SA repository tests — SQLite in-memory
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _sa_session() -> Session:  # type: ignore[misc]
    """Create an in-memory SQLite DB with Cohort and Specimen tables populated.

    The SA models use schema "omop" in their table names. SQLite supports this
    via ATTACH DATABASE, so we attach a second in-memory database as "omop"
    before creating the two tables needed for this query.
    SQLite does not enforce FK constraints by default, so individual table
    creation succeeds even though Specimen declares FKs to Person/Concept.
    """
    engine = sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as conn:
        conn.execute(sa.text("ATTACH DATABASE ':memory:' AS omop"))
        conn.commit()
    sa_model.Cohort.__table__.create(engine)
    sa_model.Specimen.__table__.create(engine)

    SessionFactory = sessionmaker(bind=engine)
    session: Session = SessionFactory()
    session.add_all(
        [
            sa_model.Cohort(
                cohort_id=_COHORT1_ID,
                cohort_definition_id=_COHORT_DEF_ID,
                subject_id=_PERSON_ID,
                cohort_start_date=_T,
                cohort_end_date=_T14,
            ),
            sa_model.Cohort(
                cohort_id=_COHORT2_ID,
                cohort_definition_id=_COHORT_DEF_ID,
                subject_id=_PERSON_ID,
                cohort_start_date=_T60,
                cohort_end_date=_T74,
            ),
            sa_model.Specimen(
                specimen_id=_SPECIMEN_A_ID,
                person_id=_PERSON_ID,
                specimen_concept_id=_CONCEPT_ID,
                specimen_type_concept_id=_CONCEPT_TYPE_ID,
                specimen_date=_T,
            ),
            sa_model.Specimen(
                specimen_id=_SPECIMEN_B_ID,
                person_id=_PERSON_ID,
                specimen_concept_id=_CONCEPT_ID,
                specimen_type_concept_id=_CONCEPT_TYPE_ID,
                specimen_date=_T2,
            ),
            sa_model.Specimen(
                specimen_id=_SPECIMEN_C_ID,
                person_id=_PERSON_ID,
                specimen_concept_id=_CONCEPT_ID,
                specimen_type_concept_id=_CONCEPT_TYPE_ID,
                specimen_date=_T60,
            ),
            sa_model.Specimen(
                specimen_id=_SPECIMEN_D_ID,
                person_id=_PERSON_ID,
                specimen_concept_id=_CONCEPT_ID,
                specimen_type_concept_id=_CONCEPT_TYPE_ID,
                specimen_date=_T62,
            ),
        ]
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
    return repo


class TestSARepositoryGetSpecimenIdsByCohortIds:

    def test_two_cohorts_date_windows(self, _sa_session: Session) -> None:
        repo = _make_sa_repo(_sa_session)
        result = repo.get_specimen_ids_by_cohort_ids(
            cohort_definition_id=_COHORT_DEF_ID,
            cohort_ids=[_COHORT1_ID, _COHORT2_ID],
        )
        assert set(result.get(_COHORT1_ID, [])) == {_SPECIMEN_A_ID, _SPECIMEN_B_ID}
        assert set(result.get(_COHORT2_ID, [])) == {_SPECIMEN_C_ID, _SPECIMEN_D_ID}
        assert not set(result.get(_COHORT1_ID, [])) & set(result.get(_COHORT2_ID, []))
