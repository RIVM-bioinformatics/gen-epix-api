import datetime
from abc import abstractmethod
from typing import Callable
from uuid import UUID

from gen_epix.casedb.domain import enum, model
from gen_epix.fastapp import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.datetime_range import DatetimeRangeFilter


class BaseCaseRepository(BaseRepository):

    @staticmethod
    def _get_date_mappers() -> (
        dict[enum.ColType, Callable[[datetime.datetime], datetime.datetime]]
    ):
        date_mappers: dict[
            enum.ColType, Callable[[datetime.datetime], datetime.datetime]
        ] = {}
        for col_type in enum.ColTypeOrder.TIME_RESOLUTION_DESC.value:
            if col_type == enum.ColType.TIME_DAY:
                date_mappers[col_type] = lambda d: d.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            elif col_type == enum.ColType.TIME_WEEK:
                date_mappers[col_type] = lambda d: (
                    d - datetime.timedelta(days=d.weekday())
                ).replace(hour=0, minute=0, second=0, microsecond=0)
            elif col_type == enum.ColType.TIME_MONTH:
                date_mappers[col_type] = lambda d: d.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
            elif col_type == enum.ColType.TIME_QUARTER:
                date_mappers[col_type] = lambda d: d.replace(
                    month=((d.month - 1) // 3) * 3 + 1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
            elif col_type == enum.ColType.TIME_YEAR:
                date_mappers[col_type] = lambda d: d.replace(
                    month=1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
            else:
                raise AssertionError(f"Unsupported ColType for time unit: {col_type}")
        return date_mappers

    DATE_MAPPERS = _get_date_mappers()

    @abstractmethod
    def retrieve_case_stats(
        self,
        uow: BaseUnitOfWork,
        case_type_id: UUID,
        data_collections_by_time_unit: dict[enum.ColType, set[UUID]] | None = None,
        private_data_collection_ids: set[UUID] | None = None,
        case_ids: set[UUID] | None = None,
        datetime_range_filter: DatetimeRangeFilter | None = None,
    ) -> model.CaseStats:
        raise NotImplementedError()
