import pytest

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.enum import (
    TimeUnit,
)
from gen_epix.transform.enum import (
    TimeUnitTransformStrategy as TimeUnitTransformStrategy,
)
from gen_epix.transform.transformers.iso_time import IsoTimeTransformer


@pytest.mark.scenario_ids("TC-MAIN-12-01")
def test_transform_iso_time() -> None:
    def assert_equal(actual: list[str | None], expected: list[str | None]) -> None:
        if (
            not isinstance(actual, list)
            or len(actual) != len(expected)
            or sum(x != y for x, y in zip(actual, expected)) > 0
        ):
            raise AssertionError(f"Actual {actual} should be {expected}")

    def test_time_transform(
        src_unit: TimeUnit,
        tgt_unit: TimeUnit,
        strategy: TimeUnitTransformStrategy,
        values: list[str],
    ) -> list[str | None]:
        """Test time transformation for a list of values."""
        # Create and apply transformer
        transformer = IsoTimeTransformer(
            field_name="time_field",
            src_unit=src_unit,
            tgt_unit=tgt_unit,
            strategy=strategy,
        )

        results = []
        for value in values:
            # Create test object with time field
            test_obj = ObjectAdapter({"time_field": value})

            # Transform the object
            result_obj = transformer.transform(test_obj)

            # Extract the result
            results.append(result_obj.get("time_field"))

        return results

    # Test cases grouped by (src_unit, tgt_unit, strategy) combinations
    test_cases: dict[
        tuple[TimeUnit, TimeUnit, TimeUnitTransformStrategy],
        list[tuple[str, str | None]],
    ] = {}

    # YEAR tests
    test_cases[(TimeUnit.YEAR, TimeUnit.YEAR, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2024", "2024"),
    ]
    test_cases[
        (TimeUnit.YEAR, TimeUnit.QUARTER, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024", None),
    ]
    test_cases[
        (TimeUnit.YEAR, TimeUnit.MONTH, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024", None),
    ]
    test_cases[(TimeUnit.YEAR, TimeUnit.WEEK, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2024", None),
    ]
    test_cases[(TimeUnit.YEAR, TimeUnit.DAY, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2024", None),
    ]

    # QUARTER tests
    test_cases[
        (TimeUnit.QUARTER, TimeUnit.YEAR, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024-Q1", "2024"),
    ]
    test_cases[
        (TimeUnit.QUARTER, TimeUnit.QUARTER, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024-Q1", "2024-Q1"),
    ]
    test_cases[
        (TimeUnit.QUARTER, TimeUnit.MONTH, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024-Q1", None),
    ]
    test_cases[
        (TimeUnit.QUARTER, TimeUnit.WEEK, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024-Q1", None),
    ]
    test_cases[
        (TimeUnit.QUARTER, TimeUnit.DAY, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024-Q1", None),
    ]

    # MONTH tests
    test_cases[
        (TimeUnit.MONTH, TimeUnit.YEAR, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024-01", "2024"),
    ]
    test_cases[
        (TimeUnit.MONTH, TimeUnit.QUARTER, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024-01", "2024-Q1"),
        ("2024-02", "2024-Q1"),
        ("2024-03", "2024-Q1"),
        ("2024-04", "2024-Q2"),
        ("2024-05", "2024-Q2"),
        ("2024-06", "2024-Q2"),
        ("2024-07", "2024-Q3"),
        ("2024-08", "2024-Q3"),
        ("2024-09", "2024-Q3"),
        ("2024-10", "2024-Q4"),
        ("2024-11", "2024-Q4"),
        ("2024-12", "2024-Q4"),
    ]
    test_cases[
        (TimeUnit.MONTH, TimeUnit.MONTH, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024-01", "2024-01"),
    ]
    test_cases[
        (TimeUnit.MONTH, TimeUnit.WEEK, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2024-01", None),
    ]
    test_cases[(TimeUnit.MONTH, TimeUnit.DAY, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2024-01", None),
    ]

    # WEEK tests with EXACT_ONLY strategy
    test_cases[(TimeUnit.WEEK, TimeUnit.YEAR, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2020-W52", "2020"),
        ("2020-W53", None),
        ("2022-W52", None),
        ("2023-W52", "2023"),
        ("2024-W01", "2024"),
    ]
    test_cases[
        (TimeUnit.WEEK, TimeUnit.YEAR, TimeUnitTransformStrategy.LARGEST_OVERLAP)
    ] = [
        ("2020-W52", "2020"),
        ("2020-W53", "2020"),
        ("2022-W52", "2022"),
        ("2023-W52", "2023"),
    ]

    test_cases[
        (TimeUnit.WEEK, TimeUnit.QUARTER, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2022-W52", None),
        ("2023-W13", None),
        ("2023-W17", "2023-Q2"),
        ("2023-W26", None),
        ("2023-W39", None),
        ("2023-W52", "2023-Q4"),
    ]
    test_cases[
        (TimeUnit.WEEK, TimeUnit.QUARTER, TimeUnitTransformStrategy.LARGEST_OVERLAP)
    ] = [
        ("2022-W52", "2022-Q4"),
        ("2023-W13", "2023-Q1"),
        ("2023-W17", "2023-Q2"),
        ("2023-W26", "2023-Q2"),
        ("2023-W39", "2023-Q3"),
        ("2023-W52", "2023-Q4"),
    ]

    test_cases[
        (TimeUnit.WEEK, TimeUnit.MONTH, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2022-W52", None),
        ("2023-W13", None),
        ("2023-W17", "2023-04"),
        ("2023-W26", None),
        ("2023-W39", None),
        ("2023-W52", "2023-12"),
    ]
    test_cases[
        (TimeUnit.WEEK, TimeUnit.MONTH, TimeUnitTransformStrategy.LARGEST_OVERLAP)
    ] = [
        ("2022-W52", "2022-12"),
        ("2023-W13", "2023-03"),
        ("2023-W17", "2023-04"),
        ("2023-W26", "2023-06"),
        ("2023-W39", "2023-09"),
        ("2023-W52", "2023-12"),
    ]

    test_cases[(TimeUnit.WEEK, TimeUnit.WEEK, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2024-W01", "2024-W01"),
    ]
    test_cases[(TimeUnit.WEEK, TimeUnit.DAY, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2024-W01", None),
    ]

    # DAY tests
    test_cases[(TimeUnit.DAY, TimeUnit.YEAR, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2023-01-01", "2023"),
    ]
    test_cases[
        (TimeUnit.DAY, TimeUnit.QUARTER, TimeUnitTransformStrategy.EXACT_ONLY)
    ] = [
        ("2023-01-01", "2023-Q1"),
    ]
    test_cases[(TimeUnit.DAY, TimeUnit.MONTH, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2023-01-01", "2023-01"),
    ]
    test_cases[(TimeUnit.DAY, TimeUnit.WEEK, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2021-01-01", "2020-W53"),
        ("2021-01-02", "2020-W53"),
        ("2021-01-03", "2020-W53"),
        ("2021-01-04", "2021-W01"),
        ("2022-01-01", "2021-W52"),
        ("2022-01-02", "2021-W52"),
        ("2022-01-03", "2022-W01"),
        ("2023-01-01", "2022-W52"),
        ("2023-01-02", "2023-W01"),
    ]
    test_cases[(TimeUnit.DAY, TimeUnit.DAY, TimeUnitTransformStrategy.EXACT_ONLY)] = [
        ("2023-01-01", "2023-01-01"),
    ]

    # Run all test cases
    for (src_unit, tgt_unit, strategy), test_data in test_cases.items():
        input_values = [x[0] for x in test_data]
        expected_outputs = [x[1] for x in test_data]
        actual_outputs = test_time_transform(src_unit, tgt_unit, strategy, input_values)
        assert_equal(actual_outputs, expected_outputs)


@pytest.mark.scenario_ids("TC-MAIN-12-01")
def test_tgt_field() -> None:
    """Test the target field name mapping."""
    # Target field equals source
    obj = ObjectAdapter({"date": "2023-01-01"})
    transformer = IsoTimeTransformer("date", TimeUnit.DAY, TimeUnit.MONTH)
    transformed = transformer.transform(obj)
    assert transformed.get("date") == "2023-01"
    # Different target field
    transformer = IsoTimeTransformer(
        "date", TimeUnit.DAY, TimeUnit.MONTH, tgt_field_name="month"
    )
    transformed = transformer.transform(obj)
    assert transformed.get("month") == "2023-01"
