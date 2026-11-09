"""Logical composition of scalar and row filter expressions."""

# pylint: disable=protected-access
# because child filter internals are used to build the configured matchers

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
_RowMapFunction = (
    dict[Hashable, Callable[[Any], Any]]
    | Callable[[Any], Any]
    | list[Callable[[Any], Any]]
    | None
)


class CompositeFilter(Filter):
    """Represents a filter that combines child filters using a logical operator.

    Model validation:
    At least one child filter is required. `NOT` requires exactly one child, `AND`
    and `OR` accept any number of children, and all other operators require exactly
    two children.
    """

    type: Literal[enum.FilterType.COMPOSITE.value] = enum.FilterType.COMPOSITE.value  # type: ignore[name-defined]
    filters: list[FilterUnion | "CompositeFilter" | Filter] = Field(
        description="The list of filters.", min_length=1, frozen=True
    )
    key: str | None = Field(default=None)
    operator: enum.LogicalOperator = Field(
        default=enum.LogicalOperator.AND,
        description="The boolean operator for the composite filter.",
        frozen=True,
    )
    _is_composite: bool = True

    def _get_row_value(
        self, row: dict | BaseModel, key: Hashable, is_model: bool
    ) -> Any:
        """Get the value from the row, handling both dict and BaseModel."""
        if key is False:
            return None
        if is_model:
            return getattr(row, key, None)  # type: ignore[call-overload]
        assert isinstance(row, dict)
        return row.get(key, None)

    def _matches_row_with_map(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        map_fns: list[Callable[[Any], Any]],
        map_fn: _RowMapFunction,
        na_values: set[Any] | None,
        is_model: bool,
    ) -> bool:
        """Match one row using normalized value maps and optional NA values."""
        # Match, per row and filter, if both key exists, value not null and value matches
        row_iterator = (
            self._not_none_row_iterator(row, is_model)
            if na_values is None
            else self._not_na_row_iterator(row, na_values, is_model)
        )
        return (
            self._match_row(
                row_iterator,
                self._iter_mapped_row_values(row, map_fns, map_fn, is_model),
                is_model=is_model,
            )
            ^ self.invert
        )

    def get_depth(self) -> int:
        """Return the maximum number of nested composite filters.

        The root composite has depth one. Leaf filters do not add to the depth.
        """
        return 1 + max(
            (
                child_filter.get_depth()
                for child_filter in self.filters
                if isinstance(child_filter, CompositeFilter)
            ),
            default=0,
        )

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
        if (
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
        self._match, self._match_row = matcher_builders[self.operator]()  # type: ignore[method-assign]

    def _match_children_value(self, value: Any) -> list[bool]:
        """Return each child's value match, including its inversion setting."""
        return [child_filter.match_value(value) for child_filter in self.filters]

    def _match_child_row(
        self,
        value_exists: bool,
        value: Any,
        child_filter: FilterUnion | Filter,
        is_model: bool,
        map_fn: _RowMapFunction,
    ) -> bool:
        """Match one child against its row value, including inversion."""
        if child_filter._is_composite:
            assert isinstance(child_filter, CompositeFilter)
            return child_filter.match_row(value, map_fn=map_fn, is_model=is_model)
        return (value_exists and child_filter._match(value)) ^ child_filter.invert

    def _match_children_row(
        self,
        value_exists: Iterable[bool],
        values: Iterable[tuple[Any, _RowMapFunction]],
        is_model: bool,
    ) -> list[bool]:
        """Return each child's row match, including inversion and missing values."""
        return [
            self._match_child_row(exists, value, child_filter, is_model, map_fn)
            for exists, (value, map_fn), child_filter in zip(
                value_exists, values, self.filters
            )
        ]

    def _get_nested_map_fn(
        self, map_fn: _RowMapFunction, child_index: int
    ) -> _RowMapFunction:
        """Return the mapping specification to pass into a nested composite."""
        if isinstance(map_fn, dict):
            return map_fn
        if isinstance(map_fn, list):
            return map_fn[child_index]
        return map_fn

    def _iter_mapped_row_values(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        map_fns: list[Callable[[Any], Any]],
        map_fn: _RowMapFunction,
        is_model: bool,
    ) -> Iterator[tuple[Any, _RowMapFunction]]:
        """Yield mapped leaf values and rows with mappings for nested children."""
        for child_index, (child_filter, child_map_fn) in enumerate(
            zip(self.filters, map_fns)
        ):
            if child_filter._is_composite:
                yield row, self._get_nested_map_fn(map_fn, child_index)
            else:
                yield (
                    child_map_fn(self._get_row_value(row, child_filter.key, is_model)),
                    None,
                )

    @staticmethod
    def _match_binary_results(
        matches: list[bool], operator: enum.LogicalOperator
    ) -> bool:
        """Combine the two child results for a binary logical operator."""
        first_match, second_match = matches
        if operator == enum.LogicalOperator.XOR:
            return first_match != second_match
        if operator == enum.LogicalOperator.NAND:
            return not (first_match and second_match)
        if operator == enum.LogicalOperator.NOR:
            return not (first_match or second_match)
        if operator == enum.LogicalOperator.XNOR:
            return first_match == second_match
        if operator == enum.LogicalOperator.IMPLIES:
            return not first_match or second_match
        if operator == enum.LogicalOperator.NIMPLIES:
            return first_match and not second_match
        raise ValueError(f"Unsupported binary logical operator: {operator}")

    def _build_not_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the NOT operator."""
        return (
            lambda x: not self._match_children_value(x)[0],
            lambda value_exists, values, is_model: not self._match_children_row(
                value_exists, values, is_model
            )[0],
        )

    def _build_and_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the AND operator."""
        return (
            lambda x: all(self._match_children_value(x)),
            lambda value_exists, values, is_model: all(
                self._match_children_row(value_exists, values, is_model)
            ),
        )

    def _build_or_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the OR operator."""
        return (
            lambda value: any(self._match_children_value(value)),
            lambda value_exists, values, is_model: any(
                self._match_children_row(value_exists, values, is_model)
            ),
        )

    def _build_xor_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the XOR operator."""
        return (
            lambda x: self._match_binary_results(
                self._match_children_value(x), enum.LogicalOperator.XOR
            ),
            lambda value_exists, values, is_model: self._match_binary_results(
                self._match_children_row(value_exists, values, is_model),
                enum.LogicalOperator.XOR,
            ),
        )

    def _build_nand_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the NAND operator."""
        return (
            lambda x: self._match_binary_results(
                self._match_children_value(x), enum.LogicalOperator.NAND
            ),
            lambda value_exists, values, is_model: self._match_binary_results(
                self._match_children_row(value_exists, values, is_model),
                enum.LogicalOperator.NAND,
            ),
        )

    def _build_nor_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the NOR operator."""
        return (
            lambda x: self._match_binary_results(
                self._match_children_value(x), enum.LogicalOperator.NOR
            ),
            lambda value_exists, values, is_model: self._match_binary_results(
                self._match_children_row(value_exists, values, is_model),
                enum.LogicalOperator.NOR,
            ),
        )

    def _build_xnor_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the XNOR operator."""
        return (
            lambda x: self._match_binary_results(
                self._match_children_value(x), enum.LogicalOperator.XNOR
            ),
            lambda value_exists, values, is_model: self._match_binary_results(
                self._match_children_row(value_exists, values, is_model),
                enum.LogicalOperator.XNOR,
            ),
        )

    def _build_implies_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the IMPLIES operator."""
        return (
            lambda x: self._match_binary_results(
                self._match_children_value(x), enum.LogicalOperator.IMPLIES
            ),
            lambda value_exists, values, is_model: self._match_binary_results(
                self._match_children_row(value_exists, values, is_model),
                enum.LogicalOperator.IMPLIES,
            ),
        )

    def _build_nimplies_matchers(self) -> tuple[Callable, Callable]:
        """Build matchers for the NIMPLIES operator."""
        return (
            lambda x: self._match_binary_results(
                self._match_children_value(x), enum.LogicalOperator.NIMPLIES
            ),
            lambda value_exists, values, is_model: self._match_binary_results(
                self._match_children_row(value_exists, values, is_model),
                enum.LogicalOperator.NIMPLIES,
            ),
        )

    def _match(self, value: Any) -> bool:
        """Match a value using the function generated during validation.

        Args:
            value: The scalar value to match.

        Returns:
            Whether the value matches the configured composition.

        Raises:
            NotImplementedError: Always, until model validation supplies the function.
        """
        raise NotImplementedError(
            "Method is implemented dynamically in _validate_state"
        )

    def _match_row(  # pylint: disable=method-hidden
        self, value_exists: Iterable[bool], value: Iterable[Any], is_model: bool
    ) -> bool:
        """Match row values using the function generated during validation.

        Args:
            value_exists: Flags indicating whether each child value exists.
            value: Values to match against the child filters.
            is_model: Whether values originate from model rows.

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
        for child_filter in self.filters:
            if isinstance(child_filter, NoFilter):
                yield True
            elif child_filter._is_composite:
                assert isinstance(child_filter, CompositeFilter)
                yield all(child_filter._not_none_row_iterator(row, is_model))
            else:
                if is_model:
                    yield self._get_row_value(
                        row, child_filter.key, is_model
                    ) is not None
                else:
                    assert isinstance(row, dict)
                    yield (
                        child_filter.key in row
                        and self._get_row_value(row, child_filter.key, is_model)
                        is not None
                    )

    def _not_na_row_iterator(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        na_values: set[Any],
        is_model: bool = False,
    ) -> Generator:
        """Yield child-value presence flags while excluding configured NA values."""
        for child_filter in self.filters:
            if isinstance(child_filter, NoFilter):
                yield True
            elif child_filter._is_composite:
                assert isinstance(child_filter, CompositeFilter)
                yield all(child_filter._not_na_row_iterator(row, na_values, is_model))
            else:
                if is_model:
                    yield self._get_row_value(
                        row, child_filter.key, is_model
                    ) not in na_values
                else:
                    assert isinstance(row, dict)
                    yield (
                        child_filter.key in row
                        and self._get_row_value(row, child_filter.key, is_model)
                        not in na_values
                    )

    def _all_subfilters_have_key(self) -> bool:
        """Return whether every leaf filter has a key for row matching."""
        retval = True
        for child_filter in self.filters:
            if child_filter._is_composite:
                assert isinstance(child_filter, CompositeFilter)
                retval = retval and child_filter._all_subfilters_have_key()
            else:
                retval = retval and (
                    isinstance(child_filter, NoFilter) or child_filter.key is not None
                )
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
        map_fn_spec = map_fn
        map_fns = self._get_map_fun_list(map_fn_spec)
        if na_values is None:
            return (
                self._match_row(
                    self._not_none_row_iterator(row, is_model),
                    self._iter_mapped_row_values(row, map_fns, map_fn_spec, is_model),
                    is_model,
                )
                ^ self.invert
            )
            # yield (
            #     key in row_dict
            #     and row_dict[key] is not None
            #     and self._match(map_fn(row_dict[key]))
            # ) ^ self.invert
        return (
            self._match_row(
                self._not_na_row_iterator(row, na_values, is_model),
                self._iter_mapped_row_values(row, map_fns, map_fn_spec, is_model),
                is_model,
            )
            ^ self.invert
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
        map_fn_spec = map_fn
        map_fns = self._get_map_fun_list(map_fn_spec)
        if na_values is None:
            for row in rows:
                yield (
                    self._match_row(
                        self._not_none_row_iterator(row, is_model),
                        self._iter_mapped_row_values(
                            row, map_fns, map_fn_spec, is_model
                        ),
                        is_model,
                    )
                    ^ self.invert
                )
        else:
            for row in rows:
                yield (
                    self._match_row(
                        self._not_na_row_iterator(row, na_values, is_model),
                        self._iter_mapped_row_values(
                            row, map_fns, map_fn_spec, is_model
                        ),
                        is_model,
                    )
                    ^ self.invert
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
    ) -> Iterator[dict[Hashable, Any | None] | BaseModel]:
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
        map_fn_spec = map_fn
        map_fns = self._get_map_fun_list(map_fn_spec)
        for row in rows:
            if self._matches_row_with_map(
                row, map_fns, map_fn_spec, na_values, is_model
            ):
                yield row

    def get_keys(self) -> list[Hashable]:
        """Return leaf-filter keys in traversal order."""
        keys: list[Hashable] = []

        def _recursion(keys: list[Hashable], filters: list[Filter]) -> None:
            """Append leaf-filter keys from a nested filter collection."""
            for child_filter in filters:
                if isinstance(child_filter, CompositeFilter):
                    _recursion(keys, child_filter.filters)
                elif not isinstance(child_filter, NoFilter):
                    keys.append(child_filter.key)

        _recursion(keys, self.filters)
        return keys

    def set_keys(
        self, key_map: dict[Hashable, Hashable] | Callable[[Hashable], Hashable]
    ) -> Self:
        """Set leaf keys using a mapping or a key transformation function."""
        for child_filter in self.filters:
            if isinstance(child_filter, CompositeFilter):
                child_filter.set_keys(key_map)
            elif isinstance(key_map, dict):
                child_filter.set_key(key_map.get(child_filter.key, child_filter.key))
            else:
                child_filter.set_key(key_map)
        return self
