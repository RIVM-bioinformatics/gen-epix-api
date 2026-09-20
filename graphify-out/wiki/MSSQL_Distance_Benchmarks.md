# MSSQL Distance Benchmarks

> 12 nodes · cohesion 0.23

## Key Concepts

- **_MssqlBenchmarkBase** (9 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`
- **TestDistanceOptimizationBenchmark** (6 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`
- **TestDistanceOptimizationBenchmarkMssql1000** (5 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`
- **TestDistanceOptimizationBenchmarkMssql10000** (5 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`
- **TestDistanceOptimizationBenchmarkMssql5000** (5 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`
- **performance** (4 connections)
- **mssql** (3 connections)
- **Shared setup/teardown and test body for MSSQL n_existing classes. Each concrete…** (1 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`
- **MSSQL benchmark at n_existing=1000. Runs before Mssql5000 (alphabetical order)…** (1 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`
- **MSSQL benchmark at n_existing=5000.** (1 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`
- **MSSQL benchmark at n_existing=10000.** (1 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`
- **Compare three distance-calculation variants on DICT and SA_SQLITE repos. Each…** (1 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (5 shared connections)
- [Benchmark Chart Generation](Benchmark_Chart_Generation.md) (4 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)
- [Seq Upload & SQL Models](Seq_Upload_&_SQL_Models.md) (1 shared connections)

## Source Files

- `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`

## Audit Trail

- EXTRACTED: 25 (93%)
- INFERRED: 2 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*