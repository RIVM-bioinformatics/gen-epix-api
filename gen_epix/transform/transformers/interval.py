"""
Number to interval transformer implementation.
"""

import math
from collections.abc import Hashable
from decimal import Decimal
from typing import Literal, NoReturn, TypedDict

from gen_epix.fastapp.enum import OnException
from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.enum import IntervalTransformStrategy
from gen_epix.transform.transformer import Transformer


# TODO: make this a regular class and add methods like __in__ that take another interval, a number or None; __eq__, __lt__, __gt__, __le__, __ge__, __str__, __repr__ etc., moving this logic from the two tranformer classes here
class IntervalDict(TypedDict):
    """Type definition for interval dictionaries."""

    name: Hashable
    lb: float
    ub: float
    lb_in: bool
    ub_in: bool


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
        # TODO: split on_no_match into on_invalid_source (default SET_NO_RETURN) and on_no_target (default SET_NONE); do this for all transformers
        on_no_match: Literal[
            OnException.RAISE, OnException.SET_NONE, OnException.SET_NO_RETURN
        ] = OnException.RAISE,
    ) -> None:
        if on_no_match not in (
            OnException.RAISE,
            OnException.SET_NONE,
            OnException.SET_NO_RETURN,
        ):
            raise ValueError(f"Invalid on_no_match value {on_no_match}")

        # Initialise some
        super().__init__(name)
        self.src_field = src_field
        self.tgt_field = tgt_field or src_field
        self._on_no_match = on_no_match
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

    def _map_to_interval(
        self,
        value: float | int | Decimal | None,
        on_no_match: Literal[
            OnException.RAISE, OnException.SET_NONE, OnException.SET_NO_RETURN
        ],
    ) -> Hashable | None | NoReturn:
        if value is None:
            return None
        if not isinstance(value, (int, float, Decimal)):
            if on_no_match == OnException.RAISE:
                raise ValueError(f"Value {value} does not match any interval")
            elif on_no_match == OnException.SET_NONE:
                return None
            elif on_no_match == OnException.SET_NO_RETURN:
                return NoReturn
            raise NotImplementedError(f"Invalid on_no_match value {on_no_match}")
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
        # Does not match to any interval
        if on_no_match == OnException.RAISE:
            raise ValueError(f"Value {value} does not match any interval")
        elif on_no_match == OnException.SET_NONE:
            return None
        elif on_no_match == OnException.SET_NO_RETURN:
            return NoReturn
        raise NotImplementedError(f"Invalid on_no_match value {on_no_match}")

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Map number to interval."""
        src_value = obj.get(self.src_field)
        tgt_value = self.transform_value(src_value)
        obj.set(self.tgt_field, tgt_value)
        return obj

    def transform_value(
        self, value: float | int | Decimal | None
    ) -> Hashable | None | NoReturn:
        """Map number to interval."""
        tgt_value = self._map_to_interval(
            value, self._on_no_match
        )  # type:ignore[arg-type]
        return tgt_value

    def is_transformable(self, value: float | int | Decimal | None) -> bool:
        """Check if a value can be transformed to an interval without performing the transformation."""
        if value is None:
            return True  # None values are always transformable

        tgt_value = self._map_to_interval(value, OnException.SET_NO_RETURN)
        return tgt_value != NoReturn


class IntervalToIntervalTransformer(Transformer):
    """
    Maps intervals from one categorization to another based on overlapping ranges.

    This transformer takes an interval from a source categorization and maps it to
    the corresponding interval(s) in a target categorization based on range overlaps.
    """

    def __init__(
        self,
        src_field: Hashable,
        src_interval_names: list[Hashable],
        src_lower_bounds: list[float | int | Decimal | None],
        src_upper_bounds: list[float | int | Decimal | None],
        tgt_interval_names: list[Hashable],
        tgt_lower_bounds: list[float | int | Decimal | None],
        tgt_upper_bounds: list[float | int | Decimal | None],
        tgt_field: Hashable | None = None,
        src_lower_bound_is_inclusive: list[bool] | bool = True,
        src_upper_bound_is_inclusive: list[bool] | bool = False,
        tgt_lower_bound_is_inclusive: list[bool] | bool = True,
        tgt_upper_bound_is_inclusive: list[bool] | bool = False,
        name: str | None = None,
        on_no_match: Literal[
            OnException.RAISE, OnException.SET_NONE, OnException.SET_NO_RETURN
        ] = OnException.RAISE,
        transform_strategy: IntervalTransformStrategy = IntervalTransformStrategy.CONTAINS_ONLY,
    ) -> None:
        if on_no_match not in (
            OnException.RAISE,
            OnException.SET_NONE,
            OnException.SET_NO_RETURN,
        ):
            raise ValueError(f"Invalid on_no_match value {on_no_match}")

        super().__init__(name)
        self.src_field = src_field
        self.tgt_field = tgt_field or src_field
        self._transform_strategy = transform_strategy
        self._on_no_match = on_no_match

        # Initialize source intervals
        self._src_intervals = self._create_interval_list(
            src_interval_names,
            src_lower_bounds,
            src_upper_bounds,
            src_lower_bound_is_inclusive,
            src_upper_bound_is_inclusive,
        )

        # Initialize target intervals
        self._tgt_intervals = self._create_interval_list(
            tgt_interval_names,
            tgt_lower_bounds,
            tgt_upper_bounds,
            tgt_lower_bound_is_inclusive,
            tgt_upper_bound_is_inclusive,
        )

        # Pre-compute mapping from source to target intervals
        self._interval_mapping = self._compute_interval_mapping()

    def _create_interval_list(
        self,
        names: list[Hashable],
        lower_bounds: list[float | int | Decimal | None],
        upper_bounds: list[float | int | Decimal | None],
        lower_inclusive: list[bool] | bool,
        upper_inclusive: list[bool] | bool,
    ) -> list[IntervalDict]:
        """Create standardized interval representation."""
        n_intervals = len(names)

        if isinstance(lower_inclusive, bool):
            lower_inclusive = [lower_inclusive] * n_intervals
        if isinstance(upper_inclusive, bool):
            upper_inclusive = [upper_inclusive] * n_intervals

        intervals = []
        for i in range(n_intervals):
            intervals.append(
                IntervalDict(
                    name=names[i],
                    lb=(
                        -math.inf
                        if lower_bounds[i] is None
                        else float(lower_bounds[i] or 0)
                    ),
                    ub=(
                        math.inf
                        if upper_bounds[i] is None
                        else float(upper_bounds[i] or 0)
                    ),
                    lb_in=lower_inclusive[i],
                    ub_in=upper_inclusive[i],
                )
            )

        return intervals

    def _compute_interval_mapping(self) -> dict[Hashable, Hashable]:
        """Pre-compute mapping from source intervals to target intervals."""
        mapping = {}

        for src_interval in self._src_intervals:
            best_match = None
            max_overlap = 0

            for tgt_interval in self._tgt_intervals:
                overlap = self._calculate_overlap(src_interval, tgt_interval)
                if self._is_contained(src_interval, tgt_interval):
                    mapping[src_interval["name"]] = tgt_interval["name"]
                    break
                if self._transform_strategy == IntervalTransformStrategy.CONTAINS_ONLY:
                    continue  # Skip if source interval is not contained in target

                if (
                    self._transform_strategy
                    == IntervalTransformStrategy.LARGEST_OVERLAP
                ):
                    # Map to target with largest overlap
                    if overlap > max_overlap:
                        max_overlap = overlap
                        best_match = tgt_interval["name"]
                    continue
                raise NotImplementedError(
                    f"transform_strategy={self._transform_strategy} not implemented"
                )

            if (
                self._transform_strategy == IntervalTransformStrategy.LARGEST_OVERLAP
                and best_match
                and max_overlap > 0
            ):
                mapping[src_interval["name"]] = best_match

        return mapping

    def _calculate_overlap(
        self,
        src_interval: IntervalDict,
        tgt_interval: IntervalDict,
    ) -> float:
        """Calculate overlap between two intervals."""
        # Determine effective bounds for overlap calculation
        overlap_start = max(src_interval["lb"], tgt_interval["lb"])
        overlap_end = min(src_interval["ub"], tgt_interval["ub"])

        if overlap_start >= overlap_end:
            return 0.0

        # Handle infinite bounds
        if math.isinf(overlap_start) or math.isinf(overlap_end):
            return float("inf")

        return overlap_end - overlap_start

    def _is_contained(
        self, src_interval: IntervalDict, tgt_interval: IntervalDict
    ) -> bool:
        """Check if source interval is completely contained in target interval."""
        # Check lower bound
        if src_interval["lb"] < tgt_interval["lb"]:
            return False
        if (
            src_interval["lb"] == tgt_interval["lb"]
            and src_interval["lb_in"]
            and not tgt_interval["lb_in"]
        ):
            return False

        # Check upper bound
        if src_interval["ub"] > tgt_interval["ub"]:
            return False
        if (
            src_interval["ub"] == tgt_interval["ub"]
            and src_interval["ub_in"]
            and not tgt_interval["ub_in"]
        ):
            return False

        return True

    def _map_interval(self, src_interval_name: Hashable) -> Hashable | None | NoReturn:
        """Map source interval name to target interval name."""
        if src_interval_name is None:
            return None

        mapped_name = self._interval_mapping.get(src_interval_name)
        if mapped_name is None:
            if self._on_no_match == OnException.RAISE:
                raise ValueError(
                    f"Source interval '{src_interval_name}' does not exist in the mapping."
                )
            elif self._on_no_match == OnException.SET_NONE:
                return None
            elif self._on_no_match == OnException.SET_NO_RETURN:
                return NoReturn
            raise NotImplementedError(
                f"on_no_match={self._on_no_match} not implemented"
            )
        return mapped_name

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform interval from source categorization to target categorization."""
        src_value = obj.get(self.src_field)
        tgt_value = self.transform_value(src_value)
        obj.set(self.tgt_field, tgt_value)
        return obj

    def transform_value(self, src_interval_name: Hashable) -> Hashable | None:
        """Transform interval name directly."""
        tgt_value = self._map_interval(src_interval_name)
        return tgt_value

    def is_transformable(self, src_interval_name: Hashable) -> bool:
        """Check if source interval can be mapped to target categorization."""
        if src_interval_name is None:
            return True

        return src_interval_name in self._interval_mapping
