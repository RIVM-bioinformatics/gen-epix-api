# Casedb Case CRUD Commands

> 248 nodes · cohesion 0.02

## Key Concepts

- **BaseUnitOfWork** (246 connections) — `gen_epix/fastapp/unit_of_work.py`
- **BaseCaseService** (149 connections) — `gen_epix/casedb/services/case/base.py`
- **case/service.py** (98 connections) — `gen_epix/casedb/services/case/service.py`
- **fastapp/unit_of_work.py** (52 connections) — `gen_epix/fastapp/unit_of_work.py`
- **casedb/services/case/base.py** (49 connections) — `gen_epix/casedb/services/case/base.py`
- **case/crud_common.py** (46 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **_crud_cascade_delete()** (45 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **casedb/domain/exc.py** (38 connections) — `gen_epix/casedb/domain/exc.py`
- **services/case/upload.py** (32 connections) — `gen_epix/casedb/services/case/upload.py`
- **crud_with_access_filter()** (29 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **get_ref_data_access_from_command()** (22 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **create_seq.py** (20 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **crud_col.py** (18 connections) — `gen_epix/casedb/services/case/crud_col.py`
- **crud_case.py** (17 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **get_case_abac_from_command()** (17 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **is_app_admin_or_above()** (17 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **crud_case_data_collection_link.py** (16 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **crud_case_set_data_collection_link.py** (16 connections) — `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- **crud_case_set_member.py** (16 connections) — `gen_epix/casedb/services/case/crud_case_set_member.py`
- **crud_case_identifier.py** (15 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **crud_case_type.py** (15 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **crud_case_type_set.py** (15 connections) — `gen_epix/casedb/services/case/crud_case_type_set.py`
- **crud_col_set_member.py** (15 connections) — `gen_epix/casedb/services/case/crud_col_set_member.py`
- **crud_ref_dim.py** (15 connections) — `gen_epix/casedb/services/case/crud_ref_dim.py`
- **crud_case_type_set_member.py** (14 connections) — `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- *... and 223 more nodes in this community*

## Relationships

- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (49 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (43 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (40 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (35 shared connections)
- [Dim CRUD Command](Dim_CRUD_Command.md) (31 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (30 shared connections)
- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (30 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (22 shared connections)
- [Casedb Retrieve Case Query Logic](Casedb_Retrieve_Case_Query_Logic.md) (22 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (21 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (16 shared connections)
- [Case CRUD Command](Case_CRUD_Command.md) (14 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/exc.py`
- `gen_epix/casedb/services/case/base.py`
- `gen_epix/casedb/services/case/create_case_set.py`
- `gen_epix/casedb/services/case/create_seq.py`
- `gen_epix/casedb/services/case/crud_case.py`
- `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- `gen_epix/casedb/services/case/crud_case_identifier.py`
- `gen_epix/casedb/services/case/crud_case_set_category.py`
- `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- `gen_epix/casedb/services/case/crud_case_set_member.py`
- `gen_epix/casedb/services/case/crud_case_set_status.py`
- `gen_epix/casedb/services/case/crud_case_type.py`
- `gen_epix/casedb/services/case/crud_case_type_set.py`
- `gen_epix/casedb/services/case/crud_case_type_set_category.py`
- `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- `gen_epix/casedb/services/case/crud_col.py`
- `gen_epix/casedb/services/case/crud_col_set.py`
- `gen_epix/casedb/services/case/crud_col_set_member.py`
- `gen_epix/casedb/services/case/crud_common.py`

## Audit Trail

- EXTRACTED: 1150 (92%)
- INFERRED: 96 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*