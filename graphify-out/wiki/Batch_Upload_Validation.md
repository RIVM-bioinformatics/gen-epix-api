# Batch Upload Validation

> 51 nodes · cohesion 0.06

## Key Concepts

- **ParentForUpload** (27 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Model** (9 connections)
- **.get_parents_for_upload()** (8 connections) — `gen_epix/commondb/domain/model/upload.py`
- **model_validator** (7 connections)
- **Self** (7 connections)
- **._compute_child_order()** (6 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._serialize_id_fields()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._validate_child_ids()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._validate_intra_parent_links()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._validate_parent_ids()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_child_order()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_all_children_for_upload()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._ensure_result_type()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._validate_identifiers()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._child_fk_dependencies()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.__pydantic_init_subclass__()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.replace_child_id()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.validate_child_parent_id()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._validate_id_field()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.validate_parent_id()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **UUID** (4 connections)
- **._validate_upload_result()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_n_parents()** (3 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_parent_class()** (3 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_identifiers()** (3 connections) — `gen_epix/commondb/domain/model/upload.py`
- *... and 26 more nodes in this community*

## Relationships

- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (14 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (6 shared connections)
- [Child Model Order Derivation](Child_Model_Order_Derivation.md) (2 shared connections)
- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (2 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (1 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (1 shared connections)
- [Parent-Child Upload Models](Parent-Child_Upload_Models.md) (1 shared connections)
- [Case Upload Validation](Case_Upload_Validation.md) (1 shared connections)
- [Sequence Sample Upload Models](Sequence_Sample_Upload_Models.md) (1 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/upload.py`

## Audit Trail

- EXTRACTED: 98 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*