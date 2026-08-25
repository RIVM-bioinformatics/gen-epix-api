from sqlalchemy import DateTime, Integer, cast, func, literal_column, type_coerce
from sqlalchemy.sql.elements import ColumnElement

from gen_epix.casedb.domain import enum


def truncate_datetime(
    column: ColumnElement, col_type: enum.ColType, dialect_name: str
) -> ColumnElement:
    """Return a SQL expression matching the case date mappers."""
    if dialect_name == "sqlite":
        if col_type == enum.ColType.TIME_DAY:
            expression = func.datetime(func.date(column))
        elif col_type == enum.ColType.TIME_WEEK:
            weekday = (cast(func.strftime("%w", column), Integer) + 6) % 7
            expression = func.datetime(
                column, func.printf("-%d days", weekday), "start of day"
            )
        elif col_type == enum.ColType.TIME_MONTH:
            expression = func.datetime(func.strftime("%Y-%m-01", column))
        elif col_type == enum.ColType.TIME_QUARTER:
            year = cast(func.strftime("%Y", column), Integer)
            month = cast(func.strftime("%m", column), Integer)
            quarter_month = ((month - 1) / 3) * 3 + 1
            expression = func.datetime(func.printf("%04d-%02d-01", year, quarter_month))
        elif col_type == enum.ColType.TIME_YEAR:
            expression = func.datetime(func.strftime("%Y-01-01", column))
        else:
            raise AssertionError(f"Unsupported ColType for time unit: {col_type}")
        return type_coerce(expression, DateTime())

    if dialect_name == "mssql":
        if col_type == enum.ColType.TIME_DAY:
            datepart = literal_column("day")
            return func.dateadd(datepart, func.datediff(datepart, 0, column), 0)
        if col_type == enum.ColType.TIME_WEEK:
            # DATEDIFF from Monday 1900-01-01 avoids the DATEFIRST setting.
            datepart = literal_column("day")
            monday_offset = func.datediff(datepart, "19000101", column) % 7
            return func.dateadd(
                datepart,
                -monday_offset,
                func.dateadd(datepart, func.datediff(datepart, 0, column), 0),
            )
        if col_type == enum.ColType.TIME_MONTH:
            datepart = literal_column("month")
            return func.dateadd(datepart, func.datediff(datepart, 0, column), 0)
        if col_type == enum.ColType.TIME_QUARTER:
            datepart = literal_column("quarter")
            return func.dateadd(datepart, func.datediff(datepart, 0, column), 0)
        if col_type == enum.ColType.TIME_YEAR:
            datepart = literal_column("year")
            return func.dateadd(datepart, func.datediff(datepart, 0, column), 0)
        raise AssertionError(f"Unsupported ColType for time unit: {col_type}")

    raise ValueError(f"Unsupported SQL dialect for case stats: {dialect_name}")
