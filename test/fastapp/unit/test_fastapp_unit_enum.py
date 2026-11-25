"""Verify FastApp enum compatibility mappings."""

import pytest

from gen_epix.fastapp.enum import IsolationLevel


@pytest.mark.parametrize(
    ("isolation_level", "expected"),
    [
        (IsolationLevel.READ_UNCOMMITTED, "READ UNCOMMITTED"),
        (IsolationLevel.READ_COMMITTED, "READ COMMITTED"),
        (IsolationLevel.REPEATABLE_READ, "REPEATABLE READ"),
        (IsolationLevel.SERIALIZABLE, "SERIALIZABLE"),
        (IsolationLevel.SNAPSHOT, "SNAPSHOT"),
    ],
)
def test_isolation_level_has_sqlalchemy_compatible_value(
    isolation_level: IsolationLevel, expected: str
) -> None:
    """Map legacy enum members to accepted SQLAlchemy isolation names."""
    assert isolation_level.get_sqlalchemy_value() == expected
