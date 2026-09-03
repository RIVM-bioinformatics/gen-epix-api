# Casedb Metadata Integration Tests

> 6 nodes

## Key Concepts

- **get_test_client()** (5 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **setup_reference_data()** (5 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **.setup()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **Env** (3 connections)
- **fixture** (3 connections)
- **Register root1_1 + org1, invite root1_2, and create minimum CaseType…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`

## Relationships

- [commondb/domain/enum.py](commondb-domain-enum.py.md) (3 shared connections)
- [CasedbTestClient](CasedbTestClient.md) (2 shared connections)
- [CaseTypeCrudCommand](CaseTypeCrudCommand.md) (1 shared connections)

## Source Files

- `test/casedb/integration/metadata/test_casedb_metadata.py`

## Audit Trail

- EXTRACTED: 10 (77%)
- INFERRED: 3 (23%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*