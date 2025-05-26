from typing import Any, Callable, Hashable, Iterable, Literal

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class ExistsFilter(Filter):

    def match_value(
        self,
        value: Any | None,
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
    ) -> bool:
        if na_values is None:
            return (value is not None) ^ self.invert
        return (value not in na_values) ^ self.invert

    def match_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
    ) -> Iterable[bool]:
        if na_values is None:
            for value in values:
                yield (value is not None) ^ self.invert
        else:
            for value in values:
                yield (value not in na_values) ^ self.invert

    def match_row(
        self,
        row: dict[Hashable, Any | None],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
    ) -> bool:
        if self.key is None:
            raise ValueError("Key must be set to apply filter to a row.")
        # Match if both key exists and value not null
        key = self.key
        if na_values is None:
            return ((key in row) and (row[key] is not None)) ^ self.invert
        return ((key in row) and (row[key] not in na_values)) ^ self.invert

    def match_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None]],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
    ) -> Iterable[bool]:
        if self.key is None:
            raise ValueError("Key must be set to apply filter to a row.")
        # Match if both key exists and value not null
        key = self.key
        if na_values is None:
            for row in rows:
                yield ((key in row) and (row[key] is not None)) ^ self.invert
        else:
            for row in rows:
                yield ((key in row) and (row[key] not in na_values)) ^ self.invert

    def _match(self, value: Any) -> bool:
        return True


class TypedExistsFilter(ExistsFilter):
    type: Literal[FilterType.EXISTS.value]
