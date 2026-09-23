# Case Upload Results

> 91 nodes · cohesion 0.03

## Key Concepts

- **LogItem** (37 connections) — `gen_epix/etl/model.py`
- **ParentUploadResult** (28 connections) — `gen_epix/commondb/domain/model/upload.py`
- **TestBaseEtlResult** (24 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **LogLevel** (21 connections) — `gen_epix/fastapp/enum.py`
- **test_omopdb_upload_base_result.py** (15 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **TestUploadResult** (14 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **SampleUploadResult** (8 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **CaseUploadResult** (7 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **PersonUploadResult** (7 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **_ConcreteResult** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **TestEtlLogItem** (6 connections) — `test/etl/test_model.py`
- **TestResultLogItem** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **.get_child_results_field_names()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.test_add_logs_accepts_one_or_many_and_propagates_errors()** (5 connections) — `test/etl/test_model.py`
- **_make_pending_upload_result()** (5 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **.convert_status()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_status_count()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.propagate_child_failures()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Get all data issues that are errors.** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._serialize_severity()** (4 connections) — `gen_epix/etl/model.py`
- **._validate_severity()** (4 connections) — `gen_epix/etl/model.py`
- **scenario_ids** (4 connections)
- **.get_errors()** (3 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **.get_error_data_issues()** (3 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.add_logs()** (3 connections) — `gen_epix/etl/model.py`
- *... and 66 more nodes in this community*

## Relationships

- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (30 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (14 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (9 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (5 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (3 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (3 shared connections)
- [Parent-Child Upload Models](Parent-Child_Upload_Models.md) (2 shared connections)
- [Sequence Sample Upload Models](Sequence_Sample_Upload_Models.md) (2 shared connections)
- [Command Exception Handling](Command_Exception_Handling.md) (2 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (2 shared connections)
- [Complete Case Type Models](Complete_Case_Type_Models.md) (1 shared connections)
- [Upload Field Mutability Tests](Upload_Field_Mutability_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/etl/model.py`
- `gen_epix/fastapp/enum.py`
- `gen_epix/omopdb/domain/model/omop/upload.py`
- `gen_epix/seqdb/domain/model/seq/upload.py`
- `test/etl/test_model.py`
- `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`

## Audit Trail

- EXTRACTED: 173 (86%)
- INFERRED: 27 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*