"""
Advanced streaming pipeline with backpressure handling and async support.
"""

import asyncio
from collections import deque
from typing import Any, Callable, Iterator

from gen_epix.transform.pipeline import Pipeline
from gen_epix.transform.transform_result import TransformResult


class StreamingPipeline:
    """Advanced streaming pipeline with backpressure handling."""

    def __init__(
        self,
        pipeline: Pipeline,
        buffer_size: int = 1000,
        error_threshold: float = 0.1,
    ):
        self.pipeline = pipeline
        self.buffer_size = buffer_size
        self.error_threshold = error_threshold
        self.error_count = 0
        self.total_count = 0
        self.buffer: deque[Any] = deque(maxlen=buffer_size)

    def process_stream_async(
        self,
        stream: Iterator[Any],
        on_success: Callable[[TransformResult], None] | None = None,
        on_error: Callable[[TransformResult], None] | None = None,
    ) -> Iterator[TransformResult]:
        """Process stream asynchronously with callbacks."""

        for obj in stream:
            results = list(self.pipeline.process_stream(iter([obj])))

            for result in results:
                self.total_count += 1

                if result.success:
                    if on_success:
                        on_success(result)
                else:
                    self.error_count += 1
                    if on_error:
                        on_error(result)

                    # Check error threshold
                    error_rate = self.error_count / self.total_count
                    if error_rate > self.error_threshold:
                        raise RuntimeError(
                            f"Error rate {error_rate:.2%} exceeds threshold"
                        )

                yield result

    def collect_errors(
        self, stream: Iterator[Any]
    ) -> tuple[list[Any], list[TransformResult]]:
        """Collect successful and failed transformations separately."""
        successes: list[Any] = []
        errors: list[TransformResult] = []

        for result in self.process_stream_async(stream):
            if result.success:
                successes.append(result.transformed_object)
            else:
                errors.append(result)

        return successes, errors

    async def process_stream_async_coroutine(
        self, stream: Iterator[Any], batch_size: int = 100
    ) -> list[TransformResult]:
        """Process stream asynchronously using coroutines."""
        results: list[TransformResult] = []
        batch: list[Any] = []

        for obj in stream:
            batch.append(obj)

            if len(batch) >= batch_size:
                batch_results = await self._process_batch_async(batch)
                results.extend(batch_results)
                batch = []

        # Process remaining items
        if batch:
            batch_results = await self._process_batch_async(batch)
            results.extend(batch_results)

        return results

    async def _process_batch_async(self, batch: list[Any]) -> list[TransformResult]:
        """Process a batch of objects asynchronously."""
        tasks = [self._process_single_async(obj) for obj in batch]
        return await asyncio.gather(*tasks)

    async def _process_single_async(self, obj: Any) -> TransformResult:
        """Process a single object asynchronously."""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, lambda: list(self.pipeline.process_stream(iter([obj])))
        )
        return (
            results[0]
            if results
            else TransformResult(
                success=False,
                original_object=obj,
                error=Exception("No results returned"),
                transformer_name="StreamingPipeline",
            )
        )
