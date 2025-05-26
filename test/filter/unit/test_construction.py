import datetime
from decimal import Decimal

import pytest

from gen_epix.filter import *
from gen_epix.filter import enum


class Util:
    @staticmethod
    def _date_to_datetime(date: datetime.date | datetime.datetime) -> datetime.datetime:
        return (
            date
            if isinstance(date, datetime.datetime)
            else datetime.datetime(date.year, date.month, date.day)
        )


class TestFilterConstruction:

    def test_exists_construction(self) -> None:
        # Normal construction and immutability
        filter = ExistsFilter()
        assert filter.invert == False
        filter = ExistsFilter(invert=True)
        assert filter.invert == True
        filter = ExistsFilter(invert=0)  # noqa E501
        assert filter.invert == False
        filter = ExistsFilter(invert="0")  # noqa E501
        assert filter.invert == False

    def test_number_range_construction(self) -> None:
        # Normal construction and immutability
        filter = NumberRangeFilter(lower_bound=10, upper_bound=20)
        assert filter.lower_bound == 10
        assert filter.lower_bound_censor == enum.ComparisonOperator.GTE
        assert filter.upper_bound == 20
        assert filter.upper_bound_censor == enum.ComparisonOperator.ST
        with pytest.raises(ValueError):
            filter.lower_bound = 0
        with pytest.raises(ValueError):
            filter.lower_bound_censor = enum.ComparisonOperator.GT
        with pytest.raises(ValueError):
            filter.upper_bound = 30
        with pytest.raises(ValueError):
            filter.upper_bound_censor = enum.ComparisonOperator.STE
        filter = NumberRangeFilter(lower_bound=10, upper_bound=20.5)
        filter = NumberRangeFilter(lower_bound=10.5, upper_bound=20)
        filter = NumberRangeFilter(lower_bound=10.5, upper_bound=20.5)
        filter = NumberRangeFilter(lower_bound=10, upper_bound=Decimal(20.5))
        filter = NumberRangeFilter(lower_bound=Decimal(10.5), upper_bound=20)
        filter = NumberRangeFilter(lower_bound=Decimal(10.5), upper_bound=Decimal(20.5))
        filter = NumberRangeFilter(
            lower_bound=10,
            upper_bound=10,
            upper_bound_censor=enum.ComparisonOperator.STE,
        )
        filter = NumberRangeFilter(
            lower_bound="10",  # noqa E501
            lower_bound_censor=">",  # noqa E501
            upper_bound="20",  # noqa E501
            upper_bound_censor="<=",  # noqa E501
        )
        assert filter.lower_bound == 10
        assert filter.lower_bound_censor == enum.ComparisonOperator.GT
        assert filter.lower_bound == 10
        assert filter.upper_bound_censor == enum.ComparisonOperator.STE
        # Model validation
        filter = NumberRangeFilter(
            lower_bound=10,
            lower_bound_censor=enum.ComparisonOperator.GTE,
            upper_bound=10,
            upper_bound_censor=enum.ComparisonOperator.STE,
        )
        with pytest.raises(ValueError):
            filter = NumberRangeFilter(lower_bound=10, upper_bound=10)
        with pytest.raises(ValueError):
            filter = NumberRangeFilter(lower_bound=20, upper_bound=10)
        with pytest.raises(ValueError):
            filter = NumberRangeFilter(
                lower_bound=10,
                lower_bound_censor=enum.ComparisonOperator.EQ,
                upper_bound=20,
            )
        with pytest.raises(ValueError):
            filter = NumberRangeFilter(
                lower_bound=10,
                upper_bound=20,
                upper_bound_censor=enum.ComparisonOperator.EQ,
            )

    def test_date_range_construction(self) -> None:
        filter = DateRangeFilter(
            lower_bound="2022-01-01", upper_bound="2022-01-31"  # noqa E501
        )  # noqa E501
        assert Util._date_to_datetime(
            filter.lower_bound
        ) == datetime.datetime.fromisoformat("2022-01-01")
        assert Util._date_to_datetime(
            filter.upper_bound
        ) == datetime.datetime.fromisoformat("2022-01-31")

    def test_regex_construction(self) -> None:
        filter = RegexFilter(pattern="^[A-Za-z]+$")
        assert filter.pattern == "^[A-Za-z]+$"
        filter = RegexFilter(pattern="^[0-9]+$")
        assert filter.pattern == "^[0-9]+$"

    def test_term_set_member_construction(self) -> None:
        filter = StringSetFilter(members={"apple", "banana", "cherry"})
        assert filter.members == {"apple", "banana", "cherry"}
        # Model validation
        filter = StringSetFilter(members=["dog", "dog", "cat", "bird"])  # noqa E501
        assert filter.members == {"dog", "cat", "bird"}
        filter = StringSetFilter(members={"APPLE", "banana"}, case_sensitive=True)
        assert filter.members == {"APPLE", "banana"}
        filter = StringSetFilter(members={"APPLE", "banana"}, case_sensitive=False)
        assert filter.members == {"APPLE", "banana"}
        assert filter._members == {"apple", "banana"}
        # Arguments are deep-copied
        terms = {"APPLE", "banana"}
        filter = StringSetFilter(members=terms, case_sensitive=False)
        terms.add("CHERRY")
        assert filter.members != {"APPLE", "banana", "CHERRY"}

    def test_composite_construction(self) -> None:
        subfilter1 = ExistsFilter()
        subfilter2 = NumberRangeFilter(lower_bound=10, upper_bound=20)
        subfilter3 = RegexFilter(pattern="^[A-Za-z]+$")
        filter = CompositeFilter(filters=[subfilter1, subfilter2, subfilter3])
        assert filter.filters == [subfilter1, subfilter2, subfilter3]
