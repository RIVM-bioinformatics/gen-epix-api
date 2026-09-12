# Graph Report - gen-epix-api  (2026-09-10)

## Corpus Check
- 906 files · ~1,189,157 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 18166 nodes · 40918 edges · 673 communities (475 shown, 180 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 2825 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2f18ddb3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BaseAppComposer
- CacheBackend
- CrudOperation
- ParentForUpload
- .filter
- DomainException
- test_omopdb_upload.py
- gen_epix/fastapp/model.py
- AppCfg
- Client
- Enum
- SeqdbEndpointTestClient
- commondb/api/organization.py
- api/case.py
- omopdb/domain/model/__init__.py
- JWKSManager
- MockRequest
- CaseService
- crud_dim.py
- BaseCrudTestCase
- BaseCaseService
- seqdb/domain/model/__init__.py
- App
- SeqService
- ._get_week_start
- commondb/repositories/__init__.py
- JsonFormatter
- validate_int_for_uuid_field
- EtlStatus
- TupleMapTransformer
- SeqdbRemoteApp
- Model
- TransformResult
- test_casedb_case_validator.py
- BaseCaseService
- test_user_manager_auto_create.py
- Run
- Filter
- test_fastapp_cache_key.py
- TokenIntrospectionManager
- Any
- BaseUnitOfWork
- TestToken
- _uuid_field_name
- ObjectAdapter
- casedb CASE Simplified ERD
- CrudEndpointSet
- create_custom_openapi_function
- CasedbTestClient
- test_seqdb_convert_seq_format.py
- BaseFilterTestCase
- .__init__
- SeqProfile
- Base
- profile_method
- SARepository
- Model
- omopdb/domain/command/__init__.py
- _get_best_id_per_sample
- TestTokenStore
- test_fastapp_rbac_service.py
- Domain
- ._validate_state
- DictRepository
- gen_epix/fastapp/enum.py
- test_alembic_migrations.py
- RequestScope
- omopdb/repositories/__init__.py
- casedb/repositories/__init__.py
- LogicalOperator
- Any
- token_endpoint
- .create_command_and_result_for_samples
- UploadPersonsCommand
- .create_client
- AbacService
- ErmGenerator
- command/case.py
- Unit
- seqdb/services/rbac.py
- crud_endpoint_generator.py
- test_fastapp_api.py
- SeqProfileForUpload
- define_edge_cases_reference.py
- .__init__
- SeqdbTestClient
- .is_allowed
- .rev_role_map
- TestClientStore
- test_seqdb_retrieve_seq_fasta.py
- BaseUploadTestCase
- EqualsUuidFilter
- TestCommondbDictModelModifier
- calculate_seq_distance.py
- TestBaseEtlResult
- TestConvertIdsStringToList
- test_seqdb_distance_optimization_benchmark.py
- crud_protocol_set.py
- ._serialize_int_enums
- UUID
- Hashable
- .create_parent_for_upload
- .get_obj
- IntEnumWithJsonSchemaMixin
- CaseAbac
- make_assoc
- Any
- test_casedb_crud_common.py
- CaseBatchUploader
- test_seqdb_calculate_seq_distances_performance.py
- sa/util.py
- User
- ImportGraphAnalyzer
- CaseValidator
- BaseService
- case_service_retrieve_is_own_cases
- Concept
- case_service_crud_case_set_data_collection_link
- Concept (omopdb.omop / OMOP CDM entity)
- test_update_user_policy.py
- _make_crud_side_effect
- test_fastapp_repository_performance.py
- DummyCommand
- CacheRegion
- Permission
- Any
- .create_case_for_upload
- test_fastapp_cache_invalidation.py
- SampleQueryResult
- Person
- PersonBatchForUpload
- TestRouterData
- ._get_allele_profile_for_ids
- RBACTestClient
- omopdb/domain/enum.py
- Concept
- LogItem
- BaseOrganizationService
- BaseRepository
- TestFilterConstruction
- .create_crud_cmd
- MemoryVersionStore
- TestModelSampleBatchForUpload
- seq/crud_tree_algorithm_class.py
- commondb/env.py
- TestUpdate
- User
- TestModelBaseSeq
- cache/__init__.py
- Case Type
- BaseCaseAbacPolicy
- test/fastapp/model.py
- OrganizationSARepository
- Data Collection
- .load
- ._validate_state
- omopdb/repositories/organization_sa.py
- ServerManager
- test_fastapp_cache_support.py
- TestParametrizedCRUD
- TestModelSeq
- CaseSet
- CaseType
- DatetimeRangeFilter
- .create_local_or_remote_app
- InMemoryOrganizationRepository
- Role
- test_casedb_upload.py
- env
- DummyCmd
- ._create_sample_seq_for_upload
- OAuth2Client
- Any
- fastapp shared application framework
- Protocol
- Person
- Protocol (seqdb entity)
- OrganizationService
- CommondbDictModelModifier
- EndpointTestClient
- .result_type
- AuthEnv
- RetrieveSeqFastaCommand
- UUID
- FakeResponse
- Gen-EpiX README
- casedb.organization.md
- ._validate_model
- RetrieveSeqDistanceLastModifiedCommand
- TestGetAllEndpoint
- CommondbRemoteApp
- computed_field
- TestDelete
- IdentifierIssuer
- case_service_crud_ref_col
- TestNonCrudHandlers
- CompositeFilter
- TestPostOneEndpoint
- log_parser_v2.py
- TrackingUnitOfWork
- TestClient
- Schema migrations
- TestNumpyAlleleIntegration
- DummyIdpClient
- UUID
- Registry
- test_cfg_log_level.py
- generate_seq_distances.py
- scenario_ids
- model/case/__init__.py
- EvictionStrategy
- TestCreateUserFromToken
- TestInitialization
- RequestorApp
- SeqGenerationSettings
- Development Guide
- Linter
- map_paired_elements
- get_test_client
- TestCommondbModelProcessMetadata
- ReadOrganizationResultsOnlyPolicy
- TestModelSeqProfileForUpload
- Runtime dependencies (requirements.txt)
- _Call
- UpdateUserPolicy
- retrieve_case.py
- convert
- TestSeqDistancePerformance
- UpdateUserPolicy
- 6f2f4fb9b3d1_drop_legacy_code_constraints.py
- CaseUploadSetup
- test_seqdb_calculate_seq_distance.py
- omop/ontology.py
- make_cdb_user
- TestCasedbMetadataMasking
- TimeoutGuard
- test_read_config.py
- TestDataLineageMixin
- .get_client
- Organization (commondb.organization entity)
- seq_service_crud_protocol
- check_docstrings.py
- get_case_abac_from_command
- TestClient
- ThreadRefreshRunner
- TestCaseDataCollectionIdHandling
- `gen_epix.fastapp.cache`
- Organization
- IdentifierIssuer (omopdb.organization entity)
- Organization
- UUID
- UserManager
- setup_reference_data
- MemoryTagIndex
- test_logging_runtime_contract.py
- TestGetOneEndpoint
- Token
- test/conftest.py
- Gen-EpiX Contributor Documentation Index
- Organization
- Sample
- TestPutOneEndpoint
- ._make_user_cmd
- SAUnitOfWork
- _encode_to_int32
- case_service_create_file_for_read_set_or_seq
- TestRead
- _make_user
- UUID
- TestDeleteOneEndpoint
- crud_allele.py
- retrieve_case_type_stats_profiled
- TestCommondbMetadataMasking
- ModelNoId
- TestHttpTimeoutConfiguration
- test_error_code_unicity
- BaseOmopService
- ._filter_users_by_organization
- App (command dispatcher / PEP)
- Organization (omopdb.organization entity)
- crud_ast_prediction.py
- crud_locus_code_map.py
- casedb/domain/command/abac.py
- HandleAuthExceptionMiddleware
- DataIssue
- NullMutex
- seq/crud_tree_algorithm.py
- TestBulkUpdateSeqDistanceContentSA
- FullSample
- JsonFormatter
- crud_sample_data_collection_link.py
- DependencyDeclaration
- ._open
- MockJWKAndToken
- TestRootTokenTTL
- OmopdbRemoteApp
- DuplicateIdsError
- commondb/api/exc.py
- IdpClient hierarchy
- Protocol
- crud_seq_classification.py
- crud_seq_profile_identifier.py
- .default_isolation_level
- ._validate_state
- ._validate_ref1_fields
- ._validate_int_for_uuid
- Transformer Framework
- .get_user
- rewrite_parametrized_dependency_markers
- retrieve_complete_case_type.py
- .data_collection_set_data_collection_update_association
- command/seq.py
- env
- delete_client
- LogParser2
- AppComposer (Composition Root)
- Region Set
- Sample
- SeqTaxonomy
- .__init__
- .__init__
- TestOIDCProviderIntegration
- omop/metadata.py
- renovate.json
- TestUpdate
- TestSQLInjection
- BaseCommondbRemoteAppTestCase
- TestAnonymizeUser
- generate_seqdb_models.py
- TestOIDCProvider
- Concept Relation
- Outage (commondb.system entity)
- Protocol
- 3.8 Comments and Docstrings
- calculate_phylogenetic_tree.py
- crud_ast_measurement.py
- IdsError
- BaseSeqService
- crud_locus.py
- crud_locus_set.py
- crud_pcr_measurement.py
- services/seq/upload.py
- crud_protocol_set_member.py
- crud_ref_seq.py
- .retrieve_cases_by_id
- .get_setting
- seq/service.py
- crud_seq_category.py
- crud_seq_category_set.py
- crud_seq_distance.py
- crud_seq_taxonomy.py
- TestOauthIdpClientIntrospection
- crud_taxon_set.py
- crud_taxon_set_member.py
- ._match
- TestVerifyUserRights
- TestDelete
- ._match
- test_logging_yaml.py
- TestDelete
- ._match
- omopdb/api/router.py
- TestUpdate
- .__init__
- start-sql-stack.sh
- TestSampleChildOrder
- schema_migration/commondb.md
- AuthorizationCodeStore
- seqdb.md
- Contact (doc)
- seqdb Overview ERD
- IdentifierIssuer
- Taxon
- Locus
- casedb/repositories/sa_alembic/__init__.py
- commondb/repositories/sa_alembic/__init__.py
- .retrieve_own_permissions
- EngineFactory
- .__init__
- .__init__
- .print_org_admin_policies
- KeyedMutex
- .print_identifier_issuers
- FeatureDisabledServiceError
- .__init__
- .__init__
- .get_mapped_class
- Entity descriptor
- Specimen
- DataCollection
- Seq
- .__init__
- JIRA Issues
- ServiceUnavailableError
- ._validate_content
- AuthException
- .__init__
- set_service_repository
- Subject
- MeasurementRelation
- ObservationPeriod
- ProcedureOccurrence
- Locus
- ReadSet
- SeqProfile
- EtlLogItem
- UUID
- ._validate_model
- .create_unique_values_temp_table
- ._serialize_seq_format
- IsOrganizationAdminPolicy
- omopdb/policies/read_user_policy.py
- IsOrganizationAdminPolicy
- ReadUserPolicy
- omopdb/repositories/sa_alembic/__init__.py
- OrganizationSARepository
- seqdb/repositories/sa_alembic/__init__.py
- OAuth Client Credential Flow Test
- TestCaseTypeProps
- init-db one-shot database creation service
- DataCollection (commondb.organization entity)
- DataCollectionSetMember
- DataCollectionSetMember
- TreeAlgorithm
- integration/api/__init__.py
- BrokenBackend
- unit/api/__init__.py
- pr.sh
- casedb/services/organization.py
- Issue Templates
- migrations/__init__.py
- Any
- ._validate_content
- seqdb/services/organization.py
- release-please-config.json
- get_test_client
- casedb/domain/service/__init__.py
- field_validator
- test_debug_console_uses_json_formatter
- Encoder
- DummyLogItem
- App.handle() command dispatch
- casedb SUBJECT Simplified ERD
- NoteNlp
- TreeAlgorithm
- SeqClassificationForUpload
- ._validate_state
- .get_errors
- TreeAlgorithm (seqdb entity)
- .organization_identifier_issuer_link_update_association
- test/enum.py
- ._validate_some_criteria
- ._validate_content
- .__init__
- .__init__
- MermaidErmGenerator
- _PytestMockConfig
- Links, Subtasks, and Dependencies
- docker-entrypoint.sh
- Default App Ports (8000/8001/8002/8010)
- CohortDefinition (omopdb.md)
- Organization
- Locus (seqdb entity)
- SeqCategory
- Locus
- crud_read_set.py
- .case_type_set_case_type_update_association
- .create_case_set
- .disease_etiological_agent_update_association
- .__init__
- CasedbRemoteApp
- .retrieve_phylogenetic_tree_by_cases
- .get_headers
- .invite_user
- .organization_set_organization_update_association
- .retrieve_outages
- crud_sample.py
- ._validate_some_criteria
- ._validate_state
- TestGetCaseDateColIds
- test_seqdb_nextclade_get_ref_alignment.py
- post-pr-comments.sh
- Bug Fixes
- Local Dev/Testing Compose Stack (DICT_EMPTY)
- Authentication vs Authorization Separation
- Model / Command / CrudCommand
- Role / Permission
- Fallback Behavior (No IDPs configured)
- OrganizationAccessCasePolicy entity
- OrganizationShareCasePolicy entity
- casedb AUTH Simplified ERD
- CaseUploadResult
- Concept
- Outage (doc)
- erm/__init__.py
- CdmSource
- Cohort
- Outage (omopdb.md)
- CdmSource
- Cohort
- IdentityProvider (doc)
- IDPUser (doc)
- LocusCodeMap
- Outage (seqdb.md)
- TreeAlgorithm
- LocusCodeMap
- SampleQuery
- Outage (seqdb.system.md concept)
- docs/__init__.py
- crud_seq_identifier.py
- RegionRelationType
- .anonymize_user
- .retrieve_feature_flags
- field_validator
- wait_for_mssql.py
- Fields, Issue Types, and Transitions
- SeqdbService
- .get_root_user
- seq_service_calculate_seq_distances_for_new_profiles
- UpdateResponseHeaderMiddleware
- ._validate_int_for_uuid
- BatchEtlResult
- Implement JIRA Issue
- Logger
- ReadSelfResultsOnlyPolicy
- seqdb_server
- ._custom_json_encoder
- ReadSelfResultsOnlyPolicy
- ReadSelfResultsOnlyPolicy
- Commit Skill
- casedb service (DICT_EMPTY, in-process LOCAL seqdb)
- omopdb service (DICT_EMPTY, no auth)
- seqdb service (DICT_EMPTY, no auth)
- Health Check Endpoint (/v1/health)
- OIDC-Only Identity Provider Support constraint
- DomainException hierarchy
- ASGI Middleware Stack (rate limit, auth exc, no-response, header)
- BaseUnitOfWork (abstract)
- Token Validation Path
- Trust Boundaries and Authority Model
- Contract Authority and Scope (casedb openapi.json)
- Multi-Service Startup (api_platform_local_mock_dict_demo, ETL loading)
- Settings Model (Dynaconf staged loading)
- Design Notes (Fire class-as-CLI, lazy imports, APP_URI/ETL_ENV dicts)
- other subcommand group (linters, mypy, ERM diagrams, oauth server)
- test subcommand group (test_all, test_{app}_{scope}_{detail})
- Outcome Interpretation (zapped/survived/timeout/error)
- WSL Setup for Windows (avoids WinError 206)
- CI Quality Gate Flow (format, lint, type-check, tests, coverage)
- Release Publication Flow (release-please, version verify, PyPI publish)
- Add a New Module/Service
- Documented Consistency Issues (license mismatch, version mismatch)
- Open Questions / <TBF elsewhere> (consolidated)
- Logging Architecture Overview (YAML config, JsonFormatter, set_log_level)
- Debug Logging Modes (logging.debug.yaml, <APP>_LOG_LEVEL)
- JSON Formatter Behavior (envelope, redaction, exception truncation)
- Common Failure Modes and Fixes
- Golden Prompt (.github/prompts/base_prompt.md)
- Co-funded by the European Union Logo
- Gen-EpiX Swagger UI Screenshot
- Gen-Epix Full Logo
- Gen-Epix Icon Logo
- OrganizationAdminPolicy entity
- IdentityProvider
- IDPUser
- CaseTools
- UserInvitationConstraints
- UserNameEmail
- casedb RBAC Diagram
- Outage
- PackageMetadata
- IdentityProvider
- IDPUser
- UserInvitationConstraints
- UserNameEmail
- Outage
- PackageMetadata
- Config
- UserInvitationConstraints
- UserNameEmail
- BaseSeq
- LocusCodeMap
- LocusSet
- Outage
- PackageMetadata
- JQL Search
- casedb/config/__init__.py
- casedb/__init__.py
- Creating Issues
- Pytest Run (capture once, inspect many times)
- case_service_crud_case_type_set_member
- test_general_dependency_list.py
- ParentUploadResult
- .__init__
- .is_invalidated
- ._validate
- fastapp/services/__init__.py
- omopdb/config/__init__.py
- gen_epix/omopdb/__init__.py
- seqdb/config/__init__.py
- gen_epix/seqdb/__init__.py
- UUID
- Gen-EpiX
- casedb/services/rbac.py
- .__init__
- ._get_dummy_link_defaults
- ._validate_state
- Examples
- gen-epix-api Version 6.1.0
- .__init__
- InvalidIdsError
- InvalidLinkIdsError
- InvalidModelIdsError
- LinkConstraintViolationError
- UuidSetFilter
- api/seq.py
- ._validate_locus
- ._validate_protocol_type_dependencies
- ._validate_model
- ._validate_state
- CalculateSeqDistancesEtlResult
- Available Tools
- TestContent
- get_test_client
- ._serialize_seq_profile_type
- omopdb/integration/build_db/create.py
- .__init__
- erm/casedb.md
- casedb.case.detailed.md
- casedb.detailed.md
- casedb.geo.md
- casedb.geo.detailed.md
- casedb.ontology.md
- casedb.ontology.detailed.md
- casedb.organization.detailed.md
- casedb.seqdb.detailed.md
- casedb.subject.detailed.md
- casedb.system.md
- casedb.system.detailed.md
- erm/commondb.md
- commondb.abac.md
- commondb.abac.detailed.md
- commondb.auth.md
- commondb.auth.detailed.md
- commondb.detailed.md
- casedb SEQDB Simplified ERD
- .col_set_col_update_association
- .__init__
- .n_loci
- .is_available
- ._validate_model
- test_casedb_remote_app.py
- TestOmopSpecification
- schema_migration/casedb.md
- omopdb.md

## God Nodes (most connected - your core abstractions)
1. `BaseUnitOfWork` - 286 edges
2. `CasedbTestClient` - 258 edges
3. `Model` - 234 edges
4. `CrudOperation` - 231 edges
5. `App` - 202 edges
6. `Entity` - 193 edges
7. `TestClient` - 188 edges
8. `BaseCaseService` - 154 edges
9. `Command` - 149 edges
10. `Base` - 143 edges

## Surprising Connections (you probably didn't know these)
- `PPR Test Docker Compose (Mock OIDC + CASEDB/SEQDB)` --semantically_similar_to--> `SQL + Mock OIDC Docker Compose (SEQDB/OMOPDB/CASEDB)`  [INFERRED] [semantically similar]
  docker-compose.ppr_test.yml → docker-compose.sql.idp.yml
- `Review Skill` --semantically_similar_to--> `CI: Static Analysis and Testing Workflow`  [INFERRED] [semantically similar]
  .agents/skills/review/SKILL.md → .github/workflows/main.yml
- `pytest-run skill` --semantically_similar_to--> `Per-app test commands (test_{app}_{scope})`  [INFERRED] [semantically similar]
  .github/instructions/python-pytest.instructions.md → docs/06-Development-Guide.md
- `casedb-seqdb-omopdb E2E Connection Test Logging Config` --semantically_similar_to--> `casedb Logging Config`  [INFERRED] [semantically similar]
  test/end_to_end/casedb_seqdb_connection/logging.yaml → gen_epix/casedb/config/logging.yaml
- `casedb-seqdb-omopdb E2E Connection Test Logging Config` --semantically_similar_to--> `omopdb Logging Config`  [INFERRED] [semantically similar]
  test/end_to_end/casedb_seqdb_connection/logging.yaml → gen_epix/omopdb/config/logging.yaml

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Gen-EpiX code quality and test toolchain** — dev_requirements_pytest, dev_requirements_isort, dev_requirements_black, dev_requirements_pylint, dev_requirements_mypy, dev_requirements_coverage [EXTRACTED 0.90]
- **Command-centric authorization flow** — agents_transport_adapter_pattern, agents_app_handle, agents_command_centric_authorization, agents_policy_phases [EXTRACTED 0.90]
- **App domains composed on the fastapp framework** — agents_fastapp_framework, agents_commondb, agents_casedb, agents_seqdb, agents_omopdb, agents_filter_transform [EXTRACTED 0.90]
- **Authentication Pipeline (AuthService -> IdpClient -> UserManager)** — docs_02a_fastapp_framework_authservice, docs_02a_fastapp_framework_idpclient, docs_02a_fastapp_framework_usermanager, docs_02a_fastapp_framework_oauthidpclient [EXTRACTED 1.00]
- **Boot & Composition Sequence (AppCfg -> AppComposer -> create_fast_api)** — docs_08a_app_composition_walkthrough_appcfg, docs_08a_app_composition_walkthrough_appcomposer, docs_08a_app_composition_walkthrough_createfastapi, docs_02_architecture_boot_sequence [EXTRACTED 1.00]
- **OMOP CDM Concept/Vocabulary/Domain/ConceptClass standard-vocabulary triangle** — docs_erm_omopdb_omop_detailed_concept, docs_erm_omopdb_omop_detailed_vocabulary, docs_erm_omopdb_omop_detailed_domain, docs_erm_omopdb_omop_detailed_conceptclass [EXTRACTED 1.00]
- **Policy Enforcement Pipeline (BEFORE/DURING/AFTER via PDP and RbacPolicy)** — docs_02_architecture_policy_enforcement_timing, docs_02a_fastapp_framework_pdp, docs_02a_fastapp_framework_app, docs_02a_fastapp_framework_rbacpolicy [EXTRACTED 1.00]
- **seqdb Service ERDs Forming Overview Schema** — docs_erm_seqdb_organization_detailed_doc, docs_erm_seqdb_seq_detailed_doc, docs_erm_seqdb_system_detailed_doc, docs_erm_seqdb_file_doc, docs_erm_seqdb_doc [EXTRACTED 1.00]
- **seqdb Sample x Protocol sequencing/measurement pipeline** — docs_erm_seqdb_detailed_sample, docs_erm_seqdb_detailed_protocol, docs_erm_seqdb_detailed_seq, docs_erm_seqdb_detailed_readset [EXTRACTED 1.00]
- **External Identifier Crosswalk Pattern (IdentifierIssuer + *Identifier bridge tables)** — docs_erm_commondb_organization_detailed_identifierissuer, docs_erm_omopdb_omop_detailed_personidentifier, docs_erm_seqdb_detailed_sampleidentifier [INFERRED 0.85]
- **Shared Debug File+Console Logging Pattern (casedb/commondb/omopdb/seqdb)** — gen_epix_casedb_config_logging_debug_logging, gen_epix_commondb_config_logging_debug_logging, gen_epix_omopdb_config_logging_debug_logging, gen_epix_seqdb_config_logging_debug_logging [INFERRED 0.95]
- **Shared Non-Debug JSON Logging Pattern (casedb/commondb/omopdb/seqdb)** — gen_epix_casedb_config_logging_logging, gen_epix_commondb_config_logging_logging, gen_epix_omopdb_config_logging_logging, gen_epix_seqdb_config_logging_logging [INFERRED 0.95]

## Communities (673 total, 180 thin omitted)

### Community 0 - "BaseAppComposer"
Cohesion: 0.09
Nodes (15): BaseAppComposer, Any, App, Dynaconf, Enum, Encapsulates dependencies and repository construction for concrete app…, Initialize abstract composition state placeholders. Raises:…, Return the application's resolved Dynaconf settings. (+7 more)

### Community 1 - "CacheBackend"
Cohesion: 0.03
Nodes (35): CacheBackend, ProxyBackend, ABC, Return a store-provided mutex for regenerating `key`. Returns: A mutex when the…, Return the counters observed by this store., Release the resources held by the store., Encapsulates altering the behavior of another backend without subclassing it.…, Initialize a ProxyBackend instance. (+27 more)

### Community 2 - "CrudOperation"
Cohesion: 0.02
Nodes (210): post-pr-comments.sh Script, Review Skill, ETL (Extract, Transform, Load) script for Gen-EpiX genomic epidemiology…, Compose and expose the configured casedb FastAPI application. This module forms…, # TODO: app variable added for backwards compatibility with startup code that…, Define casedb service, authorization, case, and schema enumerations. These…, Expose and organize casedb and shared domain models for registration. ABAC…, Define the Casedb ABAC service contract and command classifications. (+202 more)

### Community 3 - "ParentForUpload"
Cohesion: 0.05
Nodes (36): Get the batch for upload from the command., Get the number of parents in the batch for upload., BaseBatchForUpload, ParentForUpload, Any, field_serializer, field_validator, Model (+28 more)

### Community 4 - ".filter"
Cohesion: 0.18
Nodes (7): Any, Command, Return whether the command is allowed by this policy., Return policy content associated with a command., Return the type of content produced by this policy., Filter a command result according to this policy., Determine if a stored value for this field is mutable.

### Community 5 - "DomainException"
Cohesion: 0.04
Nodes (37): Any, BaseModel, Enum, field_validator, Hashable, Key, model_validator, Self (+29 more)

### Community 6 - "test_omopdb_upload.py"
Cohesion: 0.04
Nodes (90): IdentifierForUpload, BaseModel, Represents an external identifier used in an upload operation. It is defined as…, Compare issuer references and external ID with another upload identifier., Return a hash of the issuer references and external identifier., ModelFieldProps, BaseModel, Represents additional properties of a model field. The application of these… (+82 more)

### Community 7 - "gen_epix/fastapp/model.py"
Cohesion: 0.02
Nodes (137): Provide an HTTP command client for remote commondb applications. The client…, Application command dispatch, policy enforcement, and event handling. The…, Domain registry for models, commands, services, and permissions., Domain metadata types and factory helpers., Key, BaseModel, Key definitions for domain model instances., Encapsulates generating a stable key from one or more model fields. (+129 more)

### Community 8 - "AppCfg"
Cohesion: 0.04
Nodes (41): AppCfg, BaseAppCfg, _is_descendant_logger(), Dynaconf, Enum, Path, Refactored configuration management using Strategy Pattern., Loaded Dynaconf settings object. (+33 more)

### Community 9 - "Client"
Cohesion: 0.04
Nodes (41): HTTPBasicCredentials, Client, List all active clients., Create a new client with auto-generated credentials., OAuth 2.0 Client representation., Hash the client secret for security., Hash a client secret using SHA-256., Verify a client secret against the stored hash. (+33 more)

### Community 10 - "Enum"
Cohesion: 0.04
Nodes (50): field_serializer, Serialize dim-type keys and col-type sets to plain string dicts., CaseClassification, CaseTypeSetCategoryPurpose, ColConceptSetType, ColRelation, ColType, ColTypeOrder (+42 more)

### Community 11 - "SeqdbEndpointTestClient"
Cohesion: 0.08
Nodes (20): field_validator, UUID, Represents a request to retrieve complete data for sample identifiers. The…, Require every requested sample identifier to occur at most once., Represents a request to retrieve only SampleIdentifier records for sample…, Require every requested sample identifier to occur at most once., Require every requested sequence identifier to occur at most once., RetrieveSampleIdentifiersByIdCommand (+12 more)

### Community 12 - "commondb/api/organization.py"
Cohesion: 0.02
Nodes (165): create_abac_endpoints(), Any, APIRouter, App, Exception, FastAPI, NoReturn, Register casedb ABAC endpoints through the shared commondb API adapter. (+157 more)

### Community 13 - "api/case.py"
Cohesion: 0.05
Nodes (52): CaseTypeSetCaseTypeUpdateAssociationRequestBody, ColSetColUpdateAssociationRequestBody, create_case_endpoints(), CreateCaseSetRequestBody, CreateFileForReadSetRequestBody, CreateFileForSeqRequestBody, Any, APIRouter (+44 more)

### Community 14 - "omopdb/domain/model/__init__.py"
Cohesion: 0.04
Nodes (141): BaseIdentifier, Represents an identifier generated outside the system for an entity. It records…, IdentifiersMixin, Encapsulates a mixin that adds identifiers fields and validation. Assumes that…, Model, OmopDB base model with optional UUID identity metadata., Represents the shared model contract with an optional OmopDB object ID., Expose shared and OMOP model types plus their domain registration metadata. The… (+133 more)

### Community 15 - "JWKSManager"
Cohesion: 0.03
Nodes (55): JWKSManager, Any, Get the current key ID., Generate a new key pair and return the new key ID., Create an OpenID Connect ID Token., Validate only the signature of a JWT token without checking claims., Decode JWT header without verification., Decode JWT payload without verification (use carefully!). (+47 more)

### Community 16 - "MockRequest"
Cohesion: 0.03
Nodes (57): MockRequest, Any, Test OAuth2Validator initialization., Test client authentication requirement for client credentials flow., Test client authentication requirement for other grant types., Test client authentication with valid credentials., Test client authentication with invalid client ID., Test client authentication with invalid secret. (+49 more)

### Community 17 - "CaseService"
Cohesion: 0.03
Nodes (62): Expose the concrete service that handles casedb case-domain commands.…, CaseService, CaseIdentifier, CaseSet, CaseSetCategory, CaseSetMember, CaseSetStatus, CaseType (+54 more)

### Community 18 - "crud_dim.py"
Cohesion: 0.04
Nodes (61): DimCrudCommand, Represents a request to execute a CRUD operation on Dims., case_service_crud_dim(), _crud_create_dim(), _crud_dim_with_abac(), _crud_dim_without_abac(), _crud_update_dim(), _get_existing_dim() (+53 more)

### Community 19 - "BaseCrudTestCase"
Cohesion: 0.06
Nodes (39): CaseSetCrudCommand, Represents a request to execute a CRUD operation on CaseSets., case_service_crud_case_set(), _crud_case_set_with_abac(), _crud_case_set_without_abac(), CaseSet, UUID, Handle CRUD operations for case-set entities. (+31 more)

### Community 20 - "BaseCaseService"
Cohesion: 0.03
Nodes (145): DomainBaseCaseService, Re-export FastApp API and domain exceptions used by casedb contracts. Consumers…, BaseCaseService, Define the shared interface and helpers required by case service handlers. The…, Encapsulates the interface contract shared by case service handlers. This…, case_service_create_case_set(), CaseSet, Create case sets together with their collection and case associations. The… (+137 more)

### Community 21 - "seqdb/domain/model/__init__.py"
Cohesion: 0.01
Nodes (270): CrudCommand, Define casedb commands for geographic regions and region sets., Represent CRUD operations for geographic region sets., Represent CRUD operations for geographic regions., Represent CRUD operations for relationships between regions., Represent CRUD operations for shapes associated with region sets., RegionCrudCommand, RegionRelationCrudCommand (+262 more)

### Community 22 - "App"
Cohesion: 0.03
Nodes (71): Any, Initialize role maps and configured root and guest role values. Args: app:…, Register ABAC policies at their required command lifecycle phases.…, Clear cached user lookups after a command changes ABAC-related state. Args:…, Implement commondb role-based access-control services and policy registration., App, Any, datetime (+63 more)

### Community 23 - "SeqService"
Cohesion: 0.04
Nodes (57): ConvertSeqFormatCommand, Command, Represents a request to convert stored contig sequence representations.…, Represents a request to retrieve profiles similar to at least one query…, Represents a request to retrieve the best Seq ID for each requested sample.…, Represents a request to retrieve the best SeqProfile ID for each requested…, Represents a request to retrieve the best SeqClassification ID for each…, RetrieveBestSeqClassificationPerSampleCommand (+49 more)

### Community 24 - "._get_week_start"
Cohesion: 0.13
Nodes (10): date, Convert from WEEK to YEAR using exact mode., Convert from WEEK to YEAR using round mode., Convert from WEEK to QUARTER using exact mode., Convert from WEEK to QUARTER using round mode., Convert from WEEK to MONTH using exact mode., Convert from WEEK to MONTH using round mode., Calculate the start date of a given ISO week. (+2 more)

### Community 25 - "commondb/repositories/__init__.py"
Cohesion: 0.05
Nodes (45): BaseAbacRepository, Define the repository interface for commondb ABAC persistence., Encapsulates the persistence boundary for organization-administration policies., Re-export commondb repository interfaces. ABAC, organization, and system…, BaseSystemRepository, Define the repository interface for commondb system data., Encapsulates the persistence boundary for system outages and metadata., AbacDictRepository (+37 more)

### Community 26 - "JsonFormatter"
Cohesion: 0.05
Nodes (89): Formatter, _build_sensitive_re(), JsonFormatter, _normalise_sensitive_keys(), Any, LogRecord, Central JSON logging formatter for all GenEpix container applications. Ensures…, Format a Unix timestamp as a millisecond-precision UTC ISO 8601 value. Args:… (+81 more)

### Community 27 - "validate_int_for_uuid_field"
Cohesion: 0.07
Nodes (29): Validate that the input value is either a UUID or an integer that can be…, validate_int_for_uuid_field(), Any, field_validator, UUID, Normalize measurement concept identifiers to UUID form., Truncate too long values with an ellipsis, as the database field is limited to…, Normalize observation concept identifiers to UUID form. (+21 more)

### Community 28 - "EtlStatus"
Cohesion: 0.02
Nodes (155): Upload a batch of sequence samples. Implementations may persist samples and…, Model, Upsert cases and then their linked read sets and sequences. The method mutates…, Build a seqdb upload command and child-to-case index mappings. The batch ID is…, Upload samples to seqdb under the configured functional user. The command's…, Encapsulates batch-upload options and payload access for upload commands., UploadBatchCommandMixin, Encapsulates the action selected for one record during an upload. (+147 more)

### Community 29 - "TupleMapTransformer"
Cohesion: 0.03
Nodes (50): Any, Hashable, Replace the lookup map used by subsequent row transformations. Only active rows…, Encapsulates mapping source-field tuples to target-field tuples. The mapping is…, Update the row source and target fields. This allows row field names to change…, Transform an adapted object using the configured tuple mapping. Target fields…, Transform a dictionary row in place and return the same dictionary. This is the…, Return the configured source-field values for a row without transforming it.… (+42 more)

### Community 30 - "SeqdbRemoteApp"
Cohesion: 0.04
Nodes (52): CalculatePhylogeneticTreeCommand, model_validator, Self, Represents a request to calculate a phylogenetic tree from query profiles and a…, Require custom leaf names to align with the queried profile identifiers., Require a supported, same-family DNA representation conversion., PhylogeneticTree, Calculate a phylogenetic tree. Args: cmd: Tree-calculation command to execute.… (+44 more)

### Community 31 - "Model"
Cohesion: 0.02
Nodes (218): Normalize an integer enum value to a sequence-distance type., Define persisted attribute-based access-control models for commondb. The…, Model, IntEnum, Provide commondb base models and helpers for ETL result reporting. The models…, Normalize an optional value to a member of an integer enumeration. This…, Represents an optional persistent identifier to commondb audit-aware models., Normalize a value to a member of an integer enumeration. This function is… (+210 more)

### Community 32 - "TransformResult"
Cohesion: 0.04
Nodes (52): FallbackTransformer, Pipeline, Any, TransformResult, Synchronous transformer pipeline with ordered execution and error recovery., Run the wrapped transformer until it succeeds or retries are exhausted. Retries…, Encapsulates fallback transformation after a primary exception., Store the primary transformer and fallback transformer. (+44 more)

### Community 33 - "test_casedb_case_validator.py"
Cohesion: 0.04
Nodes (56): CompleteCaseType, model_validator, Self, Define the complete, user-specific view of a case type. The module combines…, Represents a case type with its related entities and effective ABAC data. The…, Validate references and replace all derived ordering fields in place., Col, Dim (+48 more)

### Community 34 - "BaseCaseService"
Cohesion: 0.03
Nodes (59): BaseCaseService, Case, CaseDataCollectionLink, CaseIdentifier, CaseSet, CaseSetCategory, CaseSetDataCollectionLink, CaseSetMember (+51 more)

### Community 35 - "test_user_manager_auto_create.py"
Cohesion: 0.08
Nodes (43): claims_basic(), make_user_manager(), mock_organization_service(), mock_rbac_service(), other_org(), other_org_id(), Any, fixture (+35 more)

### Community 37 - "Filter"
Cohesion: 0.05
Nodes (67): _default_validate_query_filter(), Allow query filters with at most one level of composite filters., Return (where_filter, None) — the full filter applies in-memory., Filter, Base abstractions for scalar, column, and row filters., Represents a filter. This is a base class from which all actual filter…, Return whether this filter combines multiple child filters., Logical composition of scalar and row filter expressions. (+59 more)

### Community 38 - "test_fastapp_cache_key.py"
Cohesion: 0.05
Nodes (57): arg_key_generator(), bind_arguments(), function_namespace(), _has_receiver(), KeyGeneratorFactory, KeySpec, kwarg_key_generator(), Any (+49 more)

### Community 39 - "TokenIntrospectionManager"
Cohesion: 0.04
Nodes (42): Any, Logger, SSLContext, Return cached introspection endpoint., Prune expired introspection cache., Encapsulates managing token introspection and discovery-endpoint caching., Return whether cached introspection token inactive., Return whether recheck introspection. (+34 more)

### Community 40 - "Any"
Cohesion: 0.05
Nodes (35): AsyncCachedFunction, BoundCachedFunction, CachedFunction, make_cached_function(), Any, Return the logical cache key for one argument combination. A writer that wants…, Return the tags attached to the entry for one argument combination. Args:…, Return the cached result without computing it. Args: *args: Positional… (+27 more)

### Community 41 - "BaseUnitOfWork"
Cohesion: 0.04
Nodes (44): Case, CaseSet, CaseSetMember, Col, CrudCommand, Model, RefCol, User (+36 more)

### Community 42 - "TestToken"
Cohesion: 0.06
Nodes (19): Any, patch, Test scopes property with multiple scopes., Test scopes property with single scope., Test scopes property with empty scope., Test scopes property handles extra whitespace., Test has_scope returns True for existing scopes., Test has_scope returns False for missing scopes. (+11 more)

### Community 43 - "_uuid_field_name"
Cohesion: 0.04
Nodes (71): Any, UUID, Shared OMOP model mixins and primary-key normalization helpers., Validate that the input value is either a UUID or a string that can be…, Validate and synchronize string-based primary key arguments. Mutates ``data``…, Validate and synchronize integer-based primary key arguments. Mutates ``data``…, validate_int_key_args(), validate_str_for_uuid_field() (+63 more)

### Community 44 - "ObjectAdapter"
Cohesion: 0.02
Nodes (128): Decimal, Validate and normalize uploaded case content against case-type metadata. The…, # TODO: transform any other col_types, # TODO: replace by pre-calculated interval_relation_map for efficiency, ObjectAdapter, Adapters that expose a common field interface for row-like objects. The…, Encapsulates adapter selection for supported object representations. Supported…, IntervalTransformStrategy (+120 more)

### Community 46 - "CrudEndpointSet"
Cohesion: 0.03
Nodes (105): CrudEndpointGenerator, Any, APIRouter, FastAPI, Hashable, Model, Create the CRUD endpoint configuration for one persistable entity. Determines…, Map CRUD permissions to the operations needed by generated endpoints. Args:… (+97 more)

### Community 47 - "create_custom_openapi_function"
Cohesion: 0.05
Nodes (32): create_custom_openapi_function(), fix_schema_nullable_and_single_element(), Any, OpenAPI schema generation and compatibility fixes., # TODO: add a function to fix read-only fields, Create a cached OpenAPI schema factory with optional schema fixes., # TODO: add a fix for read-only fields, Fixes the schema by handling 'anyOf' constructs and setting the 'nullable'… (+24 more)

### Community 48 - "CasedbTestClient"
Cohesion: 0.07
Nodes (5): CasedbTestClient, scenario_ids, skipif, TestCreate, TestCaseUploadContentDeletion

### Community 49 - "test_seqdb_convert_seq_format.py"
Cohesion: 0.07
Nodes (43): Encapsulates supported serialized representations of sequence content., SeqFormat, encode_ascii_as_gzip_base64(), Encode a string as a gzip-compressed base64 string., UUID, Implement stored sequence representation conversion., Convert all contigs in the requested sequences to a new representation., seq_service_convert_seq_format() (+35 more)

### Community 50 - "BaseFilterTestCase"
Cohesion: 0.04
Nodes (26): AlwaysTrueFilter, BaseFilterTestCase, EqualsFilter, Any, BaseModel, scenario_ids, Concrete filter for testing equality matching., Test scenarios related to column matching and filtering. (+18 more)

### Community 51 - ".__init__"
Cohesion: 0.15
Nodes (13): Any, Initialize a ServiceException instance., Return http other props., Initialize http props., Initialize a FeatureDisabledServiceError instance., Initialize a CredentialsAuthError instance., Initialize a UnauthorizedAuthError instance., Initialize a UserNotFoundAuthError instance. (+5 more)

### Community 52 - "SeqProfile"
Cohesion: 0.06
Nodes (32): Any, field_validator, model_validator, ndarray, Self, UUID, Normalize the profile type from its accepted enum representation., Validate that the content format matches the sequence profile type. (+24 more)

### Community 53 - "Base"
Cohesion: 0.01
Nodes (397): DeclarativeBase, declared_attr, OrganizationAccessCasePolicy, OrganizationShareCasePolicy, RowMetadataMixin, Define SQLAlchemy persistence mappings for casedb ABAC policy models., Persist the casedb OrganizationShareCasePolicy domain model., Persist the casedb UserShareCasePolicy domain model. (+389 more)

### Community 54 - "profile_method"
Cohesion: 0.36
Nodes (8): profile_method(), Path, Profile a callable and write its report to a timestamped log file. The returned…, test_async_returns_value(), test_async_writes_log_file(), test_sync_propagates_exception(), test_sync_returns_value(), test_sync_writes_log_file()

### Community 55 - "SARepository"
Cohesion: 0.04
Nodes (89): CaptureFixture, IsolationLevel, Encapsulates specifying the transaction isolation level for a database session., Any, BaseException, Hashable, Session, Return True if the row for the given id exists. (+81 more)

### Community 56 - "Model"
Cohesion: 0.01
Nodes (176): _annotation_to_mermaid_type(), _build_diagram(), _field_marker(), BaseModel, Mermaid-based ERM diagram generator. Produces Mermaid ``erDiagram`` markdown…, Return Mermaid column marker (PK / FK) or empty string., Return the Mermaid lines for a single entity block **with** attributes. Example…, Generate Mermaid relationship lines for a set of model classes. Each Link in an… (+168 more)

### Community 57 - "omopdb/domain/command/__init__.py"
Cohesion: 0.03
Nodes (113): Expose shared and OMOP command types plus command-registration metadata.…, CareSiteCrudCommand, CdmSourceCrudCommand, CohortCrudCommand, CohortDefinitionCrudCommand, ConceptAncestorCrudCommand, ConceptClassCrudCommand, ConceptCrudCommand (+105 more)

### Community 58 - "_get_best_id_per_sample"
Cohesion: 0.12
Nodes (24): _get_best_id_per_sample(), Retrieve the best result identifier for each requested sample. Retrieves the…, _classification_cmd(), _make_user(), _mock_service(), _mock_uow(), _profile_cmd(), Any (+16 more)

### Community 59 - "TestTokenStore"
Cohesion: 0.03
Nodes (36): Test cases for the TokenStore class., Test TokenStore initialization., Test storing a basic token., Test storing a token with refresh token creates mapping., Test storing a token without refresh token., Test storing multiple tokens., Test retrieving an existing valid token., Test retrieving a non-existent token returns None. (+28 more)

### Community 60 - "test_fastapp_rbac_service.py"
Cohesion: 0.17
Nodes (24): Model1_1CrudCommand, Model1_2CrudCommand, Model2_1CrudCommand, Model2_2CrudCommand, Enum, ServiceType, TestType, env() (+16 more)

### Community 61 - "Domain"
Cohesion: 0.03
Nodes (59): Domain the requested value., Domain, Hashable, RAISE, Initialize a Domain instance., Name the requested value., Description the requested value., Entities the requested value. (+51 more)

### Community 62 - "._validate_state"
Cohesion: 0.18
Nodes (8): datetime, model_validator, Self, Parse an ISO-formatted datetime string., Return the inclusive lower and exclusive upper datetime bounds., Derive bound intervals and build the partial-date matching function., Any, Match a value using the function generated during validation. Args: value: The…

### Community 63 - "DictRepository"
Cohesion: 0.04
Nodes (103): Get the ID of the model instance. If the ID is not set and raise_on_missing is…, In-memory dictionary-backed repository exports., DictRepository, Any, Hashable, Load a DictRepository from a zip archive containing per-entity JSON files., Apply the configured behavior to stores for unregistered models., Db the requested value. (+95 more)

### Community 64 - "gen_epix/fastapp/enum.py"
Cohesion: 0.01
Nodes (211): Retrieve the list of configured identity providers., Initialize remote commondb routes with connection and authentication settings.…, AuthProtocol, FileExtension, LogLevelSet, OAuthFlow, Enum, Enumerations shared by the application framework. (+203 more)

### Community 65 - "test_alembic_migrations.py"
Cohesion: 0.05
Nodes (37): _configure_url(), Alembic environment for casedb., run_migrations_offline(), run_migrations_online(), _get_target_metadata(), MetaData, SQLAlchemy metadata managed by casedb migrations, including common models., _configure_url() (+29 more)

### Community 66 - "RequestScope"
Cohesion: 0.06
Nodes (25): ContextVarScopeProvider, NullScopeProvider, ABC, Any, Request scope and principal partitioning. Two distinct concerns share this…, Bind identity parts for the duration of the block. Nested binds merge into the…, Encapsulates memoizing values for the duration of one request. The scope sits…, Open a fresh scope for the duration of the block. Yields: The mapping backing… (+17 more)

### Community 67 - "omopdb/repositories/__init__.py"
Cohesion: 0.03
Nodes (63): CommonBaseAbacRepository, SQLAlchemy transaction and unit-of-work implementation., BaseAbacRepository, OmopDB specialization of the shared attribute-based access repository., Encapsulates the commondb ABAC repository contract for OmopDB composition., Expose OmopDB repository contracts for shared and OMOP persistence.…, BaseOmopRepository, datetime (+55 more)

### Community 68 - "casedb/repositories/__init__.py"
Cohesion: 0.05
Nodes (43): BaseGeoRepository, Define the repository contract for Casedb geographic reference data., Provide the shared repository base for geographic persistence., Expose backend-independent repository contracts used by casedb services. Casedb…, BaseOntologyRepository, Define the repository contract for Casedb ontology reference data., Provide the shared repository base for ontology persistence., AbacDictRepository (+35 more)

### Community 69 - "LogicalOperator"
Cohesion: 0.07
Nodes (38): CaseQueryResult, Represents the case identifiers returned for an executed query., Retrieve access-filtered cases matching query criteria. Args: cmd: Case query…, case_service_retrieve_cases_by_id(), case_service_retrieve_cases_by_query(), Case, Retrieve access-filtered cases by ID subject to case-type result limits.…, Retrieve case IDs for a query after ABAC, set, and content filtering. The… (+30 more)

### Community 70 - "Any"
Cohesion: 0.12
Nodes (18): Any, BaseModel, Hashable, Self, Yield column values that match the filter., Check if a row matches the filter. Args: row (dict[Hashable, Any | None]): The…, Check if each row in a collection of rows matches the filter. Args: rows…, Yield rows that match the filter. (+10 more)

### Community 71 - "token_endpoint"
Cohesion: 0.06
Nodes (37): Request, Response, Return HTTP 204 when a disconnected request has no response., get, JSONResponse, post, RedirectResponse, authenticate_client() (+29 more)

### Community 72 - ".create_command_and_result_for_samples"
Cohesion: 0.03
Nodes (97): Represents a sequence classification intended for upload. Equal to a…, SeqClassificationForUpload, BaseUploadTestCase, create_allele_profile_base64(), Any, ReadSetForUpload, scenario_ids, SeqForUpload (+89 more)

### Community 73 - "UploadPersonsCommand"
Cohesion: 0.09
Nodes (23): Represents a request to upload of a batch of persons along with their…, UploadPersonsCommand, PersonBatchUploadResult, Represents the result of uploading a batch of persons., Upload a batch of persons. Args: cmd: Command containing people and upload…, PersonValidator, UUID, Person-upload validation and transformation extension points. (+15 more)

### Community 74 - ".create_client"
Cohesion: 0.05
Nodes (35): client(), Create a TestClient for the FastAPI app., assert_logged_with_code(), create_client(), DummyRequest, make_request(), parametrize, scenario_ids (+27 more)

### Community 75 - "AbacService"
Cohesion: 0.05
Nodes (41): CaseAbacPolicy, Command, Model, Resolve case-specific ABAC content for casedb commands., Resolve the case access model for a command. Args: cmd: Command for which case…, Apply command-scoped casedb case access resolution., AbacService, Encapsulates casedb ABAC policy registration and effective-rights lookup. Case… (+33 more)

### Community 76 - "ErmGenerator"
Cohesion: 0.09
Nodes (19): ErmGenerator, GraphvizErmGenerator, Domain, Path, Graphviz / erdantic-based ERM diagram generator. Produces PNG Entity-…, Generates Entity-Relationship Model diagrams as PNG files via ``erdantic`` /…, Generate ERM diagrams (PNG) for every domain and its services. Also writes an…, generate_hash_for_domain_models() (+11 more)

### Community 77 - "command/case.py"
Cohesion: 0.02
Nodes (117): CaseIdentifierCrudCommand, CaseSetCategoryCrudCommand, CaseSetMemberCrudCommand, CaseSetStatusCrudCommand, CaseTypeCrudCommand, CaseTypeSetCaseTypeUpdateAssociationCommand, CaseTypeSetCategoryCrudCommand, CaseTypeSetCrudCommand (+109 more)

### Community 78 - "Unit"
Cohesion: 0.08
Nodes (21): ConceptRelationType, ConceptSetType, Classify the language or value scale represented by a concept set., Identify supported semantic relationships between concepts., Identify units supported by casedb column and concept metadata., Unit, Serialize a unit as a string while preserving null., ConceptRelation (+13 more)

### Community 79 - "seqdb/services/rbac.py"
Cohesion: 0.29
Nodes (5): CommonRbacService, Implement seqdb application service behavior for services.rbac., Initialize RBAC operations using the seqdb role enumeration. Args: app:…, Encapsulates seqdb RBAC service behavior., RbacService

### Community 80 - "crud_endpoint_generator.py"
Cohesion: 0.07
Nodes (21): ApiPermission, BaseModel, Define casedb API representations for organization permissions., Represents a permission type granted for a casedb command., Command, Return permissions indexed by commondb or mapped domain role values. The…, Generate FastAPI routes that dispatch domain CRUD commands. The module…, Return the endpoint basename derived from entity naming metadata. Args: entity:… (+13 more)

### Community 81 - "test_fastapp_api.py"
Cohesion: 0.02
Nodes (101): BadRequest400HTTPException, Forbidden403HTTPException, ForeignKeyConstraint409HTTPException, InternalServerError500HTTPException, MethodNotAllowed405HTTPException, NotImplemented501HTTPException, HTTP exceptions returned by generated API routes., Construct an HTTP 409 exception with optional headers. (+93 more)

### Community 82 - "SeqProfileForUpload"
Cohesion: 0.11
Nodes (15): Return ordered MLVA repeat numbers in their JSON profile representation., model_validator, Self, Represents a sequence profile record intended for upload. Equal to a…, Format representation names for a validation error message., Require exactly one named profile representation. Args: representations:…, Require a locus code map for a map-based profile representation. Args:…, Require non-empty content for a locus profile upload. Returns: The validated… (+7 more)

### Community 83 - "define_edge_cases_reference.py"
Cohesion: 0.12
Nodes (19): _compute_expected_case_type_sets(), _compute_expected_case_types(), _compute_expected_cases(), _compute_expected_col_sets(), _compute_expected_cols(), _compute_expected_ref_cols(), _compute_expected_ref_dims(), _get_case_type_from_col() (+11 more)

### Community 84 - ".__init__"
Cohesion: 0.11
Nodes (18): IntervalDict, Hashable, NoReturn, RAISE, TypedDict, Map a single numeric value according to the configured intervals. Args: value:…, Encapsulates normalized interval bounds and endpoint metadata., Return the interval name selected for `value` under no-match policy. (+10 more)

### Community 85 - "SeqdbTestClient"
Cohesion: 0.07
Nodes (7): scenario_ids, skipif, TestCreate, Any, Path, Generate a random upload batch with Nextclade SNP profiles and seqs., SeqdbTestClient

### Community 86 - ".is_allowed"
Cohesion: 0.29
Nodes (6): cached, Command, User, Determine whether a command may proceed under the current outage state. Outage…, Determine whether a user has permission to administer an outage. Args:…, Determine whether no active outage currently restricts requests. Returns: True…

### Community 87 - ".rev_role_map"
Cohesion: 0.11
Nodes (14): Any, computed_field, Enum, field_validator, Role, User, Return the new-user dependency. Returns: Dependency that resolves a newly…, Return the identity-provider user dependency. Returns: Dependency that resolves… (+6 more)

### Community 88 - "TestClientStore"
Cohesion: 0.04
Nodes (29): Any, patch, Test cases for the ClientStore class., Set up test fixtures before each test method., Test ClientStore initialization., Test storing a client., Test storing multiple clients., Test that storing a client with same ID overwrites the previous one. (+21 more)

### Community 89 - "test_seqdb_retrieve_seq_fasta.py"
Cohesion: 0.13
Nodes (18): create_seq(), expected_fasta(), FakeMapper, FakeSession, Any, Seq, UUID, Test FASTA retrieval for all supported DNA storage representations. (+10 more)

### Community 90 - "BaseUploadTestCase"
Cohesion: 0.15
Nodes (10): BaseUploadTestCase, ReadSetForUpload, SeqForUpload, Tests for the has_case guard added to _get_upload_samples_command., Tests for CaseBatchForUpload.has_samples (the pure predicate on the batch…, Tests for the casedb-to-seqdb upload bridge in CaseBatchUploader., Base test case with common fixtures and utility methods., TestCaseBatchHasSamples (+2 more)

### Community 91 - "EqualsUuidFilter"
Cohesion: 0.05
Nodes (56): cached, User, Move a user to an organization and replace their case policies. Behaviour: -…, Compute effective case rights for a persisted user. Application administrators…, Compute reference-data access from roles and organization policies. Reference-…, case_service_calculate_case_date(), case_service_get_case_date_col_mappers(), case_service_get_case_date_col_mappers_from_cols() (+48 more)

### Community 92 - "TestCommondbDictModelModifier"
Cohesion: 0.17
Nodes (6): _fixed_factory(), _make_obj(), datetime, scenario_ids, Unit tests for CommondbDictModelModifier. Verifies that: - on_create stamps…, TestCommondbDictModelModifier

### Community 93 - "calculate_seq_distance.py"
Cohesion: 0.06
Nodes (56): ConcurrentModificationError, InvalidArgumentsError, Error for command arguments that fail validation., HTTP 409 error for a conflicting concurrent modification., Encapsulates the biological representation used by a sequence profile., SeqProfileType, Return the sequence-profile type used by this distance protocol. Returns: The…, _calculate_and_store_distances() (+48 more)

### Community 95 - "TestConvertIdsStringToList"
Cohesion: 0.15
Nodes (10): Parse comma-separated or JSON-encoded identifiers for a route parameter. Args:…, Tests for ID parsing from comma-separated or JSON strings., Verify parsing of comma-separated IDs., Verify parsing of JSON-encoded IDs., Verify handling of invalid IDs in comma-separated format., Verify handling of JSON with some invalid IDs., Verify parsing of UUID comma-separated format., Verify handling of empty ID string. (+2 more)

### Community 96 - "test_seqdb_distance_optimization_benchmark.py"
Cohesion: 0.08
Nodes (48): _extract_protocol_info(), _extract_segments(), _filter(), _fmt_s(), generate_benchmark_charts(), get_test_client(), _grouped_bars(), _init_profile_generator() (+40 more)

### Community 97 - "crud_protocol_set.py"
Cohesion: 0.15
Nodes (13): ProtocolSetCrudCommand, Represents a request to perform a CRUD operation on ProtocolSets., ProtocolSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_protocol_set., Handle CRUD operations for protocol-set entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 98 - "._serialize_int_enums"
Cohesion: 0.29
Nodes (5): field_serializer, IntEnum, UUID, Serializes the IntEnums to their int value., Serializes UUID fields as strings. If the value is None, it returns None.

### Community 99 - "UUID"
Cohesion: 0.09
Nodes (16): Any, datetime, SeqDistance, SeqProfile, UUID, Define seqdb domain interfaces and policies for domain.repository.seq., Yield profile identifiers having distance records for a protocol. Args: uow:…, Return the latest distance-record modification time for a protocol. Args: uow:… (+8 more)

### Community 100 - "Hashable"
Cohesion: 0.06
Nodes (27): DictAdapter, PolarsAdapter, Any, BaseModel, Hashable, Protocol, PydanticAdapter, Encapsulates adapting a Pydantic model to the field interface. (+19 more)

### Community 101 - ".create_parent_for_upload"
Cohesion: 0.02
Nodes (150): IdentifierIssuer, Represents a system or process that issues externally supplied identifiers. An…, Child1, Child1ForUpload, Child1UploadResult, Child2, Child2ForUpload, Child2Identifier (+142 more)

### Community 102 - ".get_obj"
Cohesion: 0.06
Nodes (33): ConceptSet, Contact, Disease, EtiologicalAgent, RegionSet, RegionSetShape, Site, Case (+25 more)

### Community 103 - "IntEnumWithJsonSchemaMixin"
Cohesion: 0.06
Nodes (35): CoreSchema, AstResultFormat, FileFormat, IntEnumWithJsonSchemaMixin, PcrResultFormat, IntEnum, QualityControlResult, Encapsulates ordered quality-control outcomes for sequence data. (+27 more)

### Community 104 - "CaseAbac"
Cohesion: 0.03
Nodes (68): CaseRight, CaseRightSet, Group case access rights by protected resource and operation., Identify access rights granted for cases and case sets., Expose case ABAC policy records, rights models, and shared admin policy types.…, CaseAbac, CaseTypeAccessAbac, CaseTypeShareAbac (+60 more)

### Community 105 - "make_assoc"
Cohesion: 0.21
Nodes (6): BaseRepositoryTestCase, make_assoc(), Base test case with common fixtures and utilities., Tests for update_association covering all branches., Helper to create association objects., TestUpdateAssociation

### Community 106 - "Any"
Cohesion: 0.15
Nodes (7): Any, Create an OpenID Connect ID Token., Validate and decode an ID token., Create userinfo endpoint response based on scopes., Create OpenID Connect discovery document., Create JWKS response., Create logout response.

### Community 107 - "test_casedb_crud_common.py"
Cohesion: 0.07
Nodes (21): EqualsStringFilter, Represents a filter matching a string value., DataCmd, DummyCmd, DummyEntity, DummyLink, MetaCmd, NoAbacCmd (+13 more)

### Community 108 - "CaseBatchUploader"
Cohesion: 0.08
Nodes (26): Represents a request to perform an atomic batch upload of cases and associated…, UploadCasesCommand, CaseBatchUploadResult, Represents the results of uploading a batch of cases., Upload a batch of cases and related data. Implementations may persist cases,…, Validate and transform the cases in a batch upload command. Where applicable,…, Return mutable content and issue-list references for all batch cases. The…, Update uploaded cases' dates from the highest-resolution time value. The… (+18 more)

### Community 109 - "test_seqdb_calculate_seq_distances_performance.py"
Cohesion: 0.08
Nodes (45): BaseSeqRepository, Encapsulates backend-independent persistence for seqdb sequence data., datetime, Provide seqdb persistence behavior for repositories.seq_dict., Encapsulates seqdb persistence behavior for sequence repositories using in-…, Return the latest modification time among a protocol's distance records., Return samples modified directly or through linked records in a time range., SeqDictRepository (+37 more)

### Community 110 - "sa/util.py"
Cohesion: 0.06
Nodes (42): compiles, ComputedFieldInfo, _create_schemas(), upgrade(), _create_schemas(), upgrade(), get_type_from_annotation(), Any (+34 more)

### Community 111 - "User"
Cohesion: 0.05
Nodes (47): Any, DataCollection, datetime, Model, Organization, OrganizationAdminPolicy, OrganizationIdentifierIssuerLink, User (+39 more)

### Community 112 - "ImportGraphAnalyzer"
Cohesion: 0.07
Nodes (30): Import, ImportFrom, analyze_imports(), ImportEdge, ImportGraphAnalyzer, ImportStatementVisitor, ModuleNode, Path (+22 more)

### Community 113 - "CaseValidator"
Cohesion: 0.07
Nodes (31): CaseDataIssue, Represents a case-content issue associated with a column., CaseValidator, Concept, NoReturn, Organization, RefCol, Region (+23 more)

### Community 114 - "BaseService"
Cohesion: 0.04
Nodes (40): Link, BaseModel, Return the tuple representation accepted by ``from_tuple``., Create a multi-link from its tuple representation., Represents a field that relates a model to another model., Return the tuple representation accepted by ``from_tuple``., Create a link from its tuple representation., model_validator (+32 more)

### Community 115 - "case_service_retrieve_is_own_cases"
Cohesion: 0.10
Nodes (27): case_service_retrieve_is_own_cases(), UUID, Map accessible requested cases to private-collection ownership flags. Invalid…, BaseIsOwnCasesTestCase, _FakeCaseAbacPolicy, Any, Case, Command (+19 more)

### Community 116 - "Concept"
Cohesion: 0.05
Nodes (40): ConceptClass, ConceptSynonym, FactRelationship, ConceptClass (omopdb.md), ConceptSynonym (omopdb.md), EpisodeEvent (omopdb.md), FactRelationship (omopdb.md), Metadata (omopdb.md) (+32 more)

### Community 117 - "case_service_crud_case_set_data_collection_link"
Cohesion: 0.24
Nodes (12): CaseSetDataCollectionLinkCrudCommand, Represents a request to execute a CRUD operation on CaseSetDataCollectionLinks., case_service_crud_case_set_data_collection_link(), _crud_case_set_data_collection_link_with_abac(), _crud_case_set_data_collection_link_without_abac(), CaseSetDataCollectionLink, UUID, Handle CRUD operations for CaseSetDataCollectionLink entities. (+4 more)

### Community 118 - "Concept (omopdb.omop / OMOP CDM entity)"
Cohesion: 0.13
Nodes (39): CareSite (omopdb.omop / OMOP CDM entity), CdmSource (omopdb.omop / OMOP CDM entity), Cohort (omopdb.omop / OMOP CDM entity), CohortDefinition (omopdb.omop / OMOP CDM entity), Concept (omopdb.omop / OMOP CDM entity), ConceptAncestor (omopdb.omop / OMOP CDM entity), ConceptClass (omopdb.omop / OMOP CDM entity), ConceptRelationship (omopdb.omop / OMOP CDM entity) (+31 more)

### Community 119 - "test_update_user_policy.py"
Cohesion: 0.26
Nodes (14): _make_abac_service(), _make_invite_cmd(), _make_policy(), _make_role_set_map(), _make_update_cmd(), _make_user(), scenario_ids, User (+6 more)

### Community 120 - "_make_crud_side_effect"
Cohesion: 0.13
Nodes (24): _CrudRecorder, _make_allele_profile(), _make_crud_side_effect(), _make_mlva_profile(), _make_seq_distance(), _make_seq_distance_protocol_for_locus_set(), Any, Model (+16 more)

### Community 121 - "test_fastapp_repository_performance.py"
Cohesion: 0.08
Nodes (22): parse_stats(), Any, Append profiler function statistics to a row-oriented result list. Args: df:…, Create a test environment for the given test type and repository type. A single…, scenario_ids, TestRead, env(), fixture (+14 more)

### Community 122 - "DummyCommand"
Cohesion: 0.13
Nodes (12): DummyCommand, Test get_headers method for different auth protocols., get_headers returns default headers with NONE protocol., get_headers caches token when not expired., get_headers refreshes token past refresh margin., Minimal command for testing., get_headers caches long-lived tokens correctly. Note: Tokens without an 'exp'…, Integration tests combining multiple features. (+4 more)

### Community 123 - "CacheRegion"
Cohesion: 0.02
Nodes (109): Return the envelope stored under `key`, or `NO_VALUE`. Args: key: The fully…, Return the envelopes for `keys` in the order given. Args: keys: The fully…, See base method. Only the keys missing from the near tier are requested…, MemoryBackend, See base method. Storing over an existing key reports the previous envelope as…, See base method. The snapshot is taken under the lock, so iteration is safe…, Remove every entry that passed its hard expiry. Lazy expiry only reclaims…, Evict entries until the weight budget is met. Args: candidate: The key that was… (+101 more)

### Community 124 - "Permission"
Cohesion: 0.01
Nodes (148): Permission, computed_field, field_serializer, PydanticBaseModel, Represents a user of the application. This can represent an actual user, or a…, Get the key of the user. The key is used to identify the user across systems,…, Represents a permission as a combination of (command_name, permission_type).…, Return the canonical permission name. (+140 more)

### Community 125 - "Any"
Cohesion: 0.06
Nodes (18): Any, Save authorization code (not used in client credentials flow)., Validate authorization code (not used in client credentials flow)., Confirm redirect URI (not used in client credentials flow)., Validate that the grant type is supported by the client., Validate bearer token and scopes., Get default redirect URI for a client., Validate redirect URI. (+10 more)

### Community 126 - ".create_case_for_upload"
Cohesion: 0.14
Nodes (10): Tests for ABAC column and creation-right verification in verify_abac_rights., Tests for _get_case_data_collections in CaseBatchUploader., Tests for default_created_in_data_collection_id behavior. NOTE: Direct unit…, When new case has NULL_ID and no default, should add error., When case explicitly sets created_in_data_collection_id, don't override., Existing cases should not be modified by default setting., TestCaseServiceUploadCasesFeatureFlag, TestGetCaseDataCollections (+2 more)

### Community 127 - "test_fastapp_cache_invalidation.py"
Cohesion: 0.02
Nodes (120): CacheConfigurationError, Error for configuring a region that already has a backend., Error for requesting a region name that the manager does not know., Error for an invalid or contradictory cache configuration., RegionAlreadyConfiguredError, RegionNotFoundError, Invalidation, LocalInvalidationBus (+112 more)

### Community 128 - "SampleQueryResult"
Cohesion: 0.23
Nodes (9): Represents a request to retrieve sample identifiers matching a query. These…, RetrieveSamplesByQueryCommand, Represents a sample query, its matching identifiers, and any result truncation., SampleQueryResult, Retrieve samples matching a query. Args: cmd: Sample-query command to execute.…, Retrieve samples matching the given query., Retrieve sample IDs based on query filters., seq_service_retrieve_samples_by_query() (+1 more)

### Community 129 - "Person"
Cohesion: 0.10
Nodes (34): ConditionOccurrenceIdentifier (omopdb.md), Observation (omopdb.md), VisitOccurrence (omopdb.md), CareSite, ConditionOccurrence, ConditionOccurrenceIdentifier, DeviceExposure, DeviceExposureIdentifier (+26 more)

### Community 130 - "PersonBatchForUpload"
Cohesion: 0.05
Nodes (45): PersonBatchForUpload, PersonForUpload, Any, computed_field, Represents a person, together with any relevant associated data, intended for…, Represents a set of persons intended for upload, together with any new…, Indicates whether there are any measurements in the person set., Indicates whether there are any observations in the person set. (+37 more)

### Community 131 - "TestRouterData"
Cohesion: 0.17
Nodes (7): Verify RouterData creates with required name and create_endpoints_fn., Verify RouterData accepts optional endpoints_function_kwargs., Verify RouterData behaves like a standard dictionary., Verify stored function in RouterData can be called., Verify stored function can receive kwargs from endpoints_function_kwargs., Tests for RouterData TypedDict., TestRouterData

### Community 132 - "._get_allele_profile_for_ids"
Cohesion: 0.08
Nodes (17): Test SampleForUpload with multiple SeqForUpload instances., Test SampleForUpload with empty seqs list., Test SampleForUpload with both seqs and Identifiers., Test SampleForUpload with seqs having different properties., Test that seqs property maintains proper structure for serialization., Test SampleForUpload without id where seqs can have their own sample_ids., Test SampleForUpload without id where seqs also have NULL_ID sample_ids., Test has_seqs computed field returns False when no samples have seqs. (+9 more)

### Community 133 - "RBACTestClient"
Cohesion: 0.11
Nodes (12): get_test_client(), Any, BaseRbacService, Enum, fixture, Hashable, Logger, scenario_ids (+4 more)

### Community 134 - "omopdb/domain/enum.py"
Cohesion: 0.06
Nodes (37): Collection, AnonMethod, AnonStrictness, Enum, Enumerations configuring OmopDB services, persistence, roles, and anonymization., Encapsulates OmopDB and shared service domains., Encapsulates supported OmopDB repository implementations., Encapsulates roles recognized by OmopDB authorization policies. (+29 more)

### Community 135 - "Concept"
Cohesion: 0.07
Nodes (32): Concept, ConceptAncestor, ConceptRelationship, ConditionEra, Cost, Domain, DoseEra, DrugEra (+24 more)

### Community 136 - "LogItem"
Cohesion: 0.09
Nodes (41): InitializationServiceError, Error while initializing an application service., Error while initializing a repository-backed service., RepositoryInitializationServiceError, LogItem, Encapsulates serializing an application log code, message, and optional…, Serialize this log item as JSON., _LargeListCommand (+33 more)

### Community 137 - "BaseOrganizationService"
Cohesion: 0.03
Nodes (58): BaseIsPermissionSubsetNewRolePolicy, Any, Provide an RBAC policy contract for role creation and updates., Encapsulates prevention of creation or updates that would elevate a role's…, Initialize the policy with its RBAC service and configuration properties. Args:…, BaseOrganizationService, Any, User (+50 more)

### Community 138 - "BaseRepository"
Cohesion: 0.06
Nodes (28): BaseRepository, Any, Hashable, Update association objects of the given model class that represent an…, Encapsulates defining the persistence contract used by application services., Initialize repository identity from optional keyword arguments., Return the repository's stable identifier., Return the repository's display name. (+20 more)

### Community 139 - "TestFilterConstruction"
Cohesion: 0.20
Nodes (5): date, datetime, scenario_ids, TestFilterConstruction, Util

### Community 140 - ".create_crud_cmd"
Cohesion: 0.11
Nodes (17): BasePolicyTestCase, CrudCommand, Model, OrganizationAdminPolicy, scenario_ids, User, UUID, Create a user with optional roles and organization. (+9 more)

### Community 141 - "MemoryVersionStore"
Cohesion: 0.18
Nodes (5): MemoryVersionStore, Encapsulates keeping generation numbers in process memory. This is exact for a…, Initialize a MemoryVersionStore instance., Adopting a remote generation must not make orphans addressable again., test_a_generation_never_moves_backwards()

### Community 142 - "TestModelSampleBatchForUpload"
Cohesion: 0.08
Nodes (14): Create a SampleForUpload with specified number of SeqForUpload instances., Test reading sample_batch_for_upload1.json as SampleBatchForUpload model., Test reading sample_batch_for_upload2.json as SampleBatchForUpload model., Test valid SampleBatchForUpload with minimal data., Test valid SampleBatchForUpload with alleles., Test valid SampleBatchForUpload with multiple samples including seqs., Test valid SampleBatchForUpload with empty samples list., Test SampleBatchForUpload where all samples contain SeqForUpload instances. (+6 more)

### Community 143 - "seq/crud_tree_algorithm_class.py"
Cohesion: 0.20
Nodes (10): TreeAlgorithmClass, TreeAlgorithmClassCrudCommand, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for tree-algorithm-class entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added (+2 more)

### Community 144 - "commondb/env.py"
Cohesion: 0.02
Nodes (92): Create and populate the casedb domain registry. Command exports provide…, complete_stored_model_field_props(), Any, Command, Domain, Hashable, Model, Complete stored model field properties with defaults for missing fields. Args:… (+84 more)

### Community 145 - "TestUpdate"
Cohesion: 0.09
Nodes (3): scenario_ids, skipif, TestUpdate

### Community 146 - "User"
Cohesion: 0.16
Nodes (11): FileCompression, Encapsulates supported compression methods for biological files., DataCollection, File, Model, Protocol, ReadSet, Sample (+3 more)

### Community 147 - "TestModelBaseSeq"
Cohesion: 0.07
Nodes (20): UUID, Unit tests for IDSDB ETL model classes. Tests the Identifier, AlleleForUpload,…, Test cases for BaseSeq model validation and functionality., Return a valid DNA sequence for testing., Return an invalid DNA sequence for testing., Compute the expected sequence hash for a given sequence., Test creating BaseSeq with valid DNA sequence., Test that DNA sequences are normalized to lowercase. (+12 more)

### Community 148 - "cache/__init__.py"
Cohesion: 0.02
Nodes (170): Abstract cache store contract. A backend is a dumb key-to-envelope store. It…, Cache store implementations. The package exposes the abstract contract and the…, A near cache in front of a shared store. `LayeredBackend` reads from a fast…, In-process cache store with capacity management and expiry. `MemoryBackend` is…, Clock, Protocol, Time sources used by the cache framework. Every expiry decision in this package…, Encapsulates supplying the monotonic and wall-clock readings a cache needs. (+162 more)

### Community 149 - "Case Type"
Cohesion: 0.07
Nodes (30): ColSet, Disease, Etiology, CaseTypeSetMember (doc), ColSet (doc), ColSetMember (doc), Case Type, Case Type Set Member (+22 more)

### Community 150 - "BaseCaseAbacPolicy"
Cohesion: 0.04
Nodes (56): BaseModel, Represents the cases returned by a similar-case request., RetrieveSimilarCasesReturnValue, BaseCaseAbacPolicy, Any, BaseAbacService, Command, Define policy helpers for attaching Casedb ABAC data to commands. (+48 more)

### Community 151 - "test/fastapp/model.py"
Cohesion: 0.39
Nodes (8): Base1, Base2, declarative_mixin, RowMetadataMixin, SAModel1_1, SAModel1_2, SAModel2_1, SAModel2_2

### Community 152 - "OrganizationSARepository"
Cohesion: 0.06
Nodes (28): BaseOrganizationRepository, User, UserInvitation, Define the repository interface for commondb organization data., Encapsulates organization-specific user lookup operations for services., Initialize the repository with its user and invitation model classes. Args:…, Determine whether a user exists for a normalized unique key. Args: uow: Unit of…, Retrieve the user associated with a normalized unique key. Args: uow: Unit of… (+20 more)

### Community 153 - "Data Collection"
Cohesion: 0.12
Nodes (28): ColSet, DataCollection, Organization, OrganizationAdminPolicy, User, CaseTypeSet (doc), Case Type Set, Col Set (+20 more)

### Community 154 - ".load"
Cohesion: 0.03
Nodes (85): ManualClock, Encapsulates advancing only when a test tells it to. Both readings start at…, Initialize a ManualClock instance., Move the clock forward and return the new reading. Args: seconds: A non-…, Set both readings to an absolute value. Args: value: The new reading. Raises:…, fixture_region(), fixture, Tests for the cached callables produced by a region decorator. (+77 more)

### Community 155 - "._validate_state"
Cohesion: 0.22
Nodes (7): _enum_to_str(), Any, model_validator, Self, Return an enum member name or the supplied string-like value., Normalize members and build the optimized membership matcher., Match a value using the function generated during validation. Args: value: The…

### Community 156 - "omopdb/repositories/organization_sa.py"
Cohesion: 0.22
Nodes (7): OrganizationSARepository, Any, CommonOrganizationSARepository, Engine, SQLAlchemy organization repository configured with OmopDB user models., Encapsulates shared organization persistence with OmopDB SQLAlchemy model types., Initialize shared SQL organization storage with OmopDB model classes.

### Community 157 - "ServerManager"
Cohesion: 0.06
Nodes (34): oauth_server(), fixture, Test OAuth OIDC Client Credential Authentication Flow This module implements a…, Start and manage ReceiverApp for the test session., Create RequestorApp instance., Test OAuth Client Credentials flow with missing token., Test that OAuth discovery endpoint is working., Test that JWKS endpoint is working. (+26 more)

### Community 158 - "test_fastapp_cache_support.py"
Cohesion: 0.03
Nodes (101): CantDeserializeError, Error for a value that could not be converted to its stored form., Error for a stored value that the current code can no longer read. A region…, SerializationError, compute_etag(), HttpCachePolicy, matches_etag(), HTTP-level caching helpers. Caching at the transport boundary is a different… (+93 more)

### Community 159 - "TestParametrizedCRUD"
Cohesion: 0.22
Nodes (6): parametrize, Parameterized tests for CRUD operations across models., Verify create then read cycle works for all models., Verify create then update cycle works for all models., Verify create then delete cycle works for all models., TestParametrizedCRUD

### Community 160 - "TestModelSeq"
Cohesion: 0.09
Nodes (16): Seq, Test cases for Seq model functionality and inheritance., Create a valid Contig for testing., Create a sample Seq with default values and optional overrides., Test creating Seq with contigs., Test creating Seq without contigs (not available)., Test that Seq inherits HasSampleMixin properties., Test that Seq inherits CodeMixin properties. (+8 more)

### Community 161 - "CaseSet"
Cohesion: 0.09
Nodes (28): Case, Case, CaseAccessAbac, CaseRights, CaseSet, CaseSetAccessAbac, CaseSetForUpload, CaseSetRights (+20 more)

### Community 162 - "CaseType"
Cohesion: 0.08
Nodes (28): CaseQuery, CaseQueryResult, CaseSetQuery, CaseType, CaseTypeAccessAbac, CaseTypeCategory, CaseTypeCol, Col (+20 more)

### Community 163 - "DatetimeRangeFilter"
Cohesion: 0.08
Nodes (32): CaseStats, model_validator, Self, Represents aggregate statistics for cases or a case set. Model validation: Own…, Validate count and case-date invariants., BaseCaseRepository, datetime, UUID (+24 more)

### Community 164 - ".create_local_or_remote_app"
Cohesion: 0.11
Nodes (15): Any, Enum, Logger, User, Register an invited user using their invitation token., Update a user's active status, roles, or organization., Update the authenticated user's own organization., Create a local or remote application instance for the requested setup type.… (+7 more)

### Community 165 - "InMemoryOrganizationRepository"
Cohesion: 0.10
Nodes (13): InMemoryOrganizationRepository, make_commondb_user_manager(), make_mock_rbac_service(), make_root_cfg(), Any, Organization, User, UserManager (+5 more)

### Community 166 - "Role"
Cohesion: 0.04
Nodes (59): Define casedb application roles for command-centric authorization., Role, Expose casedb policy contracts and shared authorization policy bases.…, CommonRoleGenerator, Define Casedb role permissions and their shared-role mappings., Encapsulates Casedb role inheritance and command permission expansion. The…, # TODO: remove UPDATE from association objects that do not have properties of…, RoleGenerator (+51 more)

### Community 167 - "test_casedb_upload.py"
Cohesion: 0.09
Nodes (22): Case, datetime, parametrize, scenario_ids, UUID, Unit tests for casedb case upload functionality., Tests for existing case data collection handling, including NULL_ID edge case.…, Existing case should maintain its created_in_data_collection_id. (+14 more)

### Community 168 - "env"
Cohesion: 0.36
Nodes (5): env(), fixture, FixtureRequest, Return a test client configured for either DICT or SA_SQLITE demo repos. The…, TestRetrievePersons

### Community 169 - "DummyCmd"
Cohesion: 0.24
Nodes (3): DummyCmd, TestHeadersAndApplyHandler, TestRouteRegistration

### Community 170 - "._create_sample_seq_for_upload"
Cohesion: 0.07
Nodes (20): Any, SeqForUpload, Create a sample SeqForUpload with default values and optional overrides., Test cases for SeqForUpload model functionality and upload-specific features., Create a sample SeqForUpload with default values and optional overrides., Test creating SeqForUpload with basic fields., Test that SeqForUpload inherits all Seq properties., Test SeqForUpload with NULL_ID for sample_id. (+12 more)

### Community 171 - "OAuth2Client"
Cohesion: 0.10
Nodes (15): demo_client_credentials_flow(), OAuth2Client, Any, Create a new OAuth client., Delete an OAuth client., List all OAuth clients., Simple OAuth 2.0 client for testing., Get a specific OAuth client. (+7 more)

### Community 172 - "Any"
Cohesion: 0.18
Nodes (7): Any, Hashable, Treat every supplied value as an existing value., Return whether a scalar value exists, respecting inversion., Yield existence matches for each value in a column., Return whether the filter key exists in a row with a value. Args: row: Row to…, Yield existence matches for each row. Args: rows: Rows to inspect. na_values:…

### Community 173 - "fastapp shared application framework"
Cohesion: 0.25
Nodes (8): casedb domain, commondb shared package, fastapp shared application framework, filter and transform support packages, omopdb domain, seqdb domain, Shared /v1 router composition pattern, pydantic

### Community 174 - "Protocol"
Cohesion: 0.12
Nodes (28): Identifier Issuer, IdentifierIssuer, File, AstMeasurement, AstPrediction, LocusSet, PcrMeasurement, Protocol (+20 more)

### Community 175 - "Person"
Cohesion: 0.15
Nodes (27): CareSite, ConditionOccurrence, ConditionOccurrenceIdentifier, DeviceExposure, DrugExposure, Location, CareSite (omopdb.md), ConditionOccurrence (omopdb.md) (+19 more)

### Community 176 - "Protocol (seqdb entity)"
Cohesion: 0.13
Nodes (27): AstMeasurement (seqdb entity), AstPrediction (seqdb entity), File (seqdb entity), IdentifierIssuer (seqdb entity), LocusSet (seqdb entity), OrganizationIdentifierIssuerLink (seqdb entity), PcrMeasurement (seqdb entity), Protocol (seqdb entity) (+19 more)

### Community 177 - "OrganizationService"
Cohesion: 0.02
Nodes (78): Expose concrete casedb and shared services for application composition. Casedb…, OntologyService, Implement casedb ontology association service behavior., Encapsulates CRUD and association command handling for ontologies., Expose local and remote seqdb collaborators used by casedb services.…, ModelMetadataPolicy, Any, Enum (+70 more)

### Community 178 - "CommondbDictModelModifier"
Cohesion: 0.07
Nodes (21): CommondbDictModelModifier, datetime, Hashable, Apply commondb audit metadata rules to in-memory persisted models., Encapsulates a DictRepository modifier for all databases that use…, Initialize the source of timezone-aware audit timestamps. Args:…, Stamp a new commondb model with creation and modification metadata. Args:…, Refresh modification metadata while preserving the stored creation time. Args:… (+13 more)

### Community 179 - "EndpointTestClient"
Cohesion: 0.13
Nodes (18): EndpointTestClient, Any, Command, CrudCommand, Response, Register a command class with its endpoint-dispatch handler. Args:…, Dispatch a supported command to its corresponding API endpoint. Args: cmd:…, Request identity providers and deserialize the returned list. Args: cmd:… (+10 more)

### Community 180 - ".result_type"
Cohesion: 0.25
Nodes (5): Create and register a new ExtractResult (or subclass), then return it.…, Create and register a new TransformResult (or subclass), then return it.…, Return the status enum implied by `success` and `error`., _T_Extract, _T_Transform

### Community 181 - "AuthEnv"
Cohesion: 0.12
Nodes (7): AuthEnv, Self-contained, per-test auth environment built around the real…, Verify that unknown users are auto-created when the flag is on, and rejected…, Verify that a root user can log in for the first time (triggering…, Drive get_existing_user_from_claims directly (no HTTP stack)., TestAutoCreateUser, TestRootUserLogin

### Community 182 - "RetrieveSeqFastaCommand"
Cohesion: 0.25
Nodes (5): Represents a request to retrieve sequences in FASTA format. The result is an…, RetrieveSeqFastaCommand, Stream sequence data in FASTA format. Args: cmd: FASTA-retrieval command to…, Stream genetic sequence FASTA data by sequence IDs., Stream repository contigs as wrapped or unwrapped FASTA records.

### Community 183 - "UUID"
Cohesion: 0.09
Nodes (15): AbstractSet, datetime, SeqDistance, SeqProfile, UUID, Yield requested sequences and their DNA contigs for FASTA generation. Args:…, Yield distance records for a protocol, optionally limited to profile IDs., Yield unique profile IDs that have distance records for a protocol. (+7 more)

### Community 184 - "FakeResponse"
Cohesion: 0.26
Nodes (3): FakeClient, FakeResponse, Any

### Community 185 - "Gen-EpiX README"
Cohesion: 0.11
Nodes (25): pr.sh Helper Script, PR Skill, CASEDB Service, COMMONDB Service, FASTAPP Shared Framework, lsp-data Repository, OMOPDB Service, SEQDB Service (+17 more)

### Community 186 - "casedb.organization.md"
Cohesion: 0.13
Nodes (25): Organization (doc), Organization Set (doc), User (doc), User Invitation (doc), casedb / ORGANIZATION — Simplified ERD, Organization Identifier Issuer Link, Organization, Organization Set (+17 more)

### Community 187 - "._validate_model"
Cohesion: 0.17
Nodes (9): decode_ascii_from_gzip_base64(), model_validator, Self, UUID, Normalize and validate the sequence representation, length, and hash. Derives…, Return the nucleotide sequence represented by this model. Args: ref_seq_str:…, Decode a gzip-compressed base64 string., Compute a hash for the given string, which is expected to contain a nucleotide… (+1 more)

### Community 188 - "RetrieveSeqDistanceLastModifiedCommand"
Cohesion: 0.25
Nodes (6): Represents a request to retrieve the last modified datetime for a SeqDistance…, RetrieveSeqDistanceLastModifiedCommand, datetime, Retrieve the latest sequence-distance modification time. Args: cmd: Last-…, datetime, Delegate distance modification-time retrieval to the distance operation.

### Community 189 - "TestGetAllEndpoint"
Cohesion: 0.25
Nodes (5): Tests for GET_ALL CRUD endpoint., Verify GET /model1 returns empty list when no records exist., Verify GET /model2 returns empty list when no records exist., Verify GET /model1 returns all records., TestGetAllEndpoint

### Community 190 - "CommondbRemoteApp"
Cohesion: 0.25
Nodes (7): CommondbRemoteApp, Encapsulates a remote app client for the commondb service with OAuth2/NONE…, _mock_response(), Any, fixture, Test the hand-written (non-CRUD) command handlers., TestNonCrudHandlers

### Community 191 - "computed_field"
Cohesion: 0.13
Nodes (8): computed_field, Return whether the sequence has at least one processed contig., Return the number of contigs in this sequence., Return the total contig length, or zero when no contigs are available., Return the longest contig length, or zero when no contigs are available., Return the shortest contig length, or zero when no contigs are available., Return the median contig length, or zero when no contigs are available., Return the assembly N50 contig length. Returns: The shortest contig length…

### Community 192 - "TestDelete"
Cohesion: 0.11
Nodes (3): scenario_ids, skipif, TestDelete

### Community 193 - "IdentifierIssuer"
Cohesion: 0.08
Nodes (24): Death, DeathIdentifier, DeviceExposureIdentifier, DrugExposureIdentifier, IdentifierIssuer, Death (omopdb.md), DeathIdentifier (omopdb.md), DeviceExposureIdentifier (omopdb.md) (+16 more)

### Community 194 - "case_service_crud_ref_col"
Cohesion: 0.13
Nodes (16): case_service_crud_ref_col(), RefCol, UUID, Validate concept-set type and unit compatibility for reference columns. Args:…, Handle reference-column CRUD with access filtering and write validation. Args:…, _verify_ref_col_concept_set_type_and_unit(), BaseRefColTestCase, Any (+8 more)

### Community 195 - "TestNonCrudHandlers"
Cohesion: 0.24
Nodes (4): _mock_response(), Any, Test the hand-written (non-CRUD) command handlers., TestNonCrudHandlers

### Community 196 - "CompositeFilter"
Cohesion: 0.12
Nodes (24): CompositeFilter, Any, BaseModel, Hashable, model_validator, Self, Match a value using the function generated during validation. Args: value: The…, Match row values using the function generated during validation. Args:… (+16 more)

### Community 197 - "TestPostOneEndpoint"
Cohesion: 0.25
Nodes (5): Tests for POST_ONE CRUD endpoint., Verify POST /model1 creates a new record., Verify POST /model2 creates a new record., Verify POST /model1 with invalid data returns error., TestPostOneEndpoint

### Community 198 - "log_parser_v2.py"
Cohesion: 0.04
Nodes (46): scenario_ids, skip, TestRead, AzureColumn, LogCode, LogParser, LogType, Any (+38 more)

### Community 199 - "TrackingUnitOfWork"
Cohesion: 0.29
Nodes (3): Seq, Track the transaction outcome for the conversion service test., TrackingUnitOfWork

### Community 200 - "TestClient"
Cohesion: 0.07
Nodes (13): Encapsulates integration-test helpers for querying and verifying application…, Retrieve a user from the app's user manager by key., Determine whether one role is subordinate to another by permissions. Set…, TestClient, scenario_ids, skipif, TestCreate, scenario_ids (+5 more)

### Community 201 - "Schema migrations"
Cohesion: 0.29
Nodes (6): Developing a migration, Existing databases, Local clean bootstrap, PRD deployment, Schema migrations, SQL Server-specific choices

### Community 202 - "TestNumpyAlleleIntegration"
Cohesion: 0.10
Nodes (12): fixture, parametrize, Protocol, Unit tests for all new numpy ALLELE distance code paths (LSP-3529)., _decode_profile with use_numpy_allele=True returns (n_loci,) S16 array; null…, The isinstance(np.ndarray) branch in…, Each invalid variant-flag combination raises ValueError., numpy_batch path stores correct cross and intra-batch distances. (+4 more)

### Community 203 - "DummyIdpClient"
Cohesion: 0.09
Nodes (13): Request, Extract claims from JWT token., Returns the claims of the user from the request or None if claims cannot be…, DummyIdpClient, Any, Request, scenario_ids, Unit tests for IdpClient base class. Follows the reference test style for… (+5 more)

### Community 204 - "UUID"
Cohesion: 0.15
Nodes (9): field_serializer, field_validator, UUID, Normalize a JSON locus-ID list to UUID objects., Serialize ordered locus identifiers as strings., Normalize a JSON locus-code map and enforce its key length limit., Serialize locus-code-map identifier values as strings., Normalize an empty gene-product code to ``None``. (+1 more)

### Community 205 - "Registry"
Cohesion: 0.08
Nodes (19): Encapsulates an example registry-backed custom transformer., Initialize the example transformer with a registry-visible name., Return the example object unchanged., StringUpperTransformer, Any, Decorator to register a transformer factory function., Encapsulates named constructors for configured transformers., Register a transformer class by name. (+11 more)

### Community 206 - "test_cfg_log_level.py"
Cohesion: 0.20
Nodes (16): _build_test_fixture(), _DummyHandler, _DummyLogger, _extract_diagnostic_payload(), _patch_logging_get_logger(), _patch_runtime_logger_dict(), MonkeyPatch, scenario_ids (+8 more)

### Community 207 - "generate_seq_distances.py"
Cohesion: 0.09
Nodes (32): computed_field, Represents a set of samples intended for upload, together with any new…, Indicates whether there are any read sets in the sample set., Indicates whether there are any sequences in the sample set., Indicates whether there are any seq taxonomies in the sample set., Indicates whether there are any seq classifications in the sample set., Indicates whether there are any sequence profiles in the sample set., Indicates whether there are any PCR measurements in the sample set. (+24 more)

### Community 208 - "scenario_ids"
Cohesion: 0.10
Nodes (12): scenario_ids, Test ValidationError when id doesn't match computed seq_hash., Test valid Identifier with identifier_issuer_code., Test valid Identifier with identifier_issuer_id., Test valid Identifier with both issuer fields., Test ValidationError when both issuer fields are missing., Test field length validation., Test valid AlleleForUpload with locus_id. (+4 more)

### Community 209 - "model/case/__init__.py"
Cohesion: 0.03
Nodes (101): BaseCasePolicy, OrganizationAccessCasePolicy, OrganizationShareCasePolicy, Define persistent organization and user ABAC policy records for cases. Access…, Represents a user's maximum access rights in one data collection. The rights…, Represents common case and case-set rights for a case-type set., Represents an organization's additional source-to-target share rights. Rights…, Represents a user's maximum source-to-target share rights. The rights are… (+93 more)

### Community 210 - "EvictionStrategy"
Cohesion: 0.02
Nodes (52): Initialize a MemoryBackend instance. Args: max_weight: Total weight the store…, CountMinSketch, create_eviction_strategy(), EvictionStrategy, FIFOEviction, LFUEviction, LRUEviction, ABC (+44 more)

### Community 211 - "TestCreateUserFromToken"
Cohesion: 0.19
Nodes (12): make_cdb_invitation(), make_cdb_organization(), parametrize, scenario_ids, UserInvitation, UUID, Return a valid future-expiring UserInvitation., Verify that the commondb UserManager correctly creates a user from an… (+4 more)

### Community 212 - "TestInitialization"
Cohesion: 0.09
Nodes (12): Test CommondbRemoteApp initialization with various configurations., Initialize with NONE auth protocol as enum., Initialize with NONE auth protocol as string., Initialize with OAUTH2 auth protocol as enum., Initialize with OAUTH2 auth protocol as string., Initialize with OAuthFlow as enum., Initialize with OAuthFlow as string., Verify default route prefix is /v1. (+4 more)

### Community 213 - "RequestorApp"
Cohesion: 0.07
Nodes (25): Response, Client application that requests access tokens and calls protected endpoints., Initialize the OIDC client., Get an access token for the specified audience., Call a protected endpoint with the access token., Create a properly formatted but invalid JWT token for testing., RequestorApp, Any (+17 more)

### Community 214 - "SeqGenerationSettings"
Cohesion: 0.17
Nodes (7): BaseModel, computed_field, field_validator, Random, SeqGenerationSettings, scenario_ids, TestGenerateRandomSequences

### Community 215 - "Development Guide"
Cohesion: 0.17
Nodes (21): Python & Pytest Conventions, Diagnose-before-editing workflow, test.util.mock_compat, pytest-run skill, Test behavior, not implementation details, Gen-EpiX Agent Guide, Graphify architecture query workflow, Claude Code Root Config (+13 more)

### Community 216 - "Linter"
Cohesion: 0.19
Nodes (5): Linter, Path, Runs the specified linting tool with the provided command-line arguments. This…, This class provides an interface to run linting tools like mypy, pylint, ruff,…, Runs a series of linting and formatting tools on the gen-epix project. This…

### Community 217 - "map_paired_elements"
Cohesion: 0.08
Nodes (14): map_paired_elements(), Any, Hashable, Group paired values by key while preserving input order for lists. With…, datetime, Any, Case, scenario_ids (+6 more)

### Community 218 - "get_test_client"
Cohesion: 0.40
Nodes (4): get_test_client(), fixture, Get a test client for casedb integration tests. This fixture initializes a test…, Auto-inject the env fixture into the class.

### Community 219 - "TestCommondbModelProcessMetadata"
Cohesion: 0.10
Nodes (13): fixture, integration, scenario_ids, modified_at must be set by the backend on creation., modified_by must be set to the creating user's id., created_at must not change when a record is updated., modified_by must be stamped with the updating user, not the creating user., modified_at supplied in the update payload must be ignored by the backend. (+5 more)

### Community 220 - "ReadOrganizationResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadOrganizationResultsOnlyPolicy, Filter casedb case-policy reads to visible organizations., Register casedb case-policy commands for organization filtering. Args:…, ReadOrganizationResultsOnlyPolicy

### Community 221 - "TestModelSeqProfileForUpload"
Cohesion: 0.08
Nodes (13): Test JSON serialization of AlleleProfileForUpload., Test valid AlleleProfileForUpload with codes., Test valid AlleleProfileForUpload with IDs., Test valid AlleleProfileForUpload with allele_ids., Test valid AlleleProfileForUpload with locus_allele_id_map., Test valid AlleleProfileForUpload with locus_code_map when using allele_ids., Test ValidationError when both protocol fields are missing., Test ValidationError when both locus_set fields are missing. (+5 more)

### Community 222 - "Runtime dependencies (requirements.txt)"
Cohesion: 0.25
Nodes (11): Dynaconf-based configuration, IDP modes (IDPS, MOCK, NONE), Repository mode parity (DICT, SA_SQLITE, SA_SQL), run.py CLI entrypoint, Local Development Model, Staged startup troubleshooting, Runtime dependencies (requirements.txt), Alembic (+3 more)

### Community 223 - "_Call"
Cohesion: 0.18
Nodes (7): _Call, Any, Encapsulates holding the shared outcome of one in-flight load. Attributes:…, Initialize a _Call instance., Return the result of `loader`, executing it at most once per key. Args: key:…, Claim leadership for `key` without blocking. A stale-while-revalidate read uses…, Return the result of awaiting `loader`, running it once per key. Args: key: The…

### Community 224 - "UpdateUserPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonUpdateUserPolicy, Encapsulates shared user-update checks with OmopDB role and user mappings., Initialize the user-update policy with OmopDB dependencies., UpdateUserPolicy

### Community 225 - "retrieve_case.py"
Cohesion: 0.14
Nodes (26): _get_map_function_for_col(), _get_map_functions_for_filters(), _get_valid_concepts(), _get_valid_region_values(), Any, Col, RefCol, User (+18 more)

### Community 226 - "convert"
Cohesion: 0.20
Nodes (5): Any, Reconstruct a nucleotide sequence from a NextClade representation. Args:…, convert(), parametrize, TestNextcladeSequenceConversion

### Community 227 - "TestSeqDistancePerformance"
Cohesion: 0.20
Nodes (8): BaseSeqDistancePerformance, ensure_datasets_exist_and_valid(), get_test_client(), fixture, parametrize, RepositoryType, scenario_ids, TestSeqDistancePerformance

### Community 228 - "UpdateUserPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonUpdateUserPolicy, Encapsulates authorizing user updates with seqdb roles and user model mappings., Configure the shared policy with seqdb role and user mappings., UpdateUserPolicy

### Community 229 - "6f2f4fb9b3d1_drop_legacy_code_constraints.py"
Cohesion: 0.33
Nodes (6): downgrade(), _drop_legacy_unique_constraint(), Drop a legacy unique constraint or index if it is present on SQL Server., Remove LSP-3497 legacy uniqueness for operational sequence entities., Do not recreate constraints: duplicate codes may already exist., upgrade()

### Community 230 - "CaseUploadSetup"
Cohesion: 0.38
Nodes (4): CaseUploadSetup, get_test_client(), fixture, Add sequencing and assembly protocols to seqdb, as well as identifier issuers.

### Community 231 - "test_seqdb_calculate_seq_distance.py"
Cohesion: 0.19
Nodes (12): Provide seqdb functionality for domain.literal., BaseCalculateSeqDistanceTestCase, _iterable(), _mock_uow(), ndarray, scenario_ids, Return an (n_loci,) S16 array where every locus has the same UUID byte., Base test case with common fixtures and utilities. (+4 more)

### Community 232 - "omop/ontology.py"
Cohesion: 0.07
Nodes (36): ConceptAncestor, ConceptClass, ConceptRelationship, ConceptSynonym, Domain, DrugStrength, Any, field_validator (+28 more)

### Community 233 - "make_cdb_user"
Cohesion: 0.20
Nodes (7): get_name_from_claims(), Get the name from the claims, checking against a list of possible name claims., make_cdb_user(), Pure unit tests for claim name-extraction helpers and update_user_name., Verify the real UserManager writes the name change to the repo., Return a fresh commondb User with the given attributes., TestAuth

### Community 234 - "TestCasedbMetadataMasking"
Cohesion: 0.14
Nodes (12): CaseType, fixture, integration, scenario_ids, User, Verifies that MaskModelProcessMetadataPolicy is correctly wired in casedb. Root…, Root user must see all three metadata fields populated — superusers bypass…, Org admin must see all three metadata fields masked to None by… (+4 more)

### Community 235 - "TimeoutGuard"
Cohesion: 0.10
Nodes (16): Return the default failure policy implied by the configuration. A configured…, BaseException, Encapsulates bounding the wall-clock duration of a backend call. The call runs…, Initialize a TimeoutGuard instance. Args: timeout: Seconds allowed for one…, Shut down the worker pool if one was created., Initialize a FailurePolicy instance., Run a backend operation under the configured protections. The breaker is…, Absorb or re-raise a failure according to the configured mode. Args: exception:… (+8 more)

### Community 236 - "test_read_config.py"
Cohesion: 0.29
Nodes (17): _assert_default_import_payload(), _assert_string_override_payload(), override_tmp_dir(), fixture, parametrize, Path, scenario_ids, Construct and compose an app config, returning key config/auth values. (+9 more)

### Community 237 - "TestDataLineageMixin"
Cohesion: 0.14
Nodes (10): FieldInfo, Tests for the DataLineageMixin class. DataLineageMixin is a plain mixin (not a…, DataLineageMixin should declare a provenance_id annotation., DataLineageMixin should declare a source_traceback annotation., The provenance_id Field should have a default of None., The source_traceback Field should have a default of None., The source_traceback Field should enforce max_length=255., The provenance_id annotation should allow UUID | None. (+2 more)

### Community 238 - ".get_client"
Cohesion: 0.29
Nodes (4): Any, Retrieve a client by client ID., Check if a client exists and is active., Update client properties.

### Community 239 - "Organization (commondb.organization entity)"
Cohesion: 0.22
Nodes (17): Contact (commondb.organization entity), IdentifierIssuer (commondb.organization entity), Organization (commondb.organization entity), OrganizationIdentifierIssuerLink (commondb.organization entity), Site (commondb.organization entity), User (commondb.organization entity), UserInvitation (commondb.organization entity), commondb / ORGANIZATION — Simplified ERD (+9 more)

### Community 240 - "seq_service_crud_protocol"
Cohesion: 0.18
Nodes (10): ProtocolCrudCommand, Represents a request to perform a CRUD operation on Protocols., Protocol, Handle a CRUD command for protocol entities. Args: cmd: Typed protocol CRUD…, Protocol, UUID, Handle CRUD operations for protocol entities. Args: self: Sequence service…, seq_service_crud_protocol() (+2 more)

### Community 241 - "check_docstrings.py"
Cohesion: 0.09
Nodes (37): audit_file(), check_coverage(), check_exception_classes(), check_package(), check_pydantic(), check_raises(), decorator_name(), has_decorator() (+29 more)

### Community 242 - "get_case_abac_from_command"
Cohesion: 0.08
Nodes (38): CaseCrudCommand, CaseDataCollectionLinkCrudCommand, Represents a request to execute a CRUD operation on Cases., Represents a request to execute a CRUD operation on CaseDataCollection links., case_service_crud_case(), _crud_case_with_abac(), _crud_case_without_abac(), case_service_crud_case_data_collection_link() (+30 more)

### Community 243 - "TestClient"
Cohesion: 0.33
Nodes (5): TestClient, Tests for DELETE_ALL CRUD endpoint., Verify DELETE /model1 deletes all records., Verify DELETE /model1 succeeds even when no records exist., TestDeleteAllEndpoint

### Community 244 - "ThreadRefreshRunner"
Cohesion: 0.33
Nodes (4): Executor, Encapsulates refreshing stale entries on a daemon thread or a supplied…, Initialize a ThreadRefreshRunner instance., ThreadRefreshRunner

### Community 245 - "TestCaseDataCollectionIdHandling"
Cohesion: 0.33
Nodes (4): Batch can contain cases from different DCs., Tests for handling cases with different created_in_data_collection_id values., New case with explicit DC ID should use that DC for ABAC., TestCaseDataCollectionIdHandling

### Community 246 - "`gen_epix.fastapp.cache`"
Cohesion: 0.06
Nodes (34): 10. Observability, 11. Testing, 12. Worked example: local cache in a service, 13.1 What must be replaced, 13.2 A Redis backend, 13.3 A Redis tag index, 13.4 A Redis version store, 13.5 A Redis invalidation bus (+26 more)

### Community 247 - "Organization"
Cohesion: 0.15
Nodes (16): Contact, Contact (omopdb.md), Organization (omopdb.md), OrganizationAdminPolicy (omopdb.md), OrganizationSet (omopdb.md), Site (omopdb.md), User (omopdb.md), UserInvitation (omopdb.md) (+8 more)

### Community 248 - "IdentifierIssuer (omopdb.organization entity)"
Cohesion: 0.12
Nodes (16): ConditionOccurrenceIdentifier (omopdb.omop / OMOP CDM entity), Death (omopdb.omop / OMOP CDM entity), DeathIdentifier (omopdb.omop / OMOP CDM entity), DeviceExposureIdentifier (omopdb.omop / OMOP CDM entity), DrugExposureIdentifier (omopdb.omop / OMOP CDM entity), MeasurementIdentifier (omopdb.omop / OMOP CDM entity), NoteIdentifier (omopdb.omop / OMOP CDM entity), NoteNlp (omopdb.omop / OMOP CDM entity) (+8 more)

### Community 249 - "Organization"
Cohesion: 0.14
Nodes (16): Contact, IdentifierIssuer, Contact (omopdb.organization.md), IdentifierIssuer (omopdb.organization.md), Organization (omopdb.organization.md), OrganizationSetMember (omopdb.organization.md), Site (omopdb.organization.md), User (omopdb.organization.md) (+8 more)

### Community 250 - "UUID"
Cohesion: 0.23
Nodes (9): Any, field_validator, UUID, Normalize the drug concept identifier to UUID form., Normalize dose-era concept identifiers to UUID form., Normalize cohort-definition concept identifiers to UUID form., Normalize episode concept identifiers to UUID form., Normalize the episode-event field concept identifier to UUID form. (+1 more)

### Community 251 - "UserManager"
Cohesion: 0.08
Nodes (25): Any, BaseRbacService, BaseUserManager, User, UUID, Construct a user from claims and configured automatic-user defaults. Args:…, Determine whether identity claims belong to the configured root user. Args:…, Determine whether a user has the configured root role. Args: user: User whose… (+17 more)

### Community 252 - "setup_reference_data"
Cohesion: 0.50
Nodes (3): fixture, Register root1_1 + org1, invite root1_2, and create minimum CaseType…, setup_reference_data()

### Community 253 - "MemoryTagIndex"
Cohesion: 0.07
Nodes (16): MemoryTagIndex, ABC, Forget `key` and remove it from every tag., Remove `tag` and return the keys that carried it., Forget every association., Return the tags currently known to the index., Encapsulates keeping tag associations in process memory. The index holds both…, Initialize a MemoryTagIndex instance. (+8 more)

### Community 254 - "test_logging_runtime_contract.py"
Cohesion: 0.28
Nodes (15): JSONDict, _emit_log_level_resolution_payloads(), _emit_log_level_resolution_payloads_for_both_modes(), _emit_runtime_payloads_for_all_yaml_paths(), _emit_runtime_payloads_via_dictconfig(), _has_message(), _load_class(), parametrize (+7 more)

### Community 255 - "TestGetOneEndpoint"
Cohesion: 0.33
Nodes (4): Tests for GET_ONE CRUD endpoint., Verify GET /model1/{id} returns the correct record., Verify GET /model1/{id} returns 404 when record not found., TestGetOneEndpoint

### Community 256 - "Token"
Cohesion: 0.03
Nodes (69): RequestValidator, FastAPI, ClientStore, OAuth 2.0 Client Store This module manages OAuth 2.0 client registration and…, Delete a client from the store., Deactivate a client (soft delete)., Clear all clients (for testing)., Get the number of stored clients. (+61 more)

### Community 257 - "test/conftest.py"
Cohesion: 0.18
Nodes (14): CallInfo, Config, Item, generate_excel_report(), Any, Session, pytest_collection_modifyitems(), pytest_runtest_makereport() (+6 more)

### Community 258 - "Gen-EpiX Contributor Documentation Index"
Cohesion: 0.14
Nodes (15): Gen-EpiX Contributor Documentation Index, Getting Started, Boot Sequence (AppCfg -> AppComposer -> create_fast_api), Request Lifecycle (endpoint -> app.handle -> policies -> handler), API Surface, Logging (namespaces, command-object summarization), Startup Lifecycle (run.py -> AppCfg -> AppComposer -> create_fast_api), Mutation Testing (pytest-gremlins) (+7 more)

### Community 259 - "Organization"
Cohesion: 0.16
Nodes (15): Contact, Contact (seqdb.md), Organization (seqdb.md), OrganizationAdminPolicy (seqdb.md), OrganizationSetMember (seqdb.md), Site (seqdb.md), User (seqdb.md), UserInvitation (seqdb.md) (+7 more)

### Community 260 - "Sample"
Cohesion: 0.24
Nodes (15): DataCollection, File, IdentifierForUpload, PcrMeasurement (seqdb.seq.md), ReadSet (seqdb.seq.md), Sample (seqdb.seq.md), SampleDataCollectionLink (seqdb.seq.md), PcrMeasurement (+7 more)

### Community 261 - "TestPutOneEndpoint"
Cohesion: 0.33
Nodes (4): Tests for PUT_ONE CRUD endpoint., Verify PUT /model1/{id} updates an existing record., Verify PUT /model1/{id} returns 404 when record not found., TestPutOneEndpoint

### Community 262 - "._make_user_cmd"
Cohesion: 0.08
Nodes (21): Any, User, UUID, Non-read operations should return results unchanged., None user should assert., User without id should assert., APP_ADMIN should receive unmodified results for READ operations., READ_ALL for org admin should include users in admin orgs and admins, including… (+13 more)

### Community 263 - "SAUnitOfWork"
Cohesion: 0.12
Nodes (14): Exception, Self, Session, TracebackType, Enter the managed context., Exit the managed context., Encapsulates a unit of work class wrapping the SQLAlchemy session. The context…, Initialize a SAUnitOfWork instance. (+6 more)

### Community 264 - "_encode_to_int32"
Cohesion: 0.22
Nodes (10): _encode_to_int32(), _hamming_allele_int32_batch(), _hamming_allele_numpy(), _hamming_allele_numpy_batch(), ndarray, Hamming distances from one existing int32 profile to all M new int32 profiles.…, Hamming distance between two (n_loci,) S16 allele arrays. S16 is a no-uint128…, Hamming distances from one existing S16 profile to all M new profiles.… (+2 more)

### Community 265 - "case_service_create_file_for_read_set_or_seq"
Cohesion: 0.04
Nodes (54): CreateFileForReadSetCommand, CreateFileForSeqCommand, Represents a request to upload a raw-reads file for a case read-set column. The…, Represents a request to upload an assembled file for a case sequence column.…, case_service_create_file_for_read_set_or_seq(), _create_file(), _get_cases_for_create_file_for_read_sets_or_seqs(), _get_hash_uuid() (+46 more)

### Community 266 - "TestRead"
Cohesion: 0.13
Nodes (8): scenario_ids, skipif, TestRead, dependency, TestCreate, TestDelete, TestRead, TestUpdate

### Community 268 - "UUID"
Cohesion: 0.09
Nodes (15): Add distance-map profiles no farther than the supplied threshold., Any, SeqDistance, SeqProfile, UUID, Return profile IDs connected by stored distances within the threshold., Yield distance records for a protocol, optionally limited to profile IDs., Yield unique profile IDs that have distance records for a protocol. (+7 more)

### Community 269 - "TestDeleteOneEndpoint"
Cohesion: 0.33
Nodes (4): Tests for DELETE_ONE CRUD endpoint., Verify DELETE /model1/{id} deletes an existing record., Verify DELETE /model1/{id} returns 404 when record not found., TestDeleteOneEndpoint

### Community 270 - "crud_allele.py"
Cohesion: 0.22
Nodes (9): Allele, UUID, Implement seqdb CRUD service operations for services.seq.crud_allele., Handle CRUD operations for allele entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 271 - "retrieve_case_type_stats_profiled"
Cohesion: 0.26
Nodes (13): get_all_case_type_ids(), get_test_client(), get_user_for_test(), fixture, parametrize, User, UUID, Profiled version of retrieve_case_type_stats. (+5 more)

### Community 272 - "TestCommondbMetadataMasking"
Cohesion: 0.17
Nodes (10): DataCollection, fixture, integration, scenario_ids, User, Only APP_ADMIN or ROOT users can see created_at, modified_at, and modified_by,…, Register root1_1 + org1, then invite an org_user and an org_admin., Verifies that commondb does NOT mask metadata fields for any user role. In… (+2 more)

### Community 273 - "ModelNoId"
Cohesion: 0.09
Nodes (15): ModelNoId, UUID, Represents creation and modification metadata to a FastApp domain model. This…, Record the current UTC time and user as the latest modification., Record the current UTC time and user as both creation and modification., Dictionary-backed organization repository configured with OmopDB user models., scenario_ids, Unit tests for ModelNoId.set_modified and ModelNoId.set_created. Test coverage:… (+7 more)

### Community 274 - "TestHttpTimeoutConfiguration"
Cohesion: 0.17
Nodes (7): Test HTTP timeout configuration per command class., DerivedRemoteApp has DEFAULT_HTTP_TIMEOUTS configured., DerivedRemoteApp can be initialized., _create_remote_app applies DEFAULT_HTTP_TIMEOUTS to remote app., Base CommondbRemoteApp has empty DEFAULT_HTTP_TIMEOUTS., Timeout configuration works independently of auth protocol., TestHttpTimeoutConfiguration

### Community 275 - "test_error_code_unicity"
Cohesion: 0.25
Nodes (13): _extract_hex_strings_from_file(), _get_all_seen_codes(), _get_python_files(), _get_repo_root(), _hanlde_duplicate_hex_codes(), _is_long_hex_string(), Path, scenario_ids (+5 more)

### Community 276 - "BaseOmopService"
Cohesion: 0.09
Nodes (21): DomainBaseOmopService, Represents a request to retrieve person IDs based on a query. These IDs can…, RetrievePersonsByQueryCommand, Retrieve persons matching a query. Args: cmd: Command containing person-query…, BaseOmopService, Any, Implementation base that supplies OmopDB runtime metadata to OMOP services., Encapsulates an omopdb service, by providing additional implementation details… (+13 more)

### Community 277 - "._filter_users_by_organization"
Cohesion: 0.18
Nodes (10): Any, BaseAbacService, Command, User, UUID, Filter or reject results according to their direct organization IDs. Args:…, Filter or reject results associated with users in visible organizations. Args:…, Initialize role mappings and the command types supported by each filter. Args:… (+2 more)

### Community 278 - "App (command dispatcher / PEP)"
Cohesion: 0.17
Nodes (13): Command-Based Execution Model, Policy Enforcement Timing (BEFORE/DURING/AFTER), App (command dispatcher / PEP), BaseRbacService, CrudEndpointGenerator, PolicyDecisionPoint, Policy (is_allowed/get_content/filter hooks), RbacPolicy (+5 more)

### Community 279 - "Organization (omopdb.organization entity)"
Cohesion: 0.29
Nodes (13): OrganizationAdminPolicy (omopdb.abac entity), omopdb / ABAC — Simplified ERD, omopdb — Full Database ERD (detailed, 69 entities), omopdb — Full Database ERD (simplified, 69 entities), Contact (omopdb.organization entity), Organization (omopdb.organization entity), OrganizationIdentifierIssuerLink (omopdb.organization entity), Site (omopdb.organization entity) (+5 more)

### Community 280 - "crud_ast_prediction.py"
Cohesion: 0.15
Nodes (13): AstPredictionCrudCommand, Represents a request to perform a CRUD operation on AstPredictions., AstPrediction, UUID, Implement seqdb CRUD service operations for services.seq.crud_ast_prediction., Handle CRUD operations for AST prediction entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 281 - "crud_locus_code_map.py"
Cohesion: 0.15
Nodes (13): LocusCodeMapCrudCommand, Represents a request to perform a CRUD operation on LocusCodeMaps., LocusCodeMap, UUID, Implement seqdb CRUD service operations for services.seq.crud_locus_code_map., Handle CRUD operations for locus-code-map entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 282 - "casedb/domain/command/abac.py"
Cohesion: 0.11
Nodes (19): OrganizationAccessCasePolicyCrudCommand, OrganizationShareCasePolicyCrudCommand, CrudCommand, Define casedb commands for case access and sharing policies., Represent CRUD operations for organization-level case access policies. Policies…, Represent CRUD operations for per-user case access policies. Effective rights…, Represent CRUD operations for organization case-sharing policies. Policies…, Represent CRUD operations for per-user case-sharing policies. User permissions… (+11 more)

### Community 283 - "HandleAuthExceptionMiddleware"
Cohesion: 0.07
Nodes (25): HandleAuthExceptionMiddleware, BaseHTTPMiddleware, Exception, FastAPI, Logger, Request, Response, Middleware that converts authentication errors to HTTP responses. (+17 more)

### Community 284 - "DataIssue"
Cohesion: 0.40
Nodes (4): DataIssue, PydanticBaseModel, Represents a validation or transformation issue for one uploaded value., Get all data issues that are errors.

### Community 286 - "seq/crud_tree_algorithm.py"
Cohesion: 0.20
Nodes (10): TreeAlgorithm, TreeAlgorithmCrudCommand, UUID, Implement seqdb CRUD service operations for services.seq.crud_tree_algorithm., Handle CRUD operations for tree-algorithm entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added (+2 more)

### Community 287 - "TestBulkUpdateSeqDistanceContentSA"
Cohesion: 0.40
Nodes (3): scenario_ids, Verify update_some_seq_distance_content against a real SA_SQLITE database., TestBulkUpdateSeqDistanceContentSA

### Community 288 - "FullSample"
Cohesion: 0.21
Nodes (12): AstMeasurement, FullSample, IdentifierIssuer, AstMeasurement (seqdb.seq.md), ReadSetIdentifier (seqdb.seq.md), SampleIdentifier (seqdb.seq.md), SeqIdentifier (seqdb.seq.md), SeqProfileIdentifier (seqdb.seq.md) (+4 more)

### Community 289 - "JsonFormatter"
Cohesion: 0.41
Nodes (12): casedb Debug Logging Config, casedb Logging Config, commondb Debug Logging Config, JsonFormatter, commondb Logging Config, Log Level Tuning Rationale (sqlalchemy/httpx/asyncio), UvicornAccessLogFilter, omopdb Debug Logging Config (+4 more)

### Community 290 - "crud_sample_data_collection_link.py"
Cohesion: 0.15
Nodes (13): Represents a request to perform a CRUD operation on SampleDataCollectionLinks., SampleDataCollectionLinkCrudCommand, SampleDataCollectionLink, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for sample-data-collection link entities. Args: self:…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 291 - "DependencyDeclaration"
Cohesion: 0.50
Nodes (3): DependencyDeclaration, Encapsulates recording what should be invalidated when one dependency changes.…, Register what a change to `dependency` invalidates. Declarations accumulate, so…

### Community 293 - "MockJWKAndToken"
Cohesion: 0.43
Nodes (3): make_idps_cfg(), Return IDP config list derived from the given mock JWK/token., MockJWKAndToken

### Community 294 - "TestRootTokenTTL"
Cohesion: 0.24
Nodes (3): Verify the root-token time-to-live enforcement. A *very* short TTL (1 second)…, Build an AuthEnv with a pre-stored root user., TestRootTokenTTL

### Community 295 - "OmopdbRemoteApp"
Cohesion: 0.09
Nodes (21): Command, field_validator, UUID, Represents a request to retrieve all data for a list of person IDs, as a list…, Validate that requested person identifiers are unique., Represents a request to retrieve specimen IDs (equivalent to SEQDB sample IDs)…, RetrievePersonsByIdCommand, RetrieveSpecimenIdsByCohortIdsCommand (+13 more)

### Community 296 - "DuplicateIdsError"
Cohesion: 0.50
Nodes (3): DuplicateIdsError, Error for duplicate object identifiers in one operation., Initialize a DuplicateIdsError instance.

### Community 297 - "commondb/api/exc.py"
Cohesion: 0.17
Nodes (21): generate_handle_exception_function(), get_logger_fmap(), _handle_auth_exception(), handle_command(), handle_exception(), _handle_service_exception(), Any, App (+13 more)

### Community 298 - "IdpClient hierarchy"
Cohesion: 0.18
Nodes (12): AuthService (concrete), IdpClient hierarchy, MockIDPClient (no-auth dev/CI), OauthIdpClient (real OIDC), BaseUserManager, Authentication (Identity Resolution Layer), User Resolution (claims -> local User), Add New IDP Configuration (+4 more)

### Community 299 - "Protocol"
Cohesion: 0.20
Nodes (11): AstMeasurement, LocusSet, AstMeasurement (seqdb.md), LocusSet (seqdb.md), PcrMeasurement (seqdb.md), Protocol (seqdb.md), ProtocolSetMember (seqdb.md), PcrMeasurement (+3 more)

### Community 300 - "crud_seq_classification.py"
Cohesion: 0.15
Nodes (13): Represents a request to perform a CRUD operation on SeqClassifications., SeqClassificationCrudCommand, SeqClassification, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for sequence-classification entities. Args: self:…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 301 - "crud_seq_profile_identifier.py"
Cohesion: 0.15
Nodes (13): Represents a request to perform a CRUD operation on SeqProfileIdentifiers., SeqProfileIdentifierCrudCommand, SeqProfileIdentifier, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for sequence-profile identifier entities. Args: self:…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 302 - ".default_isolation_level"
Cohesion: 0.50
Nodes (3): setter, Return the default isolation level for new sessions., Set the default isolation level for new sessions.

### Community 303 - "._validate_state"
Cohesion: 0.50
Nodes (3): model_validator, Self, Compile the configured regular-expression pattern.

### Community 304 - "._validate_ref1_fields"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate that either ref1_id or ref1_code is provided.

### Community 305 - "._validate_int_for_uuid"
Cohesion: 0.38
Nodes (5): Any, field_validator, UUID, Normalize payer-plan-period concept identifiers to UUID form., Normalize cost concept identifiers to UUID form.

### Community 306 - "Transformer Framework"
Cohesion: 0.25
Nodes (11): FallbackTransformer, FieldTransformer, ObjectAdapter, RetryTransformer, Streaming Pipeline Performance Rationale, StreamingPipeline, Transformer, Transformer Framework (+3 more)

### Community 307 - ".get_user"
Cohesion: 0.40
Nodes (4): skip, User, UUID, TestManual

### Community 308 - "rewrite_parametrized_dependency_markers"
Cohesion: 0.33
Nodes (6): pytest_collection_modifyitems(), pytest_collection_modifyitems(), pytest_collection_modifyitems(), pytest_collection_modifyitems(), Rewrite class-level dependency 'depends' markers to include parametrize IDs.…, rewrite_parametrized_dependency_markers()

### Community 309 - "retrieve_complete_case_type.py"
Cohesion: 0.09
Nodes (16): case_service_retrieve_complete_case_type(), Assemble complete case-type metadata filtered by the caller's ABAC access., # TODO: performance improvement, commented out for now to preserve baseline, # TODO: performance improvement, commented out for now to preserve baseline, Assemble case-type metadata and its effective collection access. Columns and…, # TODO: performance improvement, commented out for now to preserve baseline, # TODO: performance improvement, commented out for now to preserve baseline, # TODO: add geo_dim flag if needed (+8 more)

### Community 311 - "command/seq.py"
Cohesion: 0.09
Nodes (32): AlleleCrudCommand, AstMeasurementCrudCommand, LocusCrudCommand, CrudCommand, Define commands for seqdb sequence workflows and managed domain records. The…, Represents a request to perform a CRUD operation on Alleles., Represents a request to perform a CRUD operation on AstMeasurements., Represents a request to perform a CRUD operation on Loci. (+24 more)

### Community 312 - "env"
Cohesion: 0.31
Nodes (5): env(), fixture, FixtureRequest, Return a test client configured for either DICT or SA_SQLITE demo repos. The…, TestRetrieveSamples

### Community 313 - "delete_client"
Cohesion: 0.67
Nodes (3): delete, delete_client(), Delete an OAuth client.

### Community 314 - "LogParser2"
Cohesion: 0.24
Nodes (5): LogParser2, DataFrame, A class to parse and export logsas produced directly by the application or as…, Parses the log file and sorts the user journey logs. This method reads the log…, Exports the sorted user journey logs to a CSV and a pickle file. This method…

### Community 315 - "AppComposer (Composition Root)"
Cohesion: 0.12
Nodes (17): Layer Boundaries principle, System Composition (four FastAPI apps sharing a model), BaseRepository (abstract), BaseService, DictRepository (in-memory backend), SARepository (SQLAlchemy backend), Repository Modes (DICT_DEMO/EMPTY, SA_SQLITE_DEMO/EMPTY, SA_SQL), AppCfg (logger init, settings load, settings validation) (+9 more)

### Community 316 - "Region Set"
Cohesion: 0.22
Nodes (10): Region, RegionSet, Region (doc), Region Relation (doc), Region Set (doc), Region Set Shape (doc), Region, Region Relation (+2 more)

### Community 317 - "Sample"
Cohesion: 0.27
Nodes (10): AstPrediction, AstPrediction (seqdb.md), Sample (seqdb.md), Seq (seqdb.md), SeqClassification (seqdb.md), SeqTaxonomy (seqdb.md), Sample, Seq (+2 more)

### Community 318 - "SeqTaxonomy"
Cohesion: 0.20
Nodes (10): RefSeq (seqdb.seq.md), SeqTaxonomy (seqdb.seq.md), Taxon (seqdb.seq.md), TaxonSet (seqdb.seq.md), TaxonSetMember (seqdb.seq.md), RefSeq, SeqTaxonomy, Taxon (+2 more)

### Community 322 - "TestOIDCProviderIntegration"
Cohesion: 0.12
Nodes (9): Integration tests for OIDCProvider with real JWKSManager., Set up test fixtures., Test complete ID token creation and validation workflow., Test discovery document and JWKS endpoint integration., Test userinfo endpoint with scope-based claim filtering., Test nonce validation integrated with ID token workflow., Test claims extraction integrated with userinfo response., Test logout workflow integration. (+1 more)

### Community 323 - "omop/metadata.py"
Cohesion: 0.20
Nodes (11): CdmSource, Metadata, Any, field_validator, Model, UUID, Metadata domain - OMOP CDM v6.0 metadata tables. This module contains classes…, Normalize metadata concept identifiers to UUID form. (+3 more)

### Community 324 - "renovate.json"
Cohesion: 0.22
Nodes (8): config:best-practices, automerge, baseBranchPatterns, extends, packageRules, prConcurrentLimit, prHourlyLimit, $schema

### Community 325 - "TestUpdate"
Cohesion: 0.11
Nodes (11): scenario_ids, skipif, TestRead, dependency, TestCreate, TestRead, TestUpdate, scenario_ids (+3 more)

### Community 326 - "TestSQLInjection"
Cohesion: 0.31
Nodes (5): get_test_client(), fixture, scenario_ids, Session, TestSQLInjection

### Community 327 - "BaseCommondbRemoteAppTestCase"
Cohesion: 0.10
Nodes (14): BaseCommondbRemoteAppTestCase, scenario_ids, Test OAuth2 configuration validation during initialization., Raise error when OAuth2 requires discovery URL., Raise error when OAuth2 requires client ID., Raise error when OAuth2 requires scope., Raise error for OIDC auth protocol (not yet supported)., Test create_local_or_remote_app class method. (+6 more)

### Community 328 - "TestAnonymizeUser"
Cohesion: 0.18
Nodes (7): scenario_ids, Include each user ID so forgotten users in one organization remain unique., Verify anonymization of the target user., Set up test fixtures., Anonymize personal fields and deactivate the anonymized user., Anonymize personal fields and deactivate the anonymized user., TestAnonymizeUser

### Community 329 - "generate_seqdb_models.py"
Cohesion: 0.33
Nodes (9): build_random_nextclade_fields(), generate_demo_seqdb_models(), _generate_snp_objects(), Any, Random, Sample, UUID, Generate demo seqdb models. When snp_seq_length > 0, SNP-specific reference… (+1 more)

### Community 330 - "TestOIDCProvider"
Cohesion: 0.03
Nodes (38): Test discovery document includes correct supported claims., Test discovery document includes correct authentication methods., Test discovery document includes correct signing algorithms., Test discovery document includes additional OIDC features., Test creating a basic ID token., Test creating ID token with nonce., Test creating ID token with explicit auth_time., Test creating ID token with additional claims. (+30 more)

### Community 331 - "Concept Relation"
Cohesion: 0.28
Nodes (9): Concept, Concept Relation, Concept Set, Concept (doc), Concept Relation (doc), Concept, ConceptSet, Concept (doc concept) (+1 more)

### Community 332 - "Outage (commondb.system entity)"
Cohesion: 0.25
Nodes (9): Outage (commondb.system entity), commondb / SYSTEM — Simplified ERD, IdentityProvider (omopdb.auth entity), IDPUser (omopdb.auth entity), omopdb / AUTH — Simplified ERD, IdentityProvider (seqdb.auth entity), IDPUser (seqdb.auth entity), seqdb / AUTH — Simplified ERD (+1 more)

### Community 333 - "Protocol"
Cohesion: 0.28
Nodes (9): Protocol (seqdb.seq.md), ProtocolSetMember (seqdb.seq.md), SeqDistance (seqdb.seq.md), SeqProfile (seqdb.seq.md), Protocol, ProtocolSet, ProtocolSetMember, SeqDistance (+1 more)

### Community 334 - "3.8 Comments and Docstrings"
Cohesion: 0.13
Nodes (13): Audit Script, Preferred Structure, Procedure, Write Python Docstrings, 3.8.1 Docstrings, 3.8.2.1 Test modules, 3.8.2 Modules, 3.8.3.1 Overridden Methods (+5 more)

### Community 335 - "calculate_phylogenetic_tree.py"
Cohesion: 0.10
Nodes (24): ClusterNode, _correct_nj_tree_negative_branch_lengths_recursion(), _get_newick_repr_recursion(), Any, PhylogeneticTree, Implement seqdb sequence service behavior for…, # TODO: this should be parameterised, so that such higher, # TODO: convert condensed distance matrix directly to lower triangle (+16 more)

### Community 336 - "crud_ast_measurement.py"
Cohesion: 0.22
Nodes (9): AstMeasurement, UUID, Implement seqdb CRUD service operations for services.seq.crud_ast_measurement., Handle CRUD operations for AST measurement entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 337 - "IdsError"
Cohesion: 0.17
Nodes (13): __extract_invalid_ids(), _handle_invalid_ids_exception(), log_and_raise_invalid_ids_exception(), Hashable, Translate an ID exception into a validation or conflict HTTP response. Args:…, Log invalid IDs and raise an HTTP response with their public details. Args:…, Return request IDs that are also reported by an ID exception. Args: exception:…, AlreadyExistingIdsError (+5 more)

### Community 338 - "BaseSeqService"
Cohesion: 0.02
Nodes (76): BaseSeqService, Allele, AstMeasurement, AstPrediction, Locus, LocusCodeMap, LocusSet, PcrMeasurement (+68 more)

### Community 339 - "crud_locus.py"
Cohesion: 0.22
Nodes (9): Locus, UUID, Implement seqdb CRUD service operations for services.seq.crud_locus., Handle CRUD operations for locus entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 340 - "crud_locus_set.py"
Cohesion: 0.15
Nodes (13): LocusSetCrudCommand, Represents a request to perform a CRUD operation on LocusSets., LocusSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_locus_set., Handle CRUD operations for locus-set entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 341 - "crud_pcr_measurement.py"
Cohesion: 0.15
Nodes (13): PcrMeasurementCrudCommand, Represents a request to perform a CRUD operation on PcrMeasurements., PcrMeasurement, UUID, Implement seqdb CRUD service operations for services.seq.crud_pcr_measurement., Handle CRUD operations for PCR measurement entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 342 - "services/seq/upload.py"
Cohesion: 0.10
Nodes (14): Re-export concrete seqdb sequence service types., Delegate a sample-upload command to the upload operation., Implement seqdb sequence service behavior for services.seq.upload., See command.UploadSamplesCommand for details., Encapsulates validation and persistence of seqdb sample upload batches., Configure upload processing for seqdb stored model fields., Verify that the command user may upload the supplied sample batch. Args: cmd:…, # TODO: Implement ABAC rights retrieval when policies are available (+6 more)

### Community 343 - "crud_protocol_set_member.py"
Cohesion: 0.15
Nodes (13): ProtocolSetMemberCrudCommand, Represents a request to perform a CRUD operation on ProtocolSetMembers., ProtocolSetMember, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for protocol-set membership entities. Args: self:…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 344 - "crud_ref_seq.py"
Cohesion: 0.12
Nodes (15): Represents a request to perform a CRUD operation on RefSeqs., RefSeqCrudCommand, RefSeq, Handle a CRUD command for reference-sequence entities. Args: cmd: Typed…, RefSeq, UUID, Implement seqdb CRUD service operations for services.seq.crud_ref_seq., Handle CRUD operations for reference-sequence entities. Args: self: Sequence… (+7 more)

### Community 347 - "seq/service.py"
Cohesion: 0.05
Nodes (45): Represents a request to perform a CRUD operation on Seqs., SeqCrudCommand, ReadSetIdentifier, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for read-set identifier entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+37 more)

### Community 348 - "crud_seq_category.py"
Cohesion: 0.15
Nodes (13): Represents a request to perform a CRUD operation on SeqCategories., SeqCategoryCrudCommand, SeqCategory, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_category., Handle CRUD operations for sequence-category entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 349 - "crud_seq_category_set.py"
Cohesion: 0.12
Nodes (15): Represents a request to perform a CRUD operation on SeqCategorySets., SeqCategorySetCrudCommand, SeqCategorySet, Handle a CRUD command for sequence-category-set entities. Args: cmd: Typed…, SeqCategorySet, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_category_set., Handle CRUD operations for sequence-category-set entities. Args: self: Sequence… (+7 more)

### Community 350 - "crud_seq_distance.py"
Cohesion: 0.22
Nodes (9): SeqDistance, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_distance., Handle CRUD operations for sequence-distance entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 351 - "crud_seq_taxonomy.py"
Cohesion: 0.15
Nodes (13): Represents a request to perform a CRUD operation on SeqTaxonomies., SeqTaxonomyCrudCommand, SeqTaxonomy, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_taxonomy., Handle CRUD operations for sequence-taxonomy entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 352 - "crud_taxon.py"
Cohesion: 0.15
Nodes (13): Represents a request to perform a CRUD operation on Taxa., TaxonCrudCommand, Taxon, UUID, Implement seqdb CRUD service operations for services.seq.crud_taxon., Handle CRUD operations for taxon entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+5 more)

### Community 353 - "crud_taxon_set.py"
Cohesion: 0.12
Nodes (15): Represents a request to perform a CRUD operation on TaxonSets., TaxonSetCrudCommand, TaxonSet, Handle a CRUD command for taxon-set entities. Args: cmd: Typed taxon-set CRUD…, TaxonSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_taxon_set., Handle CRUD operations for taxon-set entities. Args: self: Sequence service… (+7 more)

### Community 354 - "crud_taxon_set_member.py"
Cohesion: 0.22
Nodes (9): TaxonSetMember, UUID, Implement seqdb CRUD service operations for services.seq.crud_taxon_set_member., Handle CRUD operations for taxon-set membership entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 356 - "TestVerifyUserRights"
Cohesion: 0.21
Nodes (7): _mock_uow(), Role, User, Map commondb role enums to casedb role strings with CASEDB_ prefix., Tests for RBAC verification in CaseBatchUploader.verify_user_rights., TestVerifyUserRights, _to_casedb_role_set()

### Community 357 - "TestDelete"
Cohesion: 0.25
Nodes (5): scenario_ids, skipif, RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…, TestDelete, TestDelete

### Community 359 - "test_logging_yaml.py"
Cohesion: 0.47
Nodes (8): parametrize, Path, scenario_ids, Contract tests for all production logging.yaml configuration files. These tests…, test_console_handler_uses_json_formatter(), test_root_logger_is_present_and_uses_console_handler(), test_third_party_loggers_explicitly_configured(), test_uvicorn_access_has_structured_filter()

### Community 360 - "TestDelete"
Cohesion: 0.11
Nodes (12): scenario_ids, skipif, RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…, TestDelete, scenario_ids, skipif, TestRead, dependency (+4 more)

### Community 362 - "omopdb/api/router.py"
Cohesion: 0.06
Nodes (36): Expose OmopDB API request schemas used by shared router composition. The facade…, create_omop_endpoints(), Any, APIRouter, App, Exception, FastAPI, NoReturn (+28 more)

### Community 363 - "TestUpdate"
Cohesion: 0.08
Nodes (15): scenario_ids, skipif, RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…, TestDelete, scenario_ids, skipif, TestRead, dependency (+7 more)

### Community 369 - "AuthorizationCodeStore"
Cohesion: 0.18
Nodes (6): AuthorizationCode, AuthorizationCodeStore, datetime, Authorization Code Store In-memory storage for OAuth 2.0 Authorization Codes…, Representation of an OAuth 2.0 authorization code., In-memory store managing authorization codes.

### Community 371 - "Contact (doc)"
Cohesion: 0.32
Nodes (8): Contact, Contact (doc), Site (doc), Contact, Site, Site, Contact, Site

### Community 372 - "seqdb Overview ERD"
Cohesion: 0.25
Nodes (8): seqdb Overview ERD, seqdb FILE Service ERD, seqdb ORGANIZATION Service ERD (Detailed), seqdb ORGANIZATION Service ERD (Simplified), seqdb SEQ Service ERD (Detailed), seqdb SEQ Service ERD (Simplified), seqdb SYSTEM Service ERD (Detailed), seqdb SYSTEM Service ERD (Simplified)

### Community 373 - "IdentifierIssuer"
Cohesion: 0.25
Nodes (8): IdentifierIssuer, IdentifierIssuer (seqdb.md), OrganizationIdentifierIssuerLink (seqdb.md), SampleIdentifier (seqdb.md), SeqIdentifier (seqdb.md), OrganizationIdentifierIssuerLink, SampleIdentifier, SeqIdentifier

### Community 374 - "Taxon"
Cohesion: 0.25
Nodes (8): RefSeq (seqdb.md), Taxon (seqdb.md), TaxonSet (seqdb.md), TaxonSetMember (seqdb.md), RefSeq, Taxon, TaxonSet, TaxonSetMember

### Community 375 - "Locus"
Cohesion: 0.25
Nodes (8): Allele, AlleleForUpload, Locus, Allele (seqdb.seq.md), Locus (seqdb.seq.md), RefAllele (seqdb.seq.md), RefAllele, SampleBatchForUpload

### Community 379 - "EngineFactory"
Cohesion: 0.22
Nodes (6): EngineFactory, Engine, Thread-safe SQLAlchemy engine factory., Encapsulates creation and management of SQLAlchemy engines., Initialize a EngineFactory instance., Create a new SQLAlchemy engine or return an existing one for the given…

### Community 380 - ".__init__"
Cohesion: 0.25
Nodes (7): OrganizationDictRepository, Any, CommonOrganizationDictRepository, Hashable, Model, Encapsulates shared organization persistence with OmopDB user model types., Initialize shared organization storage with OmopDB model classes.

### Community 381 - ".__init__"
Cohesion: 0.20
Nodes (8): OrganizationDictRepository, Any, CommonOrganizationDictRepository, Hashable, Model, Provide seqdb persistence behavior for repositories.organization_dict., Encapsulates seqdb persistence behavior for organization dictionaries., Initialize the repository with seqdb user and invitation model types. Args:…

### Community 383 - "KeyedMutex"
Cohesion: 0.16
Nodes (9): KeyedMutex, Acquire the mutex belonging to `key`. Args: key: The cache key being…, Release the mutex belonging to `key`. Args: key: The key whose mutex is held.…, Return whether a regeneration is in progress for `key`., Decrement the user count of `key` and forget an unused mutex., Encapsulates handing out one mutex per key and discarding it when unused.…, Initialize a KeyedMutex instance., A per-key lock registry must not grow with the key space. (+1 more)

### Community 388 - ".get_mapped_class"
Cohesion: 0.29
Nodes (6): CommandType, Command, Model, Return a mapped implementation class or the supplied supported base class.…, ModelType, PolicyType

### Community 389 - "Entity descriptor"
Cohesion: 0.29
Nodes (7): Domain (registry), Entity descriptor, Key (unique constraint), Link (foreign key descriptor), Domain Registration (register_domain_entities), casedb ABAC Simplified ERD, casedb ABAC Detailed ERD

### Community 390 - "Specimen"
Cohesion: 0.29
Nodes (7): Specimen (omopdb.md), SpecimenIdentifier (omopdb.md), Specimen (omopdb.omop.md), Specimen, SpecimenIdentifier, Specimen, SpecimenIdentifier

### Community 391 - "DataCollection"
Cohesion: 0.33
Nodes (7): DataCollection, DataCollectionSet, DataCollectionSetMember, DataCollection (seqdb.md), DataCollectionSetMember (seqdb.md), SampleDataCollectionLink (seqdb.md), SampleDataCollectionLink

### Community 392 - "Seq"
Cohesion: 0.29
Nodes (7): AstPrediction, Contig, AstPrediction (seqdb.seq.md), Seq (seqdb.seq.md), SeqClassification (seqdb.seq.md), Seq, SeqClassification

### Community 394 - "JIRA Issues"
Cohesion: 0.17
Nodes (12): Assigning Issues, Comments and Worklogs, Common Fields, Extended Capabilities, JIRA Issues, Prerequisite: Resolve `cloudId`, Repository Context, Safety Rules (+4 more)

### Community 396 - "._validate_content"
Cohesion: 0.29
Nodes (5): model_validator, Self, UUID, Validate the profile-distance-map content and reset its unused hash., Decode the stored JSON profile-distance map. Returns: Distances keyed by…

### Community 397 - "AuthException"
Cohesion: 0.15
Nodes (12): AuthException, CredentialsAuthError, Base error for authentication and authorization failures., HTTP 401 error for credentials that cannot be validated., HTTP 403 error for credentials without the required authorization., HTTP 404 error for an identity with no application user., HTTP 409 error for an identity that already has an application user., HTTP 429 error for an authentication request that exceeds its limit. (+4 more)

### Community 399 - "set_service_repository"
Cohesion: 0.22
Nodes (10): _build_snp_upload_command(), _build_upload_command(), Any, parametrize, RepositoryType, UUID, Given a created dict dataset, build a UploadSamplesCommand. db_index selects…, Build an UploadSamplesCommand for SNP profiles using the SNP protocol from the… (+2 more)

### Community 400 - "Subject"
Cohesion: 0.40
Nodes (6): DataCollection, IdentifierIssuer, Subject (doc concept), SubjectIdentifier (doc concept), Subject, SubjectIdentifier

### Community 401 - "MeasurementRelation"
Cohesion: 0.40
Nodes (6): MeasurementRelation (omopdb.md), MeasurementRelationIdentifier (omopdb.md), MeasurementRelation, MeasurementRelationIdentifier, MeasurementRelation, MeasurementRelationIdentifier

### Community 402 - "ObservationPeriod"
Cohesion: 0.40
Nodes (6): ObservationPeriod (omopdb.md), ObservationPeriodIdentifier (omopdb.md), ObservationPeriod, ObservationPeriodIdentifier, ObservationPeriod, ObservationPeriodIdentifier

### Community 403 - "ProcedureOccurrence"
Cohesion: 0.40
Nodes (6): ProcedureOccurrence (omopdb.md), ProcedureOccurrenceIdentifier (omopdb.md), ProcedureOccurrence, ProcedureOccurrenceIdentifier, ProcedureOccurrence, ProcedureOccurrenceIdentifier

### Community 404 - "Locus"
Cohesion: 0.33
Nodes (6): Allele, Locus, Allele (seqdb.md), Locus (seqdb.md), RefAllele (seqdb.md), RefAllele

### Community 405 - "ReadSet"
Cohesion: 0.33
Nodes (6): File, File (seqdb.md), ReadSet (seqdb.md), ReadSetIdentifier (seqdb.md), ReadSet, ReadSetIdentifier

### Community 406 - "SeqProfile"
Cohesion: 0.33
Nodes (6): SeqDistance (seqdb.md), SeqProfile (seqdb.md), SeqProfileIdentifier (seqdb.md), SeqDistance, SeqProfile, SeqProfileIdentifier

### Community 407 - "EtlLogItem"
Cohesion: 0.53
Nodes (6): CalculateSeqDistancesResult, EtlLogItem, SampleBatchUploadResult, SampleDataIssue, SampleUploadResult, UploadResult

### Community 408 - "UUID"
Cohesion: 0.22
Nodes (5): UUID, Move cases to a different creating data collection over HTTP., Create a file associated with a read set column., Create a file associated with a sequence column., Check whether the user owns each of the given cases.

### Community 409 - "._validate_model"
Cohesion: 0.40
Nodes (4): model_validator, Self, Derive or validate the deterministic identifier UUID., Require an issuer UUID or code.

### Community 410 - ".create_unique_values_temp_table"
Cohesion: 0.33
Nodes (5): MetaData, TypeEngine, UUID, Create an SQL temp table with a single columns with unique values. This can be…, Table

### Community 411 - "._serialize_seq_format"
Cohesion: 0.25
Nodes (5): FormatType, field_serializer, Serialize the format enum to its integer value., Serialize the quality result as its stable integer representation., Serialize the seq_format enum to its integer value.

### Community 412 - "IsOrganizationAdminPolicy"
Cohesion: 0.29
Nodes (6): IsOrganizationAdminPolicy, Any, BaseAbacService, CommonIsOrganizationAdminPolicy, Encapsulates organization-administrator checks using the OmopDB role map., Initialize the policy with OmopDB users and role mappings.

### Community 413 - "omopdb/policies/read_user_policy.py"
Cohesion: 0.22
Nodes (7): Any, BaseAbacService, CommonReadUserPolicy, Configure shared user-read policy behavior for OmopDB roles and commands., Encapsulates shared user-read checks with OmopDB role and command mappings., Initialize the user-read policy with OmopDB dependencies., ReadUserPolicy

### Community 414 - "IsOrganizationAdminPolicy"
Cohesion: 0.29
Nodes (6): IsOrganizationAdminPolicy, Any, BaseAbacService, CommonIsOrganizationAdminPolicy, Encapsulates organization-admin checks using seqdb roles and user models., Configure the shared policy with seqdb role and user mappings.

### Community 415 - "ReadUserPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadUserPolicy, Encapsulates authorizing user reads with seqdb roles and organization-admin…, Configure the shared policy with seqdb authorization dependencies., ReadUserPolicy

### Community 417 - "OrganizationSARepository"
Cohesion: 0.29
Nodes (6): OrganizationSARepository, Any, CommonOrganizationSARepository, Engine, Encapsulates seqdb persistence behavior for SQL-based organization repositories., Initialize the repository with seqdb SQLAlchemy model types. Args: engine:…

### Community 419 - "OAuth Client Credential Flow Test"
Cohesion: 0.53
Nodes (6): OAuth Client Credential Flow Test, OAuthServerManager, ReceiverApp, ReceiverAppCLI, ReceiverAppManager, RequestorApp

### Community 420 - "TestCaseTypeProps"
Cohesion: 0.17
Nodes (3): parametrize, scenario_ids, TestCaseTypeProps

### Community 421 - "init-db one-shot database creation service"
Cohesion: 0.50
Nodes (5): casedb service (SA_SQL mode, embedded LOCAL seqdb), init-db one-shot database creation service, lsp_sql SQL Server service, omopdb service (SA_SQL mode), seqdb service (SA_SQL mode)

### Community 422 - "DataCollection (commondb.organization entity)"
Cohesion: 0.50
Nodes (5): DataCollection (commondb.organization entity), DataCollection (omopdb.organization entity), DataCollection (seqdb entity), DataCollectionSetMember (seqdb entity), SampleDataCollectionLink (seqdb entity)

### Community 423 - "DataCollectionSetMember"
Cohesion: 0.50
Nodes (5): DataCollection, DataCollectionSet, DataCollectionSetMember, DataCollection (omopdb.md), DataCollectionSetMember (omopdb.md)

### Community 424 - "DataCollectionSetMember"
Cohesion: 0.50
Nodes (5): DataCollection, DataCollectionSet, DataCollectionSetMember, DataCollection (omopdb.organization.md), DataCollectionSetMember (omopdb.organization.md)

### Community 425 - "TreeAlgorithm"
Cohesion: 0.40
Nodes (5): TreeAlgorithm (seqdb.seq.md), TreeAlgorithmClass (seqdb.seq.md), PhylogeneticTree, TreeAlgorithm, TreeAlgorithmClass

### Community 427 - "BrokenBackend"
Cohesion: 0.14
Nodes (8): BrokenBackend, Backend that fails every operation, to exercise the failure policy., Fail instead of reading. Args: key: The requested key. Returns: Never returns.…, A broken cache must cost throughput, not availability., Fail instead of writing. Args: key: The key to write. value: The envelope to…, Fail instead of deleting. Args: key: The key to remove. Raises:…, Fail instead of clearing. Raises: CacheBackendError: Always., test_a_backend_failure_degrades_to_the_loader()

### Community 429 - "pr.sh"
Cohesion: 0.38
Nodes (10): branch_title(), first_plan_line(), generated_body(), plan_file_for_ticket(), print_ready_command(), require_command(), pr.sh script, ticket_id_from_branch() (+2 more)

### Community 430 - "casedb/services/organization.py"
Cohesion: 0.25
Nodes (6): OrganizationService, Any, CommonOrganizationService, Configure organization services with casedb-specific user models., Encapsulates organization operations using casedb user model types., Initialize organization handling with casedb model specializations. Args:…

### Community 431 - "Issue Templates"
Cohesion: 0.20
Nodes (6): Bug Report Template, Comment Template, Feature Request / Story Template, Issue Templates, Minimal Template, Task Template

### Community 433 - "Any"
Cohesion: 0.17
Nodes (9): Any, BaseModel, Hashable, Return the non-inverted pass-through result., Yield a pass-through match for every column value., Yield every column value when the filter is not inverted., Return the pass-through result for a row., Yield pass-through matches for rows when not inverted. (+1 more)

### Community 434 - "._validate_content"
Cohesion: 0.32
Nodes (5): model_validator, Self, Reserve post-validation for future content-hash verification., Reserve post-validation for future content-hash verification., Reserve post-validation for future content-hash verification.

### Community 435 - "seqdb/services/organization.py"
Cohesion: 0.25
Nodes (6): OrganizationService, Any, CommonOrganizationService, Implement seqdb application service behavior for services.organization., Encapsulates seqdb organization service behavior., Initialize organization operations with seqdb invitation constraints. Args:…

### Community 436 - "release-please-config.json"
Cohesion: 0.40
Nodes (4): include-component-in-tag, packages, pull-request-title-pattern, $schema

### Community 438 - "casedb/domain/service/__init__.py"
Cohesion: 0.06
Nodes (32): Command, Represent a request for regions containing specified regions., RetrieveContainingRegionCommand, Identify services available within the casedb application., ServiceType, BaseAbacService, CommonAbacService, Encapsulates Casedb access resolution and command scope metadata. The command… (+24 more)

### Community 439 - "field_validator"
Cohesion: 0.18
Nodes (6): field_validator, Normalize a supplied user key to lower case., Normalize role input to a set., Convert an empty invitation user key to an omitted key., Normalize invitation role input to a set., Strip leading and trailing whitespace from an external identifier.

### Community 440 - "test_debug_console_uses_json_formatter"
Cohesion: 0.40
Nodes (4): parametrize, Path, scenario_ids, test_debug_console_uses_json_formatter()

### Community 442 - "DummyLogItem"
Cohesion: 0.40
Nodes (3): DummyLogItem, Any, Minimal log item stub compatible with MockIDPClient usage.

### Community 443 - "App.handle() command dispatch"
Cohesion: 0.83
Nodes (4): App.handle() command dispatch, Command-centric authorization, BEFORE/DURING/AFTER policy phases, API functions as transport adapters

### Community 445 - "NoteNlp"
Cohesion: 0.50
Nodes (4): NoteNlp (omopdb.omop.md), NoteNlpIdentifier (omopdb.omop.md), NoteNlp, NoteNlpIdentifier

### Community 446 - "TreeAlgorithm"
Cohesion: 0.50
Nodes (4): TreeAlgorithm (seqdb.md), TreeAlgorithmClass (seqdb.md), TreeAlgorithm, TreeAlgorithmClass

### Community 447 - "SeqClassificationForUpload"
Cohesion: 0.67
Nodes (4): SeqCategory (seqdb.seq.md), SeqCategory, SeqCategorySet, SeqClassificationForUpload

### Community 448 - "._validate_state"
Cohesion: 0.40
Nodes (4): model_validator, Self, Ensure every supplied case belongs to the command's case type., Remove the creating data collection from additional associations.

### Community 451 - ".organization_identifier_issuer_link_update_association"
Cohesion: 0.50
Nodes (3): OrganizationIdentifierIssuerLink, Update identifier issuer links for an organization., OrganizationIdentifierIssuerUpdateAssociationCommand

### Community 452 - "test/enum.py"
Cohesion: 0.38
Nodes (6): Enum, Define test-specific enum values for test type and repository backend selection., Encapsulates the persistence backend used by commondb test configurations., Encapsulates classification of the execution category of a commondb test., RepositoryType, TestType

### Community 453 - "._validate_some_criteria"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate that at least some criteria are provided, to avoid accidentally…

### Community 454 - "._validate_content"
Cohesion: 0.40
Nodes (4): model_validator, Self, Reserve post-validation for future content-hash verification., Reserve post-validation for future content-hash verification.

### Community 455 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, Hashable, Configure the field and callable used for in-place field updates.

### Community 456 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, Hashable, Configure per-field transformation callables.

### Community 458 - "MermaidErmGenerator"
Cohesion: 0.36
Nodes (7): MermaidErmGenerator, Domain, Path, Write a Markdown file wrapping a Mermaid diagram., Generates Mermaid ``erDiagram`` markdown files from domain model definitions.…, Generate Mermaid ERD markdown files into *dir*., _write_md()

### Community 460 - "_PytestMockConfig"
Cohesion: 0.50
Nodes (3): Any, _PytestMockConfig, Minimal config shim needed by pytest-mock's backend resolver.

### Community 461 - "Links, Subtasks, and Dependencies"
Cohesion: 0.25
Nodes (8): Common link types, Direction, Epics and parents, Issue links, Links, Subtasks, and Dependencies, Reading links, Remote links, Subtasks

### Community 463 - "Default App Ports (8000/8001/8002/8010)"
Cohesion: 0.67
Nodes (3): Default App Ports (8000/8001/8002/8010), run.py quickstart command (app_type/idp_mode/repo_mode), api subcommand group (api, api_platform_local_mock_*)

### Community 464 - "CohortDefinition (omopdb.md)"
Cohesion: 0.67
Nodes (3): CohortDefinition, CohortDefinition (omopdb.md), CohortDefinition

### Community 465 - "Organization"
Cohesion: 1.00
Nodes (3): Organization, OrganizationAdminPolicy, User

### Community 466 - "Locus (seqdb entity)"
Cohesion: 0.67
Nodes (3): Allele (seqdb entity), Locus (seqdb entity), RefAllele (seqdb entity)

### Community 467 - "SeqCategory"
Cohesion: 1.00
Nodes (3): SeqCategory (seqdb.md), SeqCategory, SeqCategorySet

### Community 468 - "Locus"
Cohesion: 0.67
Nodes (3): Allele, Locus, RefAllele

### Community 471 - "crud_read_set.py"
Cohesion: 0.22
Nodes (9): ReadSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_read_set., Handle CRUD operations for read-set entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 477 - "CasedbRemoteApp"
Cohesion: 0.09
Nodes (12): CasedbRemoteApp, Protocol, Retrieve cohort links for a given case type., Retrieve cases matching the given query., Encapsulates remote casedb command dispatch over HTTP. Initialization first…, Retrieve the full definition of a case type., Retrieve statistics per case type., Retrieve statistics per case set. (+4 more)

### Community 484 - "crud_sample.py"
Cohesion: 0.22
Nodes (9): Sample, UUID, Implement seqdb CRUD service operations for services.seq.crud_sample., Handle CRUD operations for sample entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 485 - "._validate_some_criteria"
Cohesion: 0.50
Nodes (3): model_validator, Self, Require at least one last-modified datetime boundary.

### Community 486 - "._validate_state"
Cohesion: 0.50
Nodes (3): model_validator, Self, Ensure tree leaf names and profile identifiers are consistent.

### Community 517 - "crud_seq_identifier.py"
Cohesion: 0.22
Nodes (9): SeqIdentifier, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_identifier., Handle CRUD operations for sequence-identifier entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 521 - "RegionRelationType"
Cohesion: 0.22
Nodes (8): Identify spatial relationships between geographic regions., RegionRelationType, field_serializer, field_validator, Represents a directed geographic relation between two regions., Normalize a string relation value to its enum member., Serialize the relation type as its string value., RegionRelation

### Community 525 - "field_validator"
Cohesion: 0.15
Nodes (8): field_serializer, field_validator, UUID, Normalize an NCBI taxon identifier, accepting its standard prefix., Normalize JSON or prefixed NCBI ancestor identifiers to integers., Normalize a JSON ancestor identifier list to UUID objects., Normalize a taxon rank, accepting spaced NCBI rank names., Serialize ancestor taxon identifiers as strings.

### Community 532 - "Fields, Issue Types, and Transitions"
Cohesion: 0.22
Nodes (9): Clearing and replacing, Discovering fields, Discovering projects and issue types, Field shapes, Fields, Issue Types, and Transitions, Releases instead of milestones, Setting fields, Transition rules (+1 more)

### Community 534 - "SeqdbService"
Cohesion: 0.09
Nodes (18): Any, App, CrudCommand, PhylogeneticTree, Seq, UUID, Retrieve sequence objects from seqdb by ID., Return seqdb's FASTA iterator for the requested sequence IDs. Args: cmd: Casedb… (+10 more)

### Community 535 - ".get_root_user"
Cohesion: 0.17
Nodes (6): Print all organisations to stdout., Print all data collections to stdout., Print all users with their organisations and roles to stdout., Retrieve all users via the app as the root user., Retrieve all users that have the given role., Retrieve the root user from the app's user manager.

### Community 536 - "seq_service_calculate_seq_distances_for_new_profiles"
Cohesion: 0.30
Nodes (8): Calculate and persist distances for newly supplied sequence profiles. For each…, seq_service_calculate_seq_distances_for_new_profiles(), _make_nextclade_content(), _make_seq_distance_protocol_for_snp(), _make_snp_profile_for_upload(), Helper: compute SNP distance between two profiles via the service., Identical profiles are zero-distance and Nextclade states mismatch., TestCalculateSeqDistancesForNewProfiles

### Community 538 - "UpdateResponseHeaderMiddleware"
Cohesion: 0.18
Nodes (9): BaseHTTPMiddleware, FastAPI, Request, Response, Middleware that adds configured and version response headers., Encapsulates adding general or endpoint-specific headers to API responses., Initialize a UpdateResponseHeaderMiddleware instance., Process a request and add the configured response headers. (+1 more)

### Community 540 - "._validate_int_for_uuid"
Cohesion: 0.33
Nodes (6): Any, field_validator, UUID, Normalize the place-of-service concept identifier to UUID form., Normalize provider concept identifiers to UUID form., Normalize the country concept identifier to UUID form.

### Community 542 - "BatchEtlResult"
Cohesion: 0.02
Nodes (78): deprecated, BatchEtlResult, EtlLogItem, EtlResult, ExtractResult, JobEtlResult, LoadResult, Any (+70 more)

### Community 543 - "Implement JIRA Issue"
Cohesion: 0.25
Nodes (7): 1. Retrieve and Assess the Issue, 2. Create the Work Branch, 3. Establish the Test Baseline, 4. Implement Incrementally, 5. Final Validation and Delivery, Implement JIRA Issue, Safety Rules

### Community 548 - "Logger"
Cohesion: 0.22
Nodes (5): Logger, Logger used during application setup., Logger for API layer messages., Logger for application layer messages., Logger for service layer messages.

### Community 555 - "ReadSelfResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadSelfResultsOnlyPolicy, Filter casedb user case-policy reads to the current user's records., Register ownership attributes for casedb user case-policy commands. Args:…, ReadSelfResultsOnlyPolicy

### Community 560 - "seqdb_server"
Cohesion: 0.08
Nodes (25): create_root_user_from_claims(), get_existing_root_user(), App, Dynaconf, User, Retrieve the configured root user from an initialized application. Args: cfg:…, Create the configured root user through the application's claim workflow. Args:…, Path (+17 more)

### Community 562 - "._custom_json_encoder"
Cohesion: 0.29
Nodes (4): Any, Initialize a BaseLogItem instance., Serialize exceptions, datetimes, and other unsupported objects as strings., Initialize a LogItem instance.

### Community 563 - "ReadSelfResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadSelfResultsOnlyPolicy, Encapsulates restrictions on shared self-result reads according to OmopDB…, Initialize self-scoped command metadata for OmopDB., ReadSelfResultsOnlyPolicy

### Community 564 - "ReadSelfResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadSelfResultsOnlyPolicy, Encapsulates restricting eligible result reads to resources owned by the caller., Initialize the shared policy with seqdb identifier-attribute mappings., ReadSelfResultsOnlyPolicy

### Community 626 - "JQL Search"
Cohesion: 0.33
Nodes (6): Calling the tool, Common queries, JQL Search, Operators, Universal search, Values and quoting

### Community 629 - "Creating Issues"
Cohesion: 0.33
Nodes (6): Content format, Creating Issues, Description structure, Issue types, Optional parameters, Summary guidelines

### Community 630 - "Pytest Run (capture once, inspect many times)"
Cohesion: 0.33
Nodes (5): Method, Notes, Pytest Run (capture once, inspect many times), When NOT to use (rerun for real), When to use

### Community 632 - "case_service_crud_case_type_set_member"
Cohesion: 0.23
Nodes (12): CaseTypeSetMemberCrudCommand, Represents a request to execute a CRUD operation on CaseTypeSetMembers., case_service_crud_case_type_set_member(), _crud_case_type_set_member_with_abac(), _crud_case_type_set_member_without_abac(), CaseTypeSetMember, UUID, Handle CRUD operations for CaseTypeSetMember entities. (+4 more)

### Community 633 - "test_general_dependency_list.py"
Cohesion: 0.36
Nodes (8): _parse_pyproject_dependency(), _parse_requirements_line(), Path, scenario_ids, Ensure requirements.txt and pyproject.toml dependencies are identical., _read_pyproject_dependencies(), _read_requirements(), test_dependency_list_matches()

### Community 636 - "ParentUploadResult"
Cohesion: 0.09
Nodes (16): CaseUploadResult, Represents one case upload result and its content validation issues., Get all data issues that are errors., ParentUploadResult, Represents upload results for a parent payload and its children. Subclasses…, Count status occurrences across this result and its nested results. Args:…, Mark this result as failed when nested results have failed. It includes nested…, Update this result's status and logs from its data issues. Corresponding log… (+8 more)

### Community 641 - ".is_invalidated"
Cohesion: 0.33
Nodes (3): Return whether an entry written at `created_at` is affected., Return whether an entry must not be served at all., Return whether an entry may be served while a refresh runs.

### Community 642 - "._validate"
Cohesion: 0.40
Nodes (4): model_validator, Self, Validate claim mappings and public-provider credentials., Validate public-provider credentials.

### Community 658 - "UUID"
Cohesion: 0.19
Nodes (10): OrganizationAccessCasePolicy, OrganizationShareCasePolicy, UserAccessCasePolicy, UserShareCasePolicy, UUID, Expand access policies into rights by case type and data collection. Args:…, Intersect organization and user case-access rights. Args:…, Expand sharing policies into rights by case type and destination. Args:… (+2 more)

### Community 661 - "casedb/services/rbac.py"
Cohesion: 0.29
Nodes (5): CommonRbacService, Configure role-based authorization for the casedb role hierarchy., Initialize inherited RBAC policy handling with casedb roles. Args: app:…, Encapsulates casedb RBAC using the domain's role enumeration., RbacService

### Community 671 - "._validate_state"
Cohesion: 0.33
Nodes (4): model_validator, Self, Validate bound presence, ordering, and compatible censor operators. Raises:…, Validate bounds and build the optimized range matching function.

### Community 676 - "Examples"
Cohesion: 0.50
Nodes (4): Example 1: Bug report, Example 2: Feature request with priority, Example 3: Mark an issue as blocked, Examples

### Community 688 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseAbacService, Initialize role mappings and organization-ID resolvers. Args: abac_service:…

### Community 691 - "InvalidIdsError"
Cohesion: 0.40
Nodes (4): InvalidIdsError, Error for malformed or unknown object identifiers., Initialize a InvalidIdsError instance., test_does_not_update_when_read_fails()

### Community 692 - "InvalidLinkIdsError"
Cohesion: 0.50
Nodes (3): InvalidLinkIdsError, Error for identifiers that violate a model relationship., Initialize a InvalidLinkIdsError instance.

### Community 693 - "InvalidModelIdsError"
Cohesion: 0.50
Nodes (3): InvalidModelIdsError, Error for identifiers belonging to an unexpected model., Initialize a InvalidModelIdsError instance.

### Community 694 - "LinkConstraintViolationError"
Cohesion: 0.50
Nodes (3): LinkConstraintViolationError, Error for a relationship constraint violation between model instances., Initialize a LinkConstraintViolationError instance.

### Community 695 - "UuidSetFilter"
Cohesion: 0.04
Nodes (44): CaseCohortLink, CaseQuery, CaseSetQuery, BaseModel, Model, UUID, Define non-persistable case query, rights, statistics, and result models. These…, Represents labeled filter criteria for querying case sets. (+36 more)

### Community 696 - "api/seq.py"
Cohesion: 0.05
Nodes (52): Expose seqdb API request representations for router composition., CalculatePhylogeneticTreeRequestBody, ConvertSeqFormatRequestBody, create_seq_endpoints(), Any, APIRouter, App, Exception (+44 more)

### Community 697 - "._validate_locus"
Cohesion: 0.50
Nodes (3): model_validator, Self, Restrict gene-product codes to loci typed as genes.

### Community 698 - "._validate_protocol_type_dependencies"
Cohesion: 0.50
Nodes (3): model_validator, Self, Enforce fields required or disallowed by the selected protocol type.

### Community 699 - "._validate_model"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate mutually exclusive read links and paired-read values.

### Community 700 - "._validate_state"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate sequence links and derive a hash from available contigs.

### Community 702 - "CalculateSeqDistancesEtlResult"
Cohesion: 0.14
Nodes (13): CalculateSeqDistancesForNewProfilesCommand, Represents a request to calculate and store distances between new and existing…, Represents a request to create missing distances for profiles under a distance…, UpdateSeqDistancesCommand, CalculateSeqDistancesEtlResult, Represents the result of calculating distances between existing profiles and…, Calculate distances for profiles without distance records. Args: cmd: New-…, Update stored sequence-distance calculations. Args: cmd: Distance-update… (+5 more)

### Community 703 - "Available Tools"
Cohesion: 0.67
Nodes (3): Available Tools, Read operations, Write operations

### Community 704 - "TestContent"
Cohesion: 0.40
Nodes (3): scenario_ids, Happy-path test for RetrieveIsOwnCasesCommand. Finds an org user whose…, TestContent

### Community 707 - "get_test_client"
Cohesion: 0.29
Nodes (5): get_test_client(), fixture, Print the active edge cases once per class run when VERBOSE is enabled., Auto-inject the env fixture into the class., Get a test client for casedb integration tests. This fixture initializes a test…

### Community 710 - "omopdb/integration/build_db/create.py"
Cohesion: 0.33
Nodes (5): # TODO: test_create_site, # TODO: test_create_site_raise, # TODO: test_create_contact, # TODO: test_create_contact_raise, # TODO: OrganizationAdminPolicy.user does not exist

### Community 757 - "test_casedb_remote_app.py"
Cohesion: 0.50
Nodes (4): app(), mock_client(), fixture, Unit tests for the non-CRUD command handlers on CasedbRemoteApp. Each test…

## Ambiguous Edges - Review These
- `Case` → `CaseRights`  [AMBIGUOUS]
  docs/erm/casedb.case.png · relation: references
- `CaseSet` → `CaseSetRights`  [AMBIGUOUS]
  docs/erm/casedb.case.png · relation: references
- `Case Identifier` → `IdentifierForUpload`  [AMBIGUOUS]
  docs/erm/casedb.case.png · relation: references
- `CaseQuery` → `TypedCompositeFilter`  [AMBIGUOUS]
  docs/erm/casedb.case.png · relation: references
- `CaseType` → `Regimen`  [AMBIGUOUS]
  docs/erm/casedb.case.png · relation: references
- `omopdb — Full Database ERD (detailed, 69 entities)` → `IDPUser (omopdb.auth entity)`  [AMBIGUOUS]
  docs/erm/omopdb.detailed.md · relation: conceptually_related_to
- `IDPUser (seqdb.auth entity)` → `Outage (seqdb entity)`  [AMBIGUOUS]
  docs/erm/seqdb.detailed.md · relation: conceptually_related_to

## Knowledge Gaps
- **523 isolated node(s):** `post-pr-comments.sh script`, `docker-entrypoint.sh script`, `PYTHONPATH`, `Gen-EpiX`, `$schema` (+518 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 8296 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **180 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Case` and `CaseRights`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `CaseSet` and `CaseSetRights`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Case Identifier` and `IdentifierForUpload`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `CaseQuery` and `TypedCompositeFilter`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `CaseType` and `Regimen`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `omopdb — Full Database ERD (detailed, 69 entities)` and `IDPUser (omopdb.auth entity)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `IDPUser (seqdb.auth entity)` and `Outage (seqdb entity)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
