"""
Pipeline for chaining transformers with error tracking and recovery mechanisms.
"""

import logging
import time
from typing import Any, Callable, Iterator

from gen_epix.transform.stream_processer import StreamProcessor
from gen_epix.transform.transform_result import TransformResult
from gen_epix.transform.transformer import Transformer


class Pipeline(StreamProcessor):
    """Chainable pipeline of transformers with comprehensive error handling."""

    def __init__(self, transformers: list[Transformer] | None = None):
        self.transformers = transformers or []
        self.error_handlers: dict[str, Callable[[TransformResult], None]] = {}
        self.logger = logging.getLogger(__name__)

    def add(self, transformer: Transformer) -> "Pipeline":
        """Add transformer to pipeline."""
        self.transformers.append(transformer)
        return self

    def __or__(self, other: Transformer) -> "Pipeline":
        """Enable chaining with | operator."""
        return self.add(other)

    def register_error_handler(
        self, transformer_name: str, handler: Callable[[TransformResult], None]
    ) -> "Pipeline":
        """Register error handler for specific transformer."""
        self.error_handlers[transformer_name] = handler
        return self

    def process_stream(self, stream: Iterator[Any]) -> Iterator[TransformResult]:
        """Process stream through pipeline with error tracking."""
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
    """Wrapper that adds retry logic to any transformer."""

    def __init__(
        self,
        transformer: Transformer,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        name: str | None = None,
    ):
        super().__init__(name or f"Retry_{transformer.name}")
        self.transformer = transformer
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def transform(self, obj: Any) -> Any:
        """Transform with retry logic."""
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
    """Use fallback transformer if primary fails."""

    def __init__(
        self, primary: Transformer, fallback: Transformer, name: str | None = None
    ):
        super().__init__(name)
        self.primary = primary
        self.fallback = fallback

    def transform(self, obj: Any) -> Any:
        """Transform with fallback on failure."""
        try:
            return self.primary.transform(obj)
        except Exception:
            return self.fallback.transform(obj)
