# Read User Policy Tests

> 20 nodes · cohesion 0.17

## Key Concepts

- **Role** (31 connections) — `gen_epix/casedb/domain/enum.py`
- **test_read_user_policy.py** (24 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **BaseReadUserPolicyTestCase** (14 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **TestRegularUserReads** (13 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **TestOrgAdminReads** (10 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **TestUnauthenticated** (7 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **TestUnsupportedAndNonReadPaths** (7 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **TestAppAdminBypass** (6 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **scenario_ids** (5 connections)
- **.test_none_user_raises_assertion()** (3 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_unsupported_command_type_raises()** (2 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **Unit tests for ReadUserPolicy.filter. The tests cover all branches in…** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **Test unsupported command types and non-read operations.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **Unsupported command type should raise NotImplementedError.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **Test unauthenticated user conditions.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **None user should assert.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **Test APP_ADMIN users bypass ABAC filtering.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **Test organization admin read behavior.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **Base test case with common fixtures and utilities.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **Test regular user read behavior.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`

## Relationships

- [User Read Policy Tests](User_Read_Policy_Tests.md) (18 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (9 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (4 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (4 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (3 shared connections)
- [Read User Policy Filter](Read_User_Policy_Filter.md) (3 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (2 shared connections)
- [DataCollection/User Update RBAC Tests](DataCollection-User_Update_RBAC_Tests.md) (2 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (2 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (1 shared connections)
- [Casedb Test Client Helpers](Casedb_Test_Client_Helpers.md) (1 shared connections)
- [Case Type Update Tests](Case_Type_Update_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/enum.py`
- `test/commondb/unit/policies/test_read_user_policy.py`

## Audit Trail

- EXTRACTED: 65 (66%)
- INFERRED: 33 (34%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*