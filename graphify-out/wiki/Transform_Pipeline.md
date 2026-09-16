# Transform Pipeline

> 74 nodes · cohesion 0.04

## Key Concepts

- **TransformResult** (32 connections) — `gen_epix/transform/transform_result.py`
- **Pipeline** (21 connections) — `gen_epix/transform/pipeline.py`
- **StreamingPipeline** (13 connections) — `gen_epix/transform/streaming_pipeline.py`
- **StreamingPipeline** (10 connections) — `gen_epix/transform/streaming.py`
- **transform_result.py** (10 connections) — `gen_epix/transform/transform_result.py`
- **StreamProcessor** (8 connections) — `gen_epix/transform/stream_processer.py`
- **._process_single_object()** (7 connections) — `gen_epix/transform/pipeline.py`
- **stream_processer.py** (7 connections) — `gen_epix/transform/stream_processer.py`
- **streaming_pipeline.py** (7 connections) — `gen_epix/transform/streaming_pipeline.py`
- **streaming.py** (6 connections) — `gen_epix/transform/streaming.py`
- **._process_batch_async()** (6 connections) — `gen_epix/transform/streaming_pipeline.py`
- **._process_single_async()** (6 connections) — `gen_epix/transform/streaming_pipeline.py`
- **._process_batch_async()** (6 connections) — `gen_epix/transform/streaming.py`
- **._process_single_async()** (6 connections) — `gen_epix/transform/streaming.py`
- **.process_stream()** (5 connections) — `gen_epix/transform/pipeline.py`
- **Any** (5 connections)
- **.collect_errors()** (5 connections) — `gen_epix/transform/streaming_pipeline.py`
- **.process_stream_async()** (5 connections) — `gen_epix/transform/streaming_pipeline.py`
- **.process_stream_async_coroutine()** (5 connections) — `gen_epix/transform/streaming_pipeline.py`
- **Any** (5 connections)
- **.collect_errors()** (5 connections) — `gen_epix/transform/streaming.py`
- **.process_stream_async()** (5 connections) — `gen_epix/transform/streaming.py`
- **.process_stream_async_coroutine()** (5 connections) — `gen_epix/transform/streaming.py`
- **.add()** (4 connections) — `gen_epix/transform/pipeline.py`
- **._handle_error()** (4 connections) — `gen_epix/transform/pipeline.py`
- *... and 49 more nodes in this community*

## Relationships

- [Transform Adapters & Examples](Transform_Adapters_&_Examples.md) (27 shared connections)
- [Transform Enums & Intervals](Transform_Enums_&_Intervals.md) (4 shared connections)
- [Object Adapter Transforms](Object_Adapter_Transforms.md) (1 shared connections)

## Source Files

- `gen_epix/transform/pipeline.py`
- `gen_epix/transform/stream_processer.py`
- `gen_epix/transform/streaming.py`
- `gen_epix/transform/streaming_pipeline.py`
- `gen_epix/transform/transform_result.py`

## Audit Trail

- EXTRACTED: 143 (94%)
- INFERRED: 9 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*