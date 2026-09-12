"""Base class for object transformers and their result-producing call interface."""

from abc import ABC, abstractmethod
from typing import Any

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transform_result import TransformResult


class Transformer(ABC):
    """Encapsulates object transformation and failure conversion."""

    def __init__(self, name: str | None = None):
        """Set the transformer name used in transformation results."""
        self.name = name or self.__class__.__name__

    @abstractmethod
    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform a single adapted object.

        Args:
            obj: Adapter wrapping the object to transform.

        Returns:
            The transformed object adapter.
        """
        pass

    def __call__(self, obj: Any) -> TransformResult:
        """Adapt and transform an object, returning failures as `TransformResult`.

        Args:
            obj: Object to adapt and transform.

        Returns:
            A result containing the unwrapped transformed object or the caught
            exception.
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
