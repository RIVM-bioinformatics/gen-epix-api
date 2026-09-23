# Command

> God node · 181 connections · `gen_epix/commondb/domain/command/base.py`

**Community:** [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md)

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
- api/system.py `EXTRACTED`
- commondb/domain/command/system.py `EXTRACTED`
- commondb/domain/policy/abac.py `EXTRACTED`
- casedb/domain/service/abac.py `EXTRACTED`
- command/geo.py `EXTRACTED`
- commondb/domain/command/abac.py `EXTRACTED`
- command/rbac.py `EXTRACTED`
- command/file.py `EXTRACTED`
- command/seqdb.py `EXTRACTED`

### inherits
- [CrudCommand](CrudCommand.md) `EXTRACTED`
- UploadSamplesCommand `EXTRACTED`
- UploadCasesCommand `EXTRACTED`
- UpdateAssociationCommand `EXTRACTED`
- UploadPersonsCommand `EXTRACTED`
- CalculatePhylogeneticTreeCommand `EXTRACTED`
- UpdateUserOwnOrganizationCommand `EXTRACTED`
- GetIdentityProvidersCommand `EXTRACTED`
- DummyCmd `EXTRACTED`
- RetrieveCasesByIdCommand `EXTRACTED`
- InviteUserCommand `EXTRACTED`
- RegisterInvitedUserCommand `EXTRACTED`
- RetrieveInviteUserConstraintsCommand `EXTRACTED`
- UpdateUserCommand `EXTRACTED`
- RetrieveCaseRightsCommand `EXTRACTED`
- RetrieveOrganizationAdminNameEmailsCommand `EXTRACTED`
- CreateCaseSetCommand `EXTRACTED`
- CreateFileForReadSetCommand `EXTRACTED`
- CreateFileForSeqCommand `EXTRACTED`
- RetrieveCaseSetStatsCommand `EXTRACTED`
- *…and 42 more `inherits` connection(s) not listed (lowest-degree first to go)*

### method
- ._serialize_created_at() `EXTRACTED`
- ._serialize_props() `EXTRACTED`

### rationale_for
- Represents commondb user context, audit metadata, and serializable properties. `EXTRACTED`

### references
- .create_log_message() `EXTRACTED`
- .attach_abac_policy() `EXTRACTED`
- .handle() `EXTRACTED`
- .__init__() `EXTRACTED`
- .register_command() `EXTRACTED`
- register_domain_entities() `EXTRACTED`
- ._verify_command_exists() `EXTRACTED`
- .register_route_for() `EXTRACTED`
- .register_roles() `EXTRACTED`
- .filter() `EXTRACTED`
- .handle() `EXTRACTED`
- .get_mapped_class() `EXTRACTED`
- ._execute_command() `EXTRACTED`
- .request() `EXTRACTED`
- .stream() `EXTRACTED`
- .get_permissions_for_command() `EXTRACTED`
- ._filter_users_by_organization() `EXTRACTED`
- .register_handler() `EXTRACTED`
- .register_listener() `EXTRACTED`
- .unregister_listener() `EXTRACTED`
- *…and 77 more `references` connection(s) not listed (lowest-degree first to go)*

### uses
- create_system_endpoints() `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*