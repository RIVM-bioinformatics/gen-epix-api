# Casedb Domain Enums & Policy

> 50 nodes · cohesion 0.06

## Key Concepts

- **BaseCaseAbacPolicy** (26 connections) — `gen_epix/casedb/domain/policy/abac.py`
- **test_casedb_retrieve_similar_cases.py** (22 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_similar_cases.py`
- **test_casedb_retrieve_is_own_cases.py** (20 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **case_service_retrieve_is_own_cases()** (19 connections) — `gen_epix/casedb/services/case/retrieve_is_own_cases.py`
- **test_casedb_abac.py** (19 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- **retrieve_seq.py** (18 connections) — `gen_epix/casedb/services/case/retrieve_seq.py`
- **casedb/policies/__init__.py** (16 connections) — `gen_epix/casedb/policies/__init__.py`
- **casedb/domain/policy/abac.py** (15 connections) — `gen_epix/casedb/domain/policy/abac.py`
- **.get_case_abac_from_command()** (15 connections) — `gen_epix/casedb/domain/policy/abac.py`
- **case_service_retrieve_similar_cases()** (15 connections) — `gen_epix/casedb/services/case/retrieve_similar_cases.py`
- **retrieve_similar_cases.py** (14 connections) — `gen_epix/casedb/services/case/retrieve_similar_cases.py`
- **retrieve_is_own_cases.py** (12 connections) — `gen_epix/casedb/services/case/retrieve_is_own_cases.py`
- **case_service_retrieve_complete_case_type()** (11 connections) — `gen_epix/casedb/services/case/retrieve_complete_case_type.py`
- **case_service_retrieve_genetic_sequence_fasta_by_case()** (9 connections) — `gen_epix/casedb/services/case/retrieve_seq.py`
- **case_service_retrieve_phylogenetic_tree()** (8 connections) — `gen_epix/casedb/services/case/retrieve_seq.py`
- **_get_seq_ids_from_cases()** (8 connections) — `gen_epix/casedb/services/case/retrieve_seq.py`
- **CaseAbacPolicy** (7 connections) — `gen_epix/casedb/policies/case_abac_policy.py`
- **case_service_retrieve_protocols()** (7 connections) — `gen_epix/casedb/services/case/retrieve_seq.py`
- **case_abac_policy.py** (6 connections) — `gen_epix/casedb/policies/case_abac_policy.py`
- **.retrieve_complete_case_type()** (5 connections) — `gen_epix/casedb/services/case/service.py`
- **.get_ref_data_access_from_command()** (4 connections) — `gen_epix/casedb/domain/policy/abac.py`
- **BaseCaseService** (4 connections)
- **.retrieve_genetic_sequence_fasta_by_case()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.retrieve_phylogenetic_tree()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.retrieve_protocols()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- *... and 25 more nodes in this community*

## Relationships

- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (43 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (18 shared connections)
- [Own Cases Policy Tests](Own_Cases_Policy_Tests.md) (18 shared connections)
- [Similar Cases Test Fixtures](Similar_Cases_Test_Fixtures.md) (11 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (9 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (8 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (7 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (7 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (6 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (6 shared connections)
- [ABAC Test Base](ABAC_Test_Base.md) (6 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (5 shared connections)

## Source Files

- `gen_epix/casedb/domain/policy/abac.py`
- `gen_epix/casedb/policies/__init__.py`
- `gen_epix/casedb/policies/case_abac_policy.py`
- `gen_epix/casedb/services/case/retrieve_complete_case_type.py`
- `gen_epix/casedb/services/case/retrieve_is_own_cases.py`
- `gen_epix/casedb/services/case/retrieve_seq.py`
- `gen_epix/casedb/services/case/retrieve_similar_cases.py`
- `gen_epix/casedb/services/case/service.py`
- `test/casedb/unit/services/abac/test_casedb_abac.py`
- `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_similar_cases.py`

## Audit Trail

- EXTRACTED: 249 (97%)
- INFERRED: 8 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*