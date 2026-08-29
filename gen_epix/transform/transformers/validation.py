"""Transformer that validates an adapted object before it continues in a pipeline."""

from collections.abc import Callable

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class ValidationTransformer(Transformer):
    """Pass an object through when its validator returns true."""

    def __init__(
        self, validator: Callable[[ObjectAdapter], bool], name: str | None = None
    ):
        """Store the predicate used to accept or reject objects."""
        super().__init__(name)
        self.validator = validator

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Return `obj`, or raise `ValueError` when validation returns false."""
        if not self.validator(obj):
            raise ValueError(f"Validation failed for object: {obj.unwrap()}")
        return obj
