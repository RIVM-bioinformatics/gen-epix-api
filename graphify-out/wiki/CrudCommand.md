# CrudCommand

> God node · 187 connections · `gen_epix/commondb/domain/command/base.py`

**Community:** [Geographic Region Commands](Geographic_Region_Commands.md)

## Connections by Relation

### contains
- command/base.py `EXTRACTED`

### imports
- seqdb/domain/command/__init__.py `EXTRACTED`
- casedb/domain/command/__init__.py `EXTRACTED`
- omopdb/domain/command/__init__.py `EXTRACTED`
- commondb/domain/command/__init__.py `EXTRACTED`
- command/omop.py `EXTRACTED`
- command/case.py `EXTRACTED`
- command/seq.py `EXTRACTED`
- command/organization.py `EXTRACTED`
- seq/crud_common.py `EXTRACTED`
- commondb/domain/command/system.py `EXTRACTED`
- command/ontology.py `EXTRACTED`
- command/geo.py `EXTRACTED`
- commondb/domain/command/abac.py `EXTRACTED`
- command/file.py `EXTRACTED`
- casedb/domain/command/abac.py `EXTRACTED`

### inherits
- [Command](Command.md) `EXTRACTED`
- CaseTypeCrudCommand `EXTRACTED`
- Model2_2CrudCommand `EXTRACTED`
- DimCrudCommand `EXTRACTED`
- Model1_2CrudCommand `EXTRACTED`
- Model2_1CrudCommand `EXTRACTED`
- Model1_1CrudCommand `EXTRACTED`
- ColCrudCommand `EXTRACTED`
- CaseCrudCommand `EXTRACTED`
- CaseTypeSetCrudCommand `EXTRACTED`
- RefDimCrudCommand `EXTRACTED`
- CaseSetCrudCommand `EXTRACTED`
- RefColCrudCommand `EXTRACTED`
- UserCrudCommand `EXTRACTED`
- CaseDataCollectionLinkCrudCommand `EXTRACTED`
- CaseIdentifierCrudCommand `EXTRACTED`
- CaseSetDataCollectionLinkCrudCommand `EXTRACTED`
- CaseSetMemberCrudCommand `EXTRACTED`
- CaseTypeSetCategoryCrudCommand `EXTRACTED`
- CaseTypeSetMemberCrudCommand `EXTRACTED`
- *…and 118 more `inherits` connection(s) not listed (lowest-degree first to go)*

### rationale_for
- Extends parent CrudCommand with more narrowly typed properties. `EXTRACTED`

### references
- _crud_cascade_delete() `EXTRACTED`
- crud_with_access_filter() `EXTRACTED`
- get_ref_data_access_from_command() `EXTRACTED`
- get_case_abac_from_command() `EXTRACTED`
- .register_entity() `EXTRACTED`
- .crud() `EXTRACTED`
- _cascade_delete_linked_models() `EXTRACTED`
- _verify_is_read_operation() `EXTRACTED`
- ._verify_same_service_links() `EXTRACTED`
- ._link_new_command() `EXTRACTED`
- ._execute_crud_operation() `EXTRACTED`
- ._verify_other_service_links() `EXTRACTED`
- ._read_association_with_valid_ids() `EXTRACTED`
- .crud_repository() `EXTRACTED`
- .get_crud_command_for_model() `EXTRACTED`
- .handle_crud_command() `EXTRACTED`
- ._get_model_links() `EXTRACTED`
- .create_generated_crud_route_handler() `EXTRACTED`
- .register_generated_crud_route() `EXTRACTED`
- .get_crud_command_for_entity() `EXTRACTED`
- *…and 12 more `references` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*