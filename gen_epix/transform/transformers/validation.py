"""
Validation transformer implementation.
"""

from typing import Callable

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class ValidationTransformer(Transformer):
    """Validate object and fail if validation doesn't pass."""

    def __init__(
        self, validator: Callable[[ObjectAdapter], bool], name: str | None = None
    ):
        super().__init__(name)
        self.validator = validator

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Validate object and raise exception if validation fails."""
        if not self.validator(obj):
            raise ValueError(f"Validation failed for object: {obj.unwrap()}")
        return obj
