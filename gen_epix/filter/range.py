from typing import Any, Literal, Self

from pydantic import Field, model_validator

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import ComparisonOperator, FilterType


class RangeFilter(Filter):
    lower_bound: Any | None = Field(
        default=None, description="The lower bound of the range.", frozen=True
    )
    lower_bound_censor: ComparisonOperator = Field(
        default=ComparisonOperator.GTE,
        description="The censor of the lower bound.",
        frozen=True,
    )
    upper_bound: Any | None = Field(
        default=None, description="The upper bound of the range.", frozen=True
    )
    upper_bound_censor: ComparisonOperator = Field(
        default=ComparisonOperator.ST,
        description="The censor of the upper bound.",
        frozen=True,
    )

    def _validate_state_bounds(self) -> None:
        # Validate the bounds and censors
        if self.lower_bound is None:
            if self.upper_bound is None:
                raise AssertionError("At least one bound must be set.")
        else:
            if self.upper_bound is not None:
                if self.lower_bound > self.upper_bound:
                    raise AssertionError(
                        f"Lower bound ({self.lower_bound}) must be less than or equal"
                        " to upper bound ({self.upper_bound})."
                    )
                if self.lower_bound == self.upper_bound and (
                    self.lower_bound_censor != ComparisonOperator.GTE
                    or self.upper_bound_censor != ComparisonOperator.STE
                ):
                    raise AssertionError(
                        f"Lower bound censor ({self.lower_bound_censor}) must be >="
                        " and upper bound censor ({self.upper_bound_censor}) must be"
                        " <= in case both bounds are equal."
                    )
        if self.lower_bound_censor is not None and self.lower_bound_censor not in {
            ComparisonOperator.GT,
            ComparisonOperator.GTE,
        }:
            raise AssertionError("Lower bound censor must be > or >=.")
        if self.upper_bound_censor is not None and self.upper_bound_censor not in {
            ComparisonOperator.ST,
            ComparisonOperator.STE,
        }:
            raise AssertionError("Upper bound censor must be < or <=.")

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        self._validate_state_bounds()
        # Generate the function to check if a value is within the range
        # The function is generated instead of defined to be able to optimize the check
        if self.lower_bound is not None and self.upper_bound is not None:
            if self.lower_bound == self.upper_bound:
                self._match = lambda x: x == self.lower_bound  # type: ignore
            elif (
                self.lower_bound_censor == ComparisonOperator.GTE
                and self.upper_bound_censor == ComparisonOperator.ST
            ):
                self._match = (  # type: ignore
                    lambda x: self.lower_bound <= x < self.upper_bound  # type: ignore
                )
            elif (
                self.lower_bound_censor == ComparisonOperator.GTE
                and self.upper_bound_censor == ComparisonOperator.STE
            ):
                self._match = (  # type: ignore
                    lambda x: self.lower_bound <= x <= self.upper_bound  # type: ignore
                )
            elif (
                self.lower_bound_censor == ComparisonOperator.GT
                and self.upper_bound_censor == ComparisonOperator.ST
            ):
                self._match = (  # type: ignore
                    lambda x: self.lower_bound < x < self.upper_bound  # type: ignore
                )
            elif (
                self.lower_bound_censor == ComparisonOperator.GT
                and self.upper_bound_censor == ComparisonOperator.STE
            ):
                self._match = (  # type: ignore
                    lambda x: self.lower_bound < x <= self.upper_bound  # type: ignore
                )
        elif self.lower_bound is not None:
            if self.lower_bound_censor == ComparisonOperator.GTE:
                self._match = lambda x: self.lower_bound <= x  # type: ignore
            elif self.lower_bound_censor == ComparisonOperator.GT:
                self._match = lambda x: self.lower_bound < x  # type: ignore
        elif self.upper_bound is not None:
            if self.upper_bound_censor == ComparisonOperator.ST:
                self._match = lambda x: x < self.upper_bound  # type: ignore
            elif self.upper_bound_censor == ComparisonOperator.STE:
                self._match = lambda x: x <= self.upper_bound  # type: ignore
        return self

    def _match(self, value: Any) -> bool:
        # Function is implemented dynamically in _validate_state
        raise NotImplementedError()


class TypedRangeFilter(RangeFilter):
    type: Literal[FilterType.RANGE.value]
