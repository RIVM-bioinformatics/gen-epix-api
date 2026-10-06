"""Unit tests for ExistsFilter."""

import uuid
from test.filter.unit import util

import numpy as np
import pytest
from pydantic import BaseModel

from gen_epix.filter import ExistsFilter


def test_exists_match() -> None:
    """Match values according to key presence and configured NA values."""
    filter_obj = ExistsFilter(key="a")
    rows = [{"a": value} for value in [None, np.nan, "", "null"]]
    util.validate_filter_behavior(filter_obj, rows, [False, True, True, True])
    util.validate_filter_behavior(
        filter_obj, rows, [True, True, True, True], na_values=set()
    )
    util.validate_filter_behavior(
        filter_obj, rows, [False, True, True, True], na_values={None}
    )
    util.validate_filter_behavior(
        filter_obj, rows, [True, False, True, True], na_values={np.nan}
    )
    util.validate_filter_behavior(
        filter_obj, rows, [True, True, False, True], na_values={""}
    )
    util.validate_filter_behavior(
        filter_obj, rows, [True, True, True, False], na_values={"null"}
    )
    util.validate_filter_behavior(
        filter_obj, rows, [False, False, True, True], na_values={None, np.nan}
    )
    util.validate_filter_behavior(
        filter_obj, rows, [True, False, False, True], na_values={np.nan, ""}
    )
    util.validate_filter_behavior(
        filter_obj, rows, [True, True, False, False], na_values={"", "null"}
    )

    filter_obj = ExistsFilter(key="b")
    rows = [{"a": value} for value in [None, np.nan, "", "null"]]
    util.validate_filter_behavior(filter_obj, rows, [False, False, False, False])

    class RowModel(BaseModel):
        """Represent a row with one optional value field."""

        value: str | None = None

    filter_obj = ExistsFilter(key="value")
    model_rows = [RowModel(value="present"), RowModel()]
    assert filter_obj.match_row(model_rows[0], is_model=True)
    assert not filter_obj.match_row(model_rows[1], is_model=True)
    assert list(filter_obj.match_rows(model_rows, is_model=True)) == [True, False]


@pytest.mark.parametrize(("invert", "expected"), [(False, False), (True, True)])
def test_exists_model_match_treats_non_string_key_as_absent(
    invert: bool, expected: bool
) -> None:
    """Treat unsupported model keys as absent, including when inverted."""

    class RowModel(BaseModel):
        """Represent a row model whose value field differs from the filter key."""

        value: str | None = None

    filter_obj = ExistsFilter(key=uuid.uuid4(), invert=invert)

    assert filter_obj.match_row(RowModel(value="present"), is_model=True) is expected
