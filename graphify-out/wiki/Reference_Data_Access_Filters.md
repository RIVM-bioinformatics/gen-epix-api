# Reference Data Access Filters

> 113 nodes · cohesion 0.03

## Key Concepts

- **UuidSetFilter** (65 connections) — `gen_epix/filter/uuid_set.py`
- **AbacService** (21 connections) — `gen_epix/casedb/services/abac.py`
- **RefDataAccess** (19 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **seq_service_calculate_phylogenetic_tree()** (16 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **BaseAbacTestCase** (15 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **._get_filter()** (12 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **._get_case_abac_cached()** (11 connections) — `gen_epix/casedb/services/abac.py`
- **._get_ref_data_access_cached()** (10 connections) — `gen_epix/casedb/services/abac.py`
- **retrieve_sample.py** (10 connections) — `gen_epix/seqdb/services/seq/retrieve_sample.py`
- **TestGetCaseAbac** (10 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.create_cmd_with_user()** (9 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.create_user_stub()** (9 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **copy_model_field()** (8 connections) — `gen_epix/util.py`
- **map_paired_elements()** (8 connections) — `gen_epix/util.py`
- **TestTempUpdateUserOrganization** (8 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **UUID** (7 connections)
- **TestRegisterPolicies** (7 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **.get_case_type_share_abac_dict()** (6 connections) — `gen_epix/casedb/services/abac.py`
- **._get_share_dict()** (6 connections) — `gen_epix/casedb/services/abac.py`
- **._get_share_intersect()** (6 connections) — `gen_epix/casedb/services/abac.py`
- **.create_update_user_cmd()** (6 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **UUID** (6 connections)
- **.get_case_abac()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **.get_ref_data_access()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **.update_user_own_organization()** (5 connections) — `gen_epix/casedb/services/abac.py`
- *... and 88 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (35 shared connections)
- [Case Access Rights ABAC](Case_Access_Rights_ABAC.md) (6 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (6 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (6 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (6 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (6 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (5 shared connections)
- [Case Access Policies](Case_Access_Policies.md) (4 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (4 shared connections)
- [Best Sequence Retrieval](Best_Sequence_Retrieval.md) (4 shared connections)
- [Sample Retrieval Commands](Sample_Retrieval_Commands.md) (4 shared connections)
- [Phylogenetic Tree Calculation](Phylogenetic_Tree_Calculation.md) (4 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/non_persistable.py`
- `gen_epix/casedb/domain/policy/abac.py`
- `gen_epix/casedb/domain/service/abac.py`
- `gen_epix/casedb/services/abac.py`
- `gen_epix/filter/uuid_set.py`
- `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- `gen_epix/seqdb/services/seq/retrieve_sample.py`
- `gen_epix/util.py`
- `test/casedb/unit/services/abac/test_casedb_abac.py`

## Audit Trail

- EXTRACTED: 283 (94%)
- INFERRED: 18 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*