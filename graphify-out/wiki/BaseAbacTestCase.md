# BaseAbacTestCase

> 45 nodes · cohesion 0.07

## Key Concepts

- **BaseAbacTestCase** (12 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **TestGetCaseAbac** (10 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.create_cmd_with_user()** (9 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.create_user_stub()** (9 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.create_update_user_cmd()** (6 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **UUID** (6 connections)
- **TestRegisterPolicies** (6 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **TestTempUpdateUserOrganization** (6 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **OrgPolicyDumpStub** (5 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **Any** (5 connections)
- **.test_happy_path_transfers_policies_and_updates_user()** (5 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **UserModelStub** (5 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **._create_app_mock()** (4 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.setup_method()** (4 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.test_get_case_abac_caches_results()** (4 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.test_get_case_abac_full_access_short_circuits()** (4 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.test_get_case_abac_no_policies_returns_empty()** (4 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.test_get_case_abac_with_policies_builds_intersection()** (4 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **scenario_ids** (3 connections)
- **.test_get_case_abac_none_user_id_raises()** (3 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.test_no_change_same_org_returns_early()** (3 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.__init__()** (2 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.model_dump()** (2 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **get_case_abac raises UnauthorizedAuthError when cmd.user is None.** (2 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.test_get_case_abac_no_user_raises()** (2 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- *... and 20 more nodes in this community*

## Relationships

- [CrudOperation](CrudOperation.md) (5 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (1 shared connections)
- [CaseAbacPolicy](CaseAbacPolicy.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/abac/test_casedb_abac.py`

## Audit Trail

- EXTRACTED: 76 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*