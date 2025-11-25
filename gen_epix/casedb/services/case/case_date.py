import datetime
from collections.abc import Callable
from typing import Any
from uuid import UUID

import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.service.case import BaseCaseService
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_get_case_date(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    user: model.User,
    case_ids: list[UUID],
    case_type_col_ids: list[UUID],
) -> datetime.date | dict[UUID | None, datetime.date | None] | None:
    if not case_type_col_ids:
        return None

    cases: list[model.Case] = self.repository.crud(  # type:ignore[assignment]
        uow,
        user.id,
        model.Case,
        None,
        case_ids,
        CrudOperation.READ_SOME,
    )
    case_type_cols: list[model.CaseTypeCol] = (
        self.repository.crud(  # type:ignore[assignment]
            uow,
            user.id,
            model.CaseTypeCol,
            None,
            case_type_col_ids,
            CrudOperation.READ_SOME,
        )
    )
    result: dict[UUID | None, datetime.date | None] = {}
    for case in cases:
        for case_type_col in case_type_cols:
            date_value = case.content.get(case_type_col.id)
            if case_type_col.col:
                full_date = _convert_to_full_date(
                    date_value, case_type_col.col.col_type
                )
                if full_date is not None:
                    today = datetime.date.today()
                    result[case.id] = today if full_date > today else full_date
                    break
        else:
            result[case.id] = None
    return result


def case_service_get_case_date_case_type_col_ids(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    user: model.User,
    case_type_id: UUID,
    stats_time_case_type_col_id: UUID,
) -> list[tuple[UUID, Callable]]:

    case_type_cols: list[model.CaseTypeCol] = (
        self.repository.crud(  # type:ignore[assignment]
            uow,
            user.id,
            model.CaseTypeCol,
            None,
            None,
            CrudOperation.READ_ALL,
            filter=UuidSetFilter(key="case_type_id", members=frozenset({case_type_id})),
        )
    )
    # 1. retrieve cols for case type cols
    cols: list[model.Col] = self.repository.crud(  # type:ignore[assignment]
        uow,
        user.id,
        model.Col,
        None,
        list(set(x.col_id for x in case_type_cols)),
        CrudOperation.READ_SOME,
    )
    # 2. retrieve dims for cols
    dims: list[model.Dim] = self.repository.crud(  # type:ignore[assignment]
        uow,
        user.id,
        model.Dim,
        None,
        list(set(x.dim_id for x in cols)),
        CrudOperation.READ_SOME,
    )
    # 3. keep only case type cols with the same (dim, occurrence) as stats_time_case_type_col_id col
    # 4. order by time granularity
    # 5. return list of case type col ids and map functions

    # Retrieve the main case type col to get (dim, occurrence)
    main_case_type_col = next(
        (x for x in case_type_cols if x.id == stats_time_case_type_col_id),
        None,
    )
    if not main_case_type_col or not main_case_type_col.col:
        return []
    dim_id = main_case_type_col.col.dim_id
    occurrence = main_case_type_col.occurrence

    # Filter case type cols with same (dim, occurrence) and time col_type
    time_order = [
        enum.ColType.TIME_DAY,
        enum.ColType.TIME_WEEK,
        enum.ColType.TIME_MONTH,
        enum.ColType.TIME_QUARTER,
        enum.ColType.TIME_YEAR,
    ]
    filtered_case_type_cols = [
        x
        for x in case_type_cols
        if x.col
        and x.col.dim_id == dim_id
        and x.occurrence == occurrence
        and x.col.col_type in time_order
    ]
    # Order by time granularity (from finest to coarsest)
    filtered_case_type_cols.sort(key=lambda x: time_order.index(x.col.col_type))

    # Return list of (case_type_col_id, identity_map_function)
    return [(x.id, lambda x: x) for x in filtered_case_type_cols if x.id is not None]


def _convert_to_full_date(
    date_value: Any, col_type: enum.ColType
) -> datetime.date | None:

    try:
        if date_value is None:
            return None
        if col_type == enum.ColType.TIME_DAY:
            if isinstance(date_value, datetime.date):
                return date_value
            return datetime.date.fromisoformat(str(date_value))
        if col_type == enum.ColType.TIME_WEEK:
            year, week = map(int, str(date_value).split("-W"))
            return datetime.date.fromisocalendar(year, week, 1)
        if col_type == enum.ColType.TIME_MONTH:
            year, month = map(int, str(date_value).split("-"))
            return datetime.date(year, month, 1)
        if col_type == enum.ColType.TIME_QUARTER:
            year_str, quarter_str = str(date_value).split("-Q")
            year = int(year_str)
            month = (int(quarter_str) - 1) * 3 + 1
            return datetime.date(year, month, 1)
        if col_type == enum.ColType.TIME_YEAR:
            year = int(date_value)
            return datetime.date(year, 1, 1)
    except Exception:
        return None
    return None
