"""Validate adapted objects before they continue through a transformation pipeline.

The public `ValidationTransformer` applies a caller-supplied predicate and preserves
the adapter on acceptance. Rejections raise `ValueError`; when invoked through the
base transformer interface, that failure is returned in a `TransformResult`.
"""

from collections.abc import Callable

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class ValidationTransformer(Transformer):
    """Encapsulates predicate-based validation of adapted objects.

    The validator receives the adapter and decides whether the object may continue
    through the pipeline. Accepted objects retain their original adapter; rejected
    objects raise `ValueError`, which the base callable interface captures in a
    `TransformResult`.

    Attributes:
        validator: Predicate used to accept or reject an adapted object.
    """

    def __init__(
        self, validator: Callable[[ObjectAdapter], bool], name: str | None = None
    ):
        """Configure the validation predicate and optional result name.

        Args:
            validator: Predicate that returns true when an adapted object is accepted.
            name: Optional name included in transformation results.
        """
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
