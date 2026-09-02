"""Abstract interface for components that transform iterables of objects."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from gen_epix.transform.transform_result import TransformResult


class StreamProcessor(ABC):
    """Encapsulates the stream-processing contract for pipelines."""

    @abstractmethod
    def process_stream(self, stream: Iterator[Any]) -> Iterator[TransformResult]:
        """Process objects lazily and yield one result for each processed object.

        Args:
            stream: Iterator of objects to process.

        Yields:
            Transformation results in input order.
        """
        pass
