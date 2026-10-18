"""Define enum values shared by filter models and matching logic.

`FilterType` identifies serialized filter models; `LogicalOperator` and
`ComparisonOperator` define the operations they support.
"""

from enum import Enum


class FilterType(Enum):
    """Encapsulates serialized type names for the available filter models."""

    BASE = "BASE"
    COMPOSITE = "COMPOSITE"
    EXISTS = "EXISTS"
    EQUALS_BOOLEAN = "EQUALS_BOOLEAN"
    EQUALS_NUMBER = "EQUALS_NUMBER"
    EQUALS_STRING = "EQUALS_STRING"
    EQUALS_UUID = "EQUALS_UUID"
    CONTAINS_STRING = "CONTAINS_STRING"
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
    """Encapsulates boolean operators supported by composite filters."""

    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    XOR = "XOR"
    NAND = "NAND"
    NOR = "NOR"
    XNOR = "XNOR"
    IMPLIES = "IMPLIES"
    NIMPLIES = "NIMPLIES"


class LogicalOperatorSet(Enum):
    """Encapsulates sets of logical operators for composite filters."""

    UNARY = frozenset({LogicalOperator.NOT})
    BINARY = frozenset(
        {
            LogicalOperator.XOR,
            LogicalOperator.NAND,
            LogicalOperator.NOR,
            LogicalOperator.XNOR,
            LogicalOperator.IMPLIES,
            LogicalOperator.NIMPLIES,
        }
    )
    MULTARY = frozenset(
        {
            LogicalOperator.AND,
            LogicalOperator.OR,
        }
    )


class ComparisonOperator(Enum):
    """Encapsulates boundary comparison operators supported by range filters."""

    ST = "<"
    STE = "<="
    EQ = "="
    GTE = ">="
    GT = ">"
    NEQ = "!="
