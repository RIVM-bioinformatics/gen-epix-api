from datetime import datetime
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from gen_epix.casedb.domain import model
from gen_epix.casedb.repositories import sa_model
from gen_epix.casedb.repositories.case_sa import CaseSARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork

CASE_TYPE_ID = UUID("00000000-0000-0000-0000-000000000001")
CASE_ID = UUID("00000000-0000-0000-0000-000000000002")
DATA_COLLECTION_ID = UUID("00000000-0000-0000-0000-000000000003")
CASE_DATE = datetime(2024, 3, 14, 15, 9, 26)


def _make_sa_repository(session: Session) -> CaseSARepository:
    repository = CaseSARepository.__new__(CaseSARepository)
    repository._uow_context_stack = []  # type: ignore[attr-defined]
    repository.uow = lambda **kwargs: SAUnitOfWork(  # type: ignore[method-assign]
        session, context_stack=repository._uow_context_stack
    )
    return repository


def test_retrieve_case_stats_without_collection_filter(
    session: Session,
) -> None:
    repository = _make_sa_repository(session)
    result = repository.retrieve_case_stats(
        SAUnitOfWork(session),
        case_type_id=CASE_TYPE_ID,
        data_collections_by_time_unit=None,
    )

    assert result == model.CaseStats(
        case_type_id=CASE_TYPE_ID,
        n_cases=1,
        n_own_cases=0,
        first_case_date=CASE_DATE.replace(hour=0, minute=0, second=0, microsecond=0),
        last_case_date=CASE_DATE.replace(hour=0, minute=0, second=0, microsecond=0),
    )


@pytest.fixture
def session() -> Session:  # type: ignore[misc]
    engine = sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as connection:
        connection.execute(sa.text("ATTACH DATABASE ':memory:' AS \"case\""))
        connection.commit()
    sa_model.Case.__table__.create(engine)
    sa_model.CaseDataCollectionLink.__table__.create(engine)
    session = sessionmaker(bind=engine)()
    session.add(
        sa_model.Case(
            id=CASE_ID,
            case_type_id=CASE_TYPE_ID,
            created_in_data_collection_id=DATA_COLLECTION_ID,
            cohort={},
            count=1,
            case_date=CASE_DATE,
            content={},
            code=None,
        )
    )
    session.commit()
    yield session
    session.close()
    engine.dispose()
