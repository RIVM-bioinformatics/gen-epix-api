"""Test the abstract stream-processing interface."""

import inspect

from gen_epix.transform.stream_processer import StreamProcessor


def test_stream_processor_requires_process_stream_implementation() -> None:
    """Declare process_stream as an abstract method on the interface."""
    assert inspect.isabstract(StreamProcessor)
    assert StreamProcessor.__abstractmethods__ == frozenset({"process_stream"})
