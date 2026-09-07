"""Test case-statistics parity across dictionary and SQL repositories."""

from collections.abc import Iterator
from datetime import datetime
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.repositories import sa_model
from gen_epix.casedb.repositories.case_dict import CaseDictRepository
from gen_epix.casedb.repositories.case_sa import CaseSARepository
from gen_epix.fastapp.repositories.dict.unit_of_work import DictUnitOfWork
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork

_CASE_TYPE_ID = UUID("00000000-0000-0000-0000-000000000001")
_CASE_ID_ZERO = UUID("00000000-0000-0000-0000-000000000010")
_CASE_ID_ONE = UUID("00000000-0000-0000-0000-000000000011")
_CASE_ID_TARGET = UUID("00000000-0000-0000-0000-000000000012")
_PUBLIC_DATA_COLLECTION_ID = UUID("00000000-0000-0000-0000-000000000020")
_PRIVATE_DATA_COLLECTION_ID = UUID("00000000-0000-0000-0000-000000000021")
_PRIVATE_LINK_ID = UUID("00000000-0000-0000-0000-000000000030")
_ZERO_DATE = datetime(2020, 2, 3, 12)
_ONE_DATE = datetime(2021, 4, 5, 12)
_TARGET_DATE = datetime(2022, 6, 7, 12)


def _make_cases(target_count: int) -> list[model.Case]:
    return [
        model.Case(
            id=_CASE_ID_ZERO,
            case_type_id=_CASE_TYPE_ID,
            created_in_data_collection_id=_PUBLIC_DATA_COLLECTION_ID,
            count=0,
            case_date=_ZERO_DATE,
            content={},
        ),
        model.Case(
            id=_CASE_ID_ONE,
            case_type_id=_CASE_TYPE_ID,
            created_in_data_collection_id=_PUBLIC_DATA_COLLECTION_ID,
            count=1,
            case_date=_ONE_DATE,
            content={},
        ),
        model.Case(
            id=_CASE_ID_TARGET,
            case_type_id=_CASE_TYPE_ID,
            created_in_data_collection_id=_PUBLIC_DATA_COLLECTION_ID,
            count=target_count,
            case_date=_TARGET_DATE,
            content={},
        ),
    ]


def _make_links(is_private: bool) -> list[model.CaseDataCollectionLink]:
    if not is_private:
        return []
    return [
        model.CaseDataCollectionLink(
            id=_PRIVATE_LINK_ID,
            case_id=_CASE_ID_TARGET,
            data_collection_id=_PRIVATE_DATA_COLLECTION_ID,
        )
    ]


def _make_dict_repository(
    cases: list[model.Case], links: list[model.CaseDataCollectionLink]
) -> CaseDictRepository:
    repository = CaseDictRepository.__new__(CaseDictRepository)
    repository._db = {  # type: ignore[attr-defined]
        model.Case: {case.id: case for case in cases},
        model.CaseDataCollectionLink: {link.id: link for link in links},
    }
    return repository


@pytest.fixture(name="sa_session")
def fixture_sa_session() -> Iterator[Session]:
    engine = sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as connection:
        connection.execute(sa.text("ATTACH DATABASE ':memory:' AS 'case'"))
        connection.commit()
    sa_model.Case.__table__.create(engine)
    sa_model.CaseDataCollectionLink.__table__.create(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


def _make_sa_repository() -> CaseSARepository:
    return CaseSARepository.__new__(CaseSARepository)


def _persist_sa_rows(
    session: Session,
    cases: list[model.Case],
    links: list[model.CaseDataCollectionLink],
) -> None:
    session.add_all(
        [
            sa_model.Case(
                id=case.id,
                case_type_id=case.case_type_id,
                created_in_data_collection_id=case.created_in_data_collection_id,
                cohort={},
                count=case.count,
                case_date=case.case_date,
                content={},
                code=None,
            )
            for case in cases
        ]
    )
    session.add_all(
        [
            sa_model.CaseDataCollectionLink(
                id=link.id,
                case_id=link.case_id,
                data_collection_id=link.data_collection_id,
            )
            for link in links
        ]
    )
    session.flush()


@pytest.mark.parametrize("repository_type", ["DICT", "SA_SQLITE"])
@pytest.mark.parametrize("target_count", [0, 1, 3])
@pytest.mark.parametrize("is_date_restricted", [False, True])
@pytest.mark.parametrize("is_private", [False, True])
def test_retrieve_case_stats_count_access_and_private_matrix(
    repository_type: str,
    target_count: int,
    is_date_restricted: bool,
    is_private: bool,
    sa_session: Session,
) -> None:
    cases = _make_cases(target_count)
    links = _make_links(is_private)
    private_ids = {_PRIVATE_DATA_COLLECTION_ID} if is_private else set()
    data_collections_by_time_unit = (
        {
            enum.ColType.TIME_YEAR: {
                _PUBLIC_DATA_COLLECTION_ID,
                _PRIVATE_DATA_COLLECTION_ID,
            }
        }
        if is_date_restricted
        else None
    )

    repository: CaseDictRepository | CaseSARepository
    uow: BaseUnitOfWork
    if repository_type == "DICT":
        repository = _make_dict_repository(cases, links)
        uow = DictUnitOfWork()
    else:
        repository = _make_sa_repository()
        _persist_sa_rows(sa_session, cases, links)
        uow = SAUnitOfWork(sa_session)

    stats = repository.retrieve_case_stats(
        uow,
        case_type_id=_CASE_TYPE_ID,
        data_collections_by_time_unit=data_collections_by_time_unit,
        private_data_collection_ids=private_ids,
    )

    expected_target_date = datetime(2022, 1, 1) if is_date_restricted else _TARGET_DATE
    expected_one_date = datetime(2021, 1, 1) if is_date_restricted else _ONE_DATE
    assert stats.n_cases == 1 + target_count
    assert stats.n_own_cases == (target_count if is_private else 0)
    assert stats.first_case_date == expected_one_date
    assert stats.last_case_date == (
        expected_target_date if target_count > 0 else expected_one_date
    )
