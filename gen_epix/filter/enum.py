"""Enumerations used to identify filters and comparison semantics."""

from enum import Enum


class FilterType(Enum):
    """Serialized type names for the available filter models."""
    BASE = "BASE"
    EXISTS = "EXISTS"
    EQUALS_BOOLEAN = "EQUALS_BOOLEAN"
    EQUALS_NUMBER = "EQUALS_NUMBER"
    EQUALS_STRING = "EQUALS_STRING"
    EQUALS_UUID = "EQUALS_UUID"
    COMPOSITE = "COMPOSITE"
    DATE_RANGE = "DATE_RANGE"
    DATETIME_RANGE = "DATETIME_RANGE"
    NUMBER_RANGE = "NUMBER_RANGE"
    PARTIAL_DATE_RANGE = "PARTIAL_DATE_RANGE"
    RANGE = "RANGE"
    REGEX = "REGEX"
    NUMBER_SET = "NUMBER_SET"
    STRING_SET = "STRING_SET"
    UUID_SET = "UUID_SET"
    VALUE_SET = "VALUE_SET"
    NO_FILTER = "NO_FILTER"


class LogicalOperator(Enum):
    """Boolean operators supported by composite filters."""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    XOR = "XOR"
    NAND = "NAND"
    NOR = "NOR"
    XNOR = "XNOR"
    IMPLIES = "IMPLIES"
    NIMPLIES = "NIMPLIES"


class ComparisonOperator(Enum):
    """Boundary comparison operators supported by range filters."""
    ST = "<"
    STE = "<="
    EQ = "="
    GTE = ">="
    GT = ">"
    NEQ = "!="
