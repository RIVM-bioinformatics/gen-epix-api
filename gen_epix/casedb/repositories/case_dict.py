import datetime
from uuid import UUID

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.repository import BaseCaseRepository
from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class CaseDictRepository(DictRepository, BaseCaseRepository):
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
        # # Retrieve first case_date, last case_date and number of cases from all cases without filtering by data collection or adjusting case_date
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
        #         first_case_date = case.case_date
        #     elif case.case_date < first_case_date:
        #         first_case_date = case.case_date
        #     if last_case_date is None:
        #         last_case_date = case.case_date
        #     elif case.case_date > last_case_date:
        #         last_case_date = case.case_date
        # case_stats.n_cases = n_cases
        # case_stats.first_case_date = first_case_date
        # case_stats.last_case_date = last_case_date
        # return case_stats

        # @ABAC: expected case with data_collections_by_time_unit given

        # Map data_collection_id to time unit
        col_type_index_map: dict[enum.ColType, int] = {
            x: i for i, x in enumerate(enum.ColTypeOrder.TIME_RESOLUTION_DESC.value)
        }
        data_collection_time_unit_index_map: dict[UUID, int] = {}
        if has_abac:
            for col_type, data_collection_ids in data_collections_by_time_unit.items():
                col_type_index = col_type_index_map[col_type]
                for data_collection_id in data_collection_ids:
                    data_collection_time_unit_index_map[data_collection_id] = (
                        col_type_index
                    )

        # Get filtered cases
        case_map: dict[UUID, model.Case] = self.db[model.Case]  # type: ignore[assignment]
        if is_filter_by_case_ids:
            # Filter by case_type_id and case_ids
            case_map = {
                x: y
                for x, y in case_map.items()
                if y.case_type_id == case_type_id and x in case_ids
            }
        else:
            # Filter by case_type_id only
            case_map = {
                x: y for x, y in case_map.items() if y.case_type_id == case_type_id
            }

        # Get case date results based on created_in_data_collection_id
        if has_abac:
            rows: list[tuple[datetime.datetime, UUID, int, bool]] = [
                (
                    x.case_date,
                    x.id,  # type:ignore[misc]
                    data_collection_time_unit_index_map[
                        x.created_in_data_collection_id
                    ],
                    (
                        (x.created_in_data_collection_id in private_data_collection_ids)
                        if has_private_data_collections
                        else False
                    ),
                )
                for x in case_map.values()
                if x.created_in_data_collection_id
                in data_collection_time_unit_index_map
            ]
        else:
            rows = [
                (
                    x.case_date,
                    x.id,
                    0,
                    (
                        (x.created_in_data_collection_id in private_data_collection_ids)
                        if has_private_data_collections
                        else False
                    ),
                )  # type:ignore[misc]
                for x in case_map.values()
            ]

        # Add case date results based on CaseDataCollectionLink
        case_date_collection_link_map: dict[UUID, model.CaseDataCollectionLink] = self.db[model.CaseDataCollectionLink]  # type: ignore[assignment]
        for x in case_date_collection_link_map.values():
            case_id = x.case_id
            if case_id not in case_map:
                continue
            case = case_map[case_id]
            if not has_abac:
                # No ABAC restrictions, all data collections allowed
                rows.append(
                    (
                        case.case_date,
                        case_id,
                        0,
                        (
                            (
                                case.created_in_data_collection_id
                                in private_data_collection_ids
                            )
                            if has_private_data_collections
                            else False
                        ),
                    )
                )
                continue
            if x.data_collection_id not in data_collection_time_unit_index_map:
                continue
            rows.append(
                (
                    case.case_date,
                    case_id,
                    data_collection_time_unit_index_map[x.data_collection_id],
                    (
                        (x.data_collection_id in private_data_collection_ids)
                        if has_private_data_collections
                        else False
                    ),
                )
            )

        # Process rows in order of (case_id, col_type_index), i.e. highest allowed resolution first per case, to calculate stats
        date_mappers = [
            self.DATE_MAPPERS[x] for x in enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
        ]
        seen_case_ids: dict[UUID, bool | None] = {}
        for row in sorted(rows, key=lambda x: (x[1], x[2])):
            case_id = row[1]
            if case_id in seen_case_ids:
                # Already processed this case_id for all but n_own_cases
                if seen_case_ids[case_id] is not None:
                    seen_case_ids[case_id] = row[3]
                else:
                    # Case not to be counted due to datetime filter
                    pass
                continue
            seen_case_ids[case_id] = row[3]
            # Get adjusted case_date based on col_type_index
            col_type_index = row[2]
            if has_abac:
                case_date = date_mappers[col_type_index](row[0])
            else:
                case_date = row[0]
            if is_filter_by_datetime and not datetime_range_filter.match_value(
                case_date
            ):
                # Skip cases not in the given datetime range after adjusting the case date, if applicable
                # Set to None to skip counting in n_own_cases
                seen_case_ids[case_id] = None
                continue
            # Update case_type_stat
            case_stats.n_cases += 1
            if (
                case_stats.first_case_date is None
                or case_date < case_stats.first_case_date
            ):
                case_stats.first_case_date = case_date
            if (
                case_stats.last_case_date is None
                or case_date > case_stats.last_case_date
            ):
                case_stats.last_case_date = case_date
        # Calculate n_own_cases
        case_stats.n_own_cases = sum(1 for x in seen_case_ids.values() if x)
        return case_stats
