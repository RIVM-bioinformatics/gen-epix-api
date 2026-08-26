# ETL Result Logging

> 80 nodes · cohesion 0.03

## Key Concepts

- **EtlLogItem** (25 connections) — `gen_epix/commondb/domain/model/base.py`
- **TestBaseResult** (22 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **BaseEtlResult** (19 connections) — `gen_epix/commondb/domain/model/base.py`
- **test_omopdb_upload_base_result.py** (15 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **TestUploadResult** (11 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **_ConcreteResult** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **.add_error()** (4 connections) — `gen_epix/commondb/domain/model/base.py`
- **_make_pending_upload_result()** (4 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **scenario_ids** (4 connections)
- **TestResultLogItem** (4 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **.get_errors()** (3 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **.add_info()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.add_warning()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.get_errors()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.get_infos()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.get_warnings()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.set_error_status()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **._serialize_severity()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **._validate_severity()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.get_errors()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.get_errors()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.has_errors()** (2 connections) — `gen_epix/commondb/domain/model/base.py`
- **.has_infos()** (2 connections) — `gen_epix/commondb/domain/model/base.py`
- **.has_log_code()** (2 connections) — `gen_epix/commondb/domain/model/base.py`
- **.has_warnings()** (2 connections) — `gen_epix/commondb/domain/model/base.py`
- *... and 55 more nodes in this community*

## Relationships

- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (6 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (4 shared connections)
- [Seqdb Upload Test Suite](Seqdb_Upload_Test_Suite.md) (3 shared connections)
- [API Exception Handling](API_Exception_Handling.md) (3 shared connections)
- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (2 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (1 shared connections)
- [Omopdb Upload Test Suite](Omopdb_Upload_Test_Suite.md) (1 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (1 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/commondb/domain/model/base.py`
- `gen_epix/omopdb/domain/model/omop/upload.py`
- `gen_epix/seqdb/domain/model/seq/upload.py`
- `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`

## Audit Trail

- EXTRACTED: 121 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*