"""Conversion utilities for SQLAlchemy-compatible scalar values."""

import datetime
import ipaddress
from decimal import Decimal
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any, TypeVar, cast
from uuid import UUID

import sqlalchemy as sa
from pydantic import BaseModel, Json
from pydantic.fields import ComputedFieldInfo, FieldInfo
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.sql.compiler import SQLCompiler
from sqlalchemy.types import DateTime, TypeDecorator, TypeEngine
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.fastapp.domain.util import get_type_from_annotation

# Maximum string column lengths. Used to derive column type, can be overridden.
# RDBMS	Data Type	Single byte Max Length	Unicode Max Length	Notes
# PostgreSQL	VARCHAR/CHAR	1 GB (1,073,741,823 bytes)	1 GB (1,073,741,823 bytes)	Practically limited by table row size (~2 GB). No length specification required.
# PostgreSQL	TEXT	1 GB	1 GB	Unlimited text; same practical limit as VARCHAR.
# MySQL 5.7+	VARCHAR	65,535 bytes (per column)	65,535 bytes (per column)	Byte limit across entire row. Character count varies by collation (UTF-8 = 21,844 chars, UTF-16 = 32,767 chars).
# MySQL	CHAR	255 bytes (per column)	255 bytes (per column)	Fixed-length. Character count varies by collation.
# SQL Server 2008+	VARCHAR	8,000 bytes	8,000 bytes	ASCII-compatible single-byte encodings.
# SQL Server 2008+	NVARCHAR	4,000 characters	4,000 characters	Unicode (UTF-16). Each character = 2 bytes.
# SQL Server	CHAR	8,000 bytes	8,000 bytes	Fixed-length ASCII.
# SQL Server	NCHAR	4,000 characters	4,000 characters	Fixed-length Unicode (UTF-16).
# SQLite	TEXT	No enforced limit	No enforced limit	Theoretically up to 2 GB (or available memory). Practically unlimited.
# Oracle 19c+	VARCHAR2	4,000 bytes (default)	4,000 bytes (default)	Can be set to 32,767 bytes with MAX_STRING_SIZE=extended parameter.
# Oracle	NVARCHAR2	2,000 bytes (default)	2,000 bytes (default)	Unicode (UTF-16 or UTF-8). Can be 32,767 bytes with extended mode.
# Oracle	CHAR	2,000 bytes (default)	2,000 bytes (default)	Fixed-length. Extended mode: 32,767 bytes.
# MariaDB 10.2+	VARCHAR	65,535 bytes (per column)	65,535 bytes (per column)	Same row-level limit as MySQL. UTF-8: ~21,844 characters.
MAX_UNICODE_COLUMN_LENGTH = 4000
MAX_ASCII_COLUMN_LENGTH = 8000


# REVIEW 2953: double check
class UTCDateTime(TypeDecorator):
    """
    Encapsulates a DateTime column type that always returns timezone-aware datetimes (UTC).

    SQLite stores datetimes as plain strings without timezone info. SQLAlchemy
    therefore returns naive datetimes when reading from SQLite, even when the
    original value was timezone-aware. This TypeDecorator re-attaches UTC on
    read so callers always get a consistent, timezone-aware value regardless of
    the backend.
    """

    impl = DateTime
    cache_ok = True

    def process_result_value(
        self, value: datetime.datetime | None, dialect: Any
    ) -> datetime.datetime | None:
        """Process result value."""
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value


PYTHON_SQL_TYPE_MAP = {
    str: sa.Unicode,  # sa.String, sa.Text, sa.Unicode, sa.UnicodeText can be chosen
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
    Json: sa.JSON,
}


PYDANTIC_SA_FIELD_METADATA_MAP: dict[str, str] = {
    "max_length": "length",
    "max_digits": "precision",
    "decimal_places": "scale",
}

SA_METADATA_BY_TYPE: dict[type[TypeEngine], frozenset[str]] = {
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
    """Encapsulates SQLAlchemy type decorator that normalizes timestamps to UTC."""

    type = sa.TIMESTAMP()
    inherit_cache = True


@compiles(ServerUtcTimestamp, "postgresql")
def postgresql_utc_timestamp(
    _element: ServerUtcTimestamp, _compiler: SQLCompiler, **_kw: dict
) -> str:
    """Postgresql utc timestamp."""
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(ServerUtcTimestamp, "mssql")
def mssql_utc_timestamp(
    _element: ServerUtcTimestamp, _compiler: SQLCompiler, **_kw: dict
) -> str:
    """Mssql utc timestamp."""
    return "GETUTCDATE()"


@compiles(ServerUtcTimestamp, "sqlite")
def sqlite_utc_timestamp(
    _element: ServerUtcTimestamp, _compiler: SQLCompiler, **_kw: dict
) -> str:
    """Sqlite utc timestamp."""
    return "STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')"


class ServerUtcCurrentTime(expression.FunctionElement):
    """Encapsulates SQL expression that returns the database server's current UTC time."""

    type = DateTime()
    inherit_cache = True


@compiles(ServerUtcCurrentTime, "postgresql")
def postgresql_utc_current_time(
    _element: ServerUtcCurrentTime, _compiler: SQLCompiler, **_kw: dict
) -> str:
    """Postgresql utc current time."""
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(ServerUtcCurrentTime, "mssql")
def mssql_utc_current_time(
    _element: ServerUtcCurrentTime, _compiler: SQLCompiler, **_kw: dict
) -> str:
    """Mssql utc current time."""
    return "GETUTCDATE()"


@compiles(ServerUtcCurrentTime, "sqlite")
def sqlite_utc_current_time(
    _element: ServerUtcCurrentTime, _compiler: SQLCompiler, **_kw: dict
) -> str:
    """Sqlite utc current time."""
    return "CURRENT_TIMESTAMP"


def create_sa_type_from_field_info(
    field_info: FieldInfo | ComputedFieldInfo,
    annotation: type[Any] | None,
    max_unicode_column_length: int = MAX_UNICODE_COLUMN_LENGTH,
    max_ascii_column_length: int = MAX_ASCII_COLUMN_LENGTH,
    **kwargs: Any,
) -> TypeEngine:
    """Return a suitable SQLAlchemy type for a Pydantic field."""
    if isinstance(field_info, FieldInfo):
        type_ = get_type_from_annotation(annotation)
    else:
        type_ = field_info.return_type
    if isinstance(type_, TypeVar):  # type: ignore[unreachable]
        type_ = cast(type, type_.__bound__)  # type: ignore[unreachable]
        if type_ is IntEnum:
            type_ = int
        elif type_ is Enum:
            type_ = str
        else:
            raise NotImplementedError(f"Unsupported TypeVar bound for field: {type_}")

    def _create_sa_type(sa_type_class: type[TypeEngine]) -> TypeEngine:
        # Get column kwargs for this type, overridden by kwargs
        """Create sa type."""
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
        # Special case: Unicode/String longer than the maximum allowed column length becomes an unbounded text type.
        if (
            sa_type_class is sa.Unicode
            and cast(int, new_kwargs["length"]) > max_unicode_column_length
        ):
            sa_type_class = sa.UnicodeText
            override_kwargs = dict(kwargs)
            override_kwargs.pop("length", None)
            new_kwargs = (
                get_sa_type_kwargs_from_field_info(sa_type_class, field_info)
                | override_kwargs
            )
        if (
            sa_type_class is sa.String
            and cast(int, new_kwargs["length"]) > max_ascii_column_length
        ):
            sa_type_class = sa.Text
            override_kwargs = dict(kwargs)
            override_kwargs.pop("length", None)
            new_kwargs = (
                get_sa_type_kwargs_from_field_info(sa_type_class, field_info)
                | override_kwargs
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
    sa_type_class: type[sa.types.TypeEngine], field_info: FieldInfo | ComputedFieldInfo
) -> dict[str, Any]:
    # Extract column kwargs from field metadata
    """Return sa type kwargs from field info."""
    kwargs: dict[str, Any] = {}
    if isinstance(field_info, FieldInfo):
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
