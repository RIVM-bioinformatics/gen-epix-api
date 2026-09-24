"""Define backend-independent persistence operations for Casedb case data."""

import datetime
from abc import abstractmethod
from typing import Callable
from uuid import UUID

from gen_epix.casedb.domain import enum, model
from gen_epix.fastapp import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.datetime_range import DatetimeRangeFilter


class BaseCaseRepository(BaseRepository):
    """Encapsulates case persistence and aggregate statistics reads.

    Concrete dictionary and SQL repositories provide equivalent statistics
    over an existing unit of work. Date mappers normalize case dates to the
    resolutions used when access limits constrain temporal precision.

    Attributes:
        DATE_MAPPERS: Functions that normalize dates by temporal column type.
    """

    @staticmethod
    def _get_date_mappers() -> (
        dict[enum.ColType, Callable[[datetime.datetime], datetime.datetime]]
    ):
        """Build temporal-resolution date normalization functions.

        Returns:
            A mapper for each supported temporal column type.

        Raises:
            AssertionError: If the temporal resolution order contains an
                unsupported column type.
        """
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
        """Read aggregate statistics for a case type within a unit of work.

        Implementations restrict cases by the supplied identifiers and date
        range. When data-collection resolutions are provided, they also apply
        access filtering and normalize dates to the highest permitted
        resolution. The provided unit of work is used but not committed here.

        Args:
            uow: Active persistence context used for the read.
            case_type_id: Case type whose cases are aggregated.
            data_collections_by_time_unit: Accessible data collections grouped
                by permitted temporal resolution, or ``None`` for unrestricted
                collection access.
            private_data_collection_ids: Collections whose cases are counted as
                private.
            case_ids: Case identifiers to include, or ``None`` for all cases of
                the type.
            datetime_range_filter: Optional case-date range restriction.

        Returns:
            Aggregate counts and date bounds for matching cases.

        Raises:
            NotImplementedError: Always, until a concrete repository implements
                the read.
        """
        raise NotImplementedError()
