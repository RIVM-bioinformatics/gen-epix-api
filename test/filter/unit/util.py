from typing import Any, Callable, Hashable

from gen_epix.filter.base import Filter
from gen_epix.filter.composite import CompositeFilter


def _test_filter(
    filter: Filter,
    rows: list,
    expected_results: list[bool],
    na_values: set[Any] | None = None,
    map_fun: dict[Hashable, Callable[[Any], Any]] | Callable[[Any], Any] | None = None,
) -> None:
    orig_invert = filter.invert

    def _print_result() -> None:
        print("")
        print("Filter.match_row failed:")
        print(f"\tfilter class: {type(filter)}")
        print(f"\tfilter: {filter}")
        print(f"\tna_values: {na_values}")
        print(f"\tmap_fun: {map_fun}")
        print(f"\trow: {row}")
        print(f"\texpected result: {expected_result ^ invert} (invert={invert})")
        ...

    for invert in [False, True]:
        filter.invert = invert
        for row, expected_result in zip(rows, expected_results):
            result = filter.match_row(row, na_values=na_values, map_fun=map_fun)
            if result == (expected_result ^ invert):
                continue
            _print_result()
            assert False
        for result, expected_result in zip(
            expected_results,
            filter.match_rows(rows, na_values=na_values, map_fun=map_fun),
        ):
            if result == (expected_result ^ invert):
                continue
            _print_result()
            assert False
        if isinstance(filter, CompositeFilter):
            continue
        values = [x.get(filter.key) for x in rows]
        if map_fun and isinstance(map_fun, dict):
            map_fun = map_fun.get(filter.key)
        for value, expected_result in zip(values, expected_results):
            result = filter.match_value(value, na_values=na_values, map_fun=map_fun)
            if result == (expected_result ^ invert):
                continue
            _print_result()
            assert False
        for result, expected_result in zip(
            filter.match_column(values, na_values=na_values, map_fun=map_fun),
            expected_results,
        ):
            if result == (expected_result ^ invert):
                continue
            _print_result()
            assert False
    filter.invert = orig_invert
