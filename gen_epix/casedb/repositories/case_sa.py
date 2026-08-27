"""SQLAlchemy-based repository implementation for case data persistence.

Provides case statistics retrieval with support for access-based filtering,
data collection visibility controls, and temporal resolution handling.
"""

from uuid import UUID

from sqlalchemy import case as sa_case
from sqlalchemy import func, literal

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.repository import BaseCaseRepository
from gen_epix.casedb.repositories import sa_model as sa_model
from gen_epix.fastapp.repositories import SARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.datetime_range import DatetimeRangeFilter


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
        """Return statistics for cases of one type after applying access filters.

        Applies attribute-based access controls and computes case statistics
        including counts and date ranges. Dates are reduced to their allowed
        temporal resolution before filtering and range computation.

        Args:
            uow: Unit of work providing database session access.
            case_type_id: UUID of the case type to filter on.
            data_collections_by_time_unit: Maps each allowed data collection to
                its accessible temporal resolution. When supplied, the most
                precise accessible resolution is used for each case. If None,
                all collections are considered accessible.
            private_data_collection_ids: Set of collection IDs whose cases
                contribute to the ``n_own_cases`` count. If None, defaults to
                an empty set.
            case_ids: Optional set of case IDs to filter on. If None, all cases
                of the given type are considered.
            datetime_range_filter: Optional temporal range to filter cases after
                date resolution reduction. If None, no temporal filtering is
                applied.

        Returns:
            CaseStats containing:
                - n_cases: Number of visible cases after all filters.
                - n_own_cases: Count of visible cases from private collections.
                - first_case_date: Earliest visible case date (reduced to
                  allowed resolution), or None if no cases match.
                - last_case_date: Latest visible case date (reduced to allowed
                  resolution), or None if no cases match.
        """

        # Record which optional filters were provided before normalizing None values.
        case_stats = model.CaseStats(case_type_id=case_type_id)
        abac_filter_provided = data_collections_by_time_unit is not None
        case_id_filter_provided = case_ids is not None
        private_collection_filter_provided = bool(private_data_collection_ids)
        datetime_filter_provided = datetime_range_filter is not None
        if data_collections_by_time_unit is None:
            data_collections_by_time_unit = {}
        if private_data_collection_ids is None:
            private_data_collection_ids = set()
        if case_ids is None:
            case_ids = set()

        # @ABAC: no access at all
        if abac_filter_provided and not data_collections_by_time_unit:
            # An empty allowed-collection map means that no cases are accessible.
            return case_stats

        # Build CASE arguments for the best allowed date resolution and private status.
        inaccessible_resolution_index = len(
            enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
        )
        collection_id_fields = [
            sa_model.Case.created_in_data_collection_id,
            sa_model.CaseDataCollectionLink.data_collection_id,
        ]
        case_attribute_arguments: list[list[list[tuple]]] = [[[], []], [[], []]]
        # When an ABAC filter is provided, NULL linked collections should be marked as
        # inaccessible. When no ABAC filter is provided, NULL linked collections are
        # simply ignored (the created_in collection determines access).
        if abac_filter_provided:
            case_attribute_arguments[1][0].append(
                (collection_id_fields[1].is_(None), inaccessible_resolution_index)
            )
        case_attribute_arguments[1][1].append((collection_id_fields[1].is_(None), 0))
        # Add a resolution condition for every allowed collection and time unit.
        for i, col_type in enumerate(enum.ColTypeOrder.TIME_RESOLUTION_DESC.value):
            if col_type not in data_collections_by_time_unit:
                continue
            allowed_data_collection_ids = data_collections_by_time_unit[col_type]
            for j, collection_id_field in enumerate(collection_id_fields):
                case_attribute_arguments[j][0].append(
                    (collection_id_field.in_(allowed_data_collection_ids), i)
                )
        # Mark a row private when either collection field belongs to a private collection.
        for j, collection_id_field in enumerate(collection_id_fields):
            case_attribute_arguments[j][1].append(
                (collection_id_field.in_(private_data_collection_ids), 1)
            )

        # Single combined query: check both created_in and linked collections in one pass.
        # This eliminates the UNION ALL and nested grouping.
        assert isinstance(uow, SAUnitOfWork)
        session = uow.session

        # Build resolution CASE expression, or use a literal when no ABAC filter is provided.
        # When no ABAC filter is provided, all collections are accessible at the finest
        # resolution (0). A CASE with no conditions would be syntactically invalid, so we
        # use a literal instead.
        if not case_attribute_arguments[0][0] and not case_attribute_arguments[1][0]:
            # No ABAC filter, no conditions - use literal finest resolution for all cases
            combined_resolution_case = literal(0)
        else:
            # ABAC filter provided or conditions exist - use CASE expression
            combined_resolution_case = sa_case(  # type: ignore[assignment]
                *case_attribute_arguments[0][0],  # created_in_data_collection_id checks
                *case_attribute_arguments[1][0],  # linked data_collection_id checks
                else_=inaccessible_resolution_index if abac_filter_provided else 0,
            )

        # Build private CASE expression (same logic for consistency)
        if not case_attribute_arguments[0][1] and not case_attribute_arguments[1][1]:
            # No private checks - use literal 0 (not in private collection)
            combined_private_case = literal(0)
        else:
            combined_private_case = sa_case(  # type: ignore[assignment]
                *case_attribute_arguments[0][1],  # created_in private checks
                *case_attribute_arguments[1][1],  # linked private checks
                else_=0,
            )

        # Single query with LEFT OUTER JOIN to both collection sources
        query = (
            session.query(
                sa_model.Case.id,
                sa_model.Case.case_date,
                func.min(combined_resolution_case).label(
                    "data_collection_time_unit_index"
                ),
                (
                    func.max(combined_private_case).label(
                        "is_in_private_data_collection"
                    )
                    if private_collection_filter_provided
                    else literal(0).label("is_in_private_data_collection")
                ),
            )
            .outerjoin(
                sa_model.CaseDataCollectionLink,
                sa_model.Case.id == sa_model.CaseDataCollectionLink.case_id,
            )
            .where(sa_model.Case.case_type_id == case_type_id)
            .group_by(
                sa_model.Case.case_date,
                sa_model.Case.id,
            )
            .order_by(sa_model.Case.case_date.desc())
        )

        if case_id_filter_provided:
            query = query.where(sa_model.Case.id.in_(case_ids))

        # Retrieve rows and reduce each accessible case date to its allowed resolution.
        reduce_case_date_by_resolution = [
            self.DATE_MAPPERS[x] for x in enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
        ]
        for row in query.all():
            resolution_index = row[2]
            if resolution_index == inaccessible_resolution_index:
                # The case has no collection that is accessible under the filter.
                continue
            # @ABAC: reduce the date to the resolution the user may access.
            original_case_date = row[1]
            reduced_case_date = reduce_case_date_by_resolution[resolution_index](
                original_case_date
            )
            if datetime_filter_provided:
                assert datetime_range_filter is not None
                if not datetime_range_filter.match_value(reduced_case_date):
                    # The datetime filter is applied to the reduced date, not the original.
                    continue
            # Update counts and the visible date range.
            case_stats.n_cases += 1
            case_stats.n_own_cases += row[3]
            case_stats.first_case_date = (
                reduced_case_date
                if not case_stats.first_case_date
                else min(case_stats.first_case_date, reduced_case_date)
            )
            case_stats.last_case_date = (
                reduced_case_date
                if not case_stats.last_case_date
                else max(case_stats.last_case_date, reduced_case_date)
            )
        return case_stats
