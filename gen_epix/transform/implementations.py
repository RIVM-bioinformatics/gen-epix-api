"""
Concrete transformer implementations for common use cases.
"""

from typing import Any, Callable, Hashable, Optional

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.core import Transformer


class FieldTransformer(Transformer):
    """Transform a specific field in an object."""

    def __init__(
        self,
        field_name: Hashable,
        transform_fn: Callable[[Any], Any],
        name: Optional[str] = None,
    ):
        super().__init__(name)
        self.field_name = field_name
        self.transform_fn = transform_fn

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform the specified field if it exists."""
        if obj.has_key(self.field_name):
            current_value = obj.get(self.field_name)
            transformed_value = self.transform_fn(current_value)
            obj.set(self.field_name, transformed_value)
        return obj


class ConditionalTransformer(Transformer):
    """Apply transformation only when condition is met."""

    def __init__(
        self,
        condition: Callable[[ObjectAdapter], bool],
        transformer: Transformer,
        name: Optional[str] = None,
    ):
        super().__init__(name)
        self.condition = condition
        self.transformer = transformer

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Apply transformation if condition is met."""
        if self.condition(obj):
            return self.transformer.transform(obj)
        return obj


class ValidationTransformer(Transformer):
    """Validate object and fail if validation doesn't pass."""

    def __init__(
        self, validator: Callable[[ObjectAdapter], bool], name: Optional[str] = None
    ):
        super().__init__(name)
        self.validator = validator

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Validate object and raise exception if validation fails."""
        if not self.validator(obj):
            raise ValueError(f"Validation failed for object: {obj.unwrap()}")
        return obj


class MultiFieldTransformer(Transformer):
    """Transform multiple fields simultaneously."""

    def __init__(
        self,
        field_mapping: dict[Hashable, Callable[[Any], Any]],
        name: Optional[str] = None,
    ):
        super().__init__(name)
        self.field_mapping = field_mapping

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform all specified fields."""
        for field_key, transform_fn in self.field_mapping.items():
            if obj.has_key(field_key):
                old_value = obj.get(field_key)
                new_value = transform_fn(old_value)
                obj.set(field_key, new_value)
        return obj


class ObjectTransformer(Transformer):
    """Transform entire object using a custom function."""

    def __init__(self, transform_fn: Callable[[Any], Any], name: Optional[str] = None):
        super().__init__(name)
        self.transform_fn = transform_fn

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform the entire object."""
        original = obj.unwrap()
        transformed = self.transform_fn(original)
        return ObjectAdapter(transformed)
