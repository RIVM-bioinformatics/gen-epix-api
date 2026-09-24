"""Synchronous transformer pipeline with ordered execution and error recovery."""

import logging
import time
from collections.abc import Callable, Iterator
from typing import Any

from gen_epix.transform.stream_processer import StreamProcessor
from gen_epix.transform.transform_result import TransformResult
from gen_epix.transform.transformer import Transformer


class Pipeline(StreamProcessor):
    """Encapsulates ordered transformation with failure short-circuiting."""

    def __init__(self, transformers: list[Transformer] | None = None):
        """Initialize the pipeline with an optional ordered transformer list."""
        self.transformers = transformers or []
        self.error_handlers: dict[str, Callable[[TransformResult], None]] = {}
        self.logger = logging.getLogger(__name__)

    def add(self, transformer: Transformer) -> "Pipeline":
        """Append a transformer and return this pipeline for fluent composition."""
        self.transformers.append(transformer)
        return self

    def __or__(self, other: Transformer) -> "Pipeline":
        """Append `other` using the pipeline chaining operator."""
        return self.add(other)

    def register_error_handler(
        self, transformer_name: str, handler: Callable[[TransformResult], None]
    ) -> "Pipeline":
        """Register a callback invoked when the named transformer fails."""
        self.error_handlers[transformer_name] = handler
        return self

    def process_stream(self, stream: Iterator[Any]) -> Iterator[TransformResult]:
        """Lazily process each input and yield its final result."""
        for obj in stream:
            yield from self._process_single_object(obj)

    def _process_single_object(self, obj: Any) -> Iterator[TransformResult]:
        """Process single object through entire pipeline."""
        current_obj = obj

        for i, transformer in enumerate(self.transformers):
            try:
                result = transformer(current_obj)

                if not result.success:
                    # Handle transformation error
                    self._handle_error(result)
                    yield result
                    return  # Stop pipeline on error

                current_obj = result.transformed_object

                # Yield intermediate results if needed
                if i == len(self.transformers) - 1:  # Last transformer
                    yield result

            except Exception as e:
                error_result = TransformResult(
                    success=False,
                    original_object=obj,
                    error=e,
                    transformer_name=transformer.name,
                    stage=f"pipeline_stage_{i}",
                )
                self._handle_error(error_result)
                yield error_result
                return

    def _handle_error(self, result: TransformResult) -> None:
        """Handle transformation errors."""
        self.logger.error(
            f"Transformation failed in {result.transformer_name}: {result.error}"
        )

        # Call registered error handler if available
        if result.transformer_name and result.transformer_name in self.error_handlers:
            self.error_handlers[result.transformer_name](result)


class RetryTransformer(Transformer):
    """Encapsulates transformer retries with exponential backoff."""

    def __init__(
        self,
        transformer: Transformer,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        name: str | None = None,
    ):
        """Wrap a transformer and retry failed transformations with backoff."""
        super().__init__(name or f"Retry_{transformer.name}")
        self.transformer = transformer
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def transform(self, obj: Any) -> Any:
        """Run the wrapped transformer until it succeeds or retries are exhausted.

        Retries only exceptions raised by the wrapped transform method. Delays grow
        exponentially from ``backoff_factor`` between attempts.

        Args:
            obj: Object passed to the wrapped transformer.

        Returns:
            Result returned by the wrapped transformer.

        Raises:
            Exception: Re-raises the final exception from the wrapped transformer
                after the retry limit is reached.
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return self.transformer.transform(obj)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(self.backoff_factor * (2**attempt))
                    continue
                break

        raise last_exception  # type: ignore[misc]


class FallbackTransformer(Transformer):
    """Encapsulates fallback transformation after a primary exception."""

    def __init__(
        self, primary: Transformer, fallback: Transformer, name: str | None = None
    ):
        """Store the primary transformer and fallback transformer."""
        super().__init__(name)
        self.primary = primary
        self.fallback = fallback

    def transform(self, obj: Any) -> Any:
        """Return the primary result, or invoke the fallback after a primary failure."""
        try:
            return self.primary.transform(obj)
        except Exception:
            return self.fallback.transform(obj)
