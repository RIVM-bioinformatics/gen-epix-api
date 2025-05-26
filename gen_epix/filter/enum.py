from enum import Enum


class FilterType(Enum):
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


class BooleanOperator(Enum):
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
    ST = "<"
    STE = "<="
    EQ = "="
    GTE = ">="
    GT = ">"
    NEQ = "!="
