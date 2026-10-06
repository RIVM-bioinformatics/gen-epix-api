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

    @staticmethod
    def _get_data_collection_time_unit_index_map(
        data_collections_by_time_unit: dict[enum.ColType, set[UUID]] | None,
    ) -> dict[UUID, int]:
        """Map each allowed data collection to its time-resolution index."""
        if data_collections_by_time_unit is None:
            return {}
        col_type_index_map: dict[enum.ColType, int] = {
            col_type: index
            for index, col_type in enumerate(
                enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
            )
        }
        data_collection_time_unit_index_map: dict[UUID, int] = {}
        for col_type, data_collection_ids in data_collections_by_time_unit.items():
            col_type_index = col_type_index_map[col_type]
            for data_collection_id in data_collection_ids:
                data_collection_time_unit_index_map[data_collection_id] = col_type_index
        return data_collection_time_unit_index_map

    def _get_case_map(
        self, case_type_id: UUID, case_ids: set[UUID] | None
    ) -> dict[UUID, model.Case]:
        """Select cases of the requested type, optionally constrained by ID."""
        case_map: dict[UUID, model.Case] = self.db[model.Case]  # type: ignore[assignment]
        if case_ids is not None:
            return {
                case_id: case
                for case_id, case in case_map.items()
                if case.case_type_id == case_type_id and case_id in case_ids
            }
        return {
            case_id: case
            for case_id, case in case_map.items()
            if case.case_type_id == case_type_id
        }

    def _build_case_stats_rows(
        self,
        case_map: dict[UUID, model.Case],
        data_collection_time_unit_index_map: dict[UUID, int],
        private_data_collection_ids: set[UUID],
        has_abac: bool,
        has_private_data_collections: bool,
    ) -> list[tuple[datetime.datetime, UUID, int, bool]]:
        """Build initial and linked collection date rows for selected cases."""
        # Get case date results based on created_in_data_collection_id
        if has_abac:
            rows: list[tuple[datetime.datetime, UUID, int, bool]] = [
                (
                    case.timed_at,
                    case.id,  # type: ignore[misc]
                    data_collection_time_unit_index_map[
                        case.created_in_data_collection_id
                    ],
                    (
                        case.created_in_data_collection_id
                        in private_data_collection_ids
                        if has_private_data_collections
                        else False
                    ),
                )
                for case in case_map.values()
                if case.created_in_data_collection_id
                in data_collection_time_unit_index_map
            ]
        else:
            rows = [
                (
                    case.timed_at,
                    case.id,
                    0,
                    (
                        case.created_in_data_collection_id
                        in private_data_collection_ids
                        if has_private_data_collections
                        else False
                    ),
                )  # type: ignore[misc]
                for case in case_map.values()
            ]

        # Add case date results based on CaseDataCollectionLink
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
            if not has_abac:
                # No ABAC restrictions, all data collections allowed
                rows.append(
                    (
                        case.timed_at,
                        case_id,
                        0,
                        (
                            case.created_in_data_collection_id
                            in private_data_collection_ids
                            if has_private_data_collections
                            else False
                        ),
                    )
                )
                continue
            if link.data_collection_id not in data_collection_time_unit_index_map:
                continue
            rows.append(
                (
                    case.timed_at,
                    case_id,
                    data_collection_time_unit_index_map[link.data_collection_id],
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
        rows: list[tuple[datetime.datetime, UUID, int, bool]],
        has_abac: bool,
        is_filter_by_datetime: bool,
        datetime_range_filter: DatetimeRangeFilter | None,
    ) -> model.CaseStats:
        """Aggregate sorted date rows into case totals and date bounds."""
        # Process rows in order of (case_id, col_type_index), i.e. highest allowed
        # resolution first per case, to calculate stats.
        date_mappers = [
            self.DATE_MAPPERS[col_type]
            for col_type in enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
        ]
        seen_case_ids: dict[UUID, bool | None] = {}
        for row in sorted(rows, key=lambda item: (item[1], item[2])):
            case_id = row[1]
            if case_id in seen_case_ids:
                # Already processed this case_id for all but n_own_cases
                seen_case_id_value = seen_case_ids[case_id]
                if seen_case_id_value is not None:
                    seen_case_ids[case_id] = seen_case_id_value or row[3]
                else:
                    # Case not to be counted due to datetime filter
                    pass
                continue
            seen_case_ids[case_id] = seen_case_ids.get(case_id) or row[3]
            # Get adjusted timed_at based on col_type_index
            col_type_index = row[2]
            timed_at = date_mappers[col_type_index](row[0]) if has_abac else row[0]
            if is_filter_by_datetime and not datetime_range_filter.match_value(
                timed_at
            ):
                # Skip cases not in the given datetime range after adjusting the case date, if applicable
                # Set to None to skip counting in n_own_cases
                seen_case_ids[case_id] = None
                continue
            # Update case_type_stat
            case_stats.n_cases += 1
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
        # Calculate n_own_cases
        case_stats.n_own_cases = sum(
            1 for is_own_case in seen_case_ids.values() if is_own_case
        )
        return case_stats

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
            self._get_data_collection_time_unit_index_map(data_collections_by_time_unit)
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
            case_stats,
            rows,
            has_abac,
            is_filter_by_datetime,
            datetime_range_filter,
        )
