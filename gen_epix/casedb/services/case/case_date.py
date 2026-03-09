import datetime
from collections.abc import Callable
from uuid import UUID

import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.service.case import BaseCaseService
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_boolean import EqualsBooleanFilter
from gen_epix.filter.equals_uuid import EqualsUuidFilter


def convert_iso_date_to_datetime(value: str) -> datetime.datetime:
    year, month, day = map(int, value.split("-"))
    return datetime.datetime(year, month, day)


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


def case_service_get_case_date_col_mappers(
    self: BaseCaseService, uow: BaseUnitOfWork, user_id: UUID, case_type_id: UUID
) -> dict[UUID, Callable[[str], datetime.datetime]]:
    """
    Retrieve all Col IDs for the given CaseType that can be used to compute
    case date statistics, along with a callable to convert the string date values to
    full dates, and based on the provided stats_time_col_id.

    All Cols returned will have the same (ref_dim, occurrence) as the
    stats_time_col_id ref_col, will be of a time col_type, and will be ordered by
    descending time resolution. The highest time resolution returned will be that of
    the stats_time_col_id ref_col.

    The returned dict has the the Col IDs as keys, in order of descending
    time resolution, and as values a callable that converts the string date value to a
    full date. Weeks are converted to the first day of the week, months to the first day
    of the month, quarters to the first day of the first month of the quarter, and
    years to the first day of the year. As such, it is not possible to create a date in
    the future.
    """
    dims: list[model.Dim] = self.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.Dim,
        None,
        None,
        CrudOperation.READ_ALL,
        filter=CompositeFilter(
            operator=LogicalOperator.AND,
            filters=[
                EqualsUuidFilter(key="case_type_id", value=case_type_id),
                EqualsBooleanFilter(key="is_case_date_dim", value=True),
            ],
        ),
    )
    if not dims:
        # No Dims for case date, return empty dict
        return {}
    dim: model.Dim = dims[0]

    ref_dim: model.RefDim = self.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.RefDim,
        None,
        dim.ref_dim_id,
        CrudOperation.READ_ONE,
    )
    if ref_dim.dim_type != enum.DimType.TIME:
        raise ValueError(
            f"Dim {dim.id} is not of time DimType, but of {ref_dim.dim_type}"
        )

    cols: list[model.Col] = self.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.Col,
        None,
        None,
        CrudOperation.READ_ALL,
        filter=EqualsUuidFilter(key="dim_id", value=dim.id),  # type: ignore[arg-type]
    )
    if not cols:
        # No Cols for time dimension, return empty dict
        return {}

    # Verify Cols are of time col_type
    ref_col_ids = list({x.ref_col_id for x in cols})
    ref_cols: list[model.RefCol] = self.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.RefCol,
        None,
        ref_col_ids,
        CrudOperation.READ_SOME,
    )
    ref_cols_map: dict[UUID, model.RefCol] = {
        x.id: x for x in ref_cols if x.id is not None
    }
    if not all(
        ref_cols_map[x.ref_col_id].col_type in enum.ColTypeSet.TIME.value for x in cols
    ):
        raise ValueError("Not all Cols for case_date_dim are of time col_type")

    # Order Cols by descending time resolution
    cols.sort(
        key=lambda x: enum.ColTypeOrder.TIME_RESOLUTION_DESC.value[
            ref_cols_map[x.ref_col_id].col_type
        ]
    )

    return case_service_get_case_date_col_mappers_from_cols(cols, ref_cols_map)


def case_service_get_case_date_col_mappers_from_cols(
    cols: list[model.Col] | None, cols_map: dict[UUID, model.RefCol]
) -> dict[UUID, Callable[[str], datetime.datetime]]:
    if cols is None:
        return {}
    retval: dict[UUID, Callable[[str], datetime.datetime]] = {  # type: ignore[assignment]
        x.id: CONVERT_ISO_DATE_TO_FIRST_DAY_MAP[cols_map[x.ref_col_id].col_type]
        for x in cols
    }
    return retval


def case_service_calculate_case_date(
    cases: list[model.Case],
    case_date_col_mappers: dict[UUID, Callable[[str], datetime.datetime]],
) -> None:
    """
    Calculate and set the case date for each case in the provided list of cases,
    using the provided mapping of col_ids to callables that convert string
    date values to full dates. The first mapping found, is used. The
    time_col_map is expected to be ordered by descending time resolution.
    The cases are expected to have any case_date_col_ids removed that should not
    be taken into account for calculating the case date.
    """
    if not case_date_col_mappers:
        return

    for case in cases:
        for col_id, mapper in case_date_col_mappers.items():
            iso_datetime_value: str | None = case.content.get(col_id)
            if iso_datetime_value is None:
                continue
            case.case_date = mapper(iso_datetime_value)
