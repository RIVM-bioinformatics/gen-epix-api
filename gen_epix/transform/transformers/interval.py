"""
Number to interval transformer implementation.
"""

import math
from collections.abc import Hashable
from decimal import Decimal
from typing import NoReturn

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.enum import NoMatchStrategy
from gen_epix.transform.transformer import Transformer


class IntervalTransformer(Transformer):
    """
    Maps a number to an interval represented by a hashable, based on the
    bounds of the interval.
    """

    def __init__(
        self,
        src_field: Hashable,
        interval_names: list[Hashable],
        lower_bounds: list[float | int | Decimal | None],
        upper_bounds: list[float | int | Decimal | None],
        tgt_field: Hashable | None = None,
        lower_bound_is_inclusive: list[bool] | bool = True,
        upper_bound_is_inclusive: list[bool] | bool = False,
        name: str | None = None,
        no_match_strategy: NoMatchStrategy = NoMatchStrategy.RAISE,
    ) -> None:

        # Initialise some
        super().__init__(name)
        self.src_field = src_field
        self.tgt_field = tgt_field or src_field
        self._no_match_strategy = no_match_strategy
        self._n_intervals = len(lower_bounds)
        self._lower_bounds = [-math.inf if x is None else x for x in lower_bounds]
        self._upper_bounds = [math.inf if x is None else x for x in upper_bounds]
        self._interval_names = interval_names
        if isinstance(lower_bound_is_inclusive, list):
            self._lower_bound_is_inclusive = list(lower_bound_is_inclusive)
        else:
            self._lower_bound_is_inclusive = [
                lower_bound_is_inclusive
            ] * self._n_intervals
        if isinstance(upper_bound_is_inclusive, list):
            self._upper_bound_is_inclusive = list(upper_bound_is_inclusive)
        else:
            self._upper_bound_is_inclusive = [
                upper_bound_is_inclusive
            ] * self._n_intervals

        # Sort bins
        sorted_indices = sorted(
            range(self._n_intervals), key=lambda i: self._lower_bounds[i]
        )
        self._lower_bounds = [self._lower_bounds[i] for i in sorted_indices]
        self._lower_bound_is_inclusive = [
            self._lower_bound_is_inclusive[i] for i in sorted_indices
        ]
        self._upper_bounds = [self._upper_bounds[i] for i in sorted_indices]
        self._upper_bound_is_inclusive = [
            self._upper_bound_is_inclusive[i] for i in sorted_indices
        ]
        self._interval_names = [self._interval_names[i] for i in sorted_indices]

        # Verify input
        for i in range(self._n_intervals):
            lb = self._lower_bounds[i]
            ub = self._upper_bounds[i]
            if lb > ub:
                raise ValueError(f"Lower bound {lb} must be less than upper bound {ub}")
        for i, lb1 in enumerate(self._lower_bounds[0:-1]):
            lb1_is_inclusive = self._lower_bound_is_inclusive[i]
            ub1 = self._upper_bounds[i]
            ub1_is_inclusive = self._upper_bound_is_inclusive[i]
            lb2 = self._lower_bounds[i + 1]
            ub2 = self._upper_bounds[i + 1]
            lb2_is_inclusive = self._lower_bound_is_inclusive[i + 1]
            ub2_is_inclusive = self._upper_bound_is_inclusive[i + 1]
            if lb2 < ub1 or lb2 == ub1 and (lb2_is_inclusive and ub1_is_inclusive):
                lb1_str = ("[" if lb1_is_inclusive else "]") + str(lb1)
                ub1_str = str(ub1) + ("]" if ub1_is_inclusive else "[")
                lb2_str = ("[" if lb2_is_inclusive else "]") + str(lb2)
                ub2_str = str(ub2) + ("]" if ub2_is_inclusive else "[")
                raise ValueError(
                    f"Intervals overlap: {lb1_str},{ub1_str} and {lb2_str},{ub2_str}"
                )

    def _get_interval(
        self, value: float | int | Decimal | None
    ) -> Hashable | None | NoReturn:
        if value is None:
            return None
        for i in range(self._n_intervals):
            # Match interval
            match_lb = value > self._lower_bounds[i] or (
                value == self._lower_bounds[i] and self._lower_bound_is_inclusive[i]
            )
            match_ub = value < self._upper_bounds[i] or (
                value == self._upper_bounds[i] and self._upper_bound_is_inclusive[i]
            )
            if match_lb and match_ub:
                # Interval matches -> assign value to target field and stop
                return self._interval_names[i]
        return NoReturn

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Map number to interval."""
        src_value = obj.get(self.src_field)
        tgt_value = self._get_interval(src_value)
        if tgt_value == NoReturn:
            if self._no_match_strategy == NoMatchStrategy.RAISE:
                raise ValueError(f"Value {src_value} does not match any interval")
            elif self._no_match_strategy == NoMatchStrategy.SET_NONE:
                obj.set(self.tgt_field, None)
                return obj
            raise NotImplementedError(
                f"Unknown no match strategy {self._no_match_strategy}"
            )
        obj.set(self.tgt_field, tgt_value)
        return obj

    def transform_value(self, value: float | int | Decimal | None) -> Hashable | None:
        """Map number to interval."""
        tgt_value = self._get_interval(value)
        if tgt_value == NoReturn:
            if self._no_match_strategy == NoMatchStrategy.RAISE:
                raise ValueError(f"Value {value} does not match any interval")
            elif self._no_match_strategy == NoMatchStrategy.SET_NONE:
                return None
            raise NotImplementedError(
                f"Unknown no match strategy {self._no_match_strategy}"
            )
        return tgt_value
