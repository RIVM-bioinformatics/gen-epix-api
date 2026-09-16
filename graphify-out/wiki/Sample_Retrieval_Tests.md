# Sample Retrieval Tests

> 11 nodes · cohesion 0.31

## Key Concepts

- **env()** (11 connections) — `test/seqdb/integration/retrieve_samples/test_seqdb_retrieve_samples.py`
- **TestRetrieveSamples** (9 connections) — `test/seqdb/integration/retrieve_samples/test_seqdb_retrieve_samples.py`
- **._load_samples()** (4 connections) — `test/seqdb/integration/retrieve_samples/test_seqdb_retrieve_samples.py`
- **fixture** (2 connections)
- **FixtureRequest** (2 connections)
- **.test_retrieve_full_samples_by_ids()** (2 connections) — `test/seqdb/integration/retrieve_samples/test_seqdb_retrieve_samples.py`
- **.test_retrieve_full_samples_by_modified_range()** (2 connections) — `test/seqdb/integration/retrieve_samples/test_seqdb_retrieve_samples.py`
- **.test_retrieve_full_samples_with_duplicate_ids()** (2 connections) — `test/seqdb/integration/retrieve_samples/test_seqdb_retrieve_samples.py`
- **.test_retrieve_sample_identifiers_by_ids()** (2 connections) — `test/seqdb/integration/retrieve_samples/test_seqdb_retrieve_samples.py`
- **.test_retrieve_sample_identifiers_with_duplicate_ids()** (2 connections) — `test/seqdb/integration/retrieve_samples/test_seqdb_retrieve_samples.py`
- **Return a test client configured for either DICT or SA_SQLITE demo repos. The…** (1 connections) — `test/seqdb/integration/retrieve_samples/test_seqdb_retrieve_samples.py`

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [Protocol Creation Tests](Protocol_Creation_Tests.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `test/seqdb/integration/retrieve_samples/test_seqdb_retrieve_samples.py`

## Audit Trail

- EXTRACTED: 19 (86%)
- INFERRED: 3 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*