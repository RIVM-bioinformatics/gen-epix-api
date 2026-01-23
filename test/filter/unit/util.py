from collections.abc import Callable, Hashable
from typing import Any

from gen_epix.filter.base import Filter
from gen_epix.filter.composite import CompositeFilter


def validate_filter_behavior(
    filter: Filter,
    rows: list[dict[Any, Any]],
    expected_results: list[bool],
    na_values: set[Any] | None = None,
    map_fn: dict[Hashable, Callable[[Any], Any]] | Callable[[Any], Any] | None = None,
) -> None:
    """
    Given a filter, list of rows, and expected results, this method validates that the provided filter
    behaves as expected for match_row, match_rows, match_value, and match_column, both with and without inversion.
    """
    orig_invert = filter.invert

    def _print_result() -> None:
        print("")
        print("Filter.match_row failed:")
        print(f"\tfilter class: {type(filter)}")
        print(f"\tfilter: {filter}")
        print(f"\tna_values: {na_values}")
        print(f"\tmap_fn: {map_fn}")
        print(f"\trow: {row}")
        print(f"\texpected result: {expected_result ^ invert} (invert={invert})")

    for invert in [False, True]:
        filter.invert = invert
        for row, expected_result in zip(rows, expected_results):
            result = filter.match_row(row, na_values=na_values, map_fn=map_fn)  # type: ignore[arg-type]
            if result == (expected_result ^ invert):
                continue
            _print_result()
            assert False
        for result, expected_result in zip(
            expected_results,
            filter.match_rows(rows, na_values=na_values, map_fn=map_fn),  # type: ignore[arg-type]
        ):
            if result == (expected_result ^ invert):
                continue
            _print_result()
            assert False
        if isinstance(filter, CompositeFilter):
            continue
        values = [x.get(filter.key) for x in rows]
        if map_fn and isinstance(map_fn, dict):
            map_fn = map_fn.get(filter.key)
        for value, expected_result in zip(values, expected_results):
            result = filter.match_value(value, na_values=na_values, map_fn=map_fn)  # type: ignore[arg-type]
            if result == (expected_result ^ invert):
                continue
            _print_result()
            assert False
        for result, expected_result in zip(
            filter.match_column(values, na_values=na_values, map_fn=map_fn),  # type: ignore[arg-type]
            expected_results,
        ):
            if result == (expected_result ^ invert):
                continue
            _print_result()
            assert False
    filter.invert = orig_invert
