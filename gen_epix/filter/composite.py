# pylint: disable=protected-access
# because the functions are dynamically generated in _is_valid

from __future__ import annotations

from typing import (
    Annotated,
    Any,
    Callable,
    Generator,
    Hashable,
    Iterable,
    Iterator,
    Literal,
    Self,
)

from pydantic import BaseModel, Field, model_validator

from gen_epix.filter import enum
from gen_epix.filter.base import Filter
from gen_epix.filter.date_range import DateRangeFilter, TypedDateRangeFilter
from gen_epix.filter.datetime_range import DatetimeRangeFilter, TypedDatetimeRangeFilter
from gen_epix.filter.equals_boolean import EqualsBooleanFilter, TypedEqualsBooleanFilter
from gen_epix.filter.equals_number import EqualsNumberFilter, TypedEqualsNumberFilter
from gen_epix.filter.equals_string import EqualsStringFilter, TypedEqualsStringFilter
from gen_epix.filter.equals_uuid import EqualsUuidFilter, TypedEqualsUuidFilter
from gen_epix.filter.exists import ExistsFilter, TypedExistsFilter
from gen_epix.filter.no_filter import NoFilter, TypedNoFilter
from gen_epix.filter.number_range import NumberRangeFilter, TypedNumberRangeFilter
from gen_epix.filter.number_set import NumberSetFilter, TypedNumberSetFilter
from gen_epix.filter.partial_date_range import (
    PartialDateRangeFilter,
    TypedPartialDateRangeFilter,
)
from gen_epix.filter.regex import RegexFilter, TypedRegexFilter
from gen_epix.filter.string_set import StringSetFilter, TypedStringSetFilter
from gen_epix.filter.uuid_set import TypedUuidSetFilter, UuidSetFilter


class CompositeFilter(Filter):
    filters: list[
        ExistsFilter
        | EqualsBooleanFilter
        | EqualsNumberFilter
        | EqualsStringFilter
        | EqualsUuidFilter
        | NumberRangeFilter
        | DateRangeFilter
        | DatetimeRangeFilter
        | PartialDateRangeFilter
        | RegexFilter
        | NumberSetFilter
        | StringSetFilter
        | UuidSetFilter
        | NoFilter
        | CompositeFilter
    ] = Field(description="The list of filters.", min_length=1, frozen=True)
    key: str | None = Field(default=None)
    operator: enum.BooleanOperator = Field(
        default=enum.BooleanOperator.AND,
        description="The boolean operator for the composite filter.",
        frozen=True,
    )
    _is_composite: bool = True

    def _get_row_value(
        self, row: dict | BaseModel, key: Hashable, is_model: bool
    ) -> Any:
        """Get the value from the row, handling both dict and BaseModel."""
        if is_model:
            return getattr(row, key, None)
        return row.get(key, None)

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if len(self.filters) == 0:
            raise AssertionError("At least one filter must be set.")
        if self.operator == enum.BooleanOperator.NOT and len(self.filters) != 1:
            raise AssertionError("Only one filter may be set for NOT operator.")
        if len(self.filters) > 2 and self.operator not in {
            enum.BooleanOperator.AND,
            enum.BooleanOperator.OR,
        }:
            raise AssertionError("operator must be AND or OR for more than 2 filters.")
        # Generate the function to check if a value matches the composite filter
        # The function is generated instead of defined to be able to optimize the check
        # Analogously, generate the function to check if a separate value for each
        # filter
        if self.operator == enum.BooleanOperator.NOT:
            self._match = lambda x: not self.filters[0]._match(x)  # type: ignore
            self._match_row = lambda x, y: x and not self.filters[0]._match(next(y))  # type: ignore
        elif self.operator == enum.BooleanOperator.AND:
            self._match = lambda x: all(filter._match(x) for filter in self.filters)  # type: ignore
            # TODO: improve performance by not using filter.match_row for nested composite filter
            self._match_row = lambda x, y: all(  # type: ignore
                a
                and (filter.match_row(b) if filter._is_composite else filter._match(b))
                for a, b, filter in zip(x, y, self.filters)
            )
        elif self.operator == enum.BooleanOperator.OR:
            self._match = lambda x: any(filter._match(x) for filter in self.filters)  # type: ignore
            # TODO: improve performance by not using filter.match_row for nested composite filter
            self._match_row = lambda x, y: any(  # type: ignore
                a
                and (filter.match_row(b) if filter._is_composite else filter._match(b))
                for a, b, filter in zip(x, y, self.filters)
            )
        elif self.operator == enum.BooleanOperator.XOR:
            self._match = lambda x: self.filters[0]._match(x) != self.filters[1]._match(  # type: ignore
                x
            )
            self._match_row = lambda x, y: all(x) and self.filters[0]._match(  # type: ignore
                next(y)  # type: ignore
            ) != self.filters[
                1
            ]._match(
                next(y)  # type: ignore
            )
        elif self.operator == enum.BooleanOperator.NAND:
            self._match = lambda x: not (  # type: ignore
                self.filters[0]._match(x) and self.filters[1]._match(x)
            )
            self._match_row = lambda x, y: all(x) and not (  # type: ignore
                self.filters[0]._match(next(y)) and self.filters[1]._match(next(y))  # type: ignore
            )
        elif self.operator == enum.BooleanOperator.NOR:
            self._match = lambda x: not (  # type: ignore
                self.filters[0]._match(x) or self.filters[1]._match(x)
            )
            self._match_row = lambda x, y: all(x) and not (  # type: ignore
                self.filters[0]._match(next(y)) or self.filters[1]._match(next(y))  # type: ignore
            )
        elif self.operator == enum.BooleanOperator.XNOR:
            self._match = lambda x: self.filters[0]._match(x) == self.filters[1]._match(  # type: ignore
                x
            )
            self._match_row = lambda x, y: all(x) and self.filters[0]._match(  # type: ignore
                next(y)  # type: ignore
            ) == self.filters[
                1
            ]._match(
                next(y)  # type: ignore
            )
        elif self.operator == enum.BooleanOperator.IMPLIES:
            self._match = lambda x: (  # type: ignore
                not self.filters[0]._match(x) or self.filters[1]._match(x)
            )
            self._match_row = lambda x, y: all(x) and (  # type: ignore
                not self.filters[0]._match(next(y)) or self.filters[1]._match(next(y))  # type: ignore
            )
        elif self.operator == enum.BooleanOperator.NIMPLIES:
            self._match = lambda x: (  # type: ignore
                self.filters[0]._match(x) and not self.filters[1]._match(x)
            )
            self._match_row = lambda x, y: all(x) and (  # type: ignore
                self.filters[0]._match(next(y)) and not self.filters[1]._match(next(y))  # type: ignore
            )

        return self

    def _match(self, value: Any) -> bool:
        # Function is implemented dynamically in _validate_state
        raise NotImplementedError()

    def _match_row(
        self, value_exists: Iterable[bool], value: Iterable[Any], is_model: bool
    ) -> bool:
        # Function is implemented dynamically in _validate_state
        raise NotImplementedError()

    def _not_none_row_iterator(
        self, row: dict[Hashable, Any | None] | BaseModel, is_model: bool = False
    ) -> Generator:
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
        for filter in self.filters:  # type: ignore
            if filter._is_composite:
                yield all(filter._not_na_row_iterator(row, na_values, is_model))
            else:
                yield (
                    (is_model or filter.key in row)
                    and self._get_row_value(row, filter.key, is_model) not in na_values
                )

    def _all_subfilters_have_key(self) -> bool:
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
        map_fun: (
            dict[Hashable, Callable[[Any], Any]]
            | Callable[[Any], Any]
            | list[Callable[[Any], Any]]
            | None
        ) = None,
    ) -> list[Callable[[Any], Any]]:
        if not map_fun:
            map_fun = [lambda x: x for _ in self.filters]
        elif isinstance(map_fun, dict):
            map_fun = [map_fun.get(x.key, lambda x: x) for x in self.filters]
        elif not isinstance(map_fun, list):
            map_fun = [map_fun for _ in self.filters]
        if not isinstance(map_fun, list):
            raise ValueError("map_fun must be a callable, a list or a dict.")
        if len(map_fun) != len(self.filters):
            raise ValueError("map_fun must have the same length as the filters list.")
        return map_fun

    def match_row(
        self,
        row: dict[Hashable, Any | None] | BaseModel,
        na_values: set[Any] | None = None,
        map_fun: (
            Callable[[Any], Any]
            | dict[Hashable, Callable[[Any], Any]]
            | list[Callable[[Any], Any]]
            | None
        ) = None,
        is_model: bool = False,
    ) -> bool:
        if not self._all_subfilters_have_key():
            raise ValueError(
                "Key must be set for each filter to apply filter to a row."
            )
        # Match, per filter, if both key exists, value not null and value matches
        map_fun = self._get_map_fun_list(map_fun)
        if na_values is None:
            return (
                self._match_row(
                    self._not_none_row_iterator(row, is_model),
                    (
                        (
                            y(row)
                            if x._is_composite
                            else y(self._get_row_value(row, x.key, is_model))
                        )
                        for x, y in zip(self.filters, map_fun)
                    ),
                )
                ^ self.invert
            )
            # yield (
            #     key in row_dict
            #     and row_dict[key] is not None
            #     and self._match(map_fun(row_dict[key]))
            # ) ^ self.invert
        else:
            return (
                self._match_row(
                    self._not_na_row_iterator(row, na_values, is_model),
                    (
                        (
                            y(row)
                            if x._is_composite
                            else y(self._get_row_value(row, x.key, is_model))
                        )
                        for x, y in zip(self.filters, map_fun)
                    ),
                )
                ^ self.invert
            )

    def match_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fun: (
            dict[Hashable, Callable[[Any], Any]]
            | Callable[[Any], Any]
            | list[Callable[[Any], Any]]
            | None
        ) = None,
        is_model: bool = False,
    ) -> Iterator[bool]:
        # Match, per row and filter, if both key exists, value not null and value matches
        if not self._all_subfilters_have_key():
            raise ValueError(
                "Key must be set for each filter to apply filter to a row."
            )
        map_fun = self._get_map_fun_list(map_fun)
        if na_values is None:
            for row in rows:
                yield (
                    self._match_row(
                        self._not_none_row_iterator(row, is_model),
                        (
                            (
                                y(row)
                                if x._is_composite
                                else y(self._get_row_value(row, x.key, is_model))
                            )
                            for x, y in zip(self.filters, map_fun)
                        ),
                    )
                    ^ self.invert
                )
        else:
            for row in rows:
                yield (
                    self._match_row(
                        self._not_na_row_iterator(row, na_values, is_model),
                        (
                            (
                                y(row)
                                if x._is_composite
                                else y(self._get_row_value(row, x.key, is_model))
                            )
                            for x, y in zip(self.filters, map_fun)
                        ),
                    )
                    ^ self.invert
                )

    def filter_rows(
        self,
        rows: Iterable[dict[Hashable, Any | None] | BaseModel],
        na_values: set[Any] | None = None,
        map_fun: (
            dict[Hashable, Callable[[Any], Any]]
            | Callable[[Any], Any]
            | list[Callable[[Any], Any]]
            | None
        ) = None,
        is_model: bool = False,
    ) -> Iterator[dict[Hashable, Any | None]]:
        # Match, per row and filter, if both key exists, value not null and value matches
        if not self._all_subfilters_have_key():
            raise ValueError(
                "Key must be set for each filter to apply filter to a row."
            )
        map_fun = self._get_map_fun_list(map_fun)
        if na_values is None:
            for row in rows:
                if (
                    self._match_row(
                        self._not_none_row_iterator(row, is_model),
                        (
                            (
                                y(row)
                                if x._is_composite
                                else y(self._get_row_value(row, x.key, is_model))
                            )
                            for x, y in zip(self.filters, map_fun)
                        ),
                    )
                    ^ self.invert
                ):
                    yield row
        else:
            for row in rows:
                if (
                    self._match_row(
                        self._not_na_row_iterator(row, na_values, is_model),
                        (
                            (
                                y(row)
                                if x._is_composite
                                else y(self._get_row_value(row, x.key, is_model))
                            )
                            for x, y in zip(self.filters, map_fun)
                        ),
                    )
                    ^ self.invert
                ):
                    yield row

    def get_keys(self) -> list[Hashable]:
        keys = []

        def _recursion(keys: list, filters: list[Filter]) -> None:
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
        for filter in self.filters:
            if isinstance(filter, CompositeFilter):
                filter.set_keys(key_map)
            elif isinstance(key_map, dict):
                filter.set_key(key_map.get(filter.key, filter.key))
            else:
                filter.set_key(key_map)
        return self


class TypedCompositeFilter(CompositeFilter):
    type: Literal[enum.FilterType.COMPOSITE.value]
    filters: list[
        Annotated[
            TypedExistsFilter
            | TypedEqualsBooleanFilter
            | TypedEqualsNumberFilter
            | TypedEqualsStringFilter
            | TypedEqualsUuidFilter
            | TypedNumberRangeFilter
            | TypedDateRangeFilter
            | TypedDatetimeRangeFilter
            | TypedPartialDateRangeFilter
            | TypedRegexFilter
            | TypedNumberSetFilter
            | TypedStringSetFilter
            | TypedUuidSetFilter
            | TypedNoFilter
            | TypedCompositeFilter,
            Field(discriminator="type"),
        ]
    ] = Field(
        description="The list of filters."
    )  # type: ignore
