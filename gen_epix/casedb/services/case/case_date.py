import datetime
from collections.abc import Callable
from uuid import UUID

import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.service.case import BaseCaseService
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.filter.uuid_set import UuidSetFilter


def convert_iso_date_to_datetime(value: str) -> datetime.datetime:
    year, week, day = map(int, value.split("-"))
    return datetime.datetime.fromisocalendar(year, week, day)


def convert_iso_week_to_first_day_datetime(value: str) -> datetime.datetime:
    year, week = map(int, value.split("-W"))
    return datetime.datetime.fromisocalendar(year, week, 1)


def convert_iso_month_to_first_day_datetime(value: str) -> datetime.datetime:
    year, month = map(int, value.split("-"))
    return datetime.datetime(year, month, 1)


def convert_iso_quarter_to_first_day_datetime(value: str) -> datetime.datetime:
    year, quarter = map(int, value.split("-Q"))
    month = (quarter - 1) * 3 + 1
    return datetime.datetime(year, month, 1)


def convert_iso_year_to_first_day_datetime(value: str) -> datetime.datetime:
    year = int(value)
    return datetime.datetime(year, 1, 1)


CONVERT_ISO_DATE_TO_FIRST_DAY_MAP: dict[
    enum.ColType, Callable[[str], datetime.datetime]
] = {
    enum.ColType.TIME_DAY: convert_iso_date_to_datetime,
    enum.ColType.TIME_WEEK: convert_iso_week_to_first_day_datetime,
    enum.ColType.TIME_MONTH: convert_iso_month_to_first_day_datetime,
    enum.ColType.TIME_QUARTER: convert_iso_quarter_to_first_day_datetime,
    enum.ColType.TIME_YEAR: convert_iso_year_to_first_day_datetime,
}


def case_service_get_case_date_case_type_col_mappers(
    self: BaseCaseService, uow: BaseUnitOfWork, user_id: UUID, case_type_id: UUID
) -> dict[UUID, Callable[[str], datetime.datetime]]:
    """
    Retrieve all case type col ids for the given case type that can be used to compute
    case date statistics, along with a callable to convert the string date values to
    full dates, and based on the provided stats_time_case_type_col_id.

    All case type cols returned will have the same (dim, occurrence) as the
    stats_time_case_type_col_id col, will be of a time col_type, and will be ordered by
    descending time resolution. The highest time resolution returned will be that of
    the stats_time_case_type_col_id col.

    The returned dict has the the case type col ids as keys, in order of descending
    time resolution, and as values a callable that converts the string date value to a
    full date. Weeks are converted to the first day of the week, months to the first day
    of the month, quarters to the first day of the first month of the quarter, and
    years to the first day of the year. As such, it is not possible to create a date in
    the future.
    """
    case_type_dims: list[model.CaseTypeDim] = (
        self.repository.crud(  # type:ignore[assignment]
            uow,
            user_id,
            model.CaseTypeDim,
            None,
            None,
            CrudOperation.READ_ALL,
            filter=UuidSetFilter(key="case_type_id", members=frozenset({case_type_id})),
        )
    )
    if not case_type_dims:
        raise ValueError(f"No CaseTypeDims found for case_type_id {case_type_id}")
    case_type_dim: model.CaseTypeDim = case_type_dims[0]

    if case_type_dim.dim is None:
        case_type_dim_dims: list[model.Dim] = (
            self.repository.crud(  # type:ignore[assignment]
                uow,
                user_id,
                model.Dim,
                None,
                [case_type_dim.id],
                CrudOperation.READ_SOME,
            )
        )
        case_type_dim_dim = case_type_dim_dims[0]
    else:
        case_type_dim_dim = case_type_dim.dim

    if case_type_dim_dim.dim_type != enum.DimType.TIME:
        # No time dimension for case type, return empty dict
        return {}

    case_type_cols: list[model.CaseTypeCol] = (
        self.repository.crud(  # type:ignore[assignment]
            uow,
            user_id,
            model.CaseTypeCol,
            None,
            None,
            CrudOperation.READ_ALL,
            filter=UuidSetFilter(
                key="case_type_dim_id",
                members=frozenset({case_type_dim.id}),  # type:ignore[assignment]
            ),
        )
    )
    if not case_type_cols:
        # No case type cols for time dimension, return empty dict
        return {}

    col_ids = {ctc.col_id for ctc in case_type_cols}
    cols: list[model.Col] = self.repository.crud(  # type:ignore
        uow,
        user_id,
        model.Col,
        None,
        list(col_ids),
        CrudOperation.READ_SOME,
    )
    cols_map: dict[UUID, model.Col] = {x.id: x for x in cols if x.id is not None}
    case_type_cols = [
        ctc
        for ctc in case_type_cols
        if cols_map[ctc.col_id].col_type in enum.ColTypeSet.TIME.value
    ]
    if not case_type_cols:
        # No time case type cols for time dimension, return empty dict
        return {}

    # Order case type cols by descending time resolution
    case_type_cols.sort(
        key=lambda x: enum.ColTypeOrder.TIME_RESOLUTION_DESC.value[
            cols_map[x.col_id].col_type
        ]
    )

    return case_service_get_case_date_case_type_col_mappers_from_cols(
        case_type_cols, cols_map
    )


def case_service_get_case_date_case_type_col_mappers_from_cols(
    case_type_cols: list[model.CaseTypeCol] | None, cols_map: dict[UUID, model.Col]
) -> dict[UUID, Callable[[str], datetime.datetime]]:
    if case_type_cols is None:
        return {}
    retval: dict[UUID, Callable[[str], datetime.datetime]] = {  # type: ignore[assignment]
        x.id: CONVERT_ISO_DATE_TO_FIRST_DAY_MAP[cols_map[x.col_id].col_type]
        for x in case_type_cols
    }
    return retval


def case_service_calculate_case_date(
    cases: list[model.Case],
    case_date_case_type_col_mappers: dict[UUID, Callable[[str], datetime.datetime]],
) -> None:
    """
    Calculate and set the case date for each case in the provided list of cases,
    using the provided mapping of case type col ids to callables that convert string
    date values to full dates. The first mapping found, is used. The
    time_case_type_col_map is expected to be ordered by descending time resolution.
    The cases are expected to have any time case type cols removed that should not
    be taken into account for calculating the case date.
    """
    if not case_date_case_type_col_mappers:
        return

    for case in cases:
        for case_type_col_id, mapper in case_date_case_type_col_mappers.items():
            iso_datetime_value: str | None = case.content.get(case_type_col_id)
            if iso_datetime_value is None:
                continue
            case.case_date = mapper(iso_datetime_value)
