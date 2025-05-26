from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.sql.compiler import SQLCompiler
from sqlalchemy.types import DateTime, TypeEngine
from sqlalchemy_utils.types.uuid import UUIDType
from sqlmodel._compat import get_sa_type_from_type_annotation
from sqlmodel.main import get_sqlalchemy_type


class ServerUtcTimestamp(expression.FunctionElement):
    type = sa.TIMESTAMP()
    inherit_cache = True


@compiles(ServerUtcTimestamp, "postgresql")
def postgresql_utc_timestamp(
    _element: ServerUtcTimestamp, _compiler: SQLCompiler, **_kw: dict
) -> str:
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(ServerUtcTimestamp, "mssql")
def mssql_utc_timestamp(
    _element: ServerUtcTimestamp, _compiler: SQLCompiler, **_kw: dict
) -> str:
    return "GETUTCDATE()"


@compiles(ServerUtcTimestamp, "sqlite")
def sqlite_utc_timestamp(
    _element: ServerUtcTimestamp, _compiler: SQLCompiler, **_kw: dict
) -> str:
    return "STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')"


class ServerUtcCurrentTime(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(ServerUtcCurrentTime, "postgresql")
def postgresql_utc_current_time(
    _element: ServerUtcCurrentTime, _compiler: SQLCompiler, **_kw: dict
) -> str:
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(ServerUtcCurrentTime, "mssql")
def mssql_utc_current_time(
    _element: ServerUtcCurrentTime, _compiler: SQLCompiler, **_kw: dict
) -> str:
    return "GETUTCDATE()"


@compiles(ServerUtcCurrentTime, "sqlite")
def sqlite_utc_current_time(
    _element: ServerUtcCurrentTime, _compiler: SQLCompiler, **_kw: dict
) -> str:
    return "CURRENT_TIMESTAMP"


def get_pydantic_field_sa_type(fieldinfo: Any) -> TypeEngine:
    """
    Return a suitable SQLAlchemy type for a Pydantic field.
    """
    type_ = get_sa_type_from_type_annotation(fieldinfo.annotation)

    if issubclass(type_, (dict, list, set, tuple)):
        return sa.JSON()

    if issubclass(type_, UUID):
        # Use UUIDType from sqlalchemy_utils to store UUID correctly in all backends
        return UUIDType()

    return get_sqlalchemy_type(fieldinfo)
