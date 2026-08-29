# Omopdb Retrieve Persons Integration Tests

> 9 nodes

## Key Concepts

- **env()** (9 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **TestRetrievePersons** (6 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **._load_persons()** (4 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **.test_retrieve_full_persons_by_ids()** (2 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **.test_retrieve_full_persons_by_modified_range()** (2 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **.test_retrieve_full_persons_with_duplicate_ids()** (2 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **fixture** (2 connections)
- **FixtureRequest** (2 connections)
- **Return a test client configured for either DICT or SA_SQLITE demo repos. The…** (1 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`

## Relationships

- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [AppCfg](AppCfg.md) (2 shared connections)

## Source Files

- `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`

## Audit Trail

- EXTRACTED: 15 (88%)
- INFERRED: 2 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*