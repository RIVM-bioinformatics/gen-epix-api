"""Provide dictionary-backed persistence for casedb case data."""

import datetime
from uuid import UUID

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.repository import BaseCaseRepository
from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.datetime_range import DatetimeRangeFilter


class CaseDictRepository(DictRepository, BaseCaseRepository):
    """Encapsulates dictionary-backed persistence for casedb case data."""

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

        # No ABAC restrictions
        # # Retrieve first timed_at, last timed_at and number of cases from all cases without filtering by data collection or adjusting timed_at
        # if not self.db[model.Case]:
        #     return case_stats
        # n_cases = 0
        # first_case_date = None
        # last_case_date = None
        # for case in self.db[model.Case].values():
        #     assert isinstance(case, model.Case)
        #     if case.case_type_id != case_type_id:
        #         continue
        #     n_cases += 1
        #     # Update first and last case dates
        #     if first_case_date is None:
        #         first_case_date = case.timed_at
        #     elif case.timed_at < first_case_date:
        #         first_case_date = case.timed_at
        #     if last_case_date is None:
        #         last_case_date = case.timed_at
        #     elif case.timed_at > last_case_date:
        #         last_case_date = case.timed_at
        # case_stats.n_cases = n_cases
        # case_stats.first_case_date = first_case_date
        # case_stats.last_case_date = last_case_date
        # return case_stats

        # @ABAC: expected case with data_collections_by_time_unit given

        data_collection_time_unit_index_map = (
            self._get_data_collection_time_unit_index_map(
                data_collections_by_time_unit if has_abac else None
            )
        )
        case_map = self._get_case_map(
            case_type_id, case_ids if is_filter_by_case_ids else None
        )
        rows = self._build_case_stats_rows(
            case_map,
            data_collection_time_unit_index_map,
            private_data_collection_ids,
            has_abac,
            has_private_data_collections,
        )
        return self._aggregate_case_stats_rows(
            case_stats, rows, has_abac, datetime_range_filter
        )

    @staticmethod
    def _get_data_collection_time_unit_index_map(
        data_collections_by_time_unit: dict[enum.ColType, set[UUID]] | None,
    ) -> dict[UUID, int]:
        """Map each allowed data collection to its time-resolution index."""
        if data_collections_by_time_unit is None:
            return {}
        col_type_index_map = {
            col_type: index
            for index, col_type in enumerate(
                enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
            )
        }
        return {
            data_collection_id: col_type_index_map[col_type]
            for col_type, data_collection_ids in data_collections_by_time_unit.items()
            for data_collection_id in data_collection_ids
        }

    def _get_case_map(
        self, case_type_id: UUID, case_ids: set[UUID] | None
    ) -> dict[UUID, model.Case]:
        """Select cases of the requested type, optionally constrained by ID."""
        case_map: dict[UUID, model.Case] = self.db[model.Case]  # type: ignore[assignment]
        return {
            case_id: case
            for case_id, case in case_map.items()
            if case.case_type_id == case_type_id
            and (case_ids is None or case_id in case_ids)
        }

    def _build_case_stats_rows(
        self,
        case_map: dict[UUID, model.Case],
        data_collection_time_unit_index_map: dict[UUID, int],
        private_data_collection_ids: set[UUID],
        has_abac: bool,
        has_private_data_collections: bool,
    ) -> list[tuple[datetime.datetime, UUID, int, int, bool]]:
        """Build initial and linked collection date rows for selected cases."""
        rows: list[tuple[datetime.datetime, UUID, int, int, bool]] = []
        for case_id, case in case_map.items():
            created_data_collection_id = case.created_in_data_collection_id
            if (
                not has_abac
                or created_data_collection_id in data_collection_time_unit_index_map
            ):
                rows.append(
                    (
                        case.timed_at,
                        case_id,
                        case.count,
                        data_collection_time_unit_index_map.get(
                            created_data_collection_id, 0
                        ),
                        (
                            created_data_collection_id in private_data_collection_ids
                            if has_private_data_collections
                            else False
                        ),
                    )
                )

        case_date_collection_link_map: dict[
            UUID, model.CaseDataCollectionLink
        ] = self.db[
            model.CaseDataCollectionLink
        ]  # type: ignore[assignment]
        for link in case_date_collection_link_map.values():
            case_id = link.case_id
            if case_id not in case_map:
                continue
            case = case_map[case_id]
            if (
                has_abac
                and link.data_collection_id not in data_collection_time_unit_index_map
            ):
                continue
            rows.append(
                (
                    case.timed_at,
                    case_id,
                    case.count,
                    data_collection_time_unit_index_map.get(link.data_collection_id, 0),
                    (
                        link.data_collection_id in private_data_collection_ids
                        if has_private_data_collections
                        else False
                    ),
                )
            )
        return rows

    def _aggregate_case_stats_rows(
        self,
        case_stats: model.CaseStats,
        rows: list[tuple[datetime.datetime, UUID, int, int, bool]],
        has_abac: bool,
        datetime_range_filter: DatetimeRangeFilter | None,
    ) -> model.CaseStats:
        """Aggregate sorted date rows into case totals and date bounds."""
        date_mappers = [
            self.DATE_MAPPERS[col_type]
            for col_type in enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
        ]
        own_case_counts: dict[UUID, int | None] = {}
        datetime_matcher = (
            datetime_range_filter.match_value
            if datetime_range_filter is not None
            else None
        )
        for row in sorted(rows, key=lambda item: (item[1], item[3])):
            timed_at, case_id, count, col_type_index, is_private = row
            if case_id in own_case_counts:
                if own_case_counts[case_id] is not None and is_private:
                    own_case_counts[case_id] = count
                continue
            own_case_counts[case_id] = count if is_private else 0
            if has_abac:
                timed_at = date_mappers[col_type_index](timed_at)
            if datetime_matcher is not None and not datetime_matcher(timed_at):
                own_case_counts[case_id] = None
                continue
            case_stats.n_cases += count
            if count == 0:
                continue
            if (
                case_stats.first_case_date is None
                or timed_at < case_stats.first_case_date
            ):
                case_stats.first_case_date = timed_at
            if (
                case_stats.last_case_date is None
                or timed_at > case_stats.last_case_date
            ):
                case_stats.last_case_date = timed_at
        case_stats.n_own_cases = sum(
            count for count in own_case_counts.values() if count
        )
        return case_stats
