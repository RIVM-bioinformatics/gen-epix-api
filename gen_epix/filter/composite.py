"""Logical composition of scalar and row filter expressions."""

# pylint: disable=protected-access
# because the functions are dynamically generated in _is_valid

from __future__ import annotations

from collections.abc import Callable, Generator, Hashable, Iterable, Iterator
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator

from gen_epix.filter import enum
from gen_epix.filter.base import Filter
from gen_epix.filter.contains_string import ContainsStringFilter
from gen_epix.filter.date_range import DateRangeFilter
from gen_epix.filter.datetime_range import DatetimeRangeFilter
from gen_epix.filter.equals_boolean import EqualsBooleanFilter
from gen_epix.filter.equals_number import EqualsNumberFilter
from gen_epix.filter.equals_string import EqualsStringFilter
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.filter.exists import ExistsFilter
from gen_epix.filter.no_filter import NoFilter
from gen_epix.filter.number_range import NumberRangeFilter
from gen_epix.filter.number_set import NumberSetFilter
from gen_epix.filter.partial_date_range import PartialDateRangeFilter
from gen_epix.filter.regex import RegexFilter
from gen_epix.filter.string_set import StringSetFilter
from gen_epix.filter.uuid_set import UuidSetFilter

_ROW_FILTER_KEY_REQUIRED = "Key must be set for each filter to apply filter to a row."

FilterUnion = (
    ExistsFilter
    | EqualsBooleanFilter
    | EqualsNumberFilter
    | EqualsStringFilter
    | EqualsUuidFilter
    | ContainsStringFilter
    | NumberRangeFilter
    | DateRangeFilter
    | DatetimeRangeFilter
    | PartialDateRangeFilter
    | RegexFilter
    | NumberSetFilter
    | StringSetFilter
    | UuidSetFilter
    | NoFilter
)


class CompositeFilter(Filter):
    """Represents a filter that combines child filters using a logical operator.

    Model validation:
    At least one child filter is required. `NOT` requires exactly one child, `AND`
    and `OR` accept any number of children, and all other operators require exactly
    two children.
    """

    type: Literal[enum.FilterType.COMPOSITE.value] = enum.FilterType.COMPOSITE.value  # type: ignore[name-defined]
    filters: list[FilterUnion | Filter | CompositeFilter] = Field(
        description="The list of scalar or nested composite filters.",
        min_length=1,
        frozen=True,
    )
    key: str | None = Field(default=None)
    operator: enum.LogicalOperator = Field(
        default=enum.LogicalOperator.AND,
        description="The boolean operator for the composite filter.",
        frozen=True,
    )
    _is_composite: bool = True

    def is_within_max_depth(self, max_composite_depth: int) -> bool:
        """Check the maximum number of nested composite filters.

        The root composite has depth one. Leaf filters do not add to the depth.
        """
        if max_composite_depth < 0:
            raise ValueError("Maximum composite filter depth cannot be negative.")

        pending: list[tuple[CompositeFilter, int]] = [(self, 1)]
        while pending:
            composite_filter, depth = pending.pop()
            if depth > max_composite_depth:
                return False
            pending.extend(
                (child_filter, depth + 1)
                for child_filter in composite_filter.filters
                if isinstance(child_filter, CompositeFilter)
            )
        return True

    def _get_row_value(
        self, row: dict | BaseModel, key: Hashable, is_model: bool
    ) -> Any:
        """Get the value from the row, handling both dict and BaseModel."""
        if is_model:
            return getattr(row, key, None)
        return row.get(key, None)

    def _matches_row_with_map(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        map_fn: list[Callable[[Any], Any]],
        na_values: set[Any] | None,
        is_model: bool,
        nested_map_fn: (
            dict[Hashable, Callable[[Any], Any]]
            | Callable[[Any], Any]
            | list[Callable[[Any], Any]]
            | None
        ),
    ) -> bool:
        """Match one row using normalized value maps and optional NA values."""
        # Match, per row and filter, if both key exists, value not null and value matches
        row_iterator = (
            self._not_none_row_iterator(row, is_model)
            if na_values is None
            else self._not_na_row_iterator(row, na_values, is_model)
        )

        def map_child_value(
            child_filter: Filter, map_value: Callable[[Any], Any]
        ) -> Any:
            if isinstance(child_filter, CompositeFilter):
                return lambda: child_filter.match_row(
                    row,
                    na_values=na_values,
                    map_fn=nested_map_fn,
                    is_model=is_model,
                )
            return map_value(self._get_row_value(row, child_filter.key, is_model))

        mapped_values = (
            map_child_value(child_filter, map_value)
            for child_filter, map_value in zip(self.filters, map_fn)
        )
        return self._match_row(row_iterator, mapped_values) ^ self.invert

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        """Validate child-filter cardinality and build matching functions."""
        if len(self.filters) == 0:
            raise AssertionError("At least one filter must be set.")
        if (
            self.operator in enum.LogicalOperatorSet.UNARY.value
            and len(self.filters) != 1
        ):
            raise AssertionError("Only one filter may be set for NOT operator.")
        elif (
            self.operator in enum.LogicalOperatorSet.BINARY.value
            and len(self.filters) != 2
        ):
            raise AssertionError("Exactly two filters must be set for this operator.")
        self._configure_match_functions()
        return self

    def _configure_match_functions(self) -> None:
        """Assign optimized value and row matchers for the configured operator."""
        # Generate functions instead of defining them directly to optimize matching.
        # Analogously, generate a function for a separate value for each filter.
        matcher_builders = {
            enum.LogicalOperator.NOT: self._build_not_matchers,
            enum.LogicalOperator.AND: self._build_and_matchers,
            enum.LogicalOperator.OR: self._build_or_matchers,
            enum.LogicalOperator.XOR: self._build_xor_matchers,
            enum.LogicalOperator.NAND: self._build_nand_matchers,
            enum.LogicalOperator.NOR: self._build_nor_matchers,
            enum.LogicalOperator.XNOR: self._build_xnor_matchers,
            enum.LogicalOperator.IMPLIES: self._build_implies_matchers,
            enum.LogicalOperator.NIMPLIES: self._build_nimplies_matchers,
        }
        self._match, self._match_row = matcher_builders[self.operator]()

    def _match_child_value(
        self, filter: Filter, value_exists: bool, value: Any
    ) -> bool:
        """Match one scalar child using the parent's missing-value decision."""
        if isinstance(filter, CompositeFilter):
            return filter._match_scalar(value, value_exists)
        return (value_exists and filter._match(value)) ^ filter.invert

    def _match_scalar(self, value: Any, value_exists: bool) -> bool:
        """Evaluate this composite's scalar operator and its inversion."""
        return self._match(value, value_exists) ^ self.invert

    def _match_scalar_value(
        self,
        value: Any | None,
        na_values: set[Any] | None,
        map_fn: Callable[[Any], Any] | None,
    ) -> bool:
        """Apply one scalar's NA policy and mapping before evaluating children."""
        if not map_fn:
            map_fn = lambda x: x
        value_exists = (
            value is not None if na_values is None else value not in na_values
        )
        if value_exists:
            value = map_fn(value)
        return self._match_scalar(value, value_exists)

    def _match_child_row(self, filter: Filter, value_exists: bool, value: Any) -> bool:
        """Match one child filter, including inverted and nested filters."""
        if isinstance(filter, CompositeFilter):
            return bool(value())
        return (value_exists and filter._match(value)) ^ filter.invert

    def _build_not_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the NOT operator."""
        return (
            lambda x, value_exists=True: not self._match_child_value(
                self.filters[0], value_exists, x
            ),
            lambda x, y: not self._match_child_row(self.filters[0], next(x), next(y)),
        )

    def _build_and_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the AND operator."""
        return (
            lambda x, value_exists=True: all(
                self._match_child_value(filter, value_exists, x)
                for filter in self.filters
            ),
            lambda x, y: all(
                self._match_child_row(filter, value_exists, value)
                for value_exists, value, filter in zip(x, y, self.filters)
            ),
        )

    def _build_or_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the OR operator."""
        return (
            lambda x, value_exists=True: any(
                self._match_child_value(filter, value_exists, x)
                for filter in self.filters
            ),
            lambda x, y: any(
                self._match_child_row(filter, value_exists, value)
                for value_exists, value, filter in zip(x, y, self.filters)
            ),
        )

    def _build_xor_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the XOR operator."""
        return (
            lambda x, value_exists=True: self._match_child_value(
                self.filters[0], value_exists, x
            )
            != self._match_child_value(self.filters[1], value_exists, x),
            lambda x, y: self._match_child_row(self.filters[0], next(x), next(y))
            != self._match_child_row(self.filters[1], next(x), next(y)),
        )

    def _build_nand_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the NAND operator."""
        return (
            lambda x, value_exists=True: not (
                self._match_child_value(self.filters[0], value_exists, x)
                and self._match_child_value(self.filters[1], value_exists, x)
            ),
            lambda x, y: not (
                self._match_child_row(self.filters[0], next(x), next(y))
                and self._match_child_row(self.filters[1], next(x), next(y))
            ),
        )

    def _build_nor_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the NOR operator."""
        return (
            lambda x, value_exists=True: not (
                self._match_child_value(self.filters[0], value_exists, x)
                or self._match_child_value(self.filters[1], value_exists, x)
            ),
            lambda x, y: not (
                self._match_child_row(self.filters[0], next(x), next(y))
                or self._match_child_row(self.filters[1], next(x), next(y))
            ),
        )

    def _build_xnor_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the XNOR operator."""
        return (
            lambda x, value_exists=True: self._match_child_value(
                self.filters[0], value_exists, x
            )
            == self._match_child_value(self.filters[1], value_exists, x),
            lambda x, y: self._match_child_row(self.filters[0], next(x), next(y))
            == self._match_child_row(self.filters[1], next(x), next(y)),
        )

    def _build_implies_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the IMPLIES operator."""
        return (
            lambda x, value_exists=True: not self._match_child_value(
                self.filters[0], value_exists, x
            )
            or self._match_child_value(self.filters[1], value_exists, x),
            lambda x, y: not self._match_child_row(self.filters[0], next(x), next(y))
            or self._match_child_row(self.filters[1], next(x), next(y)),
        )

    def _build_nimplies_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the NIMPLIES operator."""
        return (
            lambda x, value_exists=True: self._match_child_value(
                self.filters[0], value_exists, x
            )
            and not self._match_child_value(self.filters[1], value_exists, x),
            lambda x, y: self._match_child_row(self.filters[0], next(x), next(y))
            and not self._match_child_row(self.filters[1], next(x), next(y)),
        )

    def _match(self, value: Any, value_exists: bool = True) -> bool:
        """Match a value using the function generated during validation.

        Args:
            value: The scalar value to match.
            value_exists: Whether the scalar is present under the caller's NA policy.

        Returns:
            Whether the value matches the configured composition.

        Raises:
            NotImplementedError: Always, until model validation supplies the function.
        """
        raise NotImplementedError(
            "Method is implemented dynamically in _validate_state"
        )

    def _match_row(self, value_exists: Iterable[bool], value: Iterable[Any]) -> bool:
        """Match row values using the function generated during validation.

        Args:
            value_exists: Flags indicating whether each child value exists.
            value: Values to match against the child filters.

        Returns:
            Whether the row values match the configured composition.

        Raises:
            NotImplementedError: Always, until model validation supplies the function.
        """
        raise NotImplementedError(
            "Method is implemented dynamically in _validate_state"
        )

    def _not_none_row_iterator(
        self, row: dict[Hashable, Any | None] | BaseModel, is_model: bool = False
    ) -> Generator:
        """Yield child-value presence flags while treating `None` as absent."""
        for filter in self.filters:  # type: ignore
            if filter._is_composite:
                yield all(filter._not_none_row_iterator(row, is_model))
            else:
                yield (
                    (is_model or filter.key in row)
                    and self._get_row_value(row, filter.key, is_model) is not None
                )

    def _not_na_row_iterator(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        na_values: set[Any],
        is_model: bool = False,
    ) -> Generator:
        """Yield child-value presence flags while excluding configured NA values."""
        for filter in self.filters:  # type: ignore
            if filter._is_composite:
                yield all(filter._not_na_row_iterator(row, na_values, is_model))
            else:
                yield (
                    (is_model or filter.key in row)
                    and self._get_row_value(row, filter.key, is_model) not in na_values
                )

    def _all_subfilters_have_key(self) -> bool:
        """Return whether every leaf filter has a key for row matching."""
        retval = True
        for filter in self.filters:
            if filter._is_composite:
                retval = retval and filter._all_subfilters_have_key()
            else:
                retval = retval and filter.key is not None
            if not retval:
                return retval
        return retval

    def _get_map_fun_list(
        self,
        map_fn: (
            dict[Hashable, Callable[[Any], Any]]
            | Callable[[Any], Any]
            | list[Callable[[Any], Any]]
            | None
        ) = None,
    ) -> list[Callable[[Any], Any]]:
        """Normalize row-value mappings to one function per child filter.

        Args:
            map_fn: A shared, per-key, or per-filter value mapping.

        Returns:
            A mapping function for each child filter.

        Raises:
            ValueError: If mappings are invalid or do not match the child-filter count.
        """
        if not map_fn:
            map_fn = [lambda x: x for _ in self.filters]
        elif isinstance(map_fn, dict):
            map_fn = [map_fn.get(x.key, lambda x: x) for x in self.filters]
        elif not isinstance(map_fn, list):
            map_fn = [map_fn for _ in self.filters]
        if not isinstance(map_fn, list):
            raise ValueError("map_fn must be a callable, a list or a dict.")
        if len(map_fn) != len(self.filters):
            raise ValueError("map_fn must have the same length as the filters list.")
        return map_fn

    def match_value(
        self,
        value: Any | None,
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> bool:
        """Return whether a scalar satisfies the composite filter."""
        return self._match_scalar_value(value, na_values, map_fn)

    def match_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> Iterator[bool]:
        """Yield whether each scalar satisfies the composite filter."""
        for value in values:
            yield self._match_scalar_value(value, na_values, map_fn)

    def filter_column(
        self,
        values: Iterable[Any | None],
        na_values: set[Any] | None = None,
        map_fn: Callable[[Any], Any] | None = None,
    ) -> Iterator[Any | None]:
        """Yield scalar values that satisfy the composite filter."""
        for value in values:
            if self._match_scalar_value(value, na_values, map_fn):
                yield value

    def match_row(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        na_values: set[Any] | None = None,
        map_fn: (
            Callable[[Any], Any]
            | dict[Hashable, Callable[[Any], Any]]
            | list[Callable[[Any], Any]]
            | None
        ) = None,
        is_model: bool = False,
    ) -> bool:
        """Return whether a row satisfies the composite filter.

        Args:
            row: Mapping or model row to match.
            na_values: Values treated as unavailable.
            map_fn: A shared, per-key, or per-filter value mapping.
            is_model: Whether `row` is a model instance.

        Returns:
            Whether the row satisfies the configured composition.

        Raises:
            ValueError: If a child filter lacks a row key or mappings are invalid.
        """
        if not self._all_subfilters_have_key():
            raise ValueError(_ROW_FILTER_KEY_REQUIRED)
        # Match, per filter, if both key exists, value not null and value matches
        nested_map_fn = map_fn
        map_fn = self._get_map_fun_list(map_fn)
        return self._matches_row_with_map(
            row, map_fn, na_values, is_model, nested_map_fn
        )

    def match_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fn: (
            dict[Hashable, Callable[[Any], Any]]
            | Callable[[Any], Any]
            | list[Callable[[Any], Any]]
            | None
        ) = None,
        is_model: bool = False,
    ) -> Iterator[bool]:
        """Yield composite matches for each row.

        Args:
            rows: Rows to match.
            na_values: Values treated as unavailable.
            map_fn: A shared, per-key, or per-filter value mapping.
            is_model: Whether rows are model instances.

        Yields:
            Whether each row satisfies the configured composition.

        Returns:
            An iterator over row match results.

        Raises:
            ValueError: If a child filter lacks a row key or mappings are invalid.
        """
        # Match, per row and filter, if both key exists, value not null and value matches
        if not self._all_subfilters_have_key():
            raise ValueError(_ROW_FILTER_KEY_REQUIRED)
        nested_map_fn = map_fn
        map_fn = self._get_map_fun_list(map_fn)
        for row in rows:
            yield self._matches_row_with_map(
                row, map_fn, na_values, is_model, nested_map_fn
            )

    def filter_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fn: (
            dict[Hashable, Callable[[Any], Any]]
            | Callable[[Any], Any]
            | list[Callable[[Any], Any]]
            | None
        ) = None,
        is_model: bool = False,
    ) -> Iterator[dict[Hashable, Any | None]]:
        """Yield rows that satisfy the composite filter.

        Args:
            rows: Rows to filter.
            na_values: Values treated as unavailable.
            map_fn: A shared, per-key, or per-filter value mapping.
            is_model: Whether rows are model instances.

        Yields:
            Rows that satisfy the configured composition.

        Returns:
            An iterator over matching rows.

        Raises:
            ValueError: If a child filter lacks a row key or mappings are invalid.
        """
        if not self._all_subfilters_have_key():
            raise ValueError(_ROW_FILTER_KEY_REQUIRED)
        nested_map_fn = map_fn
        map_fn = self._get_map_fun_list(map_fn)
        for row in rows:
            if self._matches_row_with_map(
                row, map_fn, na_values, is_model, nested_map_fn
            ):
                yield row

    def get_keys(self) -> list[Hashable]:
        """Return leaf-filter keys in traversal order."""
        keys = []

        def _recursion(keys: list, filters: list[Filter]) -> None:
            """Append leaf-filter keys from a nested filter collection."""
            for filter in filters:
                if isinstance(filter, CompositeFilter):
                    _recursion(keys, filter.filters)
                else:
                    keys.append(filter.key)

        _recursion(keys, self.filters)
        return keys

    def set_keys(
        self, key_map: dict[Hashable, Hashable] | Callable[[Hashable], Hashable]
    ) -> Self:
        """Set leaf keys using a mapping or a key transformation function."""
        for filter in self.filters:
            if isinstance(filter, CompositeFilter):
                filter.set_keys(key_map)
            elif isinstance(key_map, dict):
                filter.set_key(key_map.get(filter.key, filter.key))
            else:
                filter.set_key(key_map)
        return self
