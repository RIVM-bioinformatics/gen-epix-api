"""Filters that test whether values are present and non-null."""

from collections.abc import Callable, Hashable, Iterable
from typing import Any, Literal

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class ExistsFilter(Filter):
    """Represents a filter matching non-null, non-excluded values."""

    def match_value(
        self,
        value: Any | None,
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> bool:
        """Return whether a scalar value exists, respecting inversion."""
        if na_values is None:
            return (value is not None) ^ self.invert
        return (value not in na_values) ^ self.invert

    def match_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> Iterable[bool]:
        """Yield existence matches for each value in a column."""
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
        map_fn: Callable[[Any], Any] | None = None,
    ) -> bool:
        """Return whether the filter key exists in a row with a value.

        Args:
            row: Row to inspect.
            na_values: Values treated as unavailable.
            map_fn: Ignored compatibility mapping argument.

        Returns:
            Whether the configured key has a usable value.

        Raises:
            ValueError: If no row key is configured.
        """
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
        map_fn: Callable[[Any], Any] | None = None,
    ) -> Iterable[bool]:
        """Yield existence matches for each row.

        Args:
            rows: Rows to inspect.
            na_values: Values treated as unavailable.
            map_fn: Ignored compatibility mapping argument.

        Yields:
            Whether each row has a usable value at the configured key.

        Returns:
            An iterator over row match results.

        Raises:
            ValueError: If no row key is configured.
        """
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
        """Treat every supplied value as an existing value."""
        return True


class TypedExistsFilter(ExistsFilter):
    """Represents an existence filter carrying its serialized filter type."""

    type: Literal[FilterType.EXISTS.value]  # type: ignore[name-defined]
