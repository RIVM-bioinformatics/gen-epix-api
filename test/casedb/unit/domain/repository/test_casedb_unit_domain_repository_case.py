"""Unit tests for the casedb case repository base class."""

# pylint: disable=protected-access

import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.repository.case import BaseCaseRepository

MAPPER_CASES = [
    # (col_type, input, expected)
    (
        enum.ColType.TIME_DAY,
        datetime.datetime(2024, 5, 15, 13, 45, 12, 999),
        datetime.datetime(2024, 5, 15),
    ),
    (
        enum.ColType.TIME_DAY,
        datetime.datetime(2024, 5, 15),
        datetime.datetime(2024, 5, 15),
    ),
    # Wednesday maps back to Monday
    (
        enum.ColType.TIME_WEEK,
        datetime.datetime(2024, 5, 15, 13, 45),
        datetime.datetime(2024, 5, 13),
    ),
    # Monday stays on Monday
    (
        enum.ColType.TIME_WEEK,
        datetime.datetime(2024, 5, 13, 23, 59),
        datetime.datetime(2024, 5, 13),
    ),
    # Sunday maps to the preceding Monday
    (
        enum.ColType.TIME_WEEK,
        datetime.datetime(2024, 5, 19, 8),
        datetime.datetime(2024, 5, 13),
    ),
    # Week crossing a year boundary
    (
        enum.ColType.TIME_WEEK,
        datetime.datetime(2025, 1, 1, 10),
        datetime.datetime(2024, 12, 30),
    ),
    (
        enum.ColType.TIME_MONTH,
        datetime.datetime(2024, 5, 31, 23, 59, 59),
        datetime.datetime(2024, 5, 1),
    ),
    (
        enum.ColType.TIME_MONTH,
        datetime.datetime(2024, 2, 29, 1),
        datetime.datetime(2024, 2, 1),
    ),
    (
        enum.ColType.TIME_QUARTER,
        datetime.datetime(2024, 1, 15),
        datetime.datetime(2024, 1, 1),
    ),
    (
        enum.ColType.TIME_QUARTER,
        datetime.datetime(2024, 3, 31, 23),
        datetime.datetime(2024, 1, 1),
    ),
    (
        enum.ColType.TIME_QUARTER,
        datetime.datetime(2024, 4, 1),
        datetime.datetime(2024, 4, 1),
    ),
    (
        enum.ColType.TIME_QUARTER,
        datetime.datetime(2024, 8, 20),
        datetime.datetime(2024, 7, 1),
    ),
    (
        enum.ColType.TIME_QUARTER,
        datetime.datetime(2024, 12, 31, 23),
        datetime.datetime(2024, 10, 1),
    ),
    (
        enum.ColType.TIME_YEAR,
        datetime.datetime(2024, 12, 31, 23, 59, 59),
        datetime.datetime(2024, 1, 1),
    ),
    (
        enum.ColType.TIME_YEAR,
        datetime.datetime(2024, 1, 1),
        datetime.datetime(2024, 1, 1),
    ),
]


class TestDateMappers:
    """Tests for the temporal-resolution date mappers."""

    def test_date_mappers_cover_every_time_resolution(self) -> None:
        """Every time-resolution column type has a mapper."""
        assert set(BaseCaseRepository.DATE_MAPPERS) == set(
            enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
        )

    def test_date_mappers_follow_resolution_order(self) -> None:
        """Mapper keys keep the resolution-order sequence."""
        assert list(BaseCaseRepository.DATE_MAPPERS) == list(
            enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
        )

    @pytest.mark.parametrize("col_type, value, expected", MAPPER_CASES)
    def test_date_mapper_normalizes_value(
        self,
        col_type: enum.ColType,
        value: datetime.datetime,
        expected: datetime.datetime,
    ) -> None:
        """Each mapper truncates a value to its resolution start."""
        assert BaseCaseRepository.DATE_MAPPERS[col_type](value) == expected

    @pytest.mark.parametrize("col_type", list(BaseCaseRepository.DATE_MAPPERS))
    def test_date_mapper_does_not_mutate_input(self, col_type: enum.ColType) -> None:
        """Mappers leave the input datetime unchanged."""
        value = datetime.datetime(2024, 5, 15, 13, 45, 12, 999)
        BaseCaseRepository.DATE_MAPPERS[col_type](value)
        assert value == datetime.datetime(2024, 5, 15, 13, 45, 12, 999)

    @pytest.mark.parametrize("col_type", list(BaseCaseRepository.DATE_MAPPERS))
    def test_date_mapper_is_idempotent(self, col_type: enum.ColType) -> None:
        """Applying a mapper twice equals applying it once."""
        mapper = BaseCaseRepository.DATE_MAPPERS[col_type]
        value = datetime.datetime(2024, 8, 20, 13, 45, 12, 999)
        assert mapper(mapper(value)) == mapper(value)

    def test_date_mapper_preserves_timezone(self) -> None:
        """Mapped values keep the input timezone."""
        tz = datetime.timezone.utc
        value = datetime.datetime(2024, 8, 20, 13, tzinfo=tz)
        result = BaseCaseRepository.DATE_MAPPERS[enum.ColType.TIME_DAY](value)
        assert result == datetime.datetime(2024, 8, 20, tzinfo=tz)
        assert result.tzinfo is tz


class TestGetDateMappers:
    """Tests for `_get_date_mappers`."""

    def test_returns_fresh_equivalent_mapping(self) -> None:
        """Each call builds a new mapping with the same keys."""
        mappers = BaseCaseRepository._get_date_mappers()
        assert mappers is not BaseCaseRepository.DATE_MAPPERS
        assert set(mappers) == set(BaseCaseRepository.DATE_MAPPERS)

    def test_unsupported_col_type_raises(self, monkeypatch) -> None:
        """An unsupported resolution column type raises AssertionError."""
        monkeypatch.setattr(
            enum,
            "ColTypeOrder",
            SimpleNamespace(
                TIME_RESOLUTION_DESC=SimpleNamespace(value={enum.ColType.TEXT: 1})
            ),
        )
        with pytest.raises(AssertionError, match="Unsupported ColType"):
            BaseCaseRepository._get_date_mappers()


class TestRetrieveCaseStats:
    """Tests for the abstract `retrieve_case_stats` contract."""

    def test_base_class_is_abstract(self) -> None:
        """The statistics read is declared abstract."""
        assert "retrieve_case_stats" in BaseCaseRepository.__abstractmethods__

    def test_default_body_raises_not_implemented(self) -> None:
        """The abstract body raises NotImplementedError when called directly."""
        with pytest.raises(NotImplementedError):
            BaseCaseRepository.retrieve_case_stats(MagicMock(), MagicMock(), uuid4())
