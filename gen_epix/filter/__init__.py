"""Expose public filter models and operators for matching scalar and row data.

The base `Filter`, `CompositeFilter`, date and datetime range filters define
shared matching and logical-composition behavior. `ComparisonOperator`,
`FilterType`, and `LogicalOperator` configure range and composite semantics.

Equality, existence, set-membership, numeric/date range, partial-date, regex,
and no-op filters provide concrete matching behavior and carry their serialized
`FilterType` directly.
"""

# pylint: disable=useless-import-alias
# Import all filter classes, part 1
from gen_epix.filter.base import Filter as Filter
from gen_epix.filter.composite import CompositeFilter as CompositeFilter
from gen_epix.filter.composite import FilterUnion as FilterUnion
from gen_epix.filter.date_range import DateRangeFilter as DateRangeFilter
from gen_epix.filter.datetime_range import DatetimeRangeFilter as DatetimeRangeFilter

# Import relevant enums
from gen_epix.filter.enum import ComparisonOperator as ComparisonOperator
from gen_epix.filter.enum import FilterType as FilterType
from gen_epix.filter.enum import LogicalOperator as LogicalOperator

# Import all filter classes, part 2
from gen_epix.filter.equals import EqualsFilter as EqualsFilter
from gen_epix.filter.equals_boolean import EqualsBooleanFilter as EqualsBooleanFilter
from gen_epix.filter.equals_number import EqualsNumberFilter as EqualsNumberFilter
from gen_epix.filter.equals_string import EqualsStringFilter as EqualsStringFilter
from gen_epix.filter.equals_uuid import EqualsUuidFilter as EqualsUuidFilter
from gen_epix.filter.exists import ExistsFilter as ExistsFilter
from gen_epix.filter.hashable_set import HashableSetFilter as HashableSetFilter
from gen_epix.filter.no_filter import NoFilter as NoFilter
from gen_epix.filter.number_range import NumberRangeFilter as NumberRangeFilter
from gen_epix.filter.number_set import NumberSetFilter as NumberSetFilter
from gen_epix.filter.partial_date_range import (
    PartialDateRangeFilter as PartialDateRangeFilter,
)
from gen_epix.filter.range import RangeFilter as RangeFilter
from gen_epix.filter.regex import RegexFilter as RegexFilter
from gen_epix.filter.string_set import StringSetFilter as StringSetFilter
from gen_epix.filter.uuid_set import UuidSetFilter as UuidSetFilter
