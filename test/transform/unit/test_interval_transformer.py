"""
Unit tests for interval transformers.
"""

from decimal import Decimal

import pytest

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.enum import NoMatchStrategy
from gen_epix.transform.transformers.interval import (
    IntervalToIntervalTransformer,
    IntervalTransformer,
)


@pytest.mark.scenario_ids("TC-MAIN-12-01")
class TestIntervalTransformer:
    """Test cases for IntervalTransformer."""

    def test_basic_interval_mapping(self) -> None:
        """Test basic number to interval mapping."""
        transformer = IntervalTransformer(
            src_field="age",
            interval_names=["young", "middle", "old"],
            lower_bounds=[0, 30, 60],
            upper_bounds=[30, 60, 100],
            lower_bound_is_inclusive=True,
            upper_bound_is_inclusive=False,
        )

        # Test cases: (input_value, expected_interval)
        test_cases = [
            (25, "young"),  # Within first interval
            (30, "middle"),  # Boundary case - inclusive lower
            (45, "middle"),  # Within middle interval
            (60, "old"),  # Boundary case - inclusive lower
            (75, "old"),  # Within last interval
        ]

        for input_value, expected in test_cases:
            adapter = ObjectAdapter({"age": input_value})
            result = transformer.transform(adapter)
            assert (
                result.get("age") == expected
            ), f"Input {input_value} should map to {expected}"

    def test_none_values(self) -> None:
        """Test handling of None values."""
        transformer = IntervalTransformer(
            src_field="value",
            interval_names=["low", "high"],
            lower_bounds=[0, 50],
            upper_bounds=[50, 100],
        )

        adapter = ObjectAdapter({"value": None})
        result = transformer.transform(adapter)
        assert result.get("value") is None

    def test_no_match_raise_strategy(self) -> None:
        """Test NoMatchStrategy.RAISE behavior."""
        transformer = IntervalTransformer(
            src_field="value",
            interval_names=["valid"],
            lower_bounds=[10],
            upper_bounds=[20],
            no_match_strategy=NoMatchStrategy.RAISE,
        )

        adapter = ObjectAdapter({"value": 25})  # Outside valid range
        with pytest.raises(ValueError, match="Value 25 does not match any interval"):
            transformer.transform(adapter)

    def test_no_match_set_none_strategy(self) -> None:
        """Test NoMatchStrategy.SET_NONE behavior."""
        transformer = IntervalTransformer(
            src_field="value",
            interval_names=["valid"],
            lower_bounds=[10],
            upper_bounds=[20],
            no_match_strategy=NoMatchStrategy.SET_NONE,
        )

        adapter = ObjectAdapter({"value": 25})  # Outside valid range
        result = transformer.transform(adapter)
        assert result.get("value") is None

    def test_is_transformable(self) -> None:
        """Test is_transformable method."""
        transformer = IntervalTransformer(
            src_field="value",
            interval_names=["valid"],
            lower_bounds=[10],
            upper_bounds=[20],
        )

        assert transformer.is_transformable(15) is True  # Within range
        assert transformer.is_transformable(25) is False  # Outside range
        assert (
            transformer.is_transformable(None) is True
        )  # None is always transformable

    def test_transform_value_direct(self) -> None:
        """Test transform_value method for direct value transformation."""
        transformer = IntervalTransformer(
            src_field="dummy",
            interval_names=["small", "large"],
            lower_bounds=[0, 100],
            upper_bounds=[100, 200],
        )

        assert transformer.transform_value(50) == "small"
        assert transformer.transform_value(150) == "large"
        assert transformer.transform_value(None) is None

    def test_decimal_values(self) -> None:
        """Test with Decimal input values."""
        transformer = IntervalTransformer(
            src_field="value",
            interval_names=["low", "high"],
            lower_bounds=[0, 50],
            upper_bounds=[50, 100],
        )

        adapter = ObjectAdapter({"value": Decimal("25.5")})
        result = transformer.transform(adapter)
        assert result.get("value") == "low"


@pytest.mark.scenario_ids("TC-MAIN-12-01")
class TestIntervalToIntervalTransformer:
    """Test cases for IntervalToIntervalTransformer."""

    def test_basic_interval_to_interval_mapping(self) -> None:
        """Test basic interval to interval mapping with largest overlap strategy."""
        transformer = IntervalToIntervalTransformer(
            src_field="detailed_age",
            src_interval_names=["18-25", "26-35", "36-45", "46-60"],
            src_lower_bounds=[18, 26, 36, 46],
            src_upper_bounds=[25, 35, 45, 60],
            tgt_interval_names=["young", "middle", "senior"],
            tgt_lower_bounds=[18, 30, 50],
            tgt_upper_bounds=[30, 50, 70],
            overlap_strategy="largest_overlap",
        )

        # Test cases: (input_interval, expected_interval)
        test_cases = [
            ("18-25", "young"),  # Completely within young (18-30)
            (
                "26-35",
                "middle",
            ),  # Overlaps both young and middle, but larger overlap with middle
            ("36-45", "middle"),  # Completely within middle (30-50)
            (
                "46-60",
                "senior",
            ),  # Overlaps middle (4 units) and senior (10 units), larger overlap with senior
        ]

        for input_interval, expected in test_cases:
            adapter = ObjectAdapter({"detailed_age": input_interval})
            result = transformer.transform(adapter)
            assert (
                result.get("detailed_age") == expected
            ), f"Input {input_interval} should map to {expected}"

    def test_exact_fit_strategy(self) -> None:
        """Test exact fit strategy - only maps if completely contained."""
        transformer = IntervalToIntervalTransformer(
            src_field="src_interval",
            src_interval_names=["10-20", "15-25", "30-40"],
            src_lower_bounds=[10, 15, 30],
            src_upper_bounds=[20, 25, 40],
            tgt_interval_names=["small", "large"],
            tgt_lower_bounds=[0, 25],
            tgt_upper_bounds=[25, 50],
            overlap_strategy="exact_fit",
        )

        test_cases = [
            ("10-20", "small"),  # Completely contained in small (0-25)
            ("30-40", "large"),  # Completely contained in large (25-50)
        ]

        for input_interval, expected in test_cases:
            adapter = ObjectAdapter({"src_interval": input_interval})
            result = transformer.transform(adapter)
            assert result.get("src_interval") == expected

        # Test interval that truly spans across boundaries
        transformer_strict = IntervalToIntervalTransformer(
            src_field="src_interval",
            src_interval_names=["spanning"],
            src_lower_bounds=[20],
            src_upper_bounds=[30],  # Spans across small (0-25) and large (25-50)
            tgt_interval_names=["small", "large"],
            tgt_lower_bounds=[0, 25],
            tgt_upper_bounds=[25, 50],
            overlap_strategy="exact_fit",
        )

        adapter = ObjectAdapter(
            {"src_interval": "spanning"}
        )  # 20-30 spans both intervals
        with pytest.raises(
            ValueError, match="cannot be mapped to target categorization"
        ):
            transformer_strict.transform(adapter)

    def test_none_values_interval_to_interval(self) -> None:
        """Test handling of None values in interval to interval mapping."""
        transformer = IntervalToIntervalTransformer(
            src_field="interval",
            src_interval_names=["src1"],
            src_lower_bounds=[0],
            src_upper_bounds=[10],
            tgt_interval_names=["tgt1"],
            tgt_lower_bounds=[0],
            tgt_upper_bounds=[20],
        )

        adapter = ObjectAdapter({"interval": None})
        result = transformer.transform(adapter)
        assert result.get("interval") is None

    def test_no_match_strategies_interval_to_interval(self) -> None:
        """Test different no-match strategies for interval to interval mapping."""
        # Test RAISE strategy
        transformer_raise = IntervalToIntervalTransformer(
            src_field="interval",
            src_interval_names=["unmappable"],
            src_lower_bounds=[100],
            src_upper_bounds=[200],
            tgt_interval_names=["target"],
            tgt_lower_bounds=[0],
            tgt_upper_bounds=[50],  # No overlap with source
            no_match_strategy=NoMatchStrategy.RAISE,
        )

        adapter = ObjectAdapter({"interval": "unmappable"})
        with pytest.raises(
            ValueError, match="cannot be mapped to target categorization"
        ):
            transformer_raise.transform(adapter)

        # Test SET_NONE strategy
        transformer_none = IntervalToIntervalTransformer(
            src_field="interval",
            src_interval_names=["unmappable"],
            src_lower_bounds=[100],
            src_upper_bounds=[200],
            tgt_interval_names=["target"],
            tgt_lower_bounds=[0],
            tgt_upper_bounds=[50],  # No overlap with source
            no_match_strategy=NoMatchStrategy.SET_NONE,
        )

        adapter = ObjectAdapter({"interval": "unmappable"})
        result = transformer_none.transform(adapter)
        assert result.get("interval") is None

    def test_is_transformable_interval_to_interval(self) -> None:
        """Test is_transformable method for interval to interval transformer."""
        transformer = IntervalToIntervalTransformer(
            src_field="interval",
            src_interval_names=["mappable", "unmappable"],
            src_lower_bounds=[0, 100],
            src_upper_bounds=[20, 120],
            tgt_interval_names=["target"],
            tgt_lower_bounds=[0],
            tgt_upper_bounds=[50],  # Only overlaps with "mappable"
        )

        assert transformer.is_transformable("mappable") is True
        assert transformer.is_transformable("unmappable") is False
        assert transformer.is_transformable(None) is True
        assert transformer.is_transformable("nonexistent") is False

    def test_transform_value_direct_interval_to_interval(self) -> None:
        """Test transform_value method for direct interval transformation."""
        transformer = IntervalToIntervalTransformer(
            src_field="dummy",
            src_interval_names=["detailed1", "detailed2"],
            src_lower_bounds=[0, 50],
            src_upper_bounds=[30, 80],
            tgt_interval_names=["broad1", "broad2"],
            tgt_lower_bounds=[0, 40],
            tgt_upper_bounds=[40, 100],
        )

        assert transformer.transform_value("detailed1") == "broad1"  # 0-30 maps to 0-40
        assert (
            transformer.transform_value("detailed2") == "broad2"
        )  # 50-80 maps to 40-100
        assert transformer.transform_value(None) is None

    def test_overlapping_intervals_edge_cases(self) -> None:
        """Test edge cases with boundary overlaps."""
        transformer = IntervalToIntervalTransformer(
            src_field="interval",
            src_interval_names=["boundary_test"],
            src_lower_bounds=[20],
            src_upper_bounds=[30],
            tgt_interval_names=["left", "right"],
            tgt_lower_bounds=[10, 30],
            tgt_upper_bounds=[30, 50],
            src_upper_bound_is_inclusive=True,
            tgt_lower_bound_is_inclusive=True,
            overlap_strategy="largest_overlap",
        )

        # Source interval [20,30] should map to "left" [10,30] with larger overlap
        adapter = ObjectAdapter({"interval": "boundary_test"})
        result = transformer.transform(adapter)
        assert result.get("interval") == "left"

    def test_infinite_bounds(self) -> None:
        """Test handling of infinite bounds."""
        transformer = IntervalToIntervalTransformer(
            src_field="interval",
            src_interval_names=["infinite_upper"],
            src_lower_bounds=[100],
            src_upper_bounds=[None],  # Infinite upper bound
            tgt_interval_names=["also_infinite"],
            tgt_lower_bounds=[50],
            tgt_upper_bounds=[None],  # Infinite upper bound
        )

        adapter = ObjectAdapter({"interval": "infinite_upper"})
        result = transformer.transform(adapter)
        assert result.get("interval") == "also_infinite"

    def test_complex_overlap_calculation(self) -> None:
        """Test complex overlap scenarios."""
        # Age group mapping: detailed -> broad categories
        transformer = IntervalToIntervalTransformer(
            src_field="age_detailed",
            src_interval_names=["teens", "twenties", "thirties", "forties"],
            src_lower_bounds=[13, 20, 30, 40],
            src_upper_bounds=[19, 29, 39, 49],
            tgt_interval_names=["youth", "adult", "middle_age"],
            tgt_lower_bounds=[10, 25, 35],
            tgt_upper_bounds=[25, 35, 55],
            overlap_strategy="largest_overlap",
        )

        test_cases = [
            ("teens", "youth"),  # 13-19 overlaps with youth 10-25 (6 years overlap)
            (
                "twenties",
                "youth",
            ),  # 20-29 overlaps with youth 10-25 (5 years) and adult 25-35 (4 years)
            (
                "thirties",
                "adult",
            ),  # 30-39 overlaps with adult 25-35 (5 years) and middle_age 35-55 (4 years)
            (
                "forties",
                "middle_age",
            ),  # 40-49 overlaps with middle_age 35-55 (9 years overlap)
        ]

        for input_interval, expected in test_cases:
            adapter = ObjectAdapter({"age_detailed": input_interval})
            result = transformer.transform(adapter)
            assert (
                result.get("age_detailed") == expected
            ), f"Input {input_interval} should map to {expected}"
