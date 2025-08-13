import abc
from typing import Annotated, Any, Callable, Hashable, Iterable, Iterator, Literal, Self

from pydantic import BaseModel, Field, WithJsonSchema

from gen_epix.filter.enum import FilterType


class Filter(BaseModel):
    """
    Base class for filters.

    Attributes:
        invert (bool): Whether to invert the filter.
        key (Union[Hashable, None]): The column key to apply the filter to, when applied to a row. If None, the filter cannot be applied to a row, only to a column.
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
    _is_composite: bool = False

    @property
    def is_composite(self) -> bool:
        return self._is_composite

    def _get_row_value(
        self, row: dict | BaseModel, key: Hashable, is_model: bool
    ) -> Any:
        """Helper method to get a attribute value from a row model"""
        if is_model:
            return getattr(row, key, None)
        return row.get(key, None)

    def match_value(
        self,
        value: Any | None,
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
    ) -> bool:
        """
        Check if a value matches the filter.

        Args:
            value (Any | None): The value to be checked.
            na_values (set[Any] | None, optional): Set of values to be considered as NA values. Defaults to None.
            map_fun (Callable[[Any], Any] | None, optional): Function to be applied to the value before matching. Defaults to None.

        Returns:
            bool: True if the value matches the filter, False otherwise.
        """
        if not map_fun:
            map_fun = lambda x: x
        if na_values is None:
            return (value is not None and self._match(map_fun(value))) ^ self.invert
        else:
            return (
                value not in na_values and self._match(map_fun(value))
            ) ^ self.invert

    def match_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
    ) -> Iterator[bool]:
        """
        Check if each value in a column matches the filter.

        Args:
            values (Iterable[Any | None]): The values in the column.
            na_values (set[Any] | None, optional): Set of values to be considered as NA values. Defaults to None.
            map_fun (Callable[[Any], Any] | None, optional): Function to be applied to each value before matching. Defaults to None.

        Yields:
            bool: True if the value matches the filter, False otherwise.
        """
        if not map_fun:
            map_fun = lambda x: x
        if na_values is None:
            for value in values:
                yield (value is not None and self._match(map_fun(value))) ^ self.invert
        else:
            for value in values:
                yield (value not in na_values) ^ self.invert

    def filter_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
    ) -> Iterator[Any | None]:
        """
        Analogous to match_column, but yields the values that match the filter instead of a bool.
        """
        if not map_fun:
            map_fun = lambda x: x
        if na_values is None:
            for value in values:
                if (value is not None and self._match(map_fun(value))) ^ self.invert:
                    yield value
        else:
            for value in values:
                if (value not in na_values) ^ self.invert:
                    yield value

    def match_row(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> bool:
        """
        Check if a row matches the filter.

        Args:
            row (dict[Hashable, Any | None]): The row to be checked.
            na_values (set[Any] | None, optional): Set of values to be considered as NA values. Defaults to None.
            map_fun (Callable[[Any], Any] | None, optional): Function to be applied to each value before matching. Defaults to None.

        Returns:
            bool: True if the row matches the filter, False otherwise.
        """
        # Match if both key exists, value not null and value matches
        if self.key is None:
            raise ValueError("Key must be set to apply filter to a row.")
        if not map_fun:
            map_fun = lambda x: x
        key = self.key
        if na_values is None:
            return (
                (is_model or key in row)
                and self._get_row_value(row, key, is_model) is not None
                and self._match(map_fun(self._get_row_value(row, key, is_model)))
            ) ^ self.invert
        else:
            return (
                (is_model or key in row)
                and self._get_row_value(row, key, is_model) not in na_values
                and self._match(map_fun(self._get_row_value(row, key, is_model)))
            ) ^ self.invert

    def match_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> Iterator[bool]:
        """
        Check if each row in a collection of rows matches the filter.

        Args:
            rows (Iterable[dict[Hashable, Any | None]]): The collection of rows.
            na_values (set[Any] | None, optional): Set of values to be considered as NA values. Defaults to None.
            map_fun (Callable[[Any], Any] | None, optional): Function to be applied to each value before matching. Defaults to None.

        Yields:
            bool: True if the row matches the filter, False otherwise.
        """
        # Match if both key exists, value not null and value matches
        if self.key is None:
            raise ValueError("Key must be set to apply filter to a row.")
        if not map_fun:
            map_fun = lambda x: x
        key = self.key
        if na_values is None:
            for row in rows:
                yield (
                    (is_model or key in row)
                    and self._get_row_value(row, key, is_model) is not None
                    and self._match(map_fun(self._get_row_value(row, key, is_model)))
                ) ^ self.invert
        else:
            for row in rows:
                yield (
                    (is_model or key in row)
                    and self._get_row_value(row, key, is_model) not in na_values
                    and self._match(map_fun(self._get_row_value(row, key, is_model)))
                ) ^ self.invert

    def filter_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
        is_model: bool = False,
    ) -> Iterator[dict[Hashable, Any | None]]:
        """
        Analogous to match_rows, but yields the rows that match the filter instead of a bool.
        """
        # Match if both key exists, value not null and value matches
        if self.key is None:
            raise ValueError("Key must be set to apply filter to a row.")
        if not map_fun:
            map_fun = lambda x: x
        key = self.key
        if na_values is None:
            for row in rows:
                if (
                    (is_model or key in row)
                    and self._get_row_value(row, key, is_model) is not None
                    and self._match(map_fun(self._get_row_value(row, key, is_model)))
                ) ^ self.invert:
                    yield row
        else:
            for row in rows:
                if (
                    (is_model or key in row)
                    and self._get_row_value(row, key, is_model) not in na_values
                    and self._match(map_fun(self._get_row_value(row, key, is_model)))
                ) ^ self.invert:
                    yield row

    @abc.abstractmethod
    def _match(self, value: Any) -> bool:
        """
        Abstract method to be implemented by subclasses.
        Checks if a value matches the filter.

        Args:
            value (Any): The value to be checked.

        Returns:
            bool: True if the value matches the filter, False otherwise.
        """
        raise NotImplementedError()

    def set_key(self, key: Hashable | Callable[[Hashable], Hashable]) -> Self:
        if callable(key):
            self.key = key(self.key)
        else:
            self.key = key
        return self

    def get_key(self) -> Hashable:
        return self.key

    def __call__(
        self,
        data: Iterable[Any],
        axis: int = 1,
        na_values: set[Any] | None = None,
        map_fun: Callable[[Any], Any] | None = None,
    ) -> Iterator[Any]:
        """
        Apply filter to data.

        Args:
            data (Iterable[Any]): The data to be filtered.
            axis (int, optional): The axis along which to apply the filter. 0 for rows, 1 for columns. Defaults to 1.
            na_values (set[Any] | None, optional): Set of values to be considered as NA values. Defaults to None.
            map_fun (Callable[[Any], Any] | None, optional): Function to be applied to each value before matching. Defaults to None.

        Returns:
            Iterable[bool]: An iterable of booleans for each row, True if the data matches the filter, False otherwise.
        """
        if axis == 0:
            return self.filter_rows(data, na_values=na_values, map_fun=map_fun)
        if axis == 1:
            return self.filter_column(data, na_values=na_values, map_fun=map_fun)
        raise ValueError("Axis must be 0 or 1.")


class TypedFilter(Filter):
    type: Literal[FilterType.BASE.value]
