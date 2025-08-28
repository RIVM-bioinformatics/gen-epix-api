from enum import Enum


class TestType(Enum):
    UNIT = "UNIT"
    INTEGRATION = "INTEGRATION"
    PERFORMANCE = "PERFORMANCE"
    OTHER = "OTHER"
    UNDEFINED = "UNDEFINED"


class RepositoryType(Enum):
    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"
