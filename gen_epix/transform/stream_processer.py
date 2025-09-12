"""
Stream processing interfaces and base classes.
"""

from abc import ABC, abstractmethod
from typing import Any, Iterator

from gen_epix.transform.transform_result import TransformResult


class StreamProcessor(ABC):
    """Base interface for stream processing components."""

    @abstractmethod
    def process_stream(self, stream: Iterator[Any]) -> Iterator[TransformResult]:
        """
        Process a stream of objects and yield transformation results.

        Args:
            stream: Iterator of objects to process

        Yields:
            TransformResult objects containing success/failure information
        """
        pass
