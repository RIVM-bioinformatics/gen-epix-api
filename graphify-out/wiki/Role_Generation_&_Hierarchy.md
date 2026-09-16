# Role Generation & Hierarchy

> 99 nodes · cohesion 0.04

## Key Concepts

- **User** (68 connections) — `gen_epix/commondb/domain/model/organization.py`
- **Role** (57 connections) — `gen_epix/commondb/domain/enum.py`
- **test_read_user_policy.py** (24 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **._make_user_cmd()** (18 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **BaseReadUserPolicyTestCase** (17 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **test_update_case_created_in_data_collection.py** (16 connections) — `test/casedb/unit/services/case/update_case_created_in_data_collection/test_update_case_created_in_data_collection.py`
- **._make_user()** (16 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **TestRegularUserReads** (15 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **._make_org_admin_policy()** (13 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **case_service_update_case_created_in_data_collection()** (12 connections) — `gen_epix/casedb/services/case/update_case_created_in_data_collection.py`
- **LogicalOperator** (12 connections) — `gen_epix/filter/enum.py`
- **TestOrgAdminReads** (11 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **UserInvitation** (10 connections) — `gen_epix/commondb/domain/model/organization.py`
- **update_case_created_in_data_collection.py** (9 connections) — `gen_epix/casedb/services/case/update_case_created_in_data_collection.py`
- **TestUnauthenticated** (9 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **TestUnsupportedAndNonReadPaths** (9 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **._users()** (7 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **TestAppAdminBypass** (7 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **RoleGenerator** (6 connections) — `gen_epix/casedb/domain/policy/permission.py`
- **field_validator** (5 connections)
- **scenario_ids** (5 connections)
- **.test_read_all_org_admin_filters_and_allows_inactive()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_one_org_admin_allows_inactive()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_some_org_admin_authorizes_subset()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_some_org_admin_denies_outside_org()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- *... and 74 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (31 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (24 shared connections)
- [User Update ABAC Policy](User_Update_ABAC_Policy.md) (9 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (9 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (8 shared connections)
- [Seq Distance Calculation Tests](Seq_Distance_Calculation_Tests.md) (6 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (5 shared connections)
- [Role Mapping Generator](Role_Mapping_Generator.md) (4 shared connections)
- [Parent-Child Upload Models](Parent-Child_Upload_Models.md) (4 shared connections)
- [Best Sequence Retrieval](Best_Sequence_Retrieval.md) (4 shared connections)
- [Complete Case Type Retrieval Tests](Complete_Case_Type_Retrieval_Tests.md) (4 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (4 shared connections)

## Source Files

- `gen_epix/casedb/domain/policy/permission.py`
- `gen_epix/casedb/services/case/update_case_created_in_data_collection.py`
- `gen_epix/commondb/domain/enum.py`
- `gen_epix/commondb/domain/model/organization.py`
- `gen_epix/filter/enum.py`
- `test/casedb/unit/services/case/update_case_created_in_data_collection/test_update_case_created_in_data_collection.py`
- `test/commondb/unit/policies/test_read_user_policy.py`
- `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Audit Trail

- EXTRACTED: 269 (80%)
- INFERRED: 68 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*