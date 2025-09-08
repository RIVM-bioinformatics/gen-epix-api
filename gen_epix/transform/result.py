"""
Transform result types for tracking success/failure in transformation pipelines.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class TransformResultType(Enum):
    """Enum for different types of transformation results."""

    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TransformResult:
    """Result of a transformation operation, containing success/failure information."""

    success: bool
    original_object: Any
    transformed_object: Optional[Any] = None
    error: Optional[Exception] = None
    transformer_name: Optional[str] = None
    stage: Optional[str] = None

    @property
    def result_type(self) -> TransformResultType:
        """Get the result type based on success status."""
        if self.success:
            return TransformResultType.SUCCESS
        elif self.error:
            return TransformResultType.ERROR
        else:
            return TransformResultType.SKIPPED

    def __str__(self) -> str:
        """String representation of the transform result."""
        if self.success:
            return f"TransformResult(SUCCESS, transformer={self.transformer_name})"
        else:
            return f"TransformResult(FAILED, transformer={self.transformer_name}, error={self.error})"
