"""Provide SQLAlchemy-backed persistence for casedb case data."""

from typing import Any, cast
from uuid import UUID

from sqlalchemy import case as sa_case
from sqlalchemy import func, literal, true, union_all
from sqlalchemy.sql import Select

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.repository import BaseCaseRepository
from gen_epix.casedb.repositories import sa_model as sa_model
from gen_epix.fastapp.repositories import SARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.datetime_range import DatetimeRangeFilter


class CaseSARepository(SARepository, BaseCaseRepository):
    """Encapsulates SQLAlchemy-backed persistence for casedb case data."""

    def retrieve_case_stats(
        self,
        uow: BaseUnitOfWork,
        case_type_id: UUID,
        data_collections_by_time_unit: dict[enum.ColType, set[UUID]] | None = None,
        private_data_collection_ids: set[UUID] | None = None,
        case_ids: set[UUID] | None = None,
        datetime_range_filter: DatetimeRangeFilter | None = None,
    ) -> model.CaseStats:
        """See base method."""
        # Initialize some
        case_stats = model.CaseStats(case_type_id=case_type_id)
        has_abac = data_collections_by_time_unit is not None
        is_filter_by_case_ids = case_ids is not None
        has_private_data_collections = bool(private_data_collection_ids)
        if data_collections_by_time_unit is None:
            data_collections_by_time_unit = {}
        if private_data_collection_ids is None:
            private_data_collection_ids = set()
        if case_ids is None:
            case_ids = set()

        # @ABAC: no access at all
        if has_abac and not data_collections_by_time_unit:
            # If the dict is empty, there are no data collections available to filter by, so return zero cases
            return case_stats

        assert isinstance(uow, SAUnitOfWork)
        query, last_index = _build_case_stats_query(
            uow.session,
            case_type_id,
            data_collections_by_time_unit,
            private_data_collection_ids,
            has_private_data_collections,
            has_abac,
        )
        _accumulate_case_stats(
            self,
            case_stats,
            query,
            last_index,
            case_ids,
            is_filter_by_case_ids,
            datetime_range_filter,
            has_abac,
        )
        return case_stats


def _build_case_stats_query(
    session: Any,
    case_type_id: UUID,
    data_collections_by_time_unit: dict[enum.ColType, set[UUID]],
    private_data_collection_ids: set[UUID],
    has_private_data_collections: bool,
    has_abac: bool,
) -> tuple[Any, int]:
    """Build the aggregated SQL query used to calculate case statistics."""
    last_index = len(enum.ColTypeOrder.TIME_RESOLUTION_DESC.value)
    fields = [
        sa_model.Case.created_in_data_collection_id,
        sa_model.CaseDataCollectionLink.data_collection_id,
    ]
    # Prepare CASE arguments for time-unit resolution and private-collection membership.
    case_statement_args: list[list[list[tuple]]] = [[[], []], [[], []]]
    case_statement_args[1][0].append((fields[1].is_(None), last_index))
    case_statement_args[1][1].append((fields[1].is_(None), 0))
    if not has_abac:
        for field_args in case_statement_args:
            field_args[0].append((true(), 0))
    # Go over each time unit and add conditions for data collection IDs.
    for index, col_type in enumerate(enum.ColTypeOrder.TIME_RESOLUTION_DESC.value):
        if col_type not in data_collections_by_time_unit:
            continue
        data_collection_ids = data_collections_by_time_unit[col_type]
        for field_index, field in enumerate(fields):
            case_statement_args[field_index][0].append(
                (field.in_(data_collection_ids), index)
            )
    # Add conditions for private data collection IDs.
    for field_index, field in enumerate(fields):
        case_statement_args[field_index][1].append(
            (field.in_(private_data_collection_ids), 1)
        )

    query1 = (
        session.query(
            sa_model.Case.id,
            func.max(sa_model.Case.count).label("count"),
            sa_model.Case.timed_at,
            func.min(sa_case(*case_statement_args[0][0], else_=last_index)).label(
                "data_collection_time_unit_index"
            ),
            (
                func.max(sa_case(*case_statement_args[0][1], else_=0)).label(
                    "is_in_private_data_collection"
                )
                if has_private_data_collections
                else literal(0).label("is_in_private_data_collection")
            ),
        )
        .group_by(sa_model.Case.timed_at, sa_model.Case.id)
        .where(sa_model.Case.case_type_id == case_type_id)
    )
    query2 = (
        session.query(
            sa_model.Case.id,
            func.max(sa_model.Case.count).label("count"),
            sa_model.Case.timed_at,
            func.min(sa_case(*case_statement_args[1][0], else_=last_index)).label(
                "data_collection_time_unit_index"
            ),
            (
                func.max(sa_case(*case_statement_args[1][1], else_=0)).label(
                    "is_in_private_data_collection"
                )
                if has_private_data_collections
                else literal(0).label("is_in_private_data_collection")
            ),
        )
        .outerjoin(
            sa_model.CaseDataCollectionLink,
            sa_model.Case.id == sa_model.CaseDataCollectionLink.case_id,
        )
        .group_by(sa_model.Case.timed_at, sa_model.Case.id)
        .where(sa_model.Case.case_type_id == case_type_id)
    )
    # Combine both queries and group by case date and ID to get the minimum time-unit index.
    combined_query = union_all(
        cast(Select, query1.statement), cast(Select, query2.statement)
    ).alias()
    query = (
        session.query(
            combined_query.c[0],  # case_id
            func.max(combined_query.c[1]).label("count"),
            combined_query.c[2],  # timed_at
            func.min(combined_query.c[3]).label("data_collection_time_unit_index"),
            func.max(combined_query.c[4]).label("is_in_private_data_collection"),
        )
        .group_by(combined_query.c[2], combined_query.c[0])
        .order_by(func.max(combined_query.c[1]).desc())
    )
    return query, last_index


def _accumulate_case_stats(
    repository: CaseSARepository,
    case_stats: model.CaseStats,
    query: Any,
    last_index: int,
    case_ids: set[UUID],
    is_filter_by_case_ids: bool,
    datetime_range_filter: DatetimeRangeFilter | None,
    has_abac: bool,
) -> None:
    """Apply case-ID and adjusted-date filters while accumulating statistics."""
    date_mappers = [
        repository.DATE_MAPPERS[col_type]
        for col_type in enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
    ]
    datetime_matcher = (
        datetime_range_filter.match_value if datetime_range_filter is not None else None
    )
    for row in query.all():
        col_type_index = row[3]
        if col_type_index == last_index:
            continue
        case_id = row[0]
        if is_filter_by_case_ids and case_id not in case_ids:
            continue
        timed_at = row[2]
        if has_abac:
            timed_at = date_mappers[col_type_index](timed_at)
        if datetime_matcher is not None and not datetime_matcher(timed_at):
            continue
        count = row[1]
        case_stats.n_cases += count
        case_stats.n_own_cases += count if row[4] else 0
        if count == 0:
            continue
        case_stats.first_case_date = (
            timed_at
            if case_stats.first_case_date is None
            else min(case_stats.first_case_date, timed_at)
        )
        case_stats.last_case_date = (
            timed_at
            if case_stats.last_case_date is None
            else max(case_stats.last_case_date, timed_at)
        )
