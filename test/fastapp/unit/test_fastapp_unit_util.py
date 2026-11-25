"""Test general FastApp utility functions."""

import pytest

from gen_epix.fastapp.util import serialize_id


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, None), (0, "0"), (False, "False"), ("", "")],
)
def test_serialize_id_only_treats_none_as_missing(
    value: object, expected: str | None
) -> None:
    """Serialize falsey identifiers while preserving None as the missing value."""
    assert serialize_id(value) == expected
