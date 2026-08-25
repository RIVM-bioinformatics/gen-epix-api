from typing import Any, Callable, cast
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import case as sa_case
from sqlalchemy import func, not_, union_all

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.repository import BaseCaseRepository
from gen_epix.casedb.repositories import sa_model as sa_model
from gen_epix.casedb.repositories.case_stats_sql import truncate_datetime
from gen_epix.fastapp.repositories import SARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.datetime_range import DatetimeRangeFilter
from gen_epix.filter.enum import ComparisonOperator


class CaseSARepository(SARepository, BaseCaseRepository):
    def retrieve_case_stats(
        self,
        uow: BaseUnitOfWork,
        case_type_id: UUID,
        data_collections_by_time_unit: dict[enum.ColType, set[UUID]] | None = None,
        private_data_collection_ids: set[UUID] | None = None,
        case_ids: set[UUID] | None = None,
        datetime_range_filter: DatetimeRangeFilter | None = None,
    ) -> model.CaseStats:

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

        if is_filter_by_case_ids and not case_ids:
            return case_stats

        # Expected case with data_collections_by_time_unit given

        # Prepare CASE statement arguments for assigning the highest allowed time unit resolution, and assigning membership of at least one private data collection
        last_index = len(enum.ColTypeOrder.TIME_RESOLUTION_DESC.value)
        fields = [
            sa_model.Case.created_in_data_collection_id,
            sa_model.CaseDataCollectionLink.data_collection_id,
        ]
        case_statement_args: list[list[list[tuple]]] = [[[], []], [[], []]]
        case_statement_args[1][0].append((fields[1].is_(None), last_index))
        case_statement_args[1][1].append((fields[1].is_(None), 0))
        # Go over each time unit and add conditions for data collection IDs
        for i, col_type in enumerate(enum.ColTypeOrder.TIME_RESOLUTION_DESC.value):
            if col_type not in data_collections_by_time_unit:
                continue
            data_collection_ids = data_collections_by_time_unit[col_type]
            for j, field in enumerate(fields):
                case_statement_args[j][0].append((field.in_(data_collection_ids), i))
        # Add conditions for private data collection IDs
        for j, field in enumerate(fields):
            case_statement_args[j][1].append(
                (field.in_(private_data_collection_ids), 1)
            )

        # First query: cases with created_in_data_collection_id in the given data collections
        assert isinstance(uow, SAUnitOfWork)
        session = uow.session
        case_id_temp_table = None
        if is_filter_by_case_ids and session.get_bind().dialect.name == "mssql":
            case_id_temp_table = self.create_unique_values_temp_table(
                session,
                sa_model.Case.metadata,
                sa_model.Case.id.name,
                sa_model.Case.__table__.c.id.type,
                list(case_ids),
            )

        def apply_case_id_filter(query: Any) -> Any:
            if not is_filter_by_case_ids:
                return query
            if case_id_temp_table is not None:
                return query.join(
                    case_id_temp_table,
                    sa_model.Case.id == case_id_temp_table.c[sa_model.Case.id.name],
                )
            return query.where(sa_model.Case.id.in_(case_ids))

        query1 = (
            session.query(
                sa_model.Case.id,
                sa_model.Case.case_date,
                func.min(sa_case(*case_statement_args[0][0], else_=last_index)).label(
                    "data_collection_time_unit_index"
                ),
                (
                    func.max(sa_case(*case_statement_args[0][1], else_=0)).label(
                        "is_in_private_data_collection"
                    )
                    if has_private_data_collections
                    else func.literal(0).label("is_in_private_data_collection")
                ),
            )
            .group_by(
                sa_model.Case.case_date,
                sa_model.Case.id,
            )
            .where(sa_model.Case.case_type_id == case_type_id)
        )
        query1 = apply_case_id_filter(query1)

        # Second query: cases joined with CaseDataCollectionLink and the linked data_collection_ids in the given data collections
        query2 = (
            session.query(
                sa_model.Case.id,
                sa_model.Case.case_date,
                func.min(sa_case(*case_statement_args[1][0], else_=last_index)).label(
                    "data_collection_time_unit_index"
                ),
                (
                    func.max(sa_case(*case_statement_args[1][1], else_=0)).label(
                        "is_in_private_data_collection"
                    )
                    if has_private_data_collections
                    else func.literal(0).label("is_in_private_data_collection")
                ),
            )
            .outerjoin(
                sa_model.CaseDataCollectionLink,
                sa_model.Case.id == sa_model.CaseDataCollectionLink.case_id,
            )
            .group_by(
                sa_model.Case.case_date,
                sa_model.Case.id,
            )
            .where(sa_model.Case.case_type_id == case_type_id)
        )
        query2 = apply_case_id_filter(query2)

        # Collapse both sources per case before truncating and aggregating dates.
        combined_query = union_all(query1, query2).alias(  # type: ignore
            "case_stats_candidates"
        )
        collapsed = (
            session.query(
                combined_query.c[0].label("case_id"),
                combined_query.c[1].label("case_date"),
                func.min(combined_query.c[2]).label("min_index"),
                func.max(combined_query.c[3]).label("is_own"),
            )
            .group_by(combined_query.c[1], combined_query.c[0])
            .subquery()
        )
        dialect_name = session.get_bind().dialect.name
        truncated_date = sa_case(
            *[
                (
                    collapsed.c.min_index == index,
                    truncate_datetime(collapsed.c.case_date, col_type, dialect_name),
                )
                for index, col_type in enumerate(
                    enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
                )
            ],
            else_=None,
        ).label("truncated_date")
        count = cast(Callable[[], Any], getattr(func, "count"))
        stats_query = session.query(
            count().label("n_cases"),  # type: ignore[operator]
            func.coalesce(func.sum(collapsed.c.is_own), 0).label("n_own_cases"),
            func.min(truncated_date).label("first_case_date"),
            func.max(truncated_date).label("last_case_date"),
        ).where(collapsed.c.min_index != last_index)
        if datetime_range_filter is not None:
            date_filter = datetime_range_filter
            range_clauses = []
            if date_filter.lower_bound is not None:
                range_clauses.append(
                    truncated_date > date_filter.lower_bound
                    if date_filter.lower_bound_censor == ComparisonOperator.GT
                    else truncated_date >= date_filter.lower_bound
                )
            if date_filter.upper_bound is not None:
                range_clauses.append(
                    truncated_date < date_filter.upper_bound
                    if date_filter.upper_bound_censor == ComparisonOperator.ST
                    else truncated_date <= date_filter.upper_bound
                )
            range_clause = and_(*range_clauses)
            stats_query = stats_query.where(
                not_(range_clause) if date_filter.invert else range_clause
            )
        stats = stats_query.one()
        case_stats.n_cases = stats.n_cases or 0
        case_stats.n_own_cases = stats.n_own_cases or 0
        case_stats.first_case_date = stats.first_case_date
        case_stats.last_case_date = stats.last_case_date
        return case_stats
