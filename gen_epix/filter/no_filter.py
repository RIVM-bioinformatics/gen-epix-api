from typing import Any, Callable, Hashable, Iterable, Iterator, Literal

from pydantic import BaseModel

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class NoFilter(Filter):
    key: Literal[False] = False

    def _match(self, value: Any) -> bool:
        return not self.invert

    def match_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
    ) -> Iterator[bool]:
        for value in values:
            yield not self.invert

    def filter_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
    ) -> Iterator[Any | None]:
        for value in values:
            if not self.invert:
                yield value

    def match_row(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> bool:
        return not self.invert

    def match_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> Iterator[bool]:
        for row in rows:
            if not self.invert:
                yield True

    def filter_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> Iterator[dict[Hashable, Any | None]]:
        for row in rows:
            if not self.invert:
                yield row


class TypedNoFilter(NoFilter):
    type: Literal[FilterType.NO_FILTER.value]
