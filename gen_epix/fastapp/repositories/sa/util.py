import datetime
import ipaddress
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Type
from uuid import UUID

import sqlalchemy as sa
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.sql.compiler import SQLCompiler
from sqlalchemy.types import DateTime, TypeEngine
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.fastapp.domain.util import get_type_from_annotation

PYTHON_SQL_TYPE_MAP = {
    str: sa.String,  # sa.Text, sa.Unicode, sa.UnicodeText can be chosen
    int: sa.Integer,
    float: sa.Float,
    bool: sa.Boolean,
    datetime.datetime: sa.DateTime,
    datetime.date: sa.Date,
    datetime.time: sa.Time,
    datetime.timedelta: sa.Interval,
    Decimal: sa.Numeric,
    bytes: sa.LargeBinary,
    UUID: UUIDType,
    ipaddress.IPv4Address: sa.String,
    ipaddress.IPv6Address: sa.String,
    ipaddress.IPv4Network: sa.String,
    ipaddress.IPv6Network: sa.String,
    Path: sa.String,
    dict: sa.JSON,
    list: sa.JSON,
    set: sa.JSON,
    frozenset: sa.JSON,
    tuple: sa.JSON,
}

PYDANTIC_SA_FIELD_METADATA_MAP: dict[str, str] = {
    "max_length": "length",
    "max_digits": "precision",
    "decimal_places": "scale",
}

SA_METADATA_BY_TYPE: dict[Type[TypeEngine], frozenset[str]] = {
    sa.String: frozenset({"length", "collation"}),
    sa.Unicode: frozenset({"length", "collation"}),
    sa.Text: frozenset({"collation"}),
    sa.UnicodeText: frozenset({"collation"}),
    sa.Boolean: frozenset({"create_constraint", "name"}),
    sa.Integer: frozenset({}),
    sa.BigInteger: frozenset({}),
    sa.SmallInteger: frozenset({}),
    sa.Float: frozenset({"precision", "asdecimal", "decimal_return_scale"}),
    sa.Numeric: frozenset({"precision", "scale", "decimal_return_scale", "asdecimal"}),
    sa.DECIMAL: frozenset({"precision", "scale", "decimal_return_scale", "asdecimal"}),
    sa.DateTime: frozenset({"timezone"}),
    sa.Date: frozenset({}),
    sa.Time: frozenset({"timezone"}),
    sa.Interval: frozenset({"native", "second_precision", "day_precision"}),
    sa.LargeBinary: frozenset({"length"}),
    sa.BINARY: frozenset({"length"}),
    sa.VARBINARY: frozenset({"length"}),
    sa.JSON: frozenset({"none_as_null"}),
    sa.CHAR: frozenset({"length", "collation"}),
    sa.VARCHAR: frozenset({"length", "collation"}),
    sa.NCHAR: frozenset({"length", "collation"}),
    sa.NVARCHAR: frozenset({"length", "collation"}),
    sa.CLOB: frozenset({"collation"}),
    sa.BLOB: frozenset({"length"}),
    sa.TIMESTAMP: frozenset({"timezone"}),
    UUIDType: frozenset({"binary", "native"}),
}


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


def create_sa_type_from_field_info(
    field_info: FieldInfo, annotation: Type[Any] | None, **kwargs: dict
) -> TypeEngine:
    """
    Return a suitable SQLAlchemy type for a Pydantic field.
    """
    type_ = get_type_from_annotation(annotation)

    def _create_sa_type(sa_type_class: Type[TypeEngine]) -> TypeEngine:
        # Get column kwargs for this type, overridden by kwargs
        new_kwargs = (
            get_sa_type_kwargs_from_field_info(sa_type_class, field_info) | kwargs
        )
        # Special case: String without length becomes Text
        if sa_type_class is sa.String and "length" not in new_kwargs:
            sa_type_class = sa.Text
            new_kwargs = (
                get_sa_type_kwargs_from_field_info(sa_type_class, field_info) | kwargs
            )
        # Special case: Unicode without length becomes UnicodeText
        if sa_type_class is sa.Unicode and "length" not in new_kwargs:
            sa_type_class = sa.UnicodeText
            new_kwargs = (
                get_sa_type_kwargs_from_field_info(sa_type_class, field_info) | kwargs
            )
        return sa_type_class(**new_kwargs)

    if issubclass(type_, Enum):
        # Special case: construct from type itself
        return sa.Enum(type_)
    if type_ in PYTHON_SQL_TYPE_MAP:
        return _create_sa_type(PYTHON_SQL_TYPE_MAP[type_])
    if issubclass(type_, BaseModel):
        # Special case: pydantic models as JSON
        return _create_sa_type(sa.JSON)

    raise NotImplementedError(f"Unsupported field type: {type_}")


def get_sa_type_kwargs_from_field_info(
    sa_type_class: Type[sa.types.TypeEngine], field_info: FieldInfo
) -> dict[str, Any]:
    # Extract column kwargs from field metadata
    kwargs: dict[str, Any] = {}
    for metadata in field_info.metadata:
        for pydantic_name, sa_name in PYDANTIC_SA_FIELD_METADATA_MAP.items():
            if hasattr(metadata, pydantic_name):
                kwargs[sa_name] = getattr(metadata, pydantic_name)
    # Restrict column kwargs to allowed ones for this particular column type
    if sa_type_class not in SA_METADATA_BY_TYPE:
        raise NotImplementedError(
            f"Unsupported SQLAlchemy column type: {sa_type_class}"
        )
    return {x: y for x, y in kwargs.items() if x in SA_METADATA_BY_TYPE[sa_type_class]}
