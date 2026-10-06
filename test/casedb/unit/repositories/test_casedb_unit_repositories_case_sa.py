"""Test SQL case-statistics repository behavior."""

from collections.abc import Generator
from datetime import datetime, timezone
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from gen_epix.casedb.repositories import sa_model
from gen_epix.casedb.repositories.case_sa import CaseSARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Create a SQLite session containing one case with a precise timestamp."""
    engine = sa.create_engine("sqlite://", poolclass=StaticPool)
    with engine.connect() as connection:
        connection.execute(sa.text("ATTACH DATABASE ':memory:' AS \"case\""))
        connection.commit()
    sa_model.Case.__table__.create(engine)
    sa_model.CaseDataCollectionLink.__table__.create(engine)
    with Session(engine) as session:
        session.add(
            sa_model.Case(
                id=uuid4(),
                case_type_id=uuid4(),
                created_in_data_collection_id=uuid4(),
                cohort={},
                count=1,
                timed_at=datetime(2024, 1, 2, 12, 34, 56, tzinfo=timezone.utc),
                content={},
            )
        )
        session.commit()
        yield session
    engine.dispose()


def test_unrestricted_statistics_include_cases_without_truncating_dates(
    session: Session,
) -> None:
    """None access filters include all cases and retain their original dates."""
    case_type_id = session.query(sa_model.Case.case_type_id).scalar()
    assert case_type_id is not None
    repository = CaseSARepository.__new__(CaseSARepository)
    unit_of_work = SAUnitOfWork(session, context_stack=[])

    result = repository.retrieve_case_stats(unit_of_work, case_type_id)

    assert result.n_cases == 1
    assert result.first_case_date == datetime(2024, 1, 2, 12, 34, 56)
    assert result.last_case_date == result.first_case_date
