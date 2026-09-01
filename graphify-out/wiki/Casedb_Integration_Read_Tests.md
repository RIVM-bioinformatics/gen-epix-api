# Casedb Integration Read Tests

> 15 nodes

## Key Concepts

- **TestRead** (19 connections) — `test/casedb/integration/build_db/read.py`
- **Env** (11 connections)
- **skipif** (6 connections)
- **.test_read_case_set()** (3 connections) — `test/casedb/integration/build_db/read.py`
- **.test_read_case_set_raise()** (3 connections) — `test/casedb/integration/build_db/read.py`
- **.test_read_organization_access_or_share_case_policy_raise()** (3 connections) — `test/casedb/integration/build_db/read.py`
- **.test_read_organization_admin_emails_raise()** (3 connections) — `test/casedb/integration/build_db/read.py`
- **.test_read_user_access_or_share_case_policy_raise()** (3 connections) — `test/casedb/integration/build_db/read.py`
- **.test_read_user_raise()** (3 connections) — `test/casedb/integration/build_db/read.py`
- **.test_read_organization_access_or_share_case_policy()** (2 connections) — `test/casedb/integration/build_db/read.py`
- **.test_read_organization_admin_emails()** (2 connections) — `test/casedb/integration/build_db/read.py`
- **.test_read_organization_contact_by_organization_ids()** (2 connections) — `test/casedb/integration/build_db/read.py`
- **.test_read_user()** (2 connections) — `test/casedb/integration/build_db/read.py`
- **.test_read_user_access_or_share_case_policy()** (2 connections) — `test/casedb/integration/build_db/read.py`
- **scenario_ids** (1 connections)

## Relationships

- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [CasedbTestClient](CasedbTestClient.md) (1 shared connections)
- [Casedb Build DB Test Suite (CRUD Dependencies)](Casedb_Build_DB_Test_Suite_CRUD_Dependencies.md) (1 shared connections)
- [Commondb Build DB Test Suite (CRUD Dependencies)](Commondb_Build_DB_Test_Suite_CRUD_Dependencies.md) (1 shared connections)
- [Omopdb Build DB Test Suite (CRUD Dependencies)](Omopdb_Build_DB_Test_Suite_CRUD_Dependencies.md) (1 shared connections)
- [Seqdb Build DB Test Suite (CRUD Dependencies)](Seqdb_Build_DB_Test_Suite_CRUD_Dependencies.md) (1 shared connections)

## Source Files

- `test/casedb/integration/build_db/read.py`

## Audit Trail

- EXTRACTED: 31 (86%)
- INFERRED: 5 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*