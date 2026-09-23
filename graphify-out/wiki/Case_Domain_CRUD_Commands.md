# Case Domain CRUD Commands

> 358 nodes · cohesion 0.01

## Key Concepts

- **CrudOperation** (234 connections) — `gen_epix/fastapp/enum.py`
- **casedb/domain/command/__init__.py** (148 connections) — `gen_epix/casedb/domain/command/__init__.py`
- **casedb/domain/model/__init__.py** (123 connections) — `gen_epix/casedb/domain/model/__init__.py`
- **casedb/domain/enum.py** (111 connections) — `gen_epix/casedb/domain/enum.py`
- **BaseService** (80 connections) — `gen_epix/fastapp/service.py`
- **case/service.py** (68 connections) — `gen_epix/casedb/services/case/service.py`
- **command/case.py** (60 connections) — `gen_epix/casedb/domain/command/case.py`
- **mock_compat.py** (48 connections) — `test/util/mock_compat.py`
- **casedb/domain/exc.py** (40 connections) — `gen_epix/casedb/domain/exc.py`
- **retrieve_case.py** (37 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **services/case/upload.py** (33 connections) — `gen_epix/casedb/services/case/upload.py`
- **case_validator.py** (31 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **CaseBatchUploader** (31 connections) — `gen_epix/casedb/services/case/upload.py`
- **test_casedb_refdata_access.py** (26 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **UploadCasesCommand** (25 connections) — `gen_epix/casedb/domain/command/case.py`
- **casedb/services/abac.py** (24 connections) — `gen_epix/casedb/services/abac.py`
- **CaseBatchUploadResult** (23 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **BaseCaseAbacPolicy** (23 connections) — `gen_epix/casedb/domain/policy/abac.py`
- **retrieve_complete_case_type.py** (23 connections) — `gen_epix/casedb/services/case/retrieve_complete_case_type.py`
- **test_casedb_crud_dim.py** (23 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **test_casedb_retrieve_similar_cases.py** (22 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_similar_cases.py`
- **test_casedb_opsdata_access.py** (21 connections) — `test/casedb/integration/data_access/test_casedb_opsdata_access.py`
- **retrieve_seq.py** (19 connections) — `gen_epix/casedb/services/case/retrieve_seq.py`
- **seqdb/service.py** (19 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **test_casedb_abac.py** (19 connections) — `test/casedb/unit/services/abac/test_casedb_abac.py`
- *... and 333 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (151 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (48 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (41 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (35 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (32 shared connections)
- [Organization Contacts Retrieval](Organization_Contacts_Retrieval.md) (32 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (31 shared connections)
- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (30 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (29 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (29 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (24 shared connections)
- [Dimension CRUD Service](Dimension_CRUD_Service.md) (23 shared connections)

## Source Files

- `gen_epix/casedb/api/ontology.py`
- `gen_epix/casedb/domain/__init__.py`
- `gen_epix/casedb/domain/command/__init__.py`
- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/command/geo.py`
- `gen_epix/casedb/domain/enum.py`
- `gen_epix/casedb/domain/exc.py`
- `gen_epix/casedb/domain/model/__init__.py`
- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/casedb/domain/model/geo.py`
- `gen_epix/casedb/domain/model/ontology.py`
- `gen_epix/casedb/domain/policy/__init__.py`
- `gen_epix/casedb/domain/policy/abac.py`
- `gen_epix/casedb/domain/policy/permission.py`
- `gen_epix/casedb/domain/service/__init__.py`
- `gen_epix/casedb/domain/service/abac.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/domain/service/geo.py`
- `gen_epix/casedb/domain/service/ontology.py`
- `gen_epix/casedb/domain/service/seqdb.py`

## Audit Trail

- EXTRACTED: 1806 (92%)
- INFERRED: 161 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*