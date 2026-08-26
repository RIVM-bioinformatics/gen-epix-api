# Pipeline Transform Framework

> 64 nodes · cohesion 0.05

## Key Concepts

- **TransformResult** (31 connections) — `gen_epix/transform/transform_result.py`
- **Pipeline** (21 connections) — `gen_epix/transform/pipeline.py`
- **StreamingPipeline** (13 connections) — `gen_epix/transform/streaming_pipeline.py`
- **StreamingPipeline** (10 connections) — `gen_epix/transform/streaming.py`
- **StreamProcessor** (8 connections) — `gen_epix/transform/stream_processer.py`
- **stream_processer.py** (7 connections) — `gen_epix/transform/stream_processer.py`
- **._process_single_object()** (6 connections) — `gen_epix/transform/pipeline.py`
- **streaming.py** (6 connections) — `gen_epix/transform/streaming.py`
- **._process_batch_async()** (6 connections) — `gen_epix/transform/streaming_pipeline.py`
- **._process_batch_async()** (6 connections) — `gen_epix/transform/streaming.py`
- **.process_stream()** (5 connections) — `gen_epix/transform/pipeline.py`
- **Any** (5 connections)
- **.collect_errors()** (5 connections) — `gen_epix/transform/streaming_pipeline.py`
- **._process_single_async()** (5 connections) — `gen_epix/transform/streaming_pipeline.py`
- **.process_stream_async()** (5 connections) — `gen_epix/transform/streaming_pipeline.py`
- **.process_stream_async_coroutine()** (5 connections) — `gen_epix/transform/streaming_pipeline.py`
- **Any** (5 connections)
- **.collect_errors()** (5 connections) — `gen_epix/transform/streaming.py`
- **._process_single_async()** (5 connections) — `gen_epix/transform/streaming.py`
- **.process_stream_async()** (5 connections) — `gen_epix/transform/streaming.py`
- **.process_stream_async_coroutine()** (5 connections) — `gen_epix/transform/streaming.py`
- **.add()** (4 connections) — `gen_epix/transform/pipeline.py`
- **._handle_error()** (4 connections) — `gen_epix/transform/pipeline.py`
- **.__or__()** (4 connections) — `gen_epix/transform/pipeline.py`
- **Any** (4 connections)
- *... and 39 more nodes in this community*

## Relationships

- [Data Transform Strategies](Data_Transform_Strategies.md) (25 shared connections)
- [Transform Framework Registry & Pipeline](Transform_Framework_Registry_&_Pipeline.md) (5 shared connections)

## Source Files

- `gen_epix/transform/pipeline.py`
- `gen_epix/transform/stream_processer.py`
- `gen_epix/transform/streaming.py`
- `gen_epix/transform/streaming_pipeline.py`
- `gen_epix/transform/transform_result.py`

## Audit Trail

- EXTRACTED: 127 (94%)
- INFERRED: 8 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*