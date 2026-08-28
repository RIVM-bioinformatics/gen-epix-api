# BaseAnonymizer

> 32 nodes · cohesion 0.09

## Key Concepts

- **BaseAnonymizer** (10 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **ModelAnonymizer** (10 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.anonymize()** (8 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.create_anonymization_map()** (6 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.__init__()** (6 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **Collection** (5 connections)
- **.anonymize_categorical()** (5 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.anonymize_dates()** (5 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.anonymize_ints()** (4 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.anonymize_uuids()** (4 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **Any** (4 connections)
- **.anonymize_text()** (3 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.compare_models()** (3 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.identify_and_load_categoricals()** (3 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **Model** (3 connections)
- **.__init__()** (2 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.attach_model_instance()** (2 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **ABC** (2 connections)
- **UUID** (2 connections)
- **date** (1 connections)
- **Domain** (1 connections)
- **Path** (1 connections)
- **Take a collection of uuid.UUID objects and returns a dict mapping each…** (1 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **Take a collection of categorical values and returns a dict mapping each value…** (1 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **ModelAnonymizer handles a instances of "subject" models that are are built from…** (1 connections) — `test/omopdb/test_client/model_anonymizer.py`
- *... and 7 more nodes in this community*

## Relationships

- [omopdb/domain/enum.py](omopdb-domain-enum.py.md) (6 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (1 shared connections)
- [BaseRepository](BaseRepository.md) (1 shared connections)

## Source Files

- `test/omopdb/test_client/model_anonymizer.py`

## Audit Trail

- EXTRACTED: 53 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*