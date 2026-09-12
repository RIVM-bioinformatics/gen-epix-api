"""Base abstractions for scalar, column, and row filters."""

import abc
from collections.abc import Callable, Hashable, Iterable, Iterator
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, Field, WithJsonSchema

from gen_epix.filter.enum import FilterType


class Filter(BaseModel):
    """
    Represents a filter.

    This is a base class from which all actual filter implementations inherit.

    Attributes:
        invert (bool): Whether to invert the filter.
        key (Hashable | None): The column key to apply the filter to, when applied to a row. If None, the filter cannot be applied to a row, only to a column.
    """

    invert: bool = Field(default=False, description="Whether to invert the filter.")
    key: Annotated[
        Hashable | None,
        WithJsonSchema({"type": "string"}),
    ] = Field(
        default=None,
        description="The column key to apply the filter to, when applied to a row. If None, the filter cannot be applied to a row, only to a column.",
        json_schema_extra={"type": "string"},
    )
    type: Literal[FilterType.BASE.value] = FilterType.BASE.value  # type: ignore[name-defined]
    _is_composite: bool = False

    @property
    def is_composite(self) -> bool:
        """Return whether this filter combines multiple child filters."""
        return self._is_composite

    def _get_row_value(
        self, row: dict | BaseModel, key: Hashable, is_model: bool
    ) -> Any:
        """Get a value from either a mapping row or a model row."""
        if is_model:
            return getattr(row, key, None)
        return row.get(key, None)

    def match_value(
        self,
        value: Any | None,
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> bool:
        """
        Check if a value matches the filter.

        Args:
            value (Any | None): The value to be checked.
            na_values (set[Any] | None, optional): Set of values to be considered as NA values. Defaults to None.
            map_fn (Callable[[Any], Any] | None, optional): Function to be applied to the value before matching. Defaults to None.

        Returns:
            bool: True if the value matches the filter, False otherwise.
        """
        if not map_fn:
            map_fn = lambda x: x
        if na_values is None:
            return (value is not None and self._match(map_fn(value))) ^ self.invert
        else:
            return (value not in na_values and self._match(map_fn(value))) ^ self.invert

    def match_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> Iterator[bool]:
        """
        Check if each value in a column matches the filter.

        Args:
            values (Iterable[Any | None]): The values in the column.
            na_values (set[Any] | None, optional): Set of values to be considered as NA values. Defaults to None.
            map_fn (Callable[[Any], Any] | None, optional): Function to be applied to each value before matching. Defaults to None.

        Yields:
            bool: True if the value matches the filter, False otherwise.
        """
        if not map_fn:
            map_fn = lambda x: x
        if na_values is None:
            for value in values:
                yield (value is not None and self._match(map_fn(value))) ^ self.invert
        else:
            for value in values:
                yield (value not in na_values) ^ self.invert

    def filter_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> Iterator[Any | None]:
        """Yield column values that match the filter."""
        if not map_fn:
            map_fn = lambda x: x
        if na_values is None:
            for value in values:
                if (value is not None and self._match(map_fn(value))) ^ self.invert:
                    yield value
        else:
            for value in values:
                if (value not in na_values) ^ self.invert:
                    yield value

    def match_row(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> bool:
        """
        Check if a row matches the filter.

        Args:
            row (dict[Hashable, Any | None]): The row to be checked.
            na_values (set[Any] | None, optional): Set of values to be considered as NA values. Defaults to None.
            map_fn (Callable[[Any], Any] | None, optional): Function to be applied to each value before matching. Defaults to None.
            is_model (bool, optional): Whether each row is a model instance. Defaults to False.

        Returns:
            bool: True if the row matches the filter, False otherwise.
        """
        # Match if both key exists, value not null and value matches
        map_fn, key = self._initialize_mapping(map_fn)
        if na_values is None:
            return self._is_row_match_without_na_values(row, is_model, map_fn, key)
        return self._is_row_match_with_na_values(row, is_model, map_fn, key, na_values)

    def match_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> Iterator[bool]:
        """
        Check if each row in a collection of rows matches the filter.

        Args:
            rows (Iterable[dict[Hashable, Any | None]]): The collection of rows.
            na_values (set[Any] | None, optional): Set of values to be considered as NA values. Defaults to None.
            map_fn (Callable[[Any], Any] | None, optional): Function to be applied to each value before matching. Defaults to None.
            is_model (bool, optional): Whether each row is a model instance. Defaults to False.

        Yields:
            bool: True if the row matches the filter, False otherwise.
        """
        map_fn, key = self._initialize_mapping(map_fn)
        for row in rows:
            if na_values is None:
                yield self._is_row_match_without_na_values(row, is_model, map_fn, key)
            else:
                yield self._is_row_match_with_na_values(
                    row, is_model, map_fn, key, na_values
                )

    def filter_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> Iterator[dict[Hashable, Any | None] | BaseModel]:
        """Yield rows that match the filter."""
        map_fn, key = self._initialize_mapping(map_fn)
        for row in rows:
            if na_values is None:
                if self._is_row_match_without_na_values(row, is_model, map_fn, key):
                    yield row
            else:
                if self._is_row_match_with_na_values(
                    row, is_model, map_fn, key, na_values
                ):
                    yield row

    def _is_row_match_without_na_values(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        is_model: bool,
        map_fn: Callable[[Any], Any],
        key: Hashable,
    ) -> bool:
        """Return whether the configured key matches in a row without NA values."""
        if (
            (is_model or key in row)
            and self._get_row_value(row, key, is_model) is not None
            and self._match(map_fn(self._get_row_value(row, key, is_model)))
        ) ^ self.invert:
            return True
        return False

    def _is_row_match_with_na_values(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        is_model: bool,
        map_fn: Callable[[Any], Any],
        key: Hashable,
        na_values: set[Any],
    ) -> bool:
        """Return whether the configured key matches while excluding NA values."""
        if (
            (is_model or key in row)
            and self._get_row_value(row, key, is_model) not in na_values
            and self._match(map_fn(self._get_row_value(row, key, is_model)))
        ) ^ self.invert:
            return True
        return False

    def _initialize_mapping(
        self, map_fn: Callable[[Any], Any] | None
    ) -> tuple[Callable[[Any], Any], Hashable]:
        """Validate the row key and return the mapping function and key.

        Args:
            map_fn: Optional mapping applied before matching a row value.

        Returns:
            The mapping function and configured row key.

        Raises:
            ValueError: If no row key is configured.
        """
        if self.key is None:
            raise ValueError("Key must be set to apply filter to a row.")
        if not map_fn:
            map_fn = lambda x: x
        key = self.key
        return map_fn, key

    @abc.abstractmethod
    def _match(self, value: Any) -> bool:
        """Return whether a scalar value matches this filter.

        Args:
            value: The value to check.

        Returns:
            Whether the value matches the filter.

        Raises:
            NotImplementedError: Always, because subclasses provide matching logic.
        """
        raise NotImplementedError()

    def set_key(self, key: Hashable | Callable[[Hashable], Hashable]) -> Self:
        """Set the row key directly or transform the existing key."""
        if callable(key):
            self.key = key(self.key)
        else:
            self.key = key
        return self

    def get_key(self) -> Hashable:
        """Return the key configured for row matching."""
        return self.key

    def __call__(
        self,
        data: Iterable[Any],
        axis: int = 1,
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> Iterator[Any]:
        """
        Apply filter to data.

        Args:
            data (Iterable[Any]): The data to be filtered.
            axis (int, optional): The axis along which to apply the filter. 0 for rows, 1 for columns. Defaults to 1.
            na_values (set[Any] | None, optional): Set of values to be considered as NA values. Defaults to None.
            map_fn (Callable[[Any], Any] | None, optional): Function to be applied to each value before matching. Defaults to None.

        Returns:
            An iterator containing the values that match this filter.

        Raises:
            ValueError: If `axis` is not zero or one.
        """
        if axis == 0:
            return self.filter_rows(data, na_values=na_values, map_fn=map_fn)
        if axis == 1:
            return self.filter_column(data, na_values=na_values, map_fn=map_fn)
        raise ValueError("Axis must be 0 or 1.")
