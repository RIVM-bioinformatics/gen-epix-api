# ID String Parsing

> 20 nodes · cohesion 0.13

## Key Concepts

- **.convert_ids_string_to_list()** (11 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **TestConvertIdsStringToList** (10 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **.test_handles_empty_string_as_comma_separated()** (3 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **.test_handles_invalid_comma_separated()** (3 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **.test_handles_malformed_json()** (3 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **.test_handles_uuid_comma_separated()** (3 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **.test_handles_valid_json_with_some_invalid()** (3 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **.test_parses_comma_separated_ids()** (3 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **.test_parses_json_encoded_ids()** (3 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **endpoint_function()** (2 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **endpoint_function()** (2 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **Parse comma-separated or JSON-encoded identifiers for a route parameter. Args:…** (1 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **Tests for ID parsing from comma-separated or JSON strings.** (1 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **Verify parsing of comma-separated IDs.** (1 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **Verify parsing of JSON-encoded IDs.** (1 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **Verify handling of invalid IDs in comma-separated format.** (1 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **Verify handling of JSON with some invalid IDs.** (1 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **Verify parsing of UUID comma-separated format.** (1 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **Verify handling of empty ID string.** (1 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **Verify handling of malformed JSON string.** (1 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`

## Relationships

- [CRUD Endpoint Generation](CRUD_Endpoint_Generation.md) (5 shared connections)

## Source Files

- `gen_epix/fastapp/api/crud_endpoint_generator.py`
- `test/fastapp/unit/api/test_crud_endpoint_generator.py`

## Audit Trail

- EXTRACTED: 29 (97%)
- INFERRED: 1 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*