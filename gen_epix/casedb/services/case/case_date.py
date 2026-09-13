"""Derive normalized case dates from configured temporal case columns.

The conversion helpers normalize supported ISO period values to their first
calendar day. The service helpers discover eligible columns in repository
metadata and apply the highest-resolution populated value to each case.
"""

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
    """Convert an ISO calendar date to a midnight datetime.

    Args:
        value: Calendar date in ``YYYY-MM-DD`` form.

    Returns:
        The corresponding naive datetime at midnight.
    """
    year, month, day = map(int, value.split("-"))
    return datetime.datetime(year, month, day)


def convert_iso_week_to_first_day_datetime(value: str) -> datetime.datetime:
    """Convert an ISO week to a datetime for its Monday.

    Args:
        value: ISO week in ``YYYY-Www`` form.

    Returns:
        The corresponding Monday as a naive datetime at midnight.
    """
    year, week = map(int, value.split("-W"))
    return datetime.datetime.fromisocalendar(year, week, 1)


def convert_iso_month_to_first_day_datetime(value: str) -> datetime.datetime:
    """Convert an ISO month to a datetime for its first day.

    Args:
        value: Calendar month in ``YYYY-MM`` form.

    Returns:
        The month's first day as a naive datetime at midnight.
    """
    year, month = map(int, value.split("-"))
    return datetime.datetime(year, month, 1)


def convert_iso_quarter_to_first_day_datetime(value: str) -> datetime.datetime:
    """Convert an ISO quarter to a datetime for its first day.

    Args:
        value: Calendar quarter in ``YYYY-Qq`` form.

    Returns:
        The quarter's first day as a naive datetime at midnight.
    """
    year, quarter = map(int, value.split("-Q"))
    month = (quarter - 1) * 3 + 1
    return datetime.datetime(year, month, 1)


def convert_iso_year_to_first_day_datetime(value: str) -> datetime.datetime:
    """Convert an ISO year to a datetime for its first day.

    Args:
        value: Four-digit calendar year.

    Returns:
        January 1 of the year as a naive datetime at midnight.
    """
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
    """Retrieve ordered converters for a case type's case-date columns.

    The repository metadata must identify at most one case-date dimension. Its
    columns are ordered from highest to lowest time resolution. Each returned
    converter normalizes a period to its first day.

    Args:
        self: Case service whose repository supplies dimension metadata.
        uow: Unit of work used for repository reads.
        user_id: User on whose behalf metadata is read.
        case_type_id: Case type whose case-date columns are requested.

    Returns:
        A mapping from column IDs to converters in descending resolution order,
        or an empty mapping when no case-date dimension or columns exist.

    Raises:
        ValueError: If the case-date dimension is not temporal or one of its
            columns does not have a temporal column type.
    """
    dims: list[model.Dim] = self.repository.crud(
        uow,
        user_id,
        model.Dim,
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

    ref_dim: model.RefDim = self.repository.crud(
        uow,
        user_id,
        model.RefDim,
        CrudOperation.READ_ONE,
        obj_ids=dim.ref_dim_id,
    )
    if ref_dim.dim_type != enum.DimType.TIME:
        raise ValueError(
            f"Dim {dim.id} is not of time DimType, but of {ref_dim.dim_type}"
        )

    cols: list[model.Col] = self.repository.crud(
        uow,
        user_id,
        model.Col,
        CrudOperation.READ_ALL,
        filter=EqualsUuidFilter(key="dim_id", value=dim.id),  # type: ignore[arg-type]
    )
    if not cols:
        # No Cols for time dimension, return empty dict
        return {}

    # Verify Cols are of time col_type
    ref_col_ids = list({x.ref_col_id for x in cols})
    ref_cols: list[model.RefCol] = self.repository.crud(
        uow,
        user_id,
        model.RefCol,
        CrudOperation.READ_SOME,
        obj_ids=ref_col_ids,
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
    """Create ordered case-date converters from columns and reference metadata.

    Args:
        cols: Columns already ordered by descending temporal resolution.
        cols_map: Reference-column metadata keyed by identifier.

    Returns:
        A mapping from each column ID to its temporal value converter. ``None``
        produces an empty mapping.
    """
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
    """Set each case date from its highest-resolution populated time column.

    The mapping order determines precedence. Cases are mutated in place, and a
    case without a populated mapped column retains its existing date. Callers
    must remove ineligible case-date values before invoking this function.

    Args:
        cases: Cases whose ``timed_at`` values may be updated.
        case_date_col_mappers: Ordered mapping of column IDs to ISO period
            converters, from highest to lowest temporal resolution.
    """
    if not case_date_col_mappers:
        return

    for case in cases:
        for col_id, mapper in case_date_col_mappers.items():
            iso_datetime_value: str | None = case.content.get(col_id)
            if iso_datetime_value is None:
                continue
            case.timed_at = mapper(iso_datetime_value)
            break  # cols are ordered by descending resolution; stop at the first (highest-resolution) non-None value
