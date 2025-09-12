"""
Core transformer classes and interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transform_result import TransformResult


class Transformer(ABC):
    """Base transformer class for single object transformations."""

    def __init__(self, name: str | None = None):
        self.name = name or self.__class__.__name__

    @abstractmethod
    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """
        Transform a single object.

        Args:
            obj: Object adapter wrapping the object to transform

        Returns:
            Transformed object adapter
        """
        pass

    def __call__(self, obj: Any) -> TransformResult:
        """
        Transform an object with error handling.

        Args:
            obj: Object to transform

        Returns:
            TransformResult containing success/failure information
        """
        try:
            adapter = ObjectAdapter(obj)
            transformed_adapter = self.transform(adapter)
            return TransformResult(
                success=True,
                original_object=obj,
                transformed_object=transformed_adapter.unwrap(),
                transformer_name=self.name,
            )
        except Exception as e:
            return TransformResult(
                success=False, original_object=obj, error=e, transformer_name=self.name
            )
