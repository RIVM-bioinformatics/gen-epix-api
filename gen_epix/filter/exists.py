"""Filters that test whether values are present and non-null."""

from collections.abc import Callable, Hashable, Iterable
from typing import Any, Literal

from pydantic import BaseModel

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class ExistsFilter(Filter):
    """Represents a filter matching non-null, non-excluded values."""

    type: Literal[FilterType.EXISTS.value] = FilterType.EXISTS.value  # type: ignore[name-defined]

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
    ) -> Iterator[bool]:
        """Yield existence matches for each value in a column."""
        if na_values is None:
            for value in values:
                yield (value is not None) ^ self.invert
        else:
            for value in values:
                yield (value not in na_values) ^ self.invert

    def match_row(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> bool:
        """Return whether the filter key exists in a row with a value.

        Args:
            row: Row to inspect.
            na_values: Values treated as unavailable.
            map_fn: Ignored compatibility mapping argument.
            is_model: Whether the row is a model instance.

        Returns:
            Whether the configured key has a usable value.

        Raises:
            ValueError: If no row key is configured.
        """
        if self.key is None:
            raise ValueError("Key must be set to apply filter to a row.")
        key = self.key
        # Match if both key exists and value not null
        has_key = isinstance(key, str) and hasattr(row, key) if is_model else key in row
        value = self._get_row_value(row, key, is_model) if has_key else None
        if na_values is None:
            return (has_key and value is not None) ^ self.invert
        return (has_key and value not in na_values) ^ self.invert

    def match_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> Iterator[bool]:
        """Yield existence matches for each row.

        Args:
            rows: Rows to inspect.
            na_values: Values treated as unavailable.
            map_fn: Ignored compatibility mapping argument.
            is_model: Whether the rows are model instances.

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
        for row in rows:
            yield self.match_row(row, na_values=na_values, is_model=is_model)

    def _match(self, value: Any) -> bool:
        """Treat every supplied value as an existing value."""
        return True
