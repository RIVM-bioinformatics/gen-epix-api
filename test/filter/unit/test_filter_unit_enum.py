"""Verify the serialized values exposed by filter enums."""

import pytest

from gen_epix.filter.enum import ComparisonOperator, FilterType, LogicalOperator


@pytest.mark.parametrize(
    ("enum_type", "expected_members"),
    [
        pytest.param(
            FilterType,
            {
                "BASE": "BASE",
                "EXISTS": "EXISTS",
                "EQUALS_BOOLEAN": "EQUALS_BOOLEAN",
                "EQUALS_NUMBER": "EQUALS_NUMBER",
                "EQUALS_STRING": "EQUALS_STRING",
                "EQUALS_UUID": "EQUALS_UUID",
                "COMPOSITE": "COMPOSITE",
                "DATE_RANGE": "DATE_RANGE",
                "DATETIME_RANGE": "DATETIME_RANGE",
                "NUMBER_RANGE": "NUMBER_RANGE",
                "PARTIAL_DATE_RANGE": "PARTIAL_DATE_RANGE",
                "RANGE": "RANGE",
                "REGEX": "REGEX",
                "NUMBER_SET": "NUMBER_SET",
                "STRING_SET": "STRING_SET",
                "UUID_SET": "UUID_SET",
                "VALUE_SET": "VALUE_SET",
                "NO_FILTER": "NO_FILTER",
            },
            id="filter-types",
        ),
        pytest.param(
            LogicalOperator,
            {
                "AND": "AND",
                "OR": "OR",
                "NOT": "NOT",
                "XOR": "XOR",
                "NAND": "NAND",
                "NOR": "NOR",
                "XNOR": "XNOR",
                "IMPLIES": "IMPLIES",
                "NIMPLIES": "NIMPLIES",
            },
            id="logical-operators",
        ),
        pytest.param(
            ComparisonOperator,
            {
                "ST": "<",
                "STE": "<=",
                "EQ": "=",
                "GTE": ">=",
                "GT": ">",
                "NEQ": "!=",
            },
            id="comparison-operators",
        ),
    ],
)
def test_enum_members_preserve_serialized_values(enum_type, expected_members):
    assert {
        name: member.value for name, member in enum_type.__members__.items()
    } == expected_members
