"""Test SQL case-statistics repository behavior."""

from collections.abc import Generator
from datetime import datetime, timezone
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from gen_epix.casedb.domain import enum
from gen_epix.casedb.repositories import sa_model
from gen_epix.casedb.repositories.case_sa import CaseSARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.filter.datetime_range import DatetimeRangeFilter


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


def test_access_filters_aggregate_case_counts_and_adjusted_dates(
    session: Session,
) -> None:
    case_type_id = session.query(sa_model.Case.case_type_id).scalar()
    assert case_type_id is not None
    public_collection_id = uuid4()
    private_collection_id = uuid4()
    case_id = uuid4()
    zero_count_case_id = uuid4()
    timed_at = datetime(2024, 6, 7, 12, 34, 56)
    session.add_all(
        [
            sa_model.Case(
                id=case_id,
                case_type_id=case_type_id,
                created_in_data_collection_id=public_collection_id,
                cohort={},
                count=3,
                timed_at=timed_at,
                content={},
            ),
            sa_model.Case(
                id=zero_count_case_id,
                case_type_id=case_type_id,
                created_in_data_collection_id=public_collection_id,
                cohort={},
                count=0,
                timed_at=datetime(2023, 2, 3),
                content={},
            ),
            sa_model.CaseDataCollectionLink(
                id=uuid4(),
                case_id=case_id,
                data_collection_id=private_collection_id,
            ),
        ]
    )
    session.flush()
    repository = CaseSARepository.__new__(CaseSARepository)
    unit_of_work = SAUnitOfWork(session, context_stack=[])
    access = {enum.ColType.TIME_YEAR: {public_collection_id, private_collection_id}}

    result = repository.retrieve_case_stats(
        unit_of_work,
        case_type_id,
        data_collections_by_time_unit=access,
        private_data_collection_ids={private_collection_id},
        case_ids={case_id, zero_count_case_id},
        datetime_range_filter=DatetimeRangeFilter(lower_bound=datetime(2024, 1, 1)),
    )

    assert result.n_cases == 3
    assert result.n_own_cases == 3
    assert result.first_case_date == datetime(2024, 1, 1)
    assert result.last_case_date == datetime(2024, 1, 1)

    excluded_by_adjusted_date = repository.retrieve_case_stats(
        unit_of_work,
        case_type_id,
        data_collections_by_time_unit=access,
        case_ids={case_id},
        datetime_range_filter=DatetimeRangeFilter(lower_bound=datetime(2024, 2, 1)),
    )
    assert excluded_by_adjusted_date.n_cases == 0
    assert excluded_by_adjusted_date.first_case_date is None

    excluded_by_empty_access = repository.retrieve_case_stats(
        unit_of_work, case_type_id, data_collections_by_time_unit={}
    )
    assert excluded_by_empty_access.n_cases == 0

    excluded_by_empty_case_ids = repository.retrieve_case_stats(
        unit_of_work,
        case_type_id,
        data_collections_by_time_unit=access,
        case_ids=set(),
    )
    assert excluded_by_empty_case_ids.n_cases == 0
