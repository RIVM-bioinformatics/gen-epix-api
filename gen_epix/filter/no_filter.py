"""Pass-through filter models that retain all input data."""

from collections.abc import Callable, Hashable, Iterable, Iterator
from typing import Any, Literal

from pydantic import BaseModel

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class NoFilter(Filter):
    """Match and retain every value unless explicitly inverted."""
    key: Literal[False] = False

    def _match(self, value: Any) -> bool:
        """Return the non-inverted pass-through result."""
        return not self.invert

    def match_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> Iterator[bool]:
        """Yield a pass-through match for every column value."""
        for value in values:
            yield not self.invert

    def filter_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> Iterator[Any | None]:
        """Yield every column value when the filter is not inverted."""
        for value in values:
            if not self.invert:
                yield value

    def match_row(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> bool:
        """Return the pass-through result for a row."""
        return not self.invert

    def match_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> Iterator[bool]:
        """Yield pass-through matches for rows when not inverted."""
        for row in rows:
            if not self.invert:
                yield True

    def filter_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> Iterator[dict[Hashable, Any | None]]:
        """Yield every row when the filter is not inverted."""
        for row in rows:
            if not self.invert:
                yield row


class TypedNoFilter(NoFilter):
    """Pass-through filter carrying its serialized filter type."""
    type: Literal[FilterType.NO_FILTER.value]  # type: ignore[name-defined]
