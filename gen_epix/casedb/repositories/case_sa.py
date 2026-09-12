"""Provide SQLAlchemy-backed persistence for casedb case data."""

from uuid import UUID

from sqlalchemy import case as sa_case
from sqlalchemy import func, union_all

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
        is_filter_by_datetime = datetime_range_filter is not None
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
        query1 = (
            session.query(
                sa_model.Case.id,
                sa_model.Case.timed_at,
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
                sa_model.Case.timed_at,
                sa_model.Case.id,
            )
            .where(sa_model.Case.case_type_id == case_type_id)
        )

        # Second query: cases joined with CaseDataCollectionLink and the linked data_collection_ids in the given data collections
        query2 = (
            session.query(
                sa_model.Case.id,
                sa_model.Case.timed_at,
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
                sa_model.Case.timed_at,
                sa_model.Case.id,
            )
            .where(sa_model.Case.case_type_id == case_type_id)
        )

        # Combine both queries and group by case date and ID to get minimum time unit index
        combined_query = union_all(query1, query2).alias()
        query3 = (
            session.query(
                combined_query.c[0],  # case_id
                combined_query.c[1],  # timed_at
                func.min(combined_query.c[2]).label("data_collection_time_unit_index"),
                func.max(combined_query.c[3]).label("is_in_private_data_collection"),
            )
            .group_by(
                combined_query.c[1],
                combined_query.c[0],
            )
            .order_by(combined_query.c[1].desc())
        )

        # Retrieve data and adjust case dates according to resolution
        date_mappers = [
            self.DATE_MAPPERS[x] for x in enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
        ]
        for row in query3.all():
            col_type_index = row[2]
            if col_type_index == last_index:
                # No relevant data collection found, skip
                continue
            case_id = row[0]
            if is_filter_by_case_ids and case_id not in case_ids:
                # Skip case IDs not in the given set, if applicable
                continue
            # @ABAC: Adjust case date
            timed_at = row[1]
            timed_at = date_mappers[col_type_index](timed_at)
            if is_filter_by_datetime and not datetime_range_filter.match_value(
                timed_at
            ):
                # Skip cases not in the given datetime range after adjusting the case date, if applicable
                continue
            # Update case_type_stat
            case_stats.n_cases += 1
            case_stats.n_own_cases += row[3]
            case_stats.first_case_date = (
                timed_at
                if not case_stats.first_case_date
                else min(case_stats.first_case_date, timed_at)
            )
            case_stats.last_case_date = (
                timed_at
                if not case_stats.last_case_date
                else max(case_stats.last_case_date, timed_at)
            )
        return case_stats
