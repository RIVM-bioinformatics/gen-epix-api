"""
Conditional transformer implementation.
"""

from typing import Callable

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class ConditionalTransformer(Transformer):
    """Apply transformation only when condition is met."""

    def __init__(
        self,
        condition: Callable[[ObjectAdapter], bool],
        transformer: Transformer,
        name: str | None = None,
    ):
        super().__init__(name)
        self.condition = condition
        self.transformer = transformer

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Apply transformation if condition is met."""
        if self.condition(obj):
            return self.transformer.transform(obj)
        return obj
