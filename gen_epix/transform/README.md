# Transformer Framework

A comprehensive, stream-processing transformer framework for handling heterogeneous data objects including dictionaries, Pydantic models, and Polars objects.

## Features

- **Stream Processing**: Efficient processing of data streams with lazy evaluation
- **Unified Object Interface**: Works seamlessly with dict, Pydantic models, and Polars objects
- **Chainable Pipelines**: Create complex transformation pipelines using method chaining
- **Error Tracking**: Comprehensive error handling with detailed failure information
- **Retry & Fallback**: Built-in retry mechanisms and fallback transformers
- **Async Support**: Asynchronous processing capabilities for I/O-bound operations
- **Registry System**: Plugin architecture for registering custom transformers

## Quick Start

```python
from gen_epix.transform import (
    FieldTransformer,
    TransformerPipeline,
    StreamingPipeline
)

# Create transformers
name_normalizer = FieldTransformer(
    field_name="name",
    transform_fn=lambda x: str(x).title()
)

email_normalizer = FieldTransformer(
    field_name="email", 
    transform_fn=lambda x: str(x).lower()
)

# Create pipeline
pipeline = TransformerPipeline([
    name_normalizer,
    email_normalizer
])

# Process data
data = [
    {"name": "john doe", "email": "JOHN@EXAMPLE.COM"},
    {"name": "jane smith", "email": "JANE@EXAMPLE.COM"}
]

streaming_pipeline = StreamingPipeline(pipeline)
successes, errors = streaming_pipeline.collect_errors(iter(data))
```

## Core Components

### 1. Object Adapters (`adapter.py`)
- `ObjectAdapter`: Unified interface for different object types
- `DictAdapter`: Adapter for dictionary objects
- `PydanticAdapter`: Adapter for Pydantic models
- `PolarsAdapter`: Adapter for Polars objects

### 2. Core Transformers (`core.py`)
- `Transformer`: Base class for all transformers
- Abstract `transform()` method for implementing custom logic

### 3. Implementations (`implementations.py`)
- `FieldTransformer`: Transform specific fields
- `ConditionalTransformer`: Apply transformations conditionally
- `ValidationTransformer`: Validate objects during transformation
- `MultiFieldTransformer`: Transform multiple fields simultaneously
- `ObjectTransformer`: Transform entire objects

### 4. Pipeline System (`pipeline.py`)
- `TransformerPipeline`: Chain multiple transformers
- `RetryTransformer`: Add retry logic to any transformer
- `FallbackTransformer`: Use fallback on failure

### 5. Streaming (`streaming.py`)
- `StreamingPipeline`: Advanced streaming with backpressure handling
- Async processing capabilities
- Error threshold monitoring

### 6. Result Tracking (`result.py`)
- `TransformResult`: Detailed success/failure information
- `TransformResultType`: Enumeration of result types

### 7. Registry (`registry.py`)
- `TransformerRegistry`: Central registry for transformer types
- Decorator support for easy registration

## Advanced Usage

### Conditional Transformations

```python
from gen_epix.transform import ConditionalTransformer, FieldTransformer

# Only transform US phone numbers
us_phone_transformer = ConditionalTransformer(
    condition=lambda obj: obj.get("country") == "US",
    transformer=FieldTransformer(
        field_name="phone",
        transform_fn=lambda x: f"+1-{x}"
    )
)
```

### Error Handling

```python
pipeline = TransformerPipeline([transformer1, transformer2])

# Register error handler
pipeline.on_error("transformer1", lambda result: print(f"Error: {result.error}"))

# Process with error collection
successes, errors = streaming_pipeline.collect_errors(data_stream)
```

### Custom Transformers

```python
from gen_epix.transform import register_transformer, CoreTransformer

@register_transformer("custom_transformer")
class CustomTransformer(CoreTransformer):
    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        # Custom transformation logic
        return obj

# Use registered transformer
transformer = TransformerRegistry.create("custom_transformer")
```

### Async Processing

```python
import asyncio

async def process_large_dataset():
    pipeline = TransformerPipeline([...])
    streaming_pipeline = StreamingPipeline(pipeline)
    
    results = await streaming_pipeline.process_stream_async_coroutine(
        data_stream, 
        batch_size=1000
    )
    return results
```

## Error Recovery

The framework provides several mechanisms for handling failures:

1. **Retry Logic**: `RetryTransformer` with exponential backoff
2. **Fallback Transformers**: `FallbackTransformer` for graceful degradation
3. **Error Thresholds**: Stop processing if error rate exceeds threshold
4. **Detailed Error Information**: Track original objects and error details

## Performance Considerations

- Use streaming pipelines for large datasets
- Leverage async processing for I/O-bound operations
- Configure appropriate buffer sizes for memory management
- Monitor error rates to detect systemic issues

## Examples

See `examples.py` for comprehensive usage examples including:
- Basic field transformations
- Conditional processing
- Error handling
- Custom transformer registration
