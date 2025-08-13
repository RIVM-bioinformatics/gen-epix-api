# pylint: disable=useless-import-alias
# Import all filter classes, part 1
from gen_epix.filter.base import Filter as Filter
from gen_epix.filter.composite import CompositeFilter as CompositeFilter
from gen_epix.filter.composite import TypedCompositeFilter as TypedCompositeFilter
from gen_epix.filter.date_range import DateRangeFilter as DateRangeFilter
from gen_epix.filter.date_range import TypedDateRangeFilter as TypedDateRangeFilter
from gen_epix.filter.datetime_range import DatetimeRangeFilter as DatetimeRangeFilter
from gen_epix.filter.datetime_range import (
    TypedDatetimeRangeFilter as TypedDatetimeRangeFilter,
)

# Import relevant enums
from gen_epix.filter.enum import BooleanOperator as BooleanOperator
from gen_epix.filter.enum import ComparisonOperator as ComparisonOperator
from gen_epix.filter.enum import FilterType as FilterType

# Import all filter classes, part 2
from gen_epix.filter.equals import EqualsFilter as EqualsFilter
from gen_epix.filter.equals_boolean import EqualsBooleanFilter as EqualsBooleanFilter
from gen_epix.filter.equals_boolean import (
    TypedEqualsBooleanFilter as TypedEqualsBooleanFilter,
)
from gen_epix.filter.equals_number import EqualsNumberFilter as EqualsNumberFilter
from gen_epix.filter.equals_number import (
    TypedEqualsNumberFilter as TypedEqualsNumberFilter,
)
from gen_epix.filter.equals_string import EqualsStringFilter as EqualsStringFilter
from gen_epix.filter.equals_string import (
    TypedEqualsStringFilter as TypedEqualsStringFilter,
)
from gen_epix.filter.equals_uuid import EqualsUuidFilter as EqualsUuidFilter
from gen_epix.filter.equals_uuid import TypedEqualsUuidFilter as TypedEqualsUuidFilter
from gen_epix.filter.exists import ExistsFilter as ExistsFilter
from gen_epix.filter.exists import TypedExistsFilter as TypedExistsFilter
from gen_epix.filter.hashable_set import (
    HashableSetFilter as HashableSetFilter,
)  # TypedValueSetFilter does not exist
from gen_epix.filter.no_filter import NoFilter as NoFilter
from gen_epix.filter.no_filter import TypedNoFilter as TypedNoFilter
from gen_epix.filter.number_range import NumberRangeFilter as NumberRangeFilter
from gen_epix.filter.number_range import (
    TypedNumberRangeFilter as TypedNumberRangeFilter,
)
from gen_epix.filter.number_set import NumberSetFilter as NumberSetFilter
from gen_epix.filter.number_set import TypedNumberSetFilter as TypedNumberSetFilter
from gen_epix.filter.partial_date_range import (
    PartialDateRangeFilter as PartialDateRangeFilter,
)
from gen_epix.filter.partial_date_range import (
    TypedPartialDateRangeFilter as TypedPartialDateRangeFilter,
)
from gen_epix.filter.range import RangeFilter as RangeFilter
from gen_epix.filter.range import TypedRangeFilter as TypedRangeFilter
from gen_epix.filter.regex import RegexFilter as RegexFilter
from gen_epix.filter.regex import TypedRegexFilter as TypedRegexFilter
from gen_epix.filter.string_set import StringSetFilter as StringSetFilter
from gen_epix.filter.string_set import TypedStringSetFilter as TypedStringSetFilter
from gen_epix.filter.uuid_set import TypedUuidSetFilter as TypedUuidSetFilter
from gen_epix.filter.uuid_set import UuidSetFilter as UuidSetFilter
