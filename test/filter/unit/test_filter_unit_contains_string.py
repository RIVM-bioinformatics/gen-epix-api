"""Tests for ContainsStringFilter matching."""

from test.filter.unit import util

import pytest
from pydantic import ValidationError

from gen_epix.filter.contains_string import ContainsStringFilter


def test_contains_string_filter_matches_case_sensitive_substrings() -> None:
    filter_obj = ContainsStringFilter(key="value", value="tag")
    values = ["a tag in text", "tag", "prefix tag suffix", "TAG", "missing", None]
    rows = [{"value": value} for value in values]

    util.validate_filter_behavior(
        filter_obj,
        rows,
        [True, True, True, False, False, False],
    )


def test_contains_string_filter_respects_na_values() -> None:
    filter_obj = ContainsStringFilter(key="value", value="unknown")
    rows = [{"value": "unknown"}, {"value": "unknown value"}, {"value": None}]

    util.validate_filter_behavior(
        filter_obj,
        rows,
        [False, True, False],
        na_values={"unknown", None},
    )


def test_contains_string_filter_rejects_empty_substring() -> None:
    with pytest.raises(ValidationError):
        ContainsStringFilter(value="")
