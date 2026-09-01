"""Define test-specific enum values for test type and repository backend selection."""

from enum import Enum


class TestType(Enum):
    """Classify the execution category of a commondb test."""

    UNIT = "UNIT"
    INTEGRATION = "INTEGRATION"
    PERFORMANCE = "PERFORMANCE"
    OTHER = "OTHER"
    UNDEFINED = "UNDEFINED"


class RepositoryType(Enum):
    """Identify the persistence backend used by commondb test configurations."""

    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"
