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
        """Validate an adapted object and return it unchanged when it is accepted.

        Args:
            obj: Adapted object evaluated by the configured validator.

        Returns:
            The unchanged adapter when validation succeeds.

        Raises:
            ValueError: If the configured validator returns ``False``.
        """
        if not self.validator(obj):
            raise ValueError(f"Validation failed for object: {obj.unwrap()}")
        return obj
