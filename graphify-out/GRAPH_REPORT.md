# Graph Report - gen-epix-api  (2026-09-03)

## Corpus Check
- 859 files · ~1,167,244 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 17715 nodes · 38560 edges · 778 communities (581 shown, 197 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 1601 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `391adcff`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- commondb/domain/model/__init__.py
- casedb/domain/model/__init__.py
- omopdb/domain/command/__init__.py
- seqdb/domain/command/__init__.py
- gen_epix/fastapp/enum.py
- TestRoleRegistration
- .create_person_for_upload
- AuthService
- SettingsManager
- Client
- _uuid_field_name
- command/seq.py
- omopdb/api/router.py
- BaseSeqService
- Entity
- JWKSManager
- MockRequest
- CaseService
- crud_dim.py
- BaseCrudTestCase
- get_ref_data_access_from_command
- BaseCaseService
- App
- crud_locus_code_map.py
- IsoTimeTransformer
- commondb/repositories/__init__.py
- JsonFormatter
- omop/ontology.py
- BaseUnitOfWork
- TupleMapTransformer
- SeqdbRemoteApp
- seqdb/domain/model/__init__.py
- transform/__init__.py
- model/case/__init__.py
- BaseCaseService
- test_user_manager_auto_create.py
- Run
- composite.py
- TestBaseResult
- LogItem
- .create_claims
- TestGetCasesForCreateReadSetsOrSeqs
- Token
- test_general_model_field_properties.py
- ObjectAdapter
- casedb CASE Simplified ERD
- CrudEndpointGenerator
- .__call__
- TestCreate
- Model
- test_filter_base_filter.py
- handle_command
- UUID
- omopdb/repositories/sa_model/__init__.py
- test_general_dependency_list.py
- Any
- DomainException
- CrudCommand
- test_seqdb_retrieve_best.py
- TestTokenStore
- test_fastapp_rbac_service.py
- Model
- StringSetFilter
- DictRepository
- OauthIdpClient
- .__init__
- RemoteApp
- omopdb/repositories/__init__.py
- SARepository
- BaseRetrieveCaseTestCase
- Filter
- ._make_user_cmd
- .create_command_and_result_for_samples
- UploadPersonsCommand
- .create_client
- BaseAbacTestCase
- ErmGenerator
- TestCasedbModelProcessMetadata
- test_fastapp_domain.py
- RbacService
- _make_protocol
- server.py
- .create_seq_classification_for_upload
- define_edge_cases_reference.py
- IntervalToIntervalTransformer
- TestCreate
- RoleGenerator
- BaseSnpUploadTestCase
- TestClientStore
- sa_model/seq/__init__.py
- CacheRegion
- AbacService
- casedb/repositories/sa_model/__init__.py
- calculate_seq_distance.py
- BaseUploadTestCase
- .create_parent_for_upload
- test_seqdb_calculate_phylogenetic_tree.py
- sa_model/case.py
- ._serialize_int_enums
- cache/__init__.py
- Hashable
- BaseUploadTestCase
- CasedbTestClient
- IntEnumWithJsonSchemaMixin
- CaseAbac
- make_assoc
- OIDCProvider
- EqualsStringFilter
- UUID
- test_seqdb_distance_optimization_benchmark.py
- sa/util.py
- TestClient
- ImportGraphAnalyzer
- CaseValidator
- .crud
- case_service_retrieve_is_own_cases
- Concept
- .create_child1_for_upload
- Concept (omopdb.omop / OMOP CDM entity)
- test_update_user_policy.py
- test_seqdb_calculate_seq_distance.py
- .get_test_client
- DummyCommand
- CaseRight
- BaseCaseValidatorTestCase
- OAuth2Validator
- .create_case_for_upload
- Model
- SAMapper
- Person
- PersonForUpload
- TestRegistrationAndLookups
- ._get_allele_profile_for_ids
- RBACTestClient
- BaseAnonymizer
- Concept
- rights.py
- .generate_user_invitation_token
- BaseRepository
- api/seq.py
- .create_crud_cmd
- .create_child2_for_upload
- TestModelSampleBatchForUpload
- UuidSetFilter
- UUID
- TestUpdate
- SeqdbTestClient
- TestModelBaseSeq
- fastapp/api/exc.py
- Case Type
- case_service_retrieve_similar_cases
- DatetimeRangeFilter
- commondb/repositories/organization_sa.py
- Data Collection
- casedb/api/__init__.py
- Any
- ._verify_permission_exists
- test_casedb_seqdb_connection
- .create_sample_for_upload
- .upload_batch
- TestModelSeq
- CaseSet
- CaseType
- UUID
- .create_local_or_remote_app
- InMemoryOrganizationRepository
- OrganizationService
- test_casedb_upload.py
- MockIDPClient
- DummyCmd
- ._create_sample_seq_for_upload
- OAuth2Client
- CacheStatistics
- create_mapped_column
- Protocol
- Person
- Protocol (seqdb entity)
- .get_case_abac
- TestCommondbDictModelModifier
- EndpointTestClient
- User
- AuthEnv
- _DummyMapper
- test_fastapp_cache_region.py
- TestGeneratedCrudRoutes
- Gen-EpiX README
- casedb.organization.md
- ._validate_model
- case_date.py
- .crud
- CommondbRemoteApp
- computed_field
- TestDelete
- IdentifierIssuer
- test_fastapp_cache_support.py
- TestNonCrudHandlers
- CompositeFilter
- IntervalTransformer
- log_parser_v2.py
- map_paired_elements
- TestCreate
- .expectBatchProcessed
- EvictionStrategy
- IdpClient
- UUID
- Registry
- test_cfg_log_level.py
- generate_seq_distances.py
- scenario_ids
- ._validate_case_for_upload
- .read_all
- test_commondb_auth.py
- TestInitialization
- RequestorApp
- SeqGenerationSettings
- Development Guide
- Linter
- TestCaseUpload
- TestCasedbEdgeCasesAccess
- TestCommondbModelProcessMetadata
- UserManager
- TestModelSeqProfileForUpload
- fastapp shared application framework
- lock.py
- TestCreate
- SeqdbEndpointTestClient
- convert
- BaseSeqDistancePerformance
- ClientStore
- sa_model/geo.py
- .__init__
- casedb/api/router.py
- CircuitBreaker
- make_cdb_user
- TestCasedbMetadataMasking
- TestCaseTypeAccessAbac
- test_read_config.py
- TestDataLineageMixin
- ServerManager
- Organization (commondb.organization entity)
- .__init__
- case_service_crud_case_set_data_collection_link
- Domain
- .create_read_set_for_upload
- UUID
- AuthTestClient
- CasedbEndpointTestClient
- Organization
- IdentifierIssuer (omopdb.organization entity)
- Organization
- CrudCommand
- seqdb/api/router.py
- UserManager
- validate_int_for_uuid_field
- test_logging_runtime_contract.py
- check_docstrings.py
- TokenStore
- test/conftest.py
- Gen-EpiX Contributor Documentation Index
- Organization
- Sample
- validate_int_key_args
- sa/repository.py
- SAUnitOfWork
- .upload_batch
- test_fastapp_app_log_summarise.py
- TestRead
- _make_cmd
- `gen_epix.fastapp.cache`
- person_validator.py
- BaseAppComposer
- CaseStats
- TestCommondbMetadataMasking
- test_model.py
- TestHttpTimeoutConfiguration
- test_error_code_unicity
- SeqProfileForUpload
- Unit
- App (command dispatcher / PEP)
- Organization (omopdb.organization entity)
- ConceptRelationType
- RetrieveGeneticSequenceFastaByIdCommand
- casedb/domain/command/abac.py
- HandleAuthExceptionMiddleware
- ReadOrganizationResultsOnlyPolicy
- ReadOrganizationResultsOnlyPolicy
- seq/service.py
- commondb/api/organization.py
- FullSample
- JsonFormatter
- .set_obj
- MemoryTagIndex
- .create_case
- .create_uploader
- TestValidateIntForUuidField
- BasePersonUploadTestCase
- PersonBatchForUpload
- test_client_credential_flow.py
- IdpClient hierarchy
- Protocol
- api/system.py
- command/geo.py
- .__init__
- Command
- BaseRemoteService
- PayerPlanPeriod
- Transformer Framework
- .get_user
- rewrite_parametrized_dependency_markers
- CaseTypeAccessAbac
- .expectStatusCount
- test_omopdb_model.py
- env
- erm_mermaid.py
- LogParser2
- AppComposer (Composition Root)
- Region Set
- Sample
- SeqTaxonomy
- command/case.py
- CommondbSAMapper
- FieldType
- command/omop.py
- CdmSource
- renovate.json
- TestUpdate
- TestSQLInjection
- BaseCommondbRemoteAppTestCase
- TestAnonymizeUser
- ServiceTestClient
- TestOIDCProvider
- Concept Relation
- Outage (commondb.system entity)
- Protocol
- DictUnitOfWork
- crud_allele.py
- crud_ast_measurement.py
- crud_ast_prediction.py
- Copilot Chat Prompt Steering Coach
- crud_locus.py
- crud_locus_set.py
- crud_pcr_measurement.py
- crud_protocol_set.py
- crud_protocol_set_member.py
- crud_ref_seq.py
- crud_sample_data_collection_link.py
- crud_sample_identifier.py
- crud_seq.py
- crud_seq_category.py
- crud_seq_category_set.py
- crud_seq_distance.py
- crud_seq_taxonomy.py
- crud_taxon.py
- crud_taxon_set.py
- .create_measurement_for_upload
- dependency
- TestVerifyUserRights
- TestDelete
- dependency
- test_logging_yaml.py
- TestDelete
- dependency
- env
- TestDelete
- dependency
- CacheConfigurationError
- crud_ref_allele.py
- crud_sample.py
- crud_seq_classification.py
- crud_seq_identifier.py
- BaseRepository (abstract)
- Contact (doc)
- seqdb Overview ERD
- IdentifierIssuer
- Taxon
- Locus
- Enum
- casedb/repositories/__init__.py
- Any
- EngineFactory
- .__init__
- .__init__
- TestRead
- TestRead
- TestUpdate
- TestRead
- TestUpdate
- OAuth 2.0 Provider with OpenID Connect Support
- .get_mapped_class
- Entity descriptor
- Specimen
- DataCollection
- Seq
- crud_seq_profile_identifier.py
- SeqService
- ._make_user
- ._validate_content
- EdgeCaseSpec
- crud_col_set_member.py
- sa_model/ontology.py
- Subject
- MeasurementRelation
- ObservationPeriod
- ProcedureOccurrence
- Locus
- ReadSet
- SeqProfile
- EtlLogItem
- .create_file_for_read_set
- ._validate_model
- BaseSAMapper
- .__init__
- IsOrganizationAdminPolicy
- UpdateUserPolicy
- IsOrganizationAdminPolicy
- ReadUserPolicy
- UpdateUserPolicy
- retrieve_complete_case_type.py
- TestGetCaseDataCollections
- OAuth Client Credential Flow Test
- Command
- init-db one-shot database creation service
- DataCollection (commondb.organization entity)
- DataCollectionSetMember
- DataCollectionSetMember
- TreeAlgorithm
- EtlLogItem
- BaseRbacServiceTestCase
- ConcreteRbacService
- TestUserPermissions
- OrganizationService
- TestOIDCProviderIntegration
- 3.8 Comments and Docstrings
- omopdb/repositories/organization_sa.py
- ._validate_content
- OrganizationService
- release-please-config.json
- TestCaseUploadContentDeletion
- Env
- app
- test_debug_console_uses_json_formatter
- command/ontology.py
- ._filter_users_by_organization
- App.handle() command dispatch
- casedb SUBJECT Simplified ERD
- NoteNlp
- TreeAlgorithm
- SeqClassificationForUpload
- ._validate_state
- UUID
- ._validate_state
- .organization_identifier_issuer_link_update_association
- test/enum.py
- ._validate_some_criteria
- ._validate_content
- .__init__
- .__init__
- get_test_client
- TestcasedbEdgeCasesRefDataAccess
- TestOauthIdpClientIntrospection
- _PytestMockConfig
- .data_collection_set_data_collection_update_association
- docker-entrypoint.sh
- Default App Ports (8000/8001/8002/8010)
- CohortDefinition (omopdb.md)
- Organization
- Locus (seqdb entity)
- SeqCategory
- Locus
- AuthorizationCodeStore
- .validate_model
- Any
- CaseTypeSetCaseTypeUpdateAssociationCommand
- case_service_crud_col_set
- .create_case_set
- DiseaseEtiologicalAgentUpdateAssociationCommand
- CasedbRemoteApp
- case_service_crud_ref_dim
- Enum
- .retrieve_protocols
- .get_headers
- .invite_user
- .organization_set_organization_update_association
- .retrieve_outages
- model_validator
- ._validate_some_criteria
- ._validate_state
- TestGetCaseDateColIds
- test_seqdb_nextclade_get_ref_alignment.py
- post-pr-comments.sh
- CHANGELOG
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
- ModelFieldProps
- KeyedMutex
- User
- Role
- Any
- .anonymize_user
- .retrieve_feature_flags
- RetrievePersonsByIdCommand
- FakeResponse
- JIRA Issues
- casedb/repositories/sa_model/abac.py
- .filter
- OmopdbRemoteApp
- wait_for_mssql.py
- setup_case_data_operational
- TestCaseTypeProps
- BrokenBackend
- TestDAGAndCycleBehavior
- TestJWKSManagerIntegration
- pr.sh
- Issue Templates
- field_validator
- TestUploadResult
- .__init__
- TestPermissionRegistration
- TestHierarchicalRolePermissions
- TestEdgeCasesAndErrorConditions
- BaseRemoteAppTestCase
- Fields, Issue Types, and Transitions
- case/non_persistable.py
- .crud
- .idp_user_dependency
- Logger
- ._validate_int_for_uuid
- .create_file
- profile_method
- _ConcreteResult
- Implement JIRA Issue
- Links, Subtasks, and Dependencies
- RowMetadataMixin
- .set_log_level
- .is_allowed
- ._get_target_user_info
- ._verify_entity_exists
- ._validate_state
- TestServiceInitialization
- TestRoleHierarchy
- TestCommandPermissions
- Commit Skill
- test_oidc_provider.py
- ReadSelfResultsOnlyPolicy
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
- TreeAlgorithm (seqdb entity)
- UserInvitationConstraints
- UserNameEmail
- BaseSeq
- LocusCodeMap
- LocusSet
- Outage
- PackageMetadata
- ._serialize_created_at
- casedb/config/__init__.py
- casedb/__init__.py
- .filter
- ReadSelfResultsOnlyPolicy
- ReadUserPolicy
- ReadSelfResultsOnlyPolicy
- set_envvar
- scenario_ids
- JQL Search
- Creating Issues
- Pytest Run (capture once, inspect many times)
- ._serialize_cohort
- ._serialize_id
- .register_retrieve_organization_ids_handler
- .filter
- .retrieve_user_roles
- .is_invalidated
- ._validate
- .register_mappers
- ._validate_state
- crud_read_set.py
- fastapp/services/__init__.py
- .__init__
- omopdb/config/__init__.py
- gen_epix/omopdb/__init__.py
- seqdb/config/__init__.py
- .setup
- TestUnauthenticated
- gen_epix/seqdb/__init__.py
- Any
- ._generate_key_pair
- .has_read_sets
- .get_content
- Gen-EpiX
- RbacService
- ._serialize_roles
- ._invalidate_cache
- CachedError
- .name
- omopdb/repositories/sa_model/base.py
- Examples
- ._validate_unit_for_type
- gen-epix-api Version 6.1.0
- .__init__
- ._set_known_handlers_to_notset
- .add_error
- .__init__
- .__init__
- .__init__
- .__init__
- .__init__
- .__init__
- auth/util.py
- ._validate_locus
- ._validate_protocol_type_dependencies
- ._validate_model
- ._validate_state
- File
- setup_test_users_and_organizations_operational
- Available Tools
- ._transform_decimal
- .seqdb_user
- .app
- ._serialize_severity
- ._validate_severity
- .add_logs
- .repository
- .get_is_denied_exception
- ._invalidate_cache
- .retrieve_user_is_non_rbac_authorized
- .get_is_denied_exception
- ._match
- ._match
- .__init__
- .n_loci
- .get_allele_array
- .is_available
- ._validate_model
- .__init__
- EdgeCaseSpecOp
- TestModelCompleteCaseType
- get_test_client
- TestOmopSpecification
- casedb.md
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
- commondb.md
- commondb.abac.md
- commondb.abac.detailed.md
- commondb.auth.md
- commondb.auth.detailed.md
- commondb.detailed.md
- .get_combinations_with_any_rights
- .get_identity_providers
- .is_sub_role
- CareSiteCrudCommand
- CohortDefinitionCrudCommand
- ConceptSynonymCrudCommand
- ConditionEraCrudCommand
- ConditionOccurrenceIdentifierCrudCommand
- DeathCrudCommand
- DeathIdentifierCrudCommand
- DeviceExposureIdentifierCrudCommand
- DoseEraCrudCommand
- DrugEraCrudCommand
- DrugExposureCrudCommand
- EpisodeCrudCommand
- EpisodeEventCrudCommand
- LocationCrudCommand
- MeasurementCrudCommand
- MeasurementIdentifierCrudCommand
- MeasurementRelationCrudCommand
- MeasurementRelationIdentifierCrudCommand
- MetadataCrudCommand
- NoteCrudCommand
- NoteIdentifierCrudCommand
- NoteNlpCrudCommand
- ObservationCrudCommand
- ObservationPeriodCrudCommand
- PayerPlanPeriodCrudCommand
- PersonCrudCommand
- PersonIdentifierCrudCommand
- ProcedureOccurrenceCrudCommand
- ProcedureOccurrenceIdentifierCrudCommand
- SourceToConceptMapCrudCommand
- SpecimenIdentifierCrudCommand
- VisitDetailCrudCommand
- VisitOccurrenceCrudCommand
- VisitOccurrenceIdentifierCrudCommand
- .get_key_id
- casedb SEQDB Simplified ERD

## God Nodes (most connected - your core abstractions)
1. `BaseUnitOfWork` - 247 edges
2. `Entity` - 217 edges
3. `App` - 151 edges
4. `BaseCaseService` - 150 edges
5. `BaseSeqService` - 136 edges
6. `CrudOperation` - 128 edges
7. `CacheRegion` - 125 edges
8. `DictRepository` - 123 edges
9. `CasedbTestClient` - 120 edges
10. `Domain` - 109 edges

## Surprising Connections (you probably didn't know these)
- `PPR Test Docker Compose (Mock OIDC + CASEDB/SEQDB)` --semantically_similar_to--> `SQL + Mock OIDC Docker Compose (SEQDB/OMOPDB/CASEDB)`  [INFERRED] [semantically similar]
  docker-compose.ppr_test.yml → docker-compose.sql.idp.yml
- `pytest-run skill` --semantically_similar_to--> `Per-app test commands (test_{app}_{scope})`  [INFERRED] [semantically similar]
  .github/instructions/python-pytest.instructions.md → docs/06-Development-Guide.md
- `casedb-seqdb-omopdb E2E Connection Test Logging Config` --semantically_similar_to--> `casedb Logging Config`  [INFERRED] [semantically similar]
  test/end_to_end/casedb_seqdb_connection/logging.yaml → gen_epix/casedb/config/logging.yaml
- `casedb-seqdb-omopdb E2E Connection Test Logging Config` --semantically_similar_to--> `omopdb Logging Config`  [INFERRED] [semantically similar]
  test/end_to_end/casedb_seqdb_connection/logging.yaml → gen_epix/omopdb/config/logging.yaml
- `casedb-seqdb-omopdb E2E Connection Test Logging Config` --semantically_similar_to--> `seqdb Logging Config`  [INFERRED] [semantically similar]
  test/end_to_end/casedb_seqdb_connection/logging.yaml → gen_epix/seqdb/config/logging.yaml

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

## Communities (778 total, 197 thin omitted)

### Community 0 - "commondb/domain/model/__init__.py"
Cohesion: 0.01
Nodes (250): Expose casedb case request models and endpoint registration., Docstring assigned automatically, # TODO: a dedicated request body model should be created for this endpoint, RetrieveSimilarCasesResponseBody, Expose casedb policy contracts and shared authorization policy bases.…, Expose casedb policy adapters and shared policy substitutions. Casedb exports…, Extend self-only result filtering to casedb user case policies., Expose concrete casedb and shared services for application composition. Casedb… (+242 more)

### Community 1 - "casedb/domain/model/__init__.py"
Cohesion: 0.01
Nodes (267): post-pr-comments.sh Script, Review Skill, ETL (Extract, Transform, Load) script for Gen-EpiX genomic epidemiology…, Expose casedb ontology request models and endpoint registration., Compose and expose the configured casedb FastAPI application. This module forms…, # TODO: app variable added for backwards compatibility with startup code that…, Expose and group casedb and shared commands for domain registration. ABAC…, ColTypeSet (+259 more)

### Community 2 - "omopdb/domain/command/__init__.py"
Cohesion: 0.02
Nodes (119): OrganizationAdminPolicyCrudCommand, CrudCommand, Represents a request to manage policies that grant organization-administration…, Represents an extension of a commondb command with identifiers and payloads for…, UpdateAssociationCommand, AnonymizeUserCommand, ContactCrudCommand, DataCollectionCrudCommand (+111 more)

### Community 3 - "seqdb/domain/command/__init__.py"
Cohesion: 0.01
Nodes (253): Upload a batch of sequence samples. Implementations may persist samples and…, Upload samples to seqdb under the configured functional user. The command's…, EtlStatus, Encapsulates lifecycle outcomes for ETL and upload processing., Encapsulates grouping of ETL statuses by failure and processing outcome., Encapsulates the action selected for one record during an upload., UploadAction, UploadStatusSet (+245 more)

### Community 4 - "gen_epix/fastapp/enum.py"
Cohesion: 0.01
Nodes (196): Define casedb API representations for organization permissions., get_logger_fmap(), Create a mapping from application log levels to logger callables. Args: logger:…, Define the abstract composition contract shared by commondb applications., Define commondb role permissions and mappings for application domains. The…, # TODO: remove UPDATE from association objects that do not have properties of…, Apply commondb audit metadata rules to in-memory persisted models., CommondbSAMapperFactory (+188 more)

### Community 5 - "TestRoleRegistration"
Cohesion: 0.08
Nodes (13): Test role registration and management., Test registering a new role with permissions., Test registering role with invalid permissions fails., Test registering existing role without update fails., Test updating existing role succeeds., Test registering multiple roles at once., Test registering roles with root role adds all missing permissions., Test registering roles with root role and missing permissions raises error. (+5 more)

### Community 6 - ".create_person_for_upload"
Cohesion: 0.08
Nodes (28): ParentUploadResult, Person, Create a test Person domain model., Create a test PersonForUpload. A default Person is created unless person=None., Get the Person model contained in a PersonForUpload model, with optional…, Test scenarios related to providing different combinations of child objects., Test 2.1: Person without any child objects., Test 2.2: Person with measurements only. (+20 more)

### Community 7 - "AuthService"
Cohesion: 0.05
Nodes (39): create_custom_openapi_function(), fix_schema_nullable_and_single_element(), Any, OpenAPI schema generation and compatibility fixes., # TODO: add a function to fix read-only fields, Create a cached OpenAPI schema factory with optional schema fixes., # TODO: add a fix for read-only fields, Fixes the schema by handling 'anyOf' constructs and setting the 'nullable'… (+31 more)

### Community 8 - "SettingsManager"
Cohesion: 0.15
Nodes (10): Any, Dynaconf, Settings manager for handling application settings., Return loaded settings. Returns: Cached Dynaconf settings. Raises:…, Get setting value by dot-notation path. Args: key_path: Dot-separated path to…, Encapsulates application settings with environment variable overrides., Parse settings file from comma separated string., Initialize settings manager. (+2 more)

### Community 9 - "Client"
Cohesion: 0.04
Nodes (35): Client, OAuth 2.0 Client representation., Hash the client secret for security., Hash a client secret using SHA-256., Verify a client secret against the stored hash., Validate and filter requested scopes against allowed scopes., Check if the client supports a specific grant type., Check if the redirect URI is registered for this client. (+27 more)

### Community 10 - "_uuid_field_name"
Cohesion: 0.06
Nodes (40): DataLineageMixin, Any, UUID, Shared OMOP model mixins and primary-key normalization helpers., Encapsulates optional provenance and source-traceback fields to an OMOP model., Validate that the input value is either a UUID or a string that can be…, Validate and synchronize string-based primary key arguments. Mutates ``data``…, validate_str_for_uuid_field() (+32 more)

### Community 11 - "command/seq.py"
Cohesion: 0.05
Nodes (38): AlleleCrudCommand, ProtocolCrudCommand, CrudCommand, Define commands for seqdb sequence workflows and managed domain records. The…, Represents CRUD command metadata for sequence protocol records., Represents CRUD command metadata for allele records., Represents CRUD command metadata for read-set records., Represents CRUD command metadata for phylogenetic tree algorithm records. (+30 more)

### Community 12 - "omopdb/api/router.py"
Cohesion: 0.05
Nodes (46): create_abac_endpoints(), Any, APIRouter, App, Exception, FastAPI, NoReturn, ServiceType (+38 more)

### Community 13 - "BaseSeqService"
Cohesion: 0.04
Nodes (46): Represents CRUD command metadata for read-set identifier records., Represents CRUD command metadata for taxon-set membership records., ReadSetIdentifierCrudCommand, TaxonSetMemberCrudCommand, BaseSeqService, PhylogeneticTree, ReadSetIdentifier, TaxonSetMember (+38 more)

### Community 14 - "Entity"
Cohesion: 0.02
Nodes (228): Expose case ABAC policy records, rights models, and shared admin policy types.…, BaseCasePolicy, OrganizationAccessCasePolicy, OrganizationShareCasePolicy, Define persistent organization and user ABAC policy records for cases. Access…, Represents a user's maximum access rights in one data collection. The rights…, Represents common case and case-set rights for a case-type set., Represents an organization's additional source-to-target share rights. Rights… (+220 more)

### Community 15 - "JWKSManager"
Cohesion: 0.05
Nodes (34): JWKSManager, Get the public key in PEM format., Get the private key in PEM format (use with caution!)., Manages JSON Web Keys for JWT token operations., Test verification of a valid JWT token., Test verification of an invalid JWT token., Test verification fails with token signed by different key., Test getting public keys in JWKS format. (+26 more)

### Community 16 - "MockRequest"
Cohesion: 0.03
Nodes (52): MockRequest, Any, Test client authentication requirement for client credentials flow., Test client authentication requirement for other grant types., Test client authentication with valid credentials., Test client authentication with invalid client ID., Test client authentication with invalid secret., Test client authentication with missing credentials. (+44 more)

### Community 17 - "CaseService"
Cohesion: 0.03
Nodes (66): Expose the concrete service that handles casedb case-domain commands.…, CaseService, BaseCaseService, Case, CaseDataCollectionLink, CaseIdentifier, CaseSet, CaseSetCategory (+58 more)

### Community 18 - "crud_dim.py"
Cohesion: 0.04
Nodes (64): DimCrudCommand, Represent CRUD operations for dimensions that group case-type columns., Require a read operation for restricted reference-data commands. Args: cmd:…, _verify_is_read_operation(), case_service_crud_dim(), _crud_create_dim(), _crud_dim_with_abac(), _crud_dim_without_abac() (+56 more)

### Community 19 - "BaseCrudTestCase"
Cohesion: 0.03
Nodes (69): CaseSetCrudCommand, Represent CRUD operations for case sets and their context., Represent CRUD operations for reusable reference-column definitions., RefColCrudCommand, case_service_crud_case_set(), _crud_case_set_with_abac(), _crud_case_set_without_abac(), BaseCaseService (+61 more)

### Community 20 - "get_ref_data_access_from_command"
Cohesion: 0.08
Nodes (45): CaseTypeCrudCommand, CaseTypeSetMemberCrudCommand, ColCrudCommand, Represent CRUD operations for typed case-data columns., Represent CRUD operations for structural case-type definitions., Represent CRUD operations for case-type-set membership., case_service_crud_case_type(), _crud_case_type_with_abac() (+37 more)

### Community 21 - "BaseCaseService"
Cohesion: 0.03
Nodes (140): DomainBaseCaseService, CaseCrudCommand, CaseDataCollectionLinkCrudCommand, CaseSetMemberCrudCommand, CaseTypeSetCrudCommand, Represent CRUD operations for typed cases in data collections., Represent CRUD operations for case-to-data-collection links., Represent CRUD operations for classified case-set membership. (+132 more)

### Community 22 - "App"
Cohesion: 0.04
Nodes (49): App, Any, BaseUserManager, Command, datetime, Domain, Hashable, Logger (+41 more)

### Community 23 - "crud_locus_code_map.py"
Cohesion: 0.12
Nodes (15): LocusCodeMapCrudCommand, Represents CRUD command metadata for locus-code mapping records., LocusCodeMap, Handle a CRUD command for locus-code-map entities. Args: cmd: Typed locus-code-…, LocusCodeMap, UUID, Implement seqdb CRUD service operations for services.seq.crud_locus_code_map., Handle CRUD operations for locus-code-map entities. Args: self: Sequence… (+7 more)

### Community 24 - "IsoTimeTransformer"
Cohesion: 0.03
Nodes (49): IntervalTransformStrategy, Enum, Enumerations for temporal granularity, interval mapping, and result status., Encapsulates strategies for reducing ISO time granularity., Encapsulates strategies for mapping interval categorizations., Encapsulates high-level transformation categories., Encapsulates transformation outcome classifications., Encapsulates supported ISO time granularities. (+41 more)

### Community 25 - "commondb/repositories/__init__.py"
Cohesion: 0.06
Nodes (42): Expose backend-independent repository contracts used by casedb services. Casedb…, BaseAbacRepository, Define the repository interface for commondb ABAC persistence., Encapsulates the persistence boundary for organization-administration policies., Re-export commondb repository interfaces. ABAC, organization, and system…, BaseSystemRepository, Define the repository interface for commondb system data., Encapsulates the persistence boundary for system outages and metadata. (+34 more)

### Community 26 - "JsonFormatter"
Cohesion: 0.05
Nodes (89): Formatter, _build_sensitive_re(), JsonFormatter, _normalise_sensitive_keys(), Any, LogRecord, Central JSON logging formatter for all GenEpix container applications. Ensures…, Format a Unix timestamp as a millisecond-precision UTC ISO 8601 value. Args:… (+81 more)

### Community 27 - "omop/ontology.py"
Cohesion: 0.06
Nodes (40): Health economics domain - OMOP CDM v6.0 health economics tables. This module…, OMOP CDM v6.0 - Standardized Health System Models This module contains the…, Metadata domain - OMOP CDM v6.0 metadata tables. This module contains classes…, Concept, ConceptAncestor, ConceptClass, ConceptRelationship, ConceptSynonym (+32 more)

### Community 28 - "BaseUnitOfWork"
Cohesion: 0.02
Nodes (134): Represent an atomic batch upload of cases and associated data. The upload…, UploadCasesCommand, CaseBatchUploadResult, Represents the results of uploading a batch of cases., Upload a batch of cases and related data. Implementations may persist cases,…, Verify and persist a case batch and its seqdb samples. Verification and…, case_service_upload_cases(), CaseBatchUploader (+126 more)

### Community 29 - "TupleMapTransformer"
Cohesion: 0.03
Nodes (57): Any, Hashable, Replace the lookup map used by subsequent row transformations. Only active rows…, Encapsulates mapping source-field tuples to target-field tuples. The mapping is…, Update the row source and target fields. This allows row field names to change…, Transform an adapted object using the configured tuple mapping. Target fields…, Transform a dictionary row in place and return the same dictionary. This is the…, Return the configured source-field values for a row without transforming it.… (+49 more)

### Community 30 - "SeqdbRemoteApp"
Cohesion: 0.04
Nodes (45): CalculatePhylogeneticTreeRequestBody, Docstring assigned automatically., CalculatePhylogeneticTreeCommand, model_validator, Self, Represents calculating a phylogenetic tree from query profiles and a configured…, Require custom leaf names to align with the queried profile identifiers., Any (+37 more)

### Community 31 - "seqdb/domain/model/__init__.py"
Cohesion: 0.02
Nodes (227): Model, IntEnum, Provide commondb base models and helpers for ETL result reporting. The models…, Normalize a value to a member of an integer enumeration. Args: enum_class: The…, Normalize an optional value to a member of an integer enumeration. Args:…, Represents an optional persistent identifier to commondb audit-aware models., validate_int_enum_value(), validate_int_enum_value_or_none() (+219 more)

### Community 32 - "transform/__init__.py"
Cohesion: 0.04
Nodes (50): Expose the public API for the transformation framework. `DictAdapter`,…, FallbackTransformer, Pipeline, Any, Synchronous transformer pipeline with ordered execution and error recovery., Run the wrapped transformer until it succeeds or retries are exhausted. Retries…, Encapsulates fallback transformation after a primary exception., Store the primary transformer and fallback transformer. (+42 more)

### Community 33 - "model/case/__init__.py"
Cohesion: 0.04
Nodes (82): CompleteCaseType, CaseType, Define the complete, user-specific view of a case type. The module combines…, Represents a case type with its related entities and effective ABAC data. The…, Expose case-domain models for metadata, operations, queries, and uploads.…, Case, CaseDataCollectionLink, CaseIdentifier (+74 more)

### Community 34 - "BaseCaseService"
Cohesion: 0.03
Nodes (61): BaseCaseService, Any, Case, CaseDataCollectionLink, CaseIdentifier, CaseSet, CaseSetCategory, CaseSetDataCollectionLink (+53 more)

### Community 35 - "test_user_manager_auto_create.py"
Cohesion: 0.08
Nodes (43): claims_basic(), make_user_manager(), mock_organization_service(), mock_rbac_service(), other_org(), other_org_id(), Any, fixture (+35 more)

### Community 37 - "composite.py"
Cohesion: 0.05
Nodes (84): Decimal, Generate FastAPI routes that dispatch domain CRUD commands. The module…, # TODO: Add a specific exception for NotImplementedError, # TODO: Add a specific exception for NotImplementedError, # TODO: Add a specific exception for NotImplementedError, # TODO: distinguish between soft and hard delete through hard_delete:, # TODO: Add a specific exception for NotImplementedError, # TODO: Add a specific exception for NotImplementedError (+76 more)

### Community 39 - "LogItem"
Cohesion: 0.03
Nodes (76): Domain, Initialize remote commondb routes with connection and authentication settings.…, AuthProtocol, OAuthFlow, Encapsulates identifying an authentication protocol supported by an identity…, Encapsulates identifying an OAuth authorization flow., BaseLogItem, LogItem (+68 more)

### Community 40 - ".create_claims"
Cohesion: 0.04
Nodes (50): BaseAuthServiceTestCase, Any, scenario_ids, UUID, Test idp_clients property., idp_clients property returns a copy, not the original list., Test scenarios for get_existing_user_from_token., First IDP unauthorized, second IDP succeeds. (+42 more)

### Community 41 - "TestGetCasesForCreateReadSetsOrSeqs"
Cohesion: 0.06
Nodes (24): fixture, scenario_ids, UUID, Comprehensive test suite for the create_seq.py module in…, Create a mock user for testing., Test _get_cases_for_create_file_for_read_sets_or_seqs function., Create a mock UnitOfWork for testing., Create a mock repository for testing. (+16 more)

### Community 42 - "Token"
Cohesion: 0.05
Nodes (34): Any, patch, Unit tests for OAuth 2.0 Token Store This module contains comprehensive pytest…, Test scopes property with multiple scopes., Test scopes property with single scope., Test scopes property with empty scope., Test scopes property handles extra whitespace., Test has_scope returns True for existing scopes. (+26 more)

### Community 43 - "test_general_model_field_properties.py"
Cohesion: 0.21
Nodes (11): _is_iterable_type(), Any, scenario_ids, Check if the given field type is an iterable type (like List, Set, Tuple, etc.), test if domain and request body models have a max_length for all iterable…, test_model_field_properties(), is_model_class(), Any (+3 more)

### Community 44 - "ObjectAdapter"
Cohesion: 0.05
Nodes (52): ObjectAdapter, Adapters that expose a common field interface for row-like objects. The…, Encapsulates adapter selection for supported object representations. Supported…, example_conditional_transformation(), example_usage(), Person, BaseModel, Executable examples of composing field, validation, and streaming transforms. (+44 more)

### Community 46 - "CrudEndpointGenerator"
Cohesion: 0.17
Nodes (15): CrudEndpointGenerator, Any, APIRouter, FastAPI, Parse comma-separated or JSON-encoded identifiers for a route parameter. Args:…, Register the single-object update endpoint for a CRUD resource. The generated…, Encapsulates generating command-backed CRUD routes for a configured domain…, Generate delete some. (+7 more)

### Community 47 - ".__call__"
Cohesion: 0.29
Nodes (4): BaseModel, Initialize a Key instance., Get the key generator callable. Returns: ------- Callable[[BaseModel], str] The…, Generate this key for a model instance.

### Community 48 - "TestCreate"
Cohesion: 0.07
Nodes (4): Env, scenario_ids, skipif, TestCreate

### Community 49 - "Model"
Cohesion: 0.05
Nodes (41): Hashable, Get the object IDs, either from the obj_ids field or from the objs field. In…, Get the ID of the model instance. If the ID is not set and raise_on_missing is…, Any, datetime, Hashable, Model, Initialise the repository. extra_data controls behaviour when db contains… (+33 more)

### Community 50 - "test_filter_base_filter.py"
Cohesion: 0.04
Nodes (32): Represents a filter carrying an explicit serialized filter type. This is a base…, TypedFilter, AlwaysTrueFilter, BaseFilterTestCase, CompositeFilter, EqualsFilter, Any, BaseModel (+24 more)

### Community 51 - "handle_command"
Cohesion: 0.06
Nodes (42): __extract_invalid_ids(), generate_handle_exception_function(), _handle_auth_exception(), handle_command(), handle_exception(), _handle_invalid_ids_exception(), _handle_service_exception(), log_and_raise_invalid_ids_exception() (+34 more)

### Community 52 - "UUID"
Cohesion: 0.07
Nodes (22): Any, model_validator, Self, UUID, Validate that the content format matches the sequence profile type., Verify profile content and derive or validate its content hash. Upload-only…, Validate SNP content and derive its hash. Returns: The derived SNP profile…, Validate the k-mer profile content. (+14 more)

### Community 53 - "omopdb/repositories/sa_model/__init__.py"
Cohesion: 0.04
Nodes (119): NoIdRowMetadataMixin, declarative_mixin, Encapsulates audit metadata fields to a row with a nonstandard primary key., IdentifierMixin, Encapsulates SQLAlchemy columns for external identifier-derived row models., Register and expose SQLAlchemy mappings for shared and OmopDB model types. The…, CareSite, CdmSource (+111 more)

### Community 54 - "test_general_dependency_list.py"
Cohesion: 0.36
Nodes (8): _parse_pyproject_dependency(), _parse_requirements_line(), Path, scenario_ids, Ensure requirements.txt and pyproject.toml dependencies are identical., _read_pyproject_dependencies(), _read_requirements(), test_dependency_list_matches()

### Community 55 - "Any"
Cohesion: 0.10
Nodes (27): Any, Hashable, Model, Return a per-id existence flag list in the same order as obj_ids., Read a projection of specific fields, optionally filtered., Split a filter into a SQL where-clause part and a Python remainder., Helper method for debugging., Verify that obj_ids are unique and/or exist in the database. (+19 more)

### Community 56 - "DomainException"
Cohesion: 0.10
Nodes (15): Self, Name the requested value., Create api model class., Read api model class., Check if the entity has a model set. Returns: ------- bool True if the entity…, Set the repository model class for the entity, which is intended as the class…, Set the API model class for the entity, which is intended as the request model…, Set the API model class for the entity, which is intended as the model that… (+7 more)

### Community 57 - "CrudCommand"
Cohesion: 0.09
Nodes (23): CdmSourceCrudCommand, CohortCrudCommand, ConceptCrudCommand, ConditionOccurrenceCrudCommand, CostCrudCommand, DomainCrudCommand, DrugStrengthCrudCommand, ObservationIdentifierCrudCommand (+15 more)

### Community 58 - "test_seqdb_retrieve_best.py"
Cohesion: 0.08
Nodes (40): Represents retrieval of the best Seq ID for each requested sample. IDs, and…, Represents retrieval of the best SeqProfile ID for each requested sample.…, Represents retrieval of the best SeqClassification ID for each requested…, RetrieveBestSeqClassificationPerSampleCommand, RetrieveBestSeqPerSampleCommand, RetrieveBestSeqProfilePerSampleCommand, _get_best_id_per_sample(), UUID (+32 more)

### Community 59 - "TestTokenStore"
Cohesion: 0.03
Nodes (35): Test cases for the TokenStore class., Test storing a basic token., Test storing a token with refresh token creates mapping., Test storing a token without refresh token., Test storing multiple tokens., Test retrieving an existing valid token., Test retrieving a non-existent token returns None., Test that retrieving expired token auto-cleans it. (+27 more)

### Community 60 - "test_fastapp_rbac_service.py"
Cohesion: 0.21
Nodes (19): Model1_1CrudCommand, Model1_2CrudCommand, Model2_1CrudCommand, Model2_2CrudCommand, CrudCommand, Enum, ServiceType, TestType (+11 more)

### Community 61 - "Model"
Cohesion: 0.08
Nodes (17): CrudCommand, Model, RAISE, Models the requested value., Return service type for model., For all registered CRUD commands, return a dict where the key is the model…, Return entity for model., Return entity for crud command. (+9 more)

### Community 62 - "StringSetFilter"
Cohesion: 0.04
Nodes (45): DateRangeFilter, Represents a filter matching dates within the configured bounds., ExistsFilter, Any, Hashable, Represents a filter matching non-null, non-excluded values., Return whether a scalar value exists, respecting inversion., Yield existence matches for each value in a column. (+37 more)

### Community 63 - "DictRepository"
Cohesion: 0.11
Nodes (56): DictRepository, Load a DictRepository from a pickle file (plain or gzip-compressed)., Load a DictRepository from a zip archive containing per-entity JSON files., Encapsulates a repository that stores models in an in-memory dict, keyed by…, Return (where_filter, None) — the full filter applies in-memory., Instantiate a DictRepository, optionally loading data from a pkl/zip file., child_id(), ChildModel (+48 more)

### Community 64 - "OauthIdpClient"
Cohesion: 0.05
Nodes (30): OauthIdpClient, Any, Request, Response, Issuer the requested value., Audience the requested value., Scope the requested value., Update the OIDC configuration from the discovery URL or, if provided, the… (+22 more)

### Community 65 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseRbacService, Initialize the policy with its RBAC service and configuration properties. Args:…

### Community 66 - "RemoteApp"
Cohesion: 0.09
Nodes (17): App, CrudCommand, Domain, Path, SSLContext, Remote port, or None if not specified., HTTP protocol (HTTP or HTTPS)., Full base URL including protocol, host, and port. (+9 more)

### Community 67 - "omopdb/repositories/__init__.py"
Cohesion: 0.04
Nodes (61): CommonBaseAbacRepository, SQLAlchemy transaction and unit-of-work implementation., BaseAbacRepository, OmopDB specialization of the shared attribute-based access repository., Encapsulates the commondb ABAC repository contract for OmopDB composition., Expose OmopDB repository contracts for shared and OMOP persistence.…, BaseOmopRepository, datetime (+53 more)

### Community 68 - "SARepository"
Cohesion: 0.06
Nodes (48): CaptureFixture, BaseException, setter, Create an SARepository, setting up engine, schemas, and DDL. When…, Try to open a database connection; return None on success or the exception on…, Return the repository's unique identifier., Return the repository's name., Return the default isolation level for new sessions. (+40 more)

### Community 69 - "BaseRetrieveCaseTestCase"
Cohesion: 0.09
Nodes (23): BaseRetrieveCaseTestCase, _FakeCaseAbacPolicy, Any, Case, CaseType, Col, Command, datetime (+15 more)

### Community 70 - "Filter"
Cohesion: 0.10
Nodes (27): _default_validate_query_filter(), Allow query filters with at most one level of composite filters., Filter, Any, BaseModel, Hashable, Self, Yield column values that match the filter. (+19 more)

### Community 71 - "._make_user_cmd"
Cohesion: 0.16
Nodes (11): Any, READ_SOME for org admin should authorize when all users are within admin orgs., Test regular user read behavior., READ_ALL for regular user should include self and active admins of own org., READ_SOME for regular user should allow self and active admins only., READ_SOME should raise when includes users outside allowed set., READ_ONE for regular user should allow self if active., READ_ONE should raise for other org users or inactive non-admins. (+3 more)

### Community 72 - ".create_command_and_result_for_samples"
Cohesion: 0.10
Nodes (28): create_allele_profile_base64(), Any, Test the _verify_children_seq_profiles function., When sample is new, existing-profile checks are skipped., No existing rows means the profile is left untouched., A pre-skipped result should not be re-validated., A seq_id tied to another sample should fail validation., Fallback without seq_id should emit 6b2f8e10. (+20 more)

### Community 73 - "UploadPersonsCommand"
Cohesion: 0.11
Nodes (16): Represents an upload of a batch of persons along with their associated data.…, UploadPersonsCommand, PersonValidator, BaseOmopService, UUID, Encapsulates validation and transformation of person-upload content., Initialize validation state for the service and submitting user., Validate and transform the content of the persons in batch upload command.… (+8 more)

### Community 74 - ".create_client"
Cohesion: 0.07
Nodes (19): BaseOauthIdpClientTestCase, Any, scenario_ids, Tests for initialization and discovery configuration updates., Base test case with common fixtures and utilities for OauthIdpClient., Test decode raises ExpiredSignatureError and triggers CredentialsAuthError., Test decode raises PyJWTError and triggers CredentialsAuthError., Test decode raises RuntimeError and triggers CredentialsAuthError. (+11 more)

### Community 75 - "BaseAbacTestCase"
Cohesion: 0.07
Nodes (28): BaseAbacTestCase, OrgPolicyDumpStub, Any, scenario_ids, UUID, Create a command-like object with a .user containing an id., Create a user-like object for get_case_abac cached reads., Create a command-like object for update_user_own_organization. (+20 more)

### Community 76 - "ErmGenerator"
Cohesion: 0.09
Nodes (19): ErmGenerator, GraphvizErmGenerator, Domain, Path, Graphviz / erdantic-based ERM diagram generator. Produces PNG Entity-…, Generates Entity-Relationship Model diagrams as PNG files via ``erdantic`` /…, Generate ERM diagrams (PNG) for every domain and its services. Also writes an…, generate_hash_for_domain_models() (+11 more)

### Community 77 - "TestCasedbModelProcessMetadata"
Cohesion: 0.12
Nodes (13): get_test_client(), Env, fixture, integration, scenario_ids, created_at, modified_at, and modified_by must all be set by the backend on…, created_at must not change when a record is updated., modified_at supplied in the update payload must be ignored by the backend. (+5 more)

### Community 78 - "test_fastapp_domain.py"
Cohesion: 0.15
Nodes (22): BadCrudNoEntity, BadCrudNoModel, BadCrudNoModel2, CrudA, CrudB, CrudX, CrudY, DummyNonCrud (+14 more)

### Community 79 - "RbacService"
Cohesion: 0.40
Nodes (4): CommonRbacService, Initialize RBAC operations using the seqdb role enumeration. Args: app:…, Encapsulates seqdb RBAC service behavior., RbacService

### Community 80 - "_make_protocol"
Cohesion: 0.07
Nodes (28): ProtocolType, Encapsulates the laboratory or analytical purpose of a protocol., _create_field_description(), Helper function to create field descriptions based on protocol type…, _make_protocol(), _minimal_protocol_data(), Any, parametrize (+20 more)

### Community 81 - "server.py"
Cohesion: 0.07
Nodes (47): delete, ForeignKeyConstraint409HTTPException, HTTP 409 error when deletion would violate a foreign-key relationship., get, HTTPBasicCredentials, HTTPException, JSONResponse, post (+39 more)

### Community 82 - ".create_seq_classification_for_upload"
Cohesion: 0.12
Nodes (19): A seq_id tied to another sample should fail validation., Primary category mismatch with unknown seq should emit f2a84c91., Primary category mismatch with seq_id should emit 9d3a4f1b., Fallback key (protocol, None) resolves identical classification., Temporary SeqClassification IDs are replaced by existing DB IDs., With seq_id=NULL_ID, mismatch is treated as keyed mismatch (9d3a4f1b)., When id already matches DB id, no replacement info is logged., Current behavior: fallback is gated by seq_id != NULL_ID. (+11 more)

### Community 83 - "define_edge_cases_reference.py"
Cohesion: 0.12
Nodes (19): _compute_expected_case_type_sets(), _compute_expected_case_types(), _compute_expected_cases(), _compute_expected_col_sets(), _compute_expected_cols(), _compute_expected_ref_cols(), _compute_expected_ref_dims(), _get_case_type_from_col() (+11 more)

### Community 84 - "IntervalToIntervalTransformer"
Cohesion: 0.06
Nodes (34): IntervalDict, IntervalToIntervalTransformer, Hashable, NoReturn, RAISE, TypedDict, Map a single numeric value according to the configured intervals. Args: value:…, Encapsulates normalized interval bounds and endpoint metadata. (+26 more)

### Community 85 - "TestCreate"
Cohesion: 0.09
Nodes (4): Env, scenario_ids, skipif, TestCreate

### Community 86 - "RoleGenerator"
Cohesion: 0.18
Nodes (10): Command, Enum, Role, Map commondb role permissions to equivalent domain roles and commands. The…, Map the commondb role hierarchy to equivalent domain roles. The mapping…, Return string values for commondb and mapped domain roles. The mapping returns…, Return string role sets for commondb and mapped domain role sets. The mapping…, Return permissions indexed by commondb or mapped domain role values. The… (+2 more)

### Community 87 - "BaseSnpUploadTestCase"
Cohesion: 0.09
Nodes (28): BaseSnpUploadTestCase, scenario_ids, UUID, Create command and result for profiles. Uses model_construct to bypass pydantic…, Create a mock Protocol with ref_seq_id., Set up repository.crud side_effect., Get profile result at given indices., No SNP profiles → early return. (+20 more)

### Community 88 - "TestClientStore"
Cohesion: 0.04
Nodes (27): Any, patch, Test cases for the ClientStore class., Test storing a client., Test storing multiple clients., Test that storing a client with same ID overwrites the previous one., Test retrieving an existing active client., Test retrieving an existing but inactive client returns None. (+19 more)

### Community 89 - "sa_model/seq/__init__.py"
Cohesion: 0.05
Nodes (83): ContentMixin, get_mixin_mapped_column(), Any, Mapped, TypeEngine, Create a mapped column from a Pydantic model-mixin field. The helper derives…, ContentMixin, QualityMixin (+75 more)

### Community 90 - "CacheRegion"
Cohesion: 0.01
Nodes (140): CacheBackend, ProxyBackend, ABC, Abstract cache store contract. A backend is a dumb key-to-envelope store. It…, Return a store-provided mutex for regenerating `key`. Returns: A mutex when the…, Release the resources held by the store., Encapsulates altering the behavior of another backend without subclassing it.…, Initialize a ProxyBackend instance. (+132 more)

### Community 91 - "AbacService"
Cohesion: 0.11
Nodes (18): AbacService, BaseAbacService, Command, OrganizationAccessCasePolicy, OrganizationShareCasePolicy, UserAccessCasePolicy, UserShareCasePolicy, UUID (+10 more)

### Community 92 - "casedb/repositories/sa_model/__init__.py"
Cohesion: 0.05
Nodes (90): Expose and register SQLAlchemy persistence models for casedb entities. The ABAC…, OrganizationAdminPolicy, OrganizationAdminPolicyMixin, Base, declarative_mixin, RowMetadataMixin, Define SQLAlchemy rows and mixins for commondb ABAC policy persistence., Encapsulates SQLAlchemy columns for OrganizationAdminPolicy-derived row models.… (+82 more)

### Community 93 - "calculate_seq_distance.py"
Cohesion: 0.05
Nodes (64): InvalidArgumentsError, Error for command arguments that fail validation., Encapsulates the biological representation used by a sequence profile., SeqProfileType, field_serializer, Serialize the profile type as its integer enum value., Return the sequence-profile type used by this distance protocol. Returns: The…, _calculate_and_store_distances() (+56 more)

### Community 94 - "BaseUploadTestCase"
Cohesion: 0.07
Nodes (31): BaseUploadTestCase, ParentUploadResult, ReadSetForUpload, scenario_ids, SeqForUpload, UUID, Helper to create a ReadSetForUpload with default or specified properties., Test that ConcurrentModificationError in distance calculation is a soft failure. (+23 more)

### Community 95 - ".create_parent_for_upload"
Cohesion: 0.13
Nodes (15): Parent, Test scenarios related to field mutability for existing objects., Test 5.1.1: Always mutable single value field - should be updated., Test 5.1.2: Always mutable list field - should be updated., Test 5.1.3.1: Dict field - add new key with non-None value., Test 5.1.3.2: Dict field - new key with None value should not be added., Test 5.1.3.3: Dict field - update existing key with new value., Test 5.1.3.4: Dict field - remove existing key when new value is None. (+7 more)

### Community 96 - "test_seqdb_calculate_phylogenetic_tree.py"
Cohesion: 0.06
Nodes (44): ClusterNode, _correct_nj_tree_negative_branch_lengths_recursion(), _get_newick_repr_recursion(), Any, PhylogeneticTree, Recursively update negative branch lengths by adding the negative branch length…, Convert sciply.cluster.hierarchy.to_tree()-output to Newick format. :param…, Build a phylogenetic tree from stored sequence-profile distances. Args: self:… (+36 more)

### Community 97 - "sa_model/case.py"
Cohesion: 0.08
Nodes (45): Case, CaseDataCollectionLink, CaseIdentifier, CaseSet, CaseSetCategory, CaseSetDataCollectionLink, CaseSetMember, CaseSetStatus (+37 more)

### Community 98 - "._serialize_int_enums"
Cohesion: 0.29
Nodes (5): field_serializer, IntEnum, UUID, Serializes the IntEnums to their int value., Serializes UUID fields as strings. If the value is None, it returns None.

### Community 99 - "cache/__init__.py"
Cohesion: 0.02
Nodes (169): Clock, Protocol, Time sources used by the cache framework. Every expiry decision in this package…, Encapsulates supplying the monotonic and wall-clock readings a cache needs., Return a strictly non-decreasing reading in seconds., Return the current wall-clock time as a Unix timestamp., Encapsulates reading time from the operating system. Expiry uses `monotonic` so…, SystemClock (+161 more)

### Community 100 - "Hashable"
Cohesion: 0.06
Nodes (27): DictAdapter, PolarsAdapter, Any, BaseModel, Hashable, Protocol, PydanticAdapter, Encapsulates adapting a Pydantic model to the field interface. (+19 more)

### Community 101 - "BaseUploadTestCase"
Cohesion: 0.08
Nodes (21): ParentBatchUploadResult, Any, Verify and complete reference data for allele profiles., UploadParentsCommand, BaseUploadTestCase, Base test case with common fixtures and utilities., Focused edge-case tests for upload consistency and null semantics., Different non-null parent IDs across children in one parent should fail. (+13 more)

### Community 102 - "CasedbTestClient"
Cohesion: 0.07
Nodes (32): Contact, Disease, EtiologicalAgent, RegionSet, RegionSetShape, Site, CasedbTestClient, Case (+24 more)

### Community 103 - "IntEnumWithJsonSchemaMixin"
Cohesion: 0.06
Nodes (38): CoreSchema, FormatType, AstResultFormat, IntEnumWithJsonSchemaMixin, PcrResultFormat, IntEnum, QualityControlResult, Encapsulates ordered quality-control outcomes for sequence data. (+30 more)

### Community 104 - "CaseAbac"
Cohesion: 0.12
Nodes (5): CaseAbac, Represents a user's effective case ABAC rights grouped by case type., UUID, This test expects is_allowed to return False because the access map does not…, TestCaseAbac

### Community 105 - "make_assoc"
Cohesion: 0.08
Nodes (20): Raise an error when the iterable contains duplicate identifiers., AssocModel, BaseRepositoryTestCase, DummyRepository, make_assoc(), Any, Hashable, Model (+12 more)

### Community 106 - "OIDCProvider"
Cohesion: 0.10
Nodes (14): OIDCProvider, Any, Create an OpenID Connect ID Token., Validate and decode an ID token., OpenID Connect provider implementation., Create userinfo endpoint response based on scopes., Initialize OIDC provider with JWKS manager., Create OpenID Connect discovery document. (+6 more)

### Community 107 - "EqualsStringFilter"
Cohesion: 0.15
Nodes (10): EqualsStringFilter, EqualsFilter, Represents a filter matching a string value., DummyCmd, DummyEntity, DummyLink, UUID, Minimal dummy command object for testing purposes. (+2 more)

### Community 108 - "UUID"
Cohesion: 0.12
Nodes (17): CaseDataIssue, Represents a case-content issue associated with a column., RefCol, UUID, Generate all pairs of column IDs in both directions., Validate and transform the cases in a batch upload command. Where applicable,…, Return mutable content and issue-list references for all batch cases. The…, Append issues for unknown columns without removing their content. Args:… (+9 more)

### Community 109 - "test_seqdb_distance_optimization_benchmark.py"
Cohesion: 0.04
Nodes (95): BaseSeqRepository, Encapsulates backend-independent persistence for seqdb sequence data., Provide seqdb persistence behavior for repositories.seq_dict., Encapsulates seqdb persistence behavior for sequence repositories using in-…, Construct complete sample aggregates from in-memory linked records., SeqDictRepository, Provide seqdb persistence behavior for repositories.seq_sa., Encapsulates seqdb persistence behavior for sequence repositories using… (+87 more)

### Community 110 - "sa/util.py"
Cohesion: 0.09
Nodes (36): compiles, ComputedFieldInfo, get_type_from_annotation(), Any, Adapted from https://github.com/fastapi/sqlmodel v0.0.24., Repository implementations and unit-of-work exports., SQLAlchemy repository, mapper, and unit-of-work exports., create_sa_type_from_field_info() (+28 more)

### Community 111 - "TestClient"
Cohesion: 0.08
Nodes (30): Command, DataCollection, datetime, User, UserInvitation, UUID, Assert that reading all objects returns the expected identifiers. Args:…, Check whether the user has the given role (exclusively, by default). (+22 more)

### Community 112 - "ImportGraphAnalyzer"
Cohesion: 0.07
Nodes (30): Import, ImportFrom, analyze_imports(), ImportEdge, ImportGraphAnalyzer, ImportStatementVisitor, ModuleNode, Path (+22 more)

### Community 113 - "CaseValidator"
Cohesion: 0.10
Nodes (17): CaseValidator, BaseCaseService, Concept, Organization, Region, Initialize region lookups and directed containment relations., Initialize organization lookups by ID, code, and name., Retrieve concepts and build set membership and containment mappings. Returns:… (+9 more)

### Community 114 - ".crud"
Cohesion: 0.07
Nodes (24): Any, App, CrudCommand, Hashable, Logger, Model, setter, UpdateAssociationCommand (+16 more)

### Community 115 - "case_service_retrieve_is_own_cases"
Cohesion: 0.10
Nodes (27): case_service_retrieve_is_own_cases(), BaseCaseService, UUID, Map accessible requested cases to private-collection ownership flags. Invalid…, BaseIsOwnCasesTestCase, _FakeCaseAbacPolicy, Any, Case (+19 more)

### Community 116 - "Concept"
Cohesion: 0.05
Nodes (40): ConceptClass, ConceptSynonym, FactRelationship, ConceptClass (omopdb.md), ConceptSynonym (omopdb.md), EpisodeEvent (omopdb.md), FactRelationship (omopdb.md), Metadata (omopdb.md) (+32 more)

### Community 117 - ".create_child1_for_upload"
Cohesion: 0.09
Nodes (20): Test combinations of different scenarios., Test parent with both children and Identifiers., Test updating an existing parent with new child objects., Test complex reference data resolution across multiple children., Test Child2 with Identifiers in combination with parent relationships and other…, Same-service link verification should support user=None without crashing., Create a test child1 for upload., Create a test Ref1 object. (+12 more)

### Community 118 - "Concept (omopdb.omop / OMOP CDM entity)"
Cohesion: 0.13
Nodes (39): CareSite (omopdb.omop / OMOP CDM entity), CdmSource (omopdb.omop / OMOP CDM entity), Cohort (omopdb.omop / OMOP CDM entity), CohortDefinition (omopdb.omop / OMOP CDM entity), Concept (omopdb.omop / OMOP CDM entity), ConceptAncestor (omopdb.omop / OMOP CDM entity), ConceptClass (omopdb.omop / OMOP CDM entity), ConceptRelationship (omopdb.omop / OMOP CDM entity) (+31 more)

### Community 119 - "test_update_user_policy.py"
Cohesion: 0.27
Nodes (14): _make_abac_service(), _make_invite_cmd(), _make_policy(), _make_role_set_map(), _make_update_cmd(), _make_user(), scenario_ids, User (+6 more)

### Community 120 - "test_seqdb_calculate_seq_distance.py"
Cohesion: 0.06
Nodes (57): Calculate and persist distances for newly supplied sequence profiles. For each…, seq_service_calculate_seq_distances_for_new_profiles(), BaseCalculateSeqDistanceTestCase, _CrudRecorder, _iterable(), _make_allele_profile(), _make_crud_side_effect(), _make_mlva_profile() (+49 more)

### Community 121 - ".get_test_client"
Cohesion: 0.14
Nodes (7): Any, Path, Create a test environment for the given test type and repository type. A single…, scenario_ids, TestRead, scenario_ids, TestStartup

### Community 122 - "DummyCommand"
Cohesion: 0.12
Nodes (13): DummyCommand, Command, Test get_headers method for different auth protocols., get_headers returns default headers with NONE protocol., get_headers caches token when not expired., get_headers refreshes token past refresh margin., Minimal command for testing., get_headers caches long-lived tokens correctly. Note: Tokens without an 'exp'… (+5 more)

### Community 123 - "CaseRight"
Cohesion: 0.07
Nodes (27): CaseRight, Identify access rights granted for cases and case sets., CaseTypeShareAbac, BaseModel, UUID, Return an accessor for source collections granting a share right. Args: right:…, Return an accessor for source collections granting a share right. Args: right:…, Return case-type and collection pairs granting an access right. The returned… (+19 more)

### Community 124 - "BaseCaseValidatorTestCase"
Cohesion: 0.11
Nodes (17): BaseCaseValidatorTestCase, Concept, Organization, Region, scenario_ids, UUID, Base test case with common fixtures and helpers for CaseValidator tests., Regression test for LSP-3417. ``_get_col_pairs`` generates both directions, so… (+9 more)

### Community 125 - "OAuth2Validator"
Cohesion: 0.07
Nodes (22): RequestValidator, Test OAuth2Validator initialization., OAuth2Validator, Any, Save authorization code (not used in client credentials flow)., Validate authorization code (not used in client credentials flow)., Confirm redirect URI (not used in client credentials flow)., Validate that the grant type is supported by the client. (+14 more)

### Community 126 - ".create_case_for_upload"
Cohesion: 0.15
Nodes (9): Batch can contain cases from different DCs., Tests for ABAC column and creation-right verification in verify_abac_rights., Tests for CaseBatchForUpload.has_samples (the pure predicate on the batch…, When new case has NULL_ID and no default, should add error., When case explicitly sets created_in_data_collection_id, don't override., Existing cases should not be modified by default setting., New case with explicit DC ID should use that DC for ABAC., TestCaseBatchHasSamples (+1 more)

### Community 127 - "Model"
Cohesion: 0.13
Nodes (13): Any, Model, Path, Return the lookup key for an object based on MODEL_KEY_MAP., Apply update properties and linked-object IDs to a model. All field-value pairs…, Build a mapping from relationship field names to (link field, model class)…, Normalise the set_dummy_link parameter into a per-field dict and a default flag., Resolve a relationship value to its link field name and target ID. Args:… (+5 more)

### Community 128 - "SAMapper"
Cohesion: 0.07
Nodes (28): Any, Hashable, Model, Get row ID from row object or row class., Dump model object to SQLAlchemy row object., Update row with model object values., Load model object from SQLAlchemy row., Get the schema name from the row class __table_args__. (+20 more)

### Community 129 - "Person"
Cohesion: 0.10
Nodes (34): ConditionOccurrenceIdentifier (omopdb.md), Observation (omopdb.md), VisitOccurrence (omopdb.md), CareSite, ConditionOccurrence, ConditionOccurrenceIdentifier, DeviceExposure, DeviceExposureIdentifier (+26 more)

### Community 130 - "PersonForUpload"
Cohesion: 0.09
Nodes (26): PersonForUpload, ParentForUpload, Represents a person, together with any relevant associated data, intended for…, get_test_client(), _make_person(), Env, fixture, MonkeyPatch (+18 more)

### Community 131 - "TestRegistrationAndLookups"
Cohesion: 0.08
Nodes (5): BaseDomainTestCase, LSP-3650 regression: DELETE_ALL is wired into the generated DELETE /v1/{entity}…, Every CrudOperation that the generic CRUD endpoint generator actually wires up…, TestCrudPermissionTypeMapCompleteness, TestRegistrationAndLookups

### Community 132 - "._get_allele_profile_for_ids"
Cohesion: 0.08
Nodes (17): Test that seqs property maintains proper structure for serialization., Test SampleForUpload without id where seqs can have their own sample_ids., Test SampleForUpload without id where seqs also have NULL_ID sample_ids., Test has_seqs computed field returns False when no samples have seqs., Test valid SampleForUpload with sample_id., Test valid SampleForUpload with Identifiers., Test valid SampleForUpload with both sample_id and sample_ids., Test valid SampleForUpload with multiple identifiers. (+9 more)

### Community 133 - "RBACTestClient"
Cohesion: 0.10
Nodes (16): ServiceUser, get_test_client(), Any, BaseRbacService, CrudCommand, Enum, fixture, Hashable (+8 more)

### Community 134 - "BaseAnonymizer"
Cohesion: 0.09
Nodes (20): Collection, BaseAnonymizer, ModelAnonymizer, ABC, Any, date, Domain, Model (+12 more)

### Community 135 - "Concept"
Cohesion: 0.07
Nodes (32): Concept, ConceptAncestor, ConceptRelationship, ConditionEra, Cost, Domain, DoseEra, DrugEra (+24 more)

### Community 136 - "rights.py"
Cohesion: 0.11
Nodes (16): Compute effective case and case-set rights from resolved ABAC records. Access…, Return effective rights for a case in its current collections. Args: case_id:…, Return effective rights for a case set in its current collections. Args:…, Return current collections removable through private-owner access. Direct…, Return absent collections addable through private-owner access. Direct access…, # TODO: Check indirect share rights from the provided data collections, Create case or case-set rights for a user with full access. Full access grants…, Create case or case-set rights from effective ABAC records. Read and write… (+8 more)

### Community 138 - "BaseRepository"
Cohesion: 0.07
Nodes (25): Any, Enum, Return services keyed by their service type., Return repositories keyed by their service type., Create a repository using the configured persistence backend. Args: cls:…, BaseRepository, Any, Hashable (+17 more)

### Community 139 - "api/seq.py"
Cohesion: 0.07
Nodes (35): CreateFileRequestBody, PydanticBaseModel, Represents a base64-encoded file creation request., Expose seqdb API request representations for router composition., ApiPermission, BaseModel, Represents a seqdb command permission in organization API payloads., model_validator (+27 more)

### Community 140 - ".create_crud_cmd"
Cohesion: 0.06
Nodes (32): Any, BaseAbacService, CommonReadOrganizationResultsOnlyPolicy, Filter casedb case-policy reads to visible organizations., Register casedb case-policy commands for organization filtering. Args:…, ReadOrganizationResultsOnlyPolicy, BaseUserManager, BaseRbacService (+24 more)

### Community 141 - ".create_child2_for_upload"
Cohesion: 0.11
Nodes (17): Test scenarios related to Identifiers for Child2 objects., Test 9.1: No Identifiers provided for Child2 - should succeed., Test 9.2.1.1: Existing Identifier with NULL child2 ID - should set child2 ID., Test 9.2.1.2.1: Existing Identifier with same child2 ID - should succeed., Test 9.2.1.2.2: Existing Identifier with different child2 ID - should fail., Test 9.2.2: New Identifier for new child2 - should succeed., Test 9.2.3.1: Multiple Identifiers, some existing for same child2 - should…, Test 9.2.3.1: Multiple Identifiers, some existing for different child2 - should… (+9 more)

### Community 142 - "TestModelSampleBatchForUpload"
Cohesion: 0.08
Nodes (14): Create a SampleForUpload with specified number of SeqForUpload instances., Test reading sample_batch_for_upload1.json as SampleBatchForUpload model., Test reading sample_batch_for_upload2.json as SampleBatchForUpload model., Test valid SampleBatchForUpload with minimal data., Test valid SampleBatchForUpload with alleles., Test valid SampleBatchForUpload with multiple samples including seqs., Test valid SampleBatchForUpload with empty samples list., Test SampleBatchForUpload where all samples contain SeqForUpload instances. (+6 more)

### Community 143 - "UuidSetFilter"
Cohesion: 0.03
Nodes (78): CompositeFilter, CaseCohortLink, CaseQuery, CaseQueryResult, Model, Represents the case identifiers returned for an executed query., Represents a non-persistable link from a case to an OMOP cohort., Return whether the link is a null link, i.e. the case has no linked cohort.… (+70 more)

### Community 144 - "UUID"
Cohesion: 0.07
Nodes (21): UUID, Create a sequence file and return its identifier. Implementations persist file…, Retrieve profiles similar to a specified profile. Args: cmd: Similarity command…, Seq, UUID, Retrieve sequence objects from seqdb by ID., Create a seqdb file under the configured functional user. The command's…, Retrieve similar profile IDs under the configured functional user. The… (+13 more)

### Community 145 - "TestUpdate"
Cohesion: 0.15
Nodes (4): Env, scenario_ids, skipif, TestUpdate

### Community 146 - "SeqdbTestClient"
Cohesion: 0.13
Nodes (17): FileCompression, FileFormat, Encapsulates all supported biological file formats., Encapsulates supported compression methods for biological files., Any, DataCollection, File, Model (+9 more)

### Community 147 - "TestModelBaseSeq"
Cohesion: 0.08
Nodes (17): UUID, Test cases for BaseSeq model validation and functionality., Return a valid DNA sequence for testing., Return an invalid DNA sequence for testing., Compute the expected sequence hash for a given sequence., Test creating BaseSeq with valid DNA sequence., Test that DNA sequences are normalized to lowercase., Test that length is automatically calculated when set to 0. (+9 more)

### Community 148 - "fastapp/api/exc.py"
Cohesion: 0.05
Nodes (32): BadRequest400HTTPException, Forbidden403HTTPException, InternalServerError500HTTPException, MethodNotAllowed405HTTPException, NotImplemented501HTTPException, HTTP exceptions returned by generated API routes., Construct an HTTP 409 exception with optional headers., Construct an HTTP 409 exception with optional headers. (+24 more)

### Community 149 - "Case Type"
Cohesion: 0.07
Nodes (30): ColSet, Disease, Etiology, CaseTypeSetMember (doc), ColSet (doc), ColSetMember (doc), Case Type, Case Type Set Member (+22 more)

### Community 150 - "case_service_retrieve_similar_cases"
Cohesion: 0.11
Nodes (21): case_service_retrieve_similar_cases(), BaseCaseService, Retrieve accessible cases genetically similar to the query cases. Profiles are…, Run `operation`, giving up after the configured timeout. Args: operation: The…, Return the worker pool, creating it on first use., BaseSimilarCasesTestCase, Case, Col (+13 more)

### Community 151 - "DatetimeRangeFilter"
Cohesion: 0.07
Nodes (36): ColType, Classify the representation and semantics of a case-data column., BaseCaseRepository, datetime, UUID, Define backend-independent persistence operations for Casedb case data., Encapsulates case persistence and aggregate statistics reads. Concrete…, Build temporal-resolution date normalization functions. Returns: A mapper for… (+28 more)

### Community 152 - "commondb/repositories/organization_sa.py"
Cohesion: 0.05
Nodes (37): BaseOrganizationRepository, User, UserInvitation, Define the repository interface for commondb organization data., Encapsulates organization-specific user lookup operations for services., Initialize the repository with its user and invitation model classes. Args:…, Determine whether a user exists for a normalized unique key. Args: uow: Unit of…, Retrieve the user associated with a normalized unique key. Args: uow: Unit of… (+29 more)

### Community 153 - "Data Collection"
Cohesion: 0.12
Nodes (28): ColSet, DataCollection, Organization, OrganizationAdminPolicy, User, CaseTypeSet (doc), Case Type Set, Col Set (+20 more)

### Community 154 - "casedb/api/__init__.py"
Cohesion: 0.08
Nodes (31): CaseTypeSetCaseTypeUpdateAssociationRequestBody, ColSetColUpdateAssociationRequestBody, CreateFileForReadSetRequestBody, CreateFileForSeqRequestBody, field_serializer, PydanticBaseModel, Docstring assigned automatically, Docstring assigned automatically (+23 more)

### Community 155 - "Any"
Cohesion: 0.05
Nodes (28): CaseTypeSetCategoryPurpose, DimType, Identify whether a case-type-set category serves content or security., Classify the kind of data grouped by a case-type dimension., Define supported phylogenetic-tree and clustering algorithms., TreeAlgorithmType, Any, field_serializer (+20 more)

### Community 156 - "._verify_permission_exists"
Cohesion: 0.25
Nodes (4): Return entity for permission., Return model for permission., Return command for permission., Verify permission exists.

### Community 157 - "test_casedb_seqdb_connection"
Cohesion: 0.12
Nodes (19): create_root_user_from_claims(), get_existing_root_user(), App, Dynaconf, User, Retrieve the configured root user from an initialized application. Args: cfg:…, Create the configured root user through the application's claim workflow. Args:…, oauth_discovery_settings_file() (+11 more)

### Community 158 - ".create_sample_for_upload"
Cohesion: 0.08
Nodes (17): SeqTaxonomy, Test the _verify_batch_sample_refdata function., Test that _verify_batch_sample_refdata succeeds with empty samples., Test that _verify_batch_sample_refdata succeeds with samples that have no…, Test successful verification when no allele profiles are provided., Test that _verify_refdata fails when new alleles are missing from batch., Helper to create a SampleForUpload with default or specified properties., Test that _verify_refdata gives warning for superfluous alleles in batch. (+9 more)

### Community 159 - ".upload_batch"
Cohesion: 0.11
Nodes (14): Test scenarios related to the on_exists and on_new command parameters., Test 7.1: on_exists=ERROR with existing object - should fail., Test 7.2: on_exists=SKIP with existing object - should skip., Test 7.3: on_exists=UPDATE with existing object - should update., Test 7.4: on_new=CREATE with new object having provided ID - should create., Test 7.5: on_new=SKIP with new object having provided ID - should skip., Test 7.6: on_new=ERROR with new object having provided ID - should fail., Multiple existing identifiers for one parent must resolve to one internal ID. (+6 more)

### Community 160 - "TestModelSeq"
Cohesion: 0.09
Nodes (16): Seq, Test cases for Seq model functionality and inheritance., Create a valid Contig for testing., Create a sample Seq with default values and optional overrides., Test creating Seq with contigs., Test creating Seq without contigs (not available)., Test that Seq inherits HasSampleMixin properties., Test that Seq inherits CodeMixin properties. (+8 more)

### Community 161 - "CaseSet"
Cohesion: 0.09
Nodes (28): Case, Case, CaseAccessAbac, CaseRights, CaseSet, CaseSetAccessAbac, CaseSetForUpload, CaseSetRights (+20 more)

### Community 162 - "CaseType"
Cohesion: 0.08
Nodes (28): CaseQuery, CaseQueryResult, CaseSetQuery, CaseType, CaseTypeAccessAbac, CaseTypeCategory, CaseTypeCol, Col (+20 more)

### Community 163 - "UUID"
Cohesion: 0.07
Nodes (19): Case, CaseSet, CaseSetMember, Col, CrudCommand, Model, RefCol, User (+11 more)

### Community 164 - ".create_local_or_remote_app"
Cohesion: 0.11
Nodes (16): Any, App, Enum, Logger, User, Register an invited user using their invitation token., Update a user's active status, roles, or organization., Update the authenticated user's own organization. (+8 more)

### Community 165 - "InMemoryOrganizationRepository"
Cohesion: 0.08
Nodes (21): NoResultsError, Error for an operation that expected matching data but found none., Initialize a NoResultsError instance., InMemoryOrganizationRepository, make_commondb_user_manager(), make_idps_cfg(), make_mock_organization_service(), make_mock_rbac_service() (+13 more)

### Community 166 - "OrganizationService"
Cohesion: 0.33
Nodes (5): OrganizationService, Any, CommonOrganizationService, Encapsulates handling of organization commands using OmopDB user and invitation…, Initialize the shared service with OmopDB model classes.

### Community 167 - "test_casedb_upload.py"
Cohesion: 0.13
Nodes (23): BaseUploadTestCase, _mock_uow(), scenario_ids, Unit tests for casedb case upload functionality., Tests for existing case data collection handling, including NULL_ID edge case.…, Map commondb role enums to casedb role strings with CASEDB_ prefix., Base test case with common fixtures and utility methods., LSP-3647 regression: CaseBatchUploader.upsert_batch merges incoming content… (+15 more)

### Community 168 - "MockIDPClient"
Cohesion: 0.06
Nodes (31): MockIDPClient, Any, Logger, Request, UUID, Encapsulates identity-provider client that serves configured mock claims., Initialize a MockIDPClient instance., Id the requested value. (+23 more)

### Community 169 - "DummyCmd"
Cohesion: 0.22
Nodes (4): DummyCmd, Command, TestHeadersAndApplyHandler, TestRouteRegistration

### Community 170 - "._create_sample_seq_for_upload"
Cohesion: 0.09
Nodes (16): Create a sample SeqForUpload with default values and optional overrides., Test cases for SeqForUpload model functionality and upload-specific features., Test creating SeqForUpload with basic fields., Test that SeqForUpload inherits all Seq properties., Test SeqForUpload with NULL_ID for sample_id., Test that sample_id serialization handles NULL_ID correctly., Test upload-specific field handling., Test JSON serialization structure of SeqForUpload. (+8 more)

### Community 171 - "OAuth2Client"
Cohesion: 0.10
Nodes (16): demo_client_credentials_flow(), OAuth2Client, Any, OAuth 2.0 Client Test Script This script demonstrates how to use the OAuth 2.0…, Create a new OAuth client., Delete an OAuth client., List all OAuth clients., Simple OAuth 2.0 client for testing. (+8 more)

### Community 172 - "CacheStatistics"
Cohesion: 0.02
Nodes (143): Return the counters observed by this store., AsyncCachedFunction, BoundCachedFunction, CachedFunction, make_cached_function(), Any, Declarative caching of function results. `CachedFunction` is what makes…, Return the logical cache key for one argument combination. A writer that wants… (+135 more)

### Community 173 - "create_mapped_column"
Cohesion: 0.09
Nodes (26): declared_attr, Mapped, Organization, UUID, Map the owning organization ID column., Map the owning organization relationship., Map the optional site ID column., Map the optional site relationship. (+18 more)

### Community 174 - "Protocol"
Cohesion: 0.12
Nodes (28): Identifier Issuer, IdentifierIssuer, File, AstMeasurement, AstPrediction, LocusSet, PcrMeasurement, Protocol (+20 more)

### Community 175 - "Person"
Cohesion: 0.15
Nodes (27): CareSite, ConditionOccurrence, ConditionOccurrenceIdentifier, DeviceExposure, DrugExposure, Location, CareSite (omopdb.md), ConditionOccurrence (omopdb.md) (+19 more)

### Community 176 - "Protocol (seqdb entity)"
Cohesion: 0.13
Nodes (27): AstMeasurement (seqdb entity), AstPrediction (seqdb entity), File (seqdb entity), IdentifierIssuer (seqdb entity), LocusSet (seqdb entity), OrganizationIdentifierIssuerLink (seqdb entity), PcrMeasurement (seqdb entity), Protocol (seqdb entity) (+19 more)

### Community 177 - ".get_case_abac"
Cohesion: 0.40
Nodes (3): Command, Resolve reference-data access control for a command. Args: cmd: Command whose…, Resolve case access control for a command. Args: cmd: Command whose user and…

### Community 178 - "TestCommondbDictModelModifier"
Cohesion: 0.06
Nodes (27): CommondbDictModelModifier, datetime, Hashable, Model, Encapsulates a DictRepository modifier for all databases that use…, Initialize the source of timezone-aware audit timestamps. Args:…, Stamp a new commondb model with creation and modification metadata. Args:…, Refresh modification metadata while preserving the stored creation time. Args:… (+19 more)

### Community 179 - "EndpointTestClient"
Cohesion: 0.09
Nodes (23): EndpointTestClient, Any, Command, CrudCommand, Response, Register a command class with its endpoint-dispatch handler. Args:…, Dispatch a supported command to its corresponding API endpoint. Args: cmd:…, Request identity providers and deserialize the returned list. Args: cmd:… (+15 more)

### Community 180 - "User"
Cohesion: 0.09
Nodes (14): Any, Hashable, User, Update the user's name in the user manager., Get the user key, which uniquely identifies the user across systems, from the…, Construct user instance from identity claims., Create root user from identity claims., Check if claims belong to root user. (+6 more)

### Community 181 - "AuthEnv"
Cohesion: 0.12
Nodes (7): AuthEnv, Self-contained, per-test auth environment built around the real…, Verify that unknown users are auto-created when the flag is on, and rejected…, Verify that a root user can log in for the first time (triggering…, Drive get_existing_user_from_claims directly (no HTTP stack)., TestAutoCreateUser, TestRootUserLogin

### Community 182 - "_DummyMapper"
Cohesion: 0.11
Nodes (12): BaseMapperTestCase, _DummyMapper, _make_mapper(), _make_row_class(), _Model, Any, Hashable, scenario_ids (+4 more)

### Community 183 - "test_fastapp_cache_region.py"
Cohesion: 0.02
Nodes (138): ManualClock, Encapsulates advancing only when a test tells it to. Both readings start at…, Initialize a ManualClock instance., Move the clock forward and return the new reading. Args: seconds: A non-…, Set both readings to an absolute value. Args: value: The new reading. Raises:…, InlineRefreshRunner, Encapsulates refreshing stale entries on the calling thread. This makes a stale…, Random (+130 more)

### Community 184 - "TestGeneratedCrudRoutes"
Cohesion: 0.23
Nodes (8): DummyCrud, DummyModel, DummyQueryFilter, CrudCommand, Model, set_fake_response(), TestGeneratedCrudRoutes, UnsupportedCrud

### Community 185 - "Gen-EpiX README"
Cohesion: 0.11
Nodes (25): pr.sh Helper Script, PR Skill, CASEDB Service, COMMONDB Service, FASTAPP Shared Framework, lsp-data Repository, OMOPDB Service, SEQDB Service (+17 more)

### Community 186 - "casedb.organization.md"
Cohesion: 0.13
Nodes (25): Organization (doc), Organization Set (doc), User (doc), User Invitation (doc), casedb / ORGANIZATION — Simplified ERD, Organization Identifier Issuer Link, Organization, Organization Set (+17 more)

### Community 187 - "._validate_model"
Cohesion: 0.40
Nodes (4): model_validator, Self, Normalize and validate the sequence representation, length, and hash. Derives…, Validate that the content hash matches the content.

### Community 188 - "case_date.py"
Cohesion: 0.11
Nodes (26): case_service_calculate_case_date(), case_service_get_case_date_col_mappers(), case_service_get_case_date_col_mappers_from_cols(), convert_iso_date_to_datetime(), convert_iso_month_to_first_day_datetime(), convert_iso_quarter_to_first_day_datetime(), convert_iso_week_to_first_day_datetime(), convert_iso_year_to_first_day_datetime() (+18 more)

### Community 189 - ".crud"
Cohesion: 0.29
Nodes (5): Any, App, CrudCommand, Initialize mapped user models and cache invalidation handlers. Args: app:…, Execute CRUD while preventing root users from deleting themselves or home.…

### Community 190 - "CommondbRemoteApp"
Cohesion: 0.24
Nodes (7): CommondbRemoteApp, Encapsulates a remote app client for the commondb service with OAuth2/NONE…, _mock_response(), Any, fixture, Test the hand-written (non-CRUD) command handlers., TestNonCrudHandlers

### Community 191 - "computed_field"
Cohesion: 0.13
Nodes (8): computed_field, Return whether the sequence has at least one processed contig., Return the number of contigs in this sequence., Return the total contig length, or zero when no contigs are available., Return the longest contig length, or zero when no contigs are available., Return the shortest contig length, or zero when no contigs are available., Return the median contig length, or zero when no contigs are available., Return the assembly N50 contig length. Returns: The shortest contig length…

### Community 192 - "TestDelete"
Cohesion: 0.17
Nodes (4): Env, scenario_ids, skipif, TestDelete

### Community 193 - "IdentifierIssuer"
Cohesion: 0.08
Nodes (24): Death, DeathIdentifier, DeviceExposureIdentifier, DrugExposureIdentifier, IdentifierIssuer, Death (omopdb.md), DeathIdentifier (omopdb.md), DeviceExposureIdentifier (omopdb.md) (+16 more)

### Community 194 - "test_fastapp_cache_support.py"
Cohesion: 0.03
Nodes (93): CantDeserializeError, Error for a value that could not be converted to its stored form., Error for a stored value that the current code can no longer read. A region…, SerializationError, compute_etag(), HttpCachePolicy, matches_etag(), HTTP-level caching helpers. Caching at the transport boundary is a different… (+85 more)

### Community 195 - "TestNonCrudHandlers"
Cohesion: 0.25
Nodes (4): _mock_response(), Any, Test the hand-written (non-CRUD) command handlers., TestNonCrudHandlers

### Community 196 - "CompositeFilter"
Cohesion: 0.11
Nodes (24): Recursively partition a filter into a SQL-expressible subtree and a remainder…, CompositeFilter, Any, BaseModel, Hashable, model_validator, Self, Match a value using the function generated during validation. Args: value: The… (+16 more)

### Community 197 - "IntervalTransformer"
Cohesion: 0.13
Nodes (13): IntervalTransformer, Return whether `value` matches an interval without mutating an object., Encapsulates mapping a numeric field to its configured interval. Bounds may be…, scenario_ids, Test transform_value method for direct value transformation., Test with Decimal input values., Test cases for IntervalTransformer., Test basic number to interval mapping. (+5 more)

### Community 198 - "log_parser_v2.py"
Cohesion: 0.03
Nodes (64): NoFilter, Any, BaseModel, Hashable, Represents a filter retaining every value unless explicitly inverted., Return the non-inverted pass-through result., Yield a pass-through match for every column value., Yield every column value when the filter is not inverted. (+56 more)

### Community 199 - "map_paired_elements"
Cohesion: 0.18
Nodes (5): map_paired_elements(), Any, Hashable, Group paired values by key while preserving input order for lists. With…, datetime

### Community 200 - "TestCreate"
Cohesion: 0.17
Nodes (4): Env, scenario_ids, skipif, TestCreate

### Community 201 - ".expectBatchProcessed"
Cohesion: 0.10
Nodes (16): scenario_ids, Test upload with varying batch sizes., Test 8.1: Upload batch of n new parent objects., Test 8.2: Upload parent with varying number of Child1 objects., Test scenarios related to object existence in repository., Test 1.1: ID not provided or NULL_ID - object does not exist and needs to be…, Test 1.2: ID provided by batch creator (new_id); object does not exist yet -…, Test scenarios related to providing different combinations of child objects. (+8 more)

### Community 202 - "EvictionStrategy"
Cohesion: 0.02
Nodes (52): Initialize a MemoryBackend instance. Args: max_weight: Total weight the store…, CountMinSketch, create_eviction_strategy(), EvictionStrategy, FIFOEviction, LFUEviction, LRUEviction, ABC (+44 more)

### Community 203 - "IdpClient"
Cohesion: 0.07
Nodes (20): IdpClient, Request, SSLContext, UUID, Encapsulates the base client for an external identity provider., Initialize a IdpClient instance., Get identity provider configuration., Extract claims from JWT token. (+12 more)

### Community 204 - "UUID"
Cohesion: 0.13
Nodes (11): LocusType, Encapsulates the biological feature classification represented by a locus., field_serializer, field_validator, UUID, Normalize a JSON locus-ID list to UUID objects., Serialize ordered locus identifiers as strings., Normalize a JSON locus-code map and enforce its key length limit. (+3 more)

### Community 205 - "Registry"
Cohesion: 0.10
Nodes (15): Any, Decorator to register a transformer factory function., Encapsulates named constructors for configured transformers., Register a transformer class by name., Register a factory function for creating transformer instances., Create a named transformer, preferring a registered factory over a class. Args:…, List all available transformer names., Decorator for registering transformer classes. (+7 more)

### Community 206 - "test_cfg_log_level.py"
Cohesion: 0.20
Nodes (16): _build_test_fixture(), _DummyHandler, _DummyLogger, _extract_diagnostic_payload(), _patch_logging_get_logger(), _patch_runtime_logger_dict(), MonkeyPatch, scenario_ids (+8 more)

### Community 207 - "generate_seq_distances.py"
Cohesion: 0.09
Nodes (32): computed_field, Represents a set of samples intended for upload, together with any new…, Indicates whether there are any read sets in the sample set., Indicates whether there are any sequences in the sample set., Indicates whether there are any seq taxonomies in the sample set., Indicates whether there are any seq classifications in the sample set., Indicates whether there are any sequence profiles in the sample set., Indicates whether there are any PCR measurements in the sample set. (+24 more)

### Community 208 - "scenario_ids"
Cohesion: 0.10
Nodes (12): scenario_ids, Test ValidationError when id doesn't match computed seq_hash., Test valid Identifier with identifier_issuer_code., Test valid Identifier with identifier_issuer_id., Test valid Identifier with both issuer fields., Test ValidationError when both issuer fields are missing., Test field length validation., Test valid AlleleForUpload with locus_id. (+4 more)

### Community 209 - "._validate_case_for_upload"
Cohesion: 0.24
Nodes (6): model_validator, Self, Validate sample ID and assembly protocol., Validate column uniqueness and alternate sample identifier mappings., Validate that read sets and sequences use disjoint columns. Raises: ValueError:…, Validate sample ID and sequencing protocol.

### Community 210 - ".read_all"
Cohesion: 0.11
Nodes (10): Print all organisations to stdout., Print all data collections to stdout., Print all users with their organisations and roles to stdout., Print all organisation admin policies to stdout., Print all identifier issuers to stdout., Print all organisation-identifier issuer links to stdout., Retrieve all users via the app as the root user., Retrieve all users that have the given role. (+2 more)

### Community 211 - "test_commondb_auth.py"
Cohesion: 0.18
Nodes (13): make_cdb_invitation(), make_cdb_organization(), parametrize, scenario_ids, UserInvitation, UUID, Unit tests for commondb auth – uses the real…, Return a valid future-expiring UserInvitation. (+5 more)

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
Cohesion: 0.16
Nodes (21): Python & Pytest Conventions, Diagnose-before-editing workflow, test.util.mock_compat, pytest-run skill, Test behavior, not implementation details, Gen-EpiX Agent Guide, Graphify architecture query workflow, Claude Code Root Config (+13 more)

### Community 216 - "Linter"
Cohesion: 0.19
Nodes (5): Linter, Path, Runs the specified linting tool with the provided command-line arguments. This…, This class provides an interface to run linting tools like mypy, pylint, ruff,…, Runs a series of linting and formatting tools on the gen-epix project. This…

### Community 217 - "TestCaseUpload"
Cohesion: 0.09
Nodes (20): CaseUploadSetup, get_test_client(), Any, Case, Env, fixture, scenario_ids, skip (+12 more)

### Community 218 - "TestCasedbEdgeCasesAccess"
Cohesion: 0.12
Nodes (14): get_test_client(), Env, fixture, integration, scenario_ids, User, Test that a root user can create a case and that the created case is…, Test that a root user can create a case that belongs to 2 data collections and… (+6 more)

### Community 219 - "TestCommondbModelProcessMetadata"
Cohesion: 0.10
Nodes (15): get_test_client(), Env, fixture, integration, scenario_ids, modified_at must be set by the backend on creation., modified_by must be set to the creating user's id., created_at must not change when a record is updated. (+7 more)

### Community 220 - "UserManager"
Cohesion: 0.18
Nodes (7): MockUser, Any, BaseModel, BaseUserManager, Hashable, User, UserManager

### Community 221 - "TestModelSeqProfileForUpload"
Cohesion: 0.08
Nodes (13): Test JSON serialization of AlleleProfileForUpload., Test valid AlleleProfileForUpload with codes., Test valid AlleleProfileForUpload with IDs., Test valid AlleleProfileForUpload with allele_ids., Test valid AlleleProfileForUpload with locus_allele_id_map., Test valid AlleleProfileForUpload with locus_code_map when using allele_ids., Test ValidationError when both protocol fields are missing., Test ValidationError when both locus_set fields are missing. (+5 more)

### Community 222 - "fastapp shared application framework"
Cohesion: 0.13
Nodes (20): casedb domain, commondb shared package, Dynaconf-based configuration, fastapp shared application framework, filter and transform support packages, IDP modes (IDPS, MOCK, NONE), omopdb domain, Repository mode parity (DICT, SA_SQLITE, SA_SQL) (+12 more)

### Community 223 - "lock.py"
Cohesion: 0.04
Nodes (37): Executor, See base method. A process-local store needs no distributed mutex, so a plain…, AsyncSingleFlight, _Call, NullMutex, Any, Protocol, Concurrency primitives that keep one loader per key. Without coordination, the… (+29 more)

### Community 224 - "TestCreate"
Cohesion: 0.21
Nodes (4): Env, scenario_ids, skipif, TestCreate

### Community 225 - "SeqdbEndpointTestClient"
Cohesion: 0.08
Nodes (20): Represents retrieval of sample identifiers matching a query. These identifiers…, Represents retrieval of complete data for sample identifiers. The result…, RetrieveSamplesByIdCommand, RetrieveSamplesByQueryCommand, Retrieve complete samples by identifier. Args: cmd: Sample-retrieval command to…, Retrieve samples matching a query. Args: cmd: Sample-query command to execute.…, Retrieve full sample records by their IDs., Retrieve samples matching the given query. (+12 more)

### Community 226 - "convert"
Cohesion: 0.20
Nodes (5): Any, Reconstruct a nucleotide sequence from a NextClade representation. Args:…, convert(), parametrize, TestNextcladeSequenceConversion

### Community 227 - "BaseSeqDistancePerformance"
Cohesion: 0.27
Nodes (7): BaseSeqDistancePerformance, ensure_datasets_exist_and_valid(), get_test_client(), Env, fixture, parametrize, RepositoryType

### Community 228 - "ClientStore"
Cohesion: 0.04
Nodes (31): ClientStore, Any, OAuth 2.0 Client Store This module manages OAuth 2.0 client registration and…, Retrieve a client by client ID., Delete a client from the store., Deactivate a client (soft delete)., List all active clients., Check if a client exists and is active. (+23 more)

### Community 229 - "sa_model/geo.py"
Cohesion: 0.26
Nodes (11): Base, RowMetadataMixin, Define SQLAlchemy persistence mappings for casedb geographic models., Persist the casedb RegionSet domain model., Persist the casedb RegionSetShape domain model., Persist the casedb Region domain model., Persist the casedb RegionRelation domain model., Region (+3 more)

### Community 230 - ".__init__"
Cohesion: 0.33
Nodes (5): Any, App, BaseAbacRepository, Logger, Initialize ABAC model, command, policy, and role mappings. Args: app:…

### Community 231 - "casedb/api/router.py"
Cohesion: 0.05
Nodes (49): create_abac_endpoints(), Any, APIRouter, App, Exception, FastAPI, NoReturn, Register casedb ABAC endpoints through the shared commondb API adapter. (+41 more)

### Community 232 - "CircuitBreaker"
Cohesion: 0.04
Nodes (40): Return the default failure policy implied by the configuration. A configured…, CircuitBreaker, FailurePolicy, BaseException, Return the state, moving an expired open breaker to half open., Open the breaker and start its reset timer., Encapsulates bounding the wall-clock duration of a backend call. The call runs…, Initialize a TimeoutGuard instance. Args: timeout: Seconds allowed for one… (+32 more)

### Community 233 - "make_cdb_user"
Cohesion: 0.12
Nodes (10): get_name_from_claims(), Get the name from the claims, checking against a list of possible name claims., make_cdb_user(), Pure unit tests for claim name-extraction helpers and update_user_name., Verify the real UserManager writes the name change to the repo., Verify the root-token time-to-live enforcement. A *very* short TTL (1 second)…, Build an AuthEnv with a pre-stored root user., Return a fresh commondb User with the given attributes. (+2 more)

### Community 234 - "TestCasedbMetadataMasking"
Cohesion: 0.13
Nodes (14): get_test_client(), CaseType, Env, fixture, integration, scenario_ids, User, Verifies that MaskModelProcessMetadataPolicy is correctly wired in casedb. Root… (+6 more)

### Community 235 - "TestCaseTypeAccessAbac"
Cohesion: 0.22
Nodes (3): scenario_ids, TestCaseTypeAccessAbac, TestCaseTypeShareAbac

### Community 236 - "test_read_config.py"
Cohesion: 0.29
Nodes (17): _assert_default_import_payload(), _assert_string_override_payload(), override_tmp_dir(), fixture, parametrize, Path, scenario_ids, Construct and compose an app config, returning key config/auth values. (+9 more)

### Community 237 - "TestDataLineageMixin"
Cohesion: 0.13
Nodes (11): FieldInfo, scenario_ids, Tests for the DataLineageMixin class. DataLineageMixin is a plain mixin (not a…, DataLineageMixin should declare a provenance_id annotation., DataLineageMixin should declare a source_traceback annotation., The provenance_id Field should have a default of None., The source_traceback Field should have a default of None., The source_traceback Field should enforce max_length=255. (+3 more)

### Community 238 - "ServerManager"
Cohesion: 0.11
Nodes (7): Test OAuth Client Credentials flow with missing token., Test that OAuth discovery endpoint is working., Test that JWKS endpoint is working., Test client management endpoints., Any, Server manager to handle startup of multiple servers including: - casedb -…, ServerManager

### Community 239 - "Organization (commondb.organization entity)"
Cohesion: 0.22
Nodes (17): Contact (commondb.organization entity), IdentifierIssuer (commondb.organization entity), Organization (commondb.organization entity), OrganizationIdentifierIssuerLink (commondb.organization entity), Site (commondb.organization entity), User (commondb.organization entity), UserInvitation (commondb.organization entity), commondb / ORGANIZATION — Simplified ERD (+9 more)

### Community 240 - ".__init__"
Cohesion: 0.06
Nodes (35): AuthException, CredentialsAuthError, DataException, NotNullConstraintViolationError, Any, Initialize a UniqueConstraintViolationError instance., Error for data that omits a required field., Initialize a NotNullConstraintViolationError instance. (+27 more)

### Community 241 - "case_service_crud_case_set_data_collection_link"
Cohesion: 0.24
Nodes (13): CaseSetDataCollectionLinkCrudCommand, Represent CRUD operations for case-set-to-data-collection links., case_service_crud_case_set_data_collection_link(), _crud_case_set_data_collection_link_with_abac(), _crud_case_set_data_collection_link_without_abac(), BaseCaseService, CaseSetDataCollectionLink, UUID (+5 more)

### Community 242 - "Domain"
Cohesion: 0.07
Nodes (22): Domain, Hashable, Initialize a Domain instance., Name the requested value., Description the requested value., Entities the requested value., Encapsulates registering the metadata that defines an application's domain., Permissions the requested value. (+14 more)

### Community 243 - ".create_read_set_for_upload"
Cohesion: 0.16
Nodes (6): ReadSetForUpload, SeqForUpload, Tests for the has_case guard added to _get_upload_samples_command., Tests for the casedb-to-seqdb upload bridge in CaseBatchUploader., TestCaseUploadSeqdbBridge, TestGetUploadSamplesCommandNoCaseGuard

### Community 244 - "UUID"
Cohesion: 0.12
Nodes (17): Child1, Child1ForUpload, model_validator, Self, Validate that either ref1_id or ref1_code is provided., ParentForUpload, UUID, Duplicate-ID detection converts per-item hard failures into soft FAILED results. (+9 more)

### Community 245 - "AuthTestClient"
Cohesion: 0.08
Nodes (17): AuthTestClient, MockJWKAndToken, get_test_client(), fixture, parametrize, patch, scenario_ids, Test the OidcClient retrieve_jwt_with_client_credentials_flow method. (+9 more)

### Community 246 - "CasedbEndpointTestClient"
Cohesion: 0.27
Nodes (7): CreateCaseSetRequestBody, Docstring assigned automatically, CasedbEndpointTestClient, Any, App, FastAPI, Response

### Community 247 - "Organization"
Cohesion: 0.15
Nodes (16): Contact, Contact (omopdb.md), Organization (omopdb.md), OrganizationAdminPolicy (omopdb.md), OrganizationSet (omopdb.md), Site (omopdb.md), User (omopdb.md), UserInvitation (omopdb.md) (+8 more)

### Community 248 - "IdentifierIssuer (omopdb.organization entity)"
Cohesion: 0.12
Nodes (16): ConditionOccurrenceIdentifier (omopdb.omop / OMOP CDM entity), Death (omopdb.omop / OMOP CDM entity), DeathIdentifier (omopdb.omop / OMOP CDM entity), DeviceExposureIdentifier (omopdb.omop / OMOP CDM entity), DrugExposureIdentifier (omopdb.omop / OMOP CDM entity), MeasurementIdentifier (omopdb.omop / OMOP CDM entity), NoteIdentifier (omopdb.omop / OMOP CDM entity), NoteNlp (omopdb.omop / OMOP CDM entity) (+8 more)

### Community 249 - "Organization"
Cohesion: 0.14
Nodes (16): Contact, IdentifierIssuer, Contact (omopdb.organization.md), IdentifierIssuer (omopdb.organization.md), Organization (omopdb.organization.md), OrganizationSetMember (omopdb.organization.md), Site (omopdb.organization.md), User (omopdb.organization.md) (+8 more)

### Community 250 - "CrudCommand"
Cohesion: 0.11
Nodes (24): CaseIdentifierCrudCommand, CaseSetCategoryCrudCommand, CaseSetStatusCrudCommand, CaseTypeSetCategoryCrudCommand, GeneticDistanceProtocolCrudCommand, CrudCommand, Represent CRUD operations for alternate and external case identifiers., Represent CRUD operations for categories used to tag case sets. (+16 more)

### Community 251 - "seqdb/api/router.py"
Cohesion: 0.06
Nodes (38): create_auth_endpoints(), Any, APIRouter, App, Exception, FastAPI, NoReturn, ServiceType (+30 more)

### Community 252 - "UserManager"
Cohesion: 0.08
Nodes (25): Any, BaseRbacService, BaseUserManager, User, UUID, Construct a user from claims and configured automatic-user defaults. Args:…, Determine whether identity claims belong to the configured root user. Args:…, Determine whether a user has the configured root role. Args: user: User whose… (+17 more)

### Community 253 - "validate_int_for_uuid_field"
Cohesion: 0.11
Nodes (22): Validate that the input value is either a UUID or an integer that can be…, validate_int_for_uuid_field(), Any, field_validator, UUID, Normalize measurement concept identifiers to UUID form., Truncate too long values with an ellipsis, as the database field is limited to…, Normalize observation concept identifiers to UUID form. (+14 more)

### Community 254 - "test_logging_runtime_contract.py"
Cohesion: 0.28
Nodes (15): JSONDict, _emit_log_level_resolution_payloads(), _emit_log_level_resolution_payloads_for_both_modes(), _emit_runtime_payloads_for_all_yaml_paths(), _emit_runtime_payloads_via_dictconfig(), _has_message(), _load_class(), parametrize (+7 more)

### Community 255 - "check_docstrings.py"
Cohesion: 0.09
Nodes (37): audit_file(), check_coverage(), check_exception_classes(), check_package(), check_pydantic(), check_raises(), decorator_name(), has_decorator() (+29 more)

### Community 256 - "TokenStore"
Cohesion: 0.07
Nodes (18): Set up test fixtures before each test method., Test TokenStore initialization., Set up test fixtures before each test method., Delete a refresh token and its associated access token., Revoke all tokens for a specific client., Remove all expired tokens from the store., List all active (non-expired) tokens, optionally filtered by client., Check if a token exists and is not expired. (+10 more)

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

### Community 261 - "validate_int_key_args"
Cohesion: 0.10
Nodes (24): Validate and synchronize integer-based primary key arguments. Mutates ``data``…, validate_int_key_args(), generate_ulid(), int_to_uuid(), UUID, Generate a new UUID backed by a ULID. Returns: A UUID whose underlying ULID…, Derive a deterministic UUID from an unsigned 64-bit integer. The integer is…, _int_field_name() (+16 more)

### Community 262 - "sa/repository.py"
Cohesion: 0.05
Nodes (37): cached, User, Move a user to an organization and replace their case policies. Behaviour: -…, Compute effective case rights for a persisted user. Application administrators…, Compute reference-data access from roles and organization policies. Reference-…, Command, User, UUID (+29 more)

### Community 263 - "SAUnitOfWork"
Cohesion: 0.12
Nodes (14): Exception, Self, Session, TracebackType, Enter the managed context., Exit the managed context., Encapsulates a unit of work class wrapping the SQLAlchemy session. The context…, Initialize a SAUnitOfWork instance. (+6 more)

### Community 264 - ".upload_batch"
Cohesion: 0.11
Nodes (20): SpecimenIdentifier, Test scenarios related to Identifiers for Specimen objects., Test 8.1: Specimen without Identifiers - should succeed., Test 8.2.1.1: Existing Identifier with NULL specimen ID - should set specimen…, Test 8.2.1.2.1: Existing Identifier with same specimen ID - should succeed., Test 8.2.1.2.2: Existing Identifier with different specimen ID - should fail., A retried derived-specimen chain (e.g. a repeat culture attempt) that carries…, Test 8.2.2: New Identifier for new specimen - should succeed. (+12 more)

### Community 265 - "test_fastapp_app_log_summarise.py"
Cohesion: 0.09
Nodes (35): _LargeListCommand, _make_user(), Command, scenario_ids, User, TDD tests for _summarise_command_object(), the helper that prevents large list…, When disabled in config, command.object preserves full lists., Config can tune max_list_items and sample_items. (+27 more)

### Community 266 - "TestRead"
Cohesion: 0.28
Nodes (4): Env, scenario_ids, skipif, TestRead

### Community 267 - "_make_cmd"
Cohesion: 0.25
Nodes (6): _make_cmd(), _make_user(), scenario_ids, User, Build a UserCrudCommand bypassing field validation., TestModelMetadataPolicy

### Community 268 - "`gen_epix.fastapp.cache`"
Cohesion: 0.06
Nodes (34): 10. Observability, 11. Testing, 12. Worked example: local cache in a service, 13.1 What must be replaced, 13.2 A Redis backend, 13.3 A Redis tag index, 13.4 A Redis version store, 13.5 A Redis invalidation bus (+26 more)

### Community 269 - "person_validator.py"
Cohesion: 0.08
Nodes (25): DomainBaseOmopService, Represents a request to retrieve person IDs based on a query. These IDs can…, RetrievePersonsByQueryCommand, Retrieve persons matching a query. Args: cmd: Command containing person-query…, BaseOmopService, Encapsulates an omopdb service, by providing additional implementation details…, Expose the concrete service handling OmopDB OMOP commands., Person-upload validation and transformation extension points. (+17 more)

### Community 270 - "BaseAppComposer"
Cohesion: 0.15
Nodes (8): BaseAppComposer, Dynaconf, Encapsulates dependencies and repository construction for concrete app…, Initialize abstract composition state placeholders. Raises:…, Return the application's resolved Dynaconf settings., Return the API dependency that resolves registered users., Return the API dependency that resolves new users., Return the API dependency that resolves identity-provider users.

### Community 271 - "CaseStats"
Cohesion: 0.13
Nodes (21): CaseStats, model_validator, Self, Represents aggregate statistics for cases or a case set. Model validation: Own…, Validate count and case-date invariants., Retrieve statistics per case type., Retrieve statistics per case set., get_all_case_type_ids() (+13 more)

### Community 272 - "TestCommondbMetadataMasking"
Cohesion: 0.16
Nodes (11): DataCollection, Env, fixture, integration, scenario_ids, User, Only APP_ADMIN or ROOT users can see created_at, modified_at, and modified_by,…, Register root1_1 + org1, then invite an org_user and an org_admin. (+3 more)

### Community 273 - "test_model.py"
Cohesion: 0.15
Nodes (5): scenario_ids, Unit tests for ModelNoId.set_modified and ModelNoId.set_created. Test coverage:…, # TODO: check scenario ids, how are they determined?, TestSetCreated, TestSetModified

### Community 274 - "TestHttpTimeoutConfiguration"
Cohesion: 0.15
Nodes (9): DerivedRemoteApp, Minimal subclass of CommondbRemoteApp for testing timeout configuration., Test HTTP timeout configuration per command class., DerivedRemoteApp has DEFAULT_HTTP_TIMEOUTS configured., DerivedRemoteApp can be initialized., _create_remote_app applies DEFAULT_HTTP_TIMEOUTS to remote app., Base CommondbRemoteApp has empty DEFAULT_HTTP_TIMEOUTS., Timeout configuration works independently of auth protocol. (+1 more)

### Community 275 - "test_error_code_unicity"
Cohesion: 0.25
Nodes (13): _extract_hex_strings_from_file(), _get_all_seen_codes(), _get_python_files(), _get_repo_root(), _hanlde_duplicate_hex_codes(), _is_long_hex_string(), Path, scenario_ids (+5 more)

### Community 276 - "SeqProfileForUpload"
Cohesion: 0.09
Nodes (19): Return ordered allele identifiers in their encoded profile representation., Return ordered MLVA repeat numbers in their JSON profile representation., Return the deterministic content hash for ordered allele identifiers., model_validator, Self, SeqProfile, Represents a sequence profile record intended for upload. Equal to a…, Format representation names for a validation error message. (+11 more)

### Community 277 - "Unit"
Cohesion: 0.31
Nodes (6): ConceptSet, Identify units supported by casedb column and concept metadata., Unit, StrEnum, Concept, RefCol

### Community 278 - "App (command dispatcher / PEP)"
Cohesion: 0.17
Nodes (13): Command-Based Execution Model, Policy Enforcement Timing (BEFORE/DURING/AFTER), App (command dispatcher / PEP), BaseRbacService, CrudEndpointGenerator, PolicyDecisionPoint, Policy (is_allowed/get_content/filter hooks), RbacPolicy (+5 more)

### Community 279 - "Organization (omopdb.organization entity)"
Cohesion: 0.29
Nodes (13): OrganizationAdminPolicy (omopdb.abac entity), omopdb / ABAC — Simplified ERD, omopdb — Full Database ERD (detailed, 69 entities), omopdb — Full Database ERD (simplified, 69 entities), Contact (omopdb.organization entity), Organization (omopdb.organization entity), OrganizationIdentifierIssuerLink (omopdb.organization entity), Site (omopdb.organization entity) (+5 more)

### Community 280 - "ConceptRelationType"
Cohesion: 0.10
Nodes (15): ConceptRelationType, ConceptSetType, Classify the language or value scale represented by a concept set., Identify supported semantic relationships between concepts., Any, field_serializer, field_validator, Normalize supported concept properties from a mapping or JSON string. (+7 more)

### Community 281 - "RetrieveGeneticSequenceFastaByIdCommand"
Cohesion: 0.20
Nodes (8): Command, Define casedb commands that retrieve sequence data from seqdb., Represent a request for genetic sequences identified by ID., Represent a request for genetic sequences in FASTA format. The response is an…, RetrieveGeneticSequenceByIdCommand, RetrieveGeneticSequenceFastaByIdCommand, Retrieve genetic sequence data in FASTA format by identifier. Args: cmd: FASTA…, Return seqdb's FASTA iterator for the requested sequence IDs. Args: cmd: Casedb…

### Community 282 - "casedb/domain/command/abac.py"
Cohesion: 0.11
Nodes (19): OrganizationAccessCasePolicyCrudCommand, OrganizationShareCasePolicyCrudCommand, CrudCommand, Define casedb commands for case access and sharing policies., Represent CRUD operations for organization-level case access policies. Policies…, Represent CRUD operations for per-user case access policies. Effective rights…, Represent CRUD operations for organization case-sharing policies. Policies…, Represent CRUD operations for per-user case-sharing policies. User permissions… (+11 more)

### Community 283 - "HandleAuthExceptionMiddleware"
Cohesion: 0.05
Nodes (38): HandleAuthExceptionMiddleware, App, BaseHTTPMiddleware, Exception, FastAPI, Logger, Request, Response (+30 more)

### Community 284 - "ReadOrganizationResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadOrganizationResultsOnlyPolicy, Encapsulates restrictions on shared organization results according to OmopDB…, Initialize organization-scoped command metadata for OmopDB., ReadOrganizationResultsOnlyPolicy

### Community 285 - "ReadOrganizationResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadOrganizationResultsOnlyPolicy, Encapsulates restricting result reads to the caller's authorized organization…, Initialize the shared policy with seqdb command-attribute mappings., ReadOrganizationResultsOnlyPolicy

### Community 286 - "seq/service.py"
Cohesion: 0.05
Nodes (43): Represents CRUD command metadata for sequence profile records., SeqProfileCrudCommand, SeqProfile, Handle a CRUD command for sequence-profile entities. Args: cmd: Typed sequence-…, _get_not_implemented_message(), CrudCommand, Format an unsupported CRUD-operation message including the caller's roles., SeqProfile (+35 more)

### Community 287 - "commondb/api/organization.py"
Cohesion: 0.10
Nodes (29): Re-export commondb API endpoint factories and request/response schemas. The…, ApiPermission, create_organization_endpoints(), DataCollectionSetDataCollectionUpdateAssociationRequestBody, InviteUserRequestBody, OrganizationIdentifierIssuerUpdateAssociationRequestBody, OrganizationSetOrganizationUpdateAssociationRequestBody, Any (+21 more)

### Community 288 - "FullSample"
Cohesion: 0.21
Nodes (12): AstMeasurement, FullSample, IdentifierIssuer, AstMeasurement (seqdb.seq.md), ReadSetIdentifier (seqdb.seq.md), SampleIdentifier (seqdb.seq.md), SeqIdentifier (seqdb.seq.md), SeqProfileIdentifier (seqdb.seq.md) (+4 more)

### Community 289 - "JsonFormatter"
Cohesion: 0.41
Nodes (12): casedb Debug Logging Config, casedb Logging Config, commondb Debug Logging Config, JsonFormatter, commondb Logging Config, Log Level Tuning Rationale (sqlalchemy/httpx/asyncio), UvicornAccessLogFilter, omopdb Debug Logging Config (+4 more)

### Community 290 - ".set_obj"
Cohesion: 0.18
Nodes (9): Organization, OrganizationAdminPolicy, OrganizationIdentifierIssuerLink, Store an object locally, optionally replacing an existing entry. Args: obj:…, Create an organization and store it in the local object store., Create an organization admin policy and store it in the local object store., Create an identifier issuer and store it in the local object store., Create an organization-identifier issuer link and store it in the local object… (+1 more)

### Community 291 - "MemoryTagIndex"
Cohesion: 0.07
Nodes (16): MemoryTagIndex, ABC, Forget `key` and remove it from every tag., Remove `tag` and return the keys that carried it., Forget every association., Return the tags currently known to the index., Encapsulates keeping tag associations in process memory. The index holds both…, Initialize a MemoryTagIndex instance. (+8 more)

### Community 292 - ".create_case"
Cohesion: 0.27
Nodes (6): Case, datetime, parametrize, UUID, Existing case should maintain its created_in_data_collection_id., Existing cases must not be changed to a different created_in_data_collection_id.

### Community 293 - ".create_uploader"
Cohesion: 0.23
Nodes (3): After re-validation, case_date set by calculate_case_date must not be reset to…, read_fields row[1] keys may be UUID objects (DICT) or strings (SQL); both must…, TestExistingContentKeyNormalization

### Community 294 - "TestValidateIntForUuidField"
Cohesion: 0.08
Nodes (15): parametrize, Types other than UUID, int, str, or None should raise ValueError., A negative integer should raise because int_to_uuid uses unsigned bytes., Converting the same integer twice should yield the same UUID., Different integers should produce different UUIDs., Types other than UUID, str, or None should raise ValueError., Tests for the validate_int_for_uuid_field function., A UUID input should be returned unchanged. (+7 more)

### Community 295 - "BasePersonUploadTestCase"
Cohesion: 0.09
Nodes (20): BasePersonUploadTestCase, scenario_ids, Base test case with common fixtures and utilities for person upload tests., Test combinations of different scenarios., Test scenarios related to person existence in repository., Test 1.1: ID not provided or NULL_ID - person does not exist and needs to be…, Test 1.2: ID provided by batch creator (new_id); person does not exist yet -…, Test scenarios related to person_id links in child objects. (+12 more)

### Community 296 - "PersonBatchForUpload"
Cohesion: 0.10
Nodes (15): PersonBatchForUpload, Any, computed_field, Represents a set of persons intended for upload, together with any new…, Indicates whether there are any measurements in the person set., Indicates whether there are any observations in the person set., Indicates whether there are any specimens in the person set., Total number of persons in the batch. (+7 more)

### Community 297 - "test_client_credential_flow.py"
Cohesion: 0.10
Nodes (21): oauth_server(), fixture, Test OAuth OIDC Client Credential Authentication Flow This module implements a…, Start and manage ReceiverApp for the test session., Create RequestorApp instance., Start and manage OAuth server for the test session., receiver_app(), requestor_app() (+13 more)

### Community 298 - "IdpClient hierarchy"
Cohesion: 0.20
Nodes (11): AuthService (concrete), IdpClient hierarchy, MockIDPClient (no-auth dev/CI), OauthIdpClient (real OIDC), BaseUserManager, Authentication (Identity Resolution Layer), User Resolution (claims -> local User), Add New IDP Configuration (+3 more)

### Community 299 - "Protocol"
Cohesion: 0.20
Nodes (11): AstMeasurement, LocusSet, AstMeasurement (seqdb.md), LocusSet (seqdb.md), PcrMeasurement (seqdb.md), Protocol (seqdb.md), ProtocolSetMember (seqdb.md), PcrMeasurement (+3 more)

### Community 300 - "api/system.py"
Cohesion: 0.10
Nodes (24): create_system_endpoints(), FeatureFlagsResponseBody, HealthResponseBody, HealthStatus, LicensesResponseBody, LogItem, LogRequestBody, Any (+16 more)

### Community 301 - "command/geo.py"
Cohesion: 0.12
Nodes (16): Command, CrudCommand, Define casedb commands for geographic regions and region sets., Represent a request for regions containing specified regions., Represent CRUD operations for geographic region sets., Represent CRUD operations for geographic regions., Represent CRUD operations for relationships between regions., Represent CRUD operations for shapes associated with region sets. (+8 more)

### Community 302 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseAbacService, Initialize role mappings and organization-ID resolvers. Args: abac_service:…

### Community 303 - "Command"
Cohesion: 0.10
Nodes (11): Command, Commands the requested value., Return service type for command., Return command for name., Return permissions for command., Return permission for command instance., Return and initialize a command class's canonical name., Return and initialize the permissions required by a command class. (+3 more)

### Community 304 - "BaseRemoteService"
Cohesion: 0.15
Nodes (9): Remote application service exports., BaseRemoteService, Any, App, Command, setter, Encapsulates the base service that forwards commands to a remote application., Initialize a BaseRemoteService instance. (+1 more)

### Community 305 - "PayerPlanPeriod"
Cohesion: 0.21
Nodes (11): Cost, PayerPlanPeriod, Any, DataLineageMixin, field_validator, Model, UUID, Normalize payer-plan-period concept identifiers to UUID form. (+3 more)

### Community 306 - "Transformer Framework"
Cohesion: 0.25
Nodes (11): FallbackTransformer, FieldTransformer, ObjectAdapter, RetryTransformer, Streaming Pipeline Performance Rationale, StreamingPipeline, Transformer, Transformer Framework (+3 more)

### Community 307 - ".get_user"
Cohesion: 0.44
Nodes (5): Env, skip, User, UUID, TestManual

### Community 308 - "rewrite_parametrized_dependency_markers"
Cohesion: 0.33
Nodes (6): pytest_collection_modifyitems(), pytest_collection_modifyitems(), pytest_collection_modifyitems(), pytest_collection_modifyitems(), Rewrite class-level dependency 'depends' markers to include parametrize IDs.…, rewrite_parametrized_dependency_markers()

### Community 309 - "CaseTypeAccessAbac"
Cohesion: 0.22
Nodes (6): CaseTypeAccessAbac, Represents effective access rights for one case type and data collection., Return whether at least one access right is granted., Any, User, TestRetrieveCompleteCaseType

### Community 310 - ".expectStatusCount"
Cohesion: 0.13
Nodes (13): ParentUploadResult, Test scenarios related to Identifiers for parent objects., Test 6.1: No Identifiers provided - should succeed., Test 6.2.1.1: Existing Identifier with NULL parent ID - should set parent ID., Test 6.2.1.2.1: Existing Identifier with same parent ID - should succeed., Test 6.2.1.2.2: Existing Identifier with different parent ID - should fail., Test 6.2.2: New Identifier for new parent - should succeed., Test 6.2.3.1: Multiple Identifiers, some existing for same parent - should… (+5 more)

### Community 311 - "test_omopdb_model.py"
Cohesion: 0.24
Nodes (15): Location, The LOCATION table represents a generic way to capture physical location or…, common_data(), Encoder, location_data(), measurement_data(), observation_data(), person_data() (+7 more)

### Community 312 - "env"
Cohesion: 0.31
Nodes (5): env(), fixture, FixtureRequest, Return a test client configured for either DICT or SA_SQLITE demo repos. The…, TestRetrieveSamples

### Community 313 - "erm_mermaid.py"
Cohesion: 0.15
Nodes (19): _annotation_to_mermaid_type(), _build_diagram(), _field_marker(), MermaidErmGenerator, BaseModel, Domain, Path, Mermaid-based ERM diagram generator. Produces Mermaid ``erDiagram`` markdown… (+11 more)

### Community 314 - "LogParser2"
Cohesion: 0.24
Nodes (5): LogParser2, DataFrame, A class to parse and export logsas produced directly by the application or as…, Parses the log file and sorts the user journey logs. This method reads the log…, Exports the sorted user journey logs to a CSV and a pickle file. This method…

### Community 315 - "AppComposer (Composition Root)"
Cohesion: 0.22
Nodes (10): System Composition (four FastAPI apps sharing a model), AppCfg (logger init, settings load, settings validation), AppComposer (Composition Root), AppImplDetails (state bag), create_fast_api Assembly (lifespan, middleware, routers, OpenAPI), Entry Point app.py (SCHEMA_KWARGS, APP_CFG, APP_COMPOSER, FAST_API), Exception Handling (api/exc.py, handle_exception/handle_command), Repository + Service Loop (compose_application/_initialize_repository) (+2 more)

### Community 316 - "Region Set"
Cohesion: 0.22
Nodes (10): Region, RegionSet, Region (doc), Region Relation (doc), Region Set (doc), Region Set Shape (doc), Region, Region Relation (+2 more)

### Community 317 - "Sample"
Cohesion: 0.27
Nodes (10): AstPrediction, AstPrediction (seqdb.md), Sample (seqdb.md), Seq (seqdb.md), SeqClassification (seqdb.md), SeqTaxonomy (seqdb.md), Sample, Seq (+2 more)

### Community 318 - "SeqTaxonomy"
Cohesion: 0.20
Nodes (10): RefSeq (seqdb.seq.md), SeqTaxonomy (seqdb.seq.md), Taxon (seqdb.seq.md), TaxonSet (seqdb.seq.md), TaxonSetMember (seqdb.seq.md), RefSeq, SeqTaxonomy, Taxon (+2 more)

### Community 319 - "command/case.py"
Cohesion: 0.02
Nodes (106): CreateCaseSetCommand, CreateFileForReadSetCommand, CreateFileForSeqCommand, BaseModel, Command, field_validator, UUID, Define casedb commands for case schemas, content, sets, and sequence links. (+98 more)

### Community 320 - "CommondbSAMapper"
Cohesion: 0.25
Nodes (8): CommondbSAMapper, Any, Hashable, Model, Create a mapper that enforces commondb audit metadata behavior. Args:…, Encapsulates a SAMapper subclass for all databases that use RowMetadataMixin.…, Update a SQLAlchemy row from a domain model using commondb metadata rules.…, Dump a domain model while hiding protected audit metadata. For users without…

### Community 321 - "FieldType"
Cohesion: 0.09
Nodes (12): Get the field names of the entity. Parameters ---------- by_alias : bool,…, Get the ID field name of the entity. Parameters ---------- by_alias : bool,…, Get the link field names of the entity. Parameters ---------- by_alias : bool,…, Get the relationship field names of the entity. Parameters ---------- by_alias…, Get the value field names of the entity. Parameters ---------- by_alias : bool,…, FieldType, Encapsulates this enumeration is used to categorize the different types of…, Get row field names by field type. (+4 more)

### Community 322 - "command/omop.py"
Cohesion: 0.09
Nodes (21): ConceptAncestorCrudCommand, ConceptClassCrudCommand, ConceptRelationshipCrudCommand, DeviceExposureCrudCommand, DrugExposureIdentifierCrudCommand, FactRelationshipCrudCommand, NoteNlpIdentifierCrudCommand, Commands for OMOP CRUD operations, person upload, and retrieval. (+13 more)

### Community 323 - "CdmSource"
Cohesion: 0.21
Nodes (10): CdmSource, Metadata, Any, field_validator, Model, UUID, Normalize metadata concept identifiers to UUID form., The CDM_SOURCE table contains detail about the source database and the process… (+2 more)

### Community 324 - "renovate.json"
Cohesion: 0.20
Nodes (9): config:best-practices, dev, automerge, baseBranchPatterns, extends, packageRules, prConcurrentLimit, prHourlyLimit (+1 more)

### Community 325 - "TestUpdate"
Cohesion: 0.29
Nodes (5): Env, scenario_ids, skipif, Anonymize and deactivate a user's personal information., TestUpdate

### Community 326 - "TestSQLInjection"
Cohesion: 0.31
Nodes (6): get_test_client(), Env, fixture, scenario_ids, Session, TestSQLInjection

### Community 327 - "BaseCommondbRemoteAppTestCase"
Cohesion: 0.10
Nodes (14): BaseCommondbRemoteAppTestCase, scenario_ids, Test OAuth2 configuration validation during initialization., Raise error when OAuth2 requires discovery URL., Raise error when OAuth2 requires client ID., Raise error when OAuth2 requires scope., Raise error for OIDC auth protocol (not yet supported)., Test create_local_or_remote_app class method. (+6 more)

### Community 328 - "TestAnonymizeUser"
Cohesion: 0.18
Nodes (7): scenario_ids, Include each user ID so forgotten users in one organization remain unique., Verify anonymization of the target user., Set up test fixtures., Anonymize personal fields and deactivate the anonymized user., Anonymize personal fields and deactivate the anonymized user., TestAnonymizeUser

### Community 329 - "ServiceTestClient"
Cohesion: 0.12
Nodes (13): env(), fixture, FixtureRequest, TestRepository, Any, Model, ServiceType, ServiceTestClient (+5 more)

### Community 330 - "TestOIDCProvider"
Cohesion: 0.03
Nodes (37): Test discovery document includes correct supported claims., Test discovery document includes correct authentication methods., Test discovery document includes correct signing algorithms., Test discovery document includes additional OIDC features., Test creating a basic ID token., Test creating ID token with nonce., Test creating ID token with explicit auth_time., Test creating ID token with additional claims. (+29 more)

### Community 331 - "Concept Relation"
Cohesion: 0.28
Nodes (9): Concept, Concept Relation, Concept Set, Concept (doc), Concept Relation (doc), Concept, ConceptSet, Concept (doc concept) (+1 more)

### Community 332 - "Outage (commondb.system entity)"
Cohesion: 0.25
Nodes (9): Outage (commondb.system entity), commondb / SYSTEM — Simplified ERD, IdentityProvider (omopdb.auth entity), IDPUser (omopdb.auth entity), omopdb / AUTH — Simplified ERD, IdentityProvider (seqdb.auth entity), IDPUser (seqdb.auth entity), seqdb / AUTH — Simplified ERD (+1 more)

### Community 333 - "Protocol"
Cohesion: 0.28
Nodes (9): Protocol (seqdb.seq.md), ProtocolSetMember (seqdb.seq.md), SeqDistance (seqdb.seq.md), SeqProfile (seqdb.seq.md), Protocol, ProtocolSet, ProtocolSetMember, SeqDistance (+1 more)

### Community 334 - "DictUnitOfWork"
Cohesion: 0.18
Nodes (7): In-memory dictionary-backed repository exports., Return a no-op unit-of-work suitable for the in-memory backend., DictUnitOfWork, Dictionary repository unit-of-work implementation., Commit the requested value., Rollback the requested value., Encapsulates a unit of work for the in-memory dictionary repository.

### Community 335 - "crud_allele.py"
Cohesion: 0.33
Nodes (5): Implement seqdb CRUD service operations for services.seq.crud_allele., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign…

### Community 336 - "crud_ast_measurement.py"
Cohesion: 0.12
Nodes (15): AstMeasurementCrudCommand, Represents CRUD command metadata for antimicrobial-susceptibility measurements., AstMeasurement, Handle a CRUD command for AST measurement entities. Args: cmd: Typed AST-…, AstMeasurement, UUID, Implement seqdb CRUD service operations for services.seq.crud_ast_measurement., Handle CRUD operations for AST measurement entities. Args: self: Sequence… (+7 more)

### Community 337 - "crud_ast_prediction.py"
Cohesion: 0.12
Nodes (15): AstPredictionCrudCommand, Represents CRUD command metadata for antimicrobial-susceptibility predictions., AstPrediction, Handle a CRUD command for AST prediction entities. Args: cmd: Typed AST-…, AstPrediction, UUID, Implement seqdb CRUD service operations for services.seq.crud_ast_prediction., Handle CRUD operations for AST prediction entities. Args: self: Sequence… (+7 more)

### Community 338 - "Copilot Chat Prompt Steering Coach"
Cohesion: 0.10
Nodes (20): Context Ingestion, Copilot Chat Prompt Steering Coach, Debugging a failing test, Edge Cases and Anti-Patterns, Evaluation Framework, Evidence and Certainty, Explaining or reviewing code, Inputs (+12 more)

### Community 339 - "crud_locus.py"
Cohesion: 0.12
Nodes (15): LocusCrudCommand, Represents CRUD command metadata for locus records., Locus, Handle a CRUD command for locus entities. Args: cmd: Typed locus CRUD command…, Locus, UUID, Implement seqdb CRUD service operations for services.seq.crud_locus., Handle CRUD operations for locus entities. Args: self: Sequence service… (+7 more)

### Community 340 - "crud_locus_set.py"
Cohesion: 0.12
Nodes (15): LocusSetCrudCommand, Represents CRUD command metadata for locus-set records., LocusSet, Handle a CRUD command for locus-set entities. Args: cmd: Typed locus-set CRUD…, LocusSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_locus_set., Handle CRUD operations for locus-set entities. Args: self: Sequence service… (+7 more)

### Community 341 - "crud_pcr_measurement.py"
Cohesion: 0.12
Nodes (15): PcrMeasurementCrudCommand, Represents CRUD command metadata for PCR measurement records., PcrMeasurement, Handle a CRUD command for PCR measurement entities. Args: cmd: Typed PCR-…, PcrMeasurement, UUID, Implement seqdb CRUD service operations for services.seq.crud_pcr_measurement., Handle CRUD operations for PCR measurement entities. Args: self: Sequence… (+7 more)

### Community 342 - "crud_protocol_set.py"
Cohesion: 0.12
Nodes (15): ProtocolSetCrudCommand, Represents CRUD command metadata for sequence protocol-set records., ProtocolSet, Handle a CRUD command for protocol-set entities. Args: cmd: Typed protocol-set…, ProtocolSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_protocol_set., Handle CRUD operations for protocol-set entities. Args: self: Sequence service… (+7 more)

### Community 343 - "crud_protocol_set_member.py"
Cohesion: 0.12
Nodes (15): ProtocolSetMemberCrudCommand, Represents CRUD command metadata for sequence protocol-set memberships., ProtocolSetMember, Handle a CRUD command for protocol-set membership entities. Args: cmd: Typed…, ProtocolSetMember, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for protocol-set membership entities. Args: self:… (+7 more)

### Community 344 - "crud_ref_seq.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for reference sequence records., RefSeqCrudCommand, RefSeq, Handle a CRUD command for reference-sequence entities. Args: cmd: Typed…, RefSeq, UUID, Implement seqdb CRUD service operations for services.seq.crud_ref_seq., Handle CRUD operations for reference-sequence entities. Args: self: Sequence… (+7 more)

### Community 345 - "crud_sample_data_collection_link.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for sample data-collection links., SampleDataCollectionLinkCrudCommand, SampleDataCollectionLink, Handle a CRUD command for sample-data-collection link entities. Args: cmd:…, SampleDataCollectionLink, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for sample-data-collection link entities. Args: self:… (+7 more)

### Community 346 - "crud_sample_identifier.py"
Cohesion: 0.06
Nodes (28): field_validator, UUID, Require every requested sample identifier to occur at most once., Represents retrieval of only SampleIdentifier records for sample identifiers.…, Require every requested sample identifier to occur at most once., Represents CRUD command metadata for sample identifier records., RetrieveSampleIdentifiersByIdCommand, SampleIdentifierCrudCommand (+20 more)

### Community 347 - "crud_seq.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for assembled sequence records., SeqCrudCommand, Seq, Handle a CRUD command for sequence entities. Args: cmd: Typed sequence CRUD…, Seq, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq., Handle CRUD operations for sequence entities. Args: self: Sequence service… (+7 more)

### Community 348 - "crud_seq_category.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for sequence category records., SeqCategoryCrudCommand, SeqCategory, Handle a CRUD command for sequence-category entities. Args: cmd: Typed…, SeqCategory, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_category., Handle CRUD operations for sequence-category entities. Args: self: Sequence… (+7 more)

### Community 349 - "crud_seq_category_set.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for sequence category-set records., SeqCategorySetCrudCommand, SeqCategorySet, Handle a CRUD command for sequence-category-set entities. Args: cmd: Typed…, SeqCategorySet, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_category_set., Handle CRUD operations for sequence-category-set entities. Args: self: Sequence… (+7 more)

### Community 350 - "crud_seq_distance.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for pairwise sequence-distance records., SeqDistanceCrudCommand, SeqDistance, Handle a CRUD command for sequence-distance entities. Args: cmd: Typed…, SeqDistance, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_distance., Handle CRUD operations for sequence-distance entities. Args: self: Sequence… (+7 more)

### Community 351 - "crud_seq_taxonomy.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for sequence taxonomy records., SeqTaxonomyCrudCommand, SeqTaxonomy, Handle a CRUD command for sequence-taxonomy entities. Args: cmd: Typed…, SeqTaxonomy, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_taxonomy., Handle CRUD operations for sequence-taxonomy entities. Args: self: Sequence… (+7 more)

### Community 352 - "crud_taxon.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for taxon records., TaxonCrudCommand, Taxon, Handle a CRUD command for taxon entities. Args: cmd: Typed taxon CRUD command…, Taxon, UUID, Implement seqdb CRUD service operations for services.seq.crud_taxon., Handle CRUD operations for taxon entities. Args: self: Sequence service… (+7 more)

### Community 353 - "crud_taxon_set.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for taxon-set records., TaxonSetCrudCommand, TaxonSet, Handle a CRUD command for taxon-set entities. Args: cmd: Typed taxon-set CRUD…, TaxonSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_taxon_set., Handle CRUD operations for taxon-set entities. Args: self: Sequence service… (+7 more)

### Community 354 - ".create_measurement_for_upload"
Cohesion: 0.15
Nodes (12): PersonIdentifier, date, datetime, UUID, Test person with all child types and Identifiers., Test batch with multiple persons having different child type combinations., Create a test MeasurementForUpload with integer concept IDs. Required concept…, Create a test ObservationForUpload with integer concept IDs. Required concept… (+4 more)

### Community 355 - "dependency"
Cohesion: 0.22
Nodes (9): dependency, ModuleTestCreate, ModuleTestDelete, ModuleTestRead, ModuleTestUpdate, TestCreate, TestDelete, TestRead (+1 more)

### Community 356 - "TestVerifyUserRights"
Cohesion: 0.36
Nodes (4): Role, User, Tests for RBAC verification in CaseBatchUploader.verify_user_rights., TestVerifyUserRights

### Community 357 - "TestDelete"
Cohesion: 0.33
Nodes (5): Env, scenario_ids, skipif, RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…, TestDelete

### Community 358 - "dependency"
Cohesion: 0.22
Nodes (9): dependency, ModuleTestCreate, ModuleTestDelete, ModuleTestRead, ModuleTestUpdate, TestCreate, TestDelete, TestRead (+1 more)

### Community 359 - "test_logging_yaml.py"
Cohesion: 0.47
Nodes (8): parametrize, Path, scenario_ids, Contract tests for all production logging.yaml configuration files. These tests…, test_console_handler_uses_json_formatter(), test_root_logger_is_present_and_uses_console_handler(), test_third_party_loggers_explicitly_configured(), test_uvicorn_access_has_structured_filter()

### Community 360 - "TestDelete"
Cohesion: 0.33
Nodes (5): Env, scenario_ids, skipif, RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…, TestDelete

### Community 361 - "dependency"
Cohesion: 0.22
Nodes (9): dependency, ModuleTestCreate, ModuleTestDelete, ModuleTestRead, ModuleTestUpdate, TestCreate, TestDelete, TestRead (+1 more)

### Community 362 - "env"
Cohesion: 0.36
Nodes (5): env(), fixture, FixtureRequest, Return a test client configured for either DICT or SA_SQLITE demo repos. The…, TestRetrievePersons

### Community 363 - "TestDelete"
Cohesion: 0.33
Nodes (5): Env, scenario_ids, skipif, RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…, TestDelete

### Community 364 - "dependency"
Cohesion: 0.22
Nodes (9): dependency, ModuleTestCreate, ModuleTestDelete, ModuleTestRead, ModuleTestUpdate, TestCreate, TestDelete, TestRead (+1 more)

### Community 365 - "CacheConfigurationError"
Cohesion: 0.13
Nodes (16): CacheConfigurationError, Error for an invalid or contradictory cache configuration., Return the field names referenced by a format string. Args: template: The…, _template_field_names(), _as_scope_parts(), Any, Build a region, register it and return it. Args: config: The declarative policy…, Create every region described by a settings mapping. Args: settings: Region… (+8 more)

### Community 366 - "crud_ref_allele.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for reference allele records., RefAlleleCrudCommand, RefAllele, Handle a CRUD command for reference-allele entities. Args: cmd: Typed…, RefAllele, UUID, Implement seqdb CRUD service operations for services.seq.crud_ref_allele., Handle CRUD operations for reference-allele entities. Args: self: Sequence… (+7 more)

### Community 367 - "crud_sample.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for sample records., SampleCrudCommand, Sample, Handle a CRUD command for sample entities. Args: cmd: Typed sample CRUD command…, Sample, UUID, Implement seqdb CRUD service operations for services.seq.crud_sample., Handle CRUD operations for sample entities. Args: self: Sequence service… (+7 more)

### Community 368 - "crud_seq_classification.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for sequence classification records., SeqClassificationCrudCommand, SeqClassification, Handle a CRUD command for sequence-classification entities. Args: cmd: Typed…, SeqClassification, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for sequence-classification entities. Args: self:… (+7 more)

### Community 369 - "crud_seq_identifier.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for sequence identifier records., SeqIdentifierCrudCommand, SeqIdentifier, Handle a CRUD command for sequence-identifier entities. Args: cmd: Typed…, SeqIdentifier, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_identifier., Handle CRUD operations for sequence-identifier entities. Args: self: Sequence… (+7 more)

### Community 370 - "BaseRepository (abstract)"
Cohesion: 0.25
Nodes (8): Layer Boundaries principle, BaseRepository (abstract), BaseService, DictRepository (in-memory backend), SARepository (SQLAlchemy backend), Repository Modes (DICT_DEMO/EMPTY, SA_SQLITE_DEMO/EMPTY, SA_SQL), Architectural Constraints table, Copilot Chat + Repo Docs Guide

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

### Community 376 - "Enum"
Cohesion: 0.07
Nodes (25): CaseClassification, CaseRightSet, ColConceptSetType, ColRelation, ColTypeOrder, ConceptSetTypeSet, DimColTypeSet, FeatureFlag (+17 more)

### Community 377 - "casedb/repositories/__init__.py"
Cohesion: 0.05
Nodes (41): BaseGeoRepository, Define the repository contract for Casedb geographic reference data., Provide the shared repository base for geographic persistence., BaseOntologyRepository, Define the repository contract for Casedb ontology reference data., Provide the shared repository base for ontology persistence., AbacDictRepository, BaseAbacRepository (+33 more)

### Community 378 - "Any"
Cohesion: 0.11
Nodes (12): Any, Enum, field_validator, Hashable, Key, model_validator, Convert enum name values to their string values., Set a persistable entity's default identifier field. (+4 more)

### Community 379 - "EngineFactory"
Cohesion: 0.22
Nodes (6): EngineFactory, Engine, Thread-safe SQLAlchemy engine factory., Encapsulates creation and management of SQLAlchemy engines., Initialize a EngineFactory instance., Create a new SQLAlchemy engine or return an existing one for the given…

### Community 380 - ".__init__"
Cohesion: 0.25
Nodes (7): OrganizationDictRepository, Any, CommonOrganizationDictRepository, Hashable, Model, Encapsulates shared organization persistence with OmopDB user model types., Initialize shared organization storage with OmopDB model classes.

### Community 381 - ".__init__"
Cohesion: 0.25
Nodes (7): OrganizationDictRepository, Any, CommonOrganizationDictRepository, Hashable, Model, Encapsulates seqdb persistence behavior for organization dictionaries., Initialize the repository with seqdb user and invitation model types. Args:…

### Community 382 - "TestRead"
Cohesion: 0.39
Nodes (4): Env, scenario_ids, skipif, TestRead

### Community 383 - "TestRead"
Cohesion: 0.39
Nodes (4): Env, scenario_ids, skipif, TestRead

### Community 384 - "TestUpdate"
Cohesion: 0.36
Nodes (4): Env, scenario_ids, skipif, TestUpdate

### Community 385 - "TestRead"
Cohesion: 0.39
Nodes (4): Env, scenario_ids, skipif, TestRead

### Community 386 - "TestUpdate"
Cohesion: 0.36
Nodes (4): Env, scenario_ids, skipif, TestUpdate

### Community 387 - "OAuth 2.0 Provider with OpenID Connect Support"
Cohesion: 0.43
Nodes (8): client_store.py, demo_client.py, OAuth 2.0 Provider with OpenID Connect Support, jwks.py, oidc_provider.py, server.py (OAuth FastAPI app), token_store.py, validators.py

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

### Community 393 - "crud_seq_profile_identifier.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for sequence profile identifier records., SeqProfileIdentifierCrudCommand, SeqProfileIdentifier, Handle a CRUD command for sequence-profile identifier entities. Args: cmd:…, SeqProfileIdentifier, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for sequence-profile identifier entities. Args: self:… (+7 more)

### Community 394 - "SeqService"
Cohesion: 0.05
Nodes (32): CalculateSeqDistancesForNewProfilesCommand, Command, Represents calculating and storing distances between new and existing sequence…, Represents creating missing distances for profiles under a distance protocol.…, Represents retrieval of sequences in FASTA format. as an iterable that yields…, Represents retrieval of the last modified datetime for a SeqDistance protocol.…, RetrieveSeqDistanceLastModifiedCommand, RetrieveSeqFastaCommand (+24 more)

### Community 395 - "._make_user"
Cohesion: 0.16
Nodes (12): BaseReadUserPolicyTestCase, User, UUID, Test organization admin read behavior., READ_ALL for org admin should include users in admin orgs and admins, including…, READ_SOME should raise when any user is outside admin orgs., Base test case with common fixtures and utilities., READ_ONE for org admin allows inactive user in admin orgs. (+4 more)

### Community 396 - "._validate_content"
Cohesion: 0.29
Nodes (5): model_validator, Self, UUID, Validate the profile-distance-map content and reset its unused hash., Decode the stored JSON profile-distance map. Returns: Distances keyed by…

### Community 397 - "EdgeCaseSpec"
Cohesion: 0.16
Nodes (10): EdgeCaseSpec, Declarative specification for a single ABAC edge case. Captures all relevant…, parametrize, skip, For each edge case, assert that the set of accessible CaseTypes exactly matches…, For each edge case, assert that the set of accessible CaseTypeSets exactly…, For each edge case, assert that the set of accessible ColSets exactly matches…, For each edge case, assert that the set of accessible cols exactly matches the… (+2 more)

### Community 398 - "crud_col_set_member.py"
Cohesion: 0.22
Nodes (14): ColSetMemberCrudCommand, Represent CRUD operations for column-set membership., case_service_crud_col_set_member(), _crud_col_set_member_with_abac(), _crud_col_set_member_without_abac(), BaseCaseService, ColSetMember, UUID (+6 more)

### Community 399 - "sa_model/ontology.py"
Cohesion: 0.21
Nodes (15): Concept, ConceptRelation, ConceptSet, Disease, EtiologicalAgent, Etiology, Base, RowMetadataMixin (+7 more)

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

### Community 408 - ".create_file_for_read_set"
Cohesion: 0.29
Nodes (4): UUID, Create a file associated with a read set column., Create a file associated with a sequence column., Check whether the user owns each of the given cases.

### Community 409 - "._validate_model"
Cohesion: 0.40
Nodes (4): model_validator, Self, Derive or validate the deterministic identifier UUID., Require an issuer UUID or code.

### Community 410 - "BaseSAMapper"
Cohesion: 0.06
Nodes (22): BaseSAMapper, MappedColumn, Get row field names by field type set., Get the row ID column., Encapsulates an abstract mapper between SQLAlchemy rows and Pydantic models. It…, Create a SAMapper instance for model and row classes., Get a field name map between model and row fields. If one of the fields does…, Return the row ID column. (+14 more)

### Community 411 - ".__init__"
Cohesion: 0.29
Nodes (5): Command, Hashable, User, Initialize a RbacPolicy instance., Return whether allowed.

### Community 412 - "IsOrganizationAdminPolicy"
Cohesion: 0.29
Nodes (6): IsOrganizationAdminPolicy, Any, BaseAbacService, CommonIsOrganizationAdminPolicy, Encapsulates organization-administrator checks using the OmopDB role map., Initialize the policy with OmopDB users and role mappings.

### Community 413 - "UpdateUserPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonUpdateUserPolicy, Encapsulates shared user-update checks with OmopDB role and user mappings., Initialize the user-update policy with OmopDB dependencies., UpdateUserPolicy

### Community 414 - "IsOrganizationAdminPolicy"
Cohesion: 0.29
Nodes (6): IsOrganizationAdminPolicy, Any, BaseAbacService, CommonIsOrganizationAdminPolicy, Encapsulates organization-admin checks using seqdb roles and user models., Configure the shared policy with seqdb role and user mappings.

### Community 415 - "ReadUserPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadUserPolicy, Encapsulates authorizing user reads with seqdb roles and organization-admin…, Configure the shared policy with seqdb authorization dependencies., ReadUserPolicy

### Community 416 - "UpdateUserPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonUpdateUserPolicy, Encapsulates authorizing user updates with seqdb roles and user model mappings., Configure the shared policy with seqdb role and user mappings., UpdateUserPolicy

### Community 417 - "retrieve_complete_case_type.py"
Cohesion: 0.12
Nodes (14): case_service_retrieve_complete_case_type(), BaseCaseService, Assemble complete case-type metadata filtered by the caller's ABAC access., # TODO: performance improvement, commented out for now to preserve baseline, # TODO: performance improvement, commented out for now to preserve baseline, Assemble case-type metadata and its effective collection access. Columns and…, # TODO: performance improvement, commented out for now to preserve baseline, # TODO: performance improvement, commented out for now to preserve baseline (+6 more)

### Community 419 - "OAuth Client Credential Flow Test"
Cohesion: 0.53
Nodes (6): OAuth Client Credential Flow Test, OAuthServerManager, ReceiverApp, ReceiverAppCLI, ReceiverAppManager, RequestorApp

### Community 420 - "Command"
Cohesion: 0.19
Nodes (9): Command, PydanticBaseModel, Return the registered URL for the given command, raising if not found., Get headers for the command. Override to include e.g. authorization header., Get the timeout in seconds for a specific command class. Returns the custom…, Set a custom timeout for a specific command class. This will be used instead of…, Get an httpx.Client instance with the appropriate SSL context and timeout for…, Execute an HTTP request for a command and method and return the parsed JSON… (+1 more)

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

### Community 426 - "EtlLogItem"
Cohesion: 0.10
Nodes (11): Get all data issues that are errors., EtlLogItem, BaseModel, Append a WARN-severity log item., Append an INFO-severity log item., Return a list of log items with ERROR severity., Return a list of log items with WARN severity., Return a list of log items with INFO severity. (+3 more)

### Community 427 - "BaseRbacServiceTestCase"
Cohesion: 0.14
Nodes (10): BaseRbacServiceTestCase, Base test case with common fixtures and utilities., Set up test fixtures., Create a test command., Test user authorization behavior methods., Test that retrieve_user_is_root returns False by default., Test that retrieve_user_is_root can be overridden in concrete implementation., Test that retrieve_user_is_non_rbac_authorized returns False by default in… (+2 more)

### Community 428 - "ConcreteRbacService"
Cohesion: 0.17
Nodes (11): ConcreteRbacService, Any, App, BaseRbacService, Hashable, UUID, Concrete implementation of BaseRbacService for testing., Retrieve roles for a user. (+3 more)

### Community 429 - "TestUserPermissions"
Cohesion: 0.12
Nodes (9): Test user permission retrieval and authorization checks., Test that user permissions are union of all their role permissions., Test that user with no roles has no permissions., Test that user has all RBAC permissions when they actually do., Test that user doesn't have all RBAC permissions when missing some., Test checking if user has more permissions than another user., Test checking if user has more permissions than a set of roles., Test that user doesn't have more permissions when they're a subset. (+1 more)

### Community 430 - "OrganizationService"
Cohesion: 0.33
Nodes (5): OrganizationService, Any, CommonOrganizationService, Encapsulates organization operations using casedb user model types., Initialize organization handling with casedb model specializations. Args:…

### Community 431 - "TestOIDCProviderIntegration"
Cohesion: 0.12
Nodes (9): Integration tests for OIDCProvider with real JWKSManager., Set up test fixtures., Test complete ID token creation and validation workflow., Test discovery document and JWKS endpoint integration., Test userinfo endpoint with scope-based claim filtering., Test nonce validation integrated with ID token workflow., Test claims extraction integrated with userinfo response., Test logout workflow integration. (+1 more)

### Community 432 - "3.8 Comments and Docstrings"
Cohesion: 0.13
Nodes (13): Audit Script, Preferred Structure, Procedure, Write Python Docstrings, 3.8.1 Docstrings, 3.8.2.1 Test modules, 3.8.2 Modules, 3.8.3.1 Overridden Methods (+5 more)

### Community 433 - "omopdb/repositories/organization_sa.py"
Cohesion: 0.22
Nodes (7): OrganizationSARepository, Any, CommonOrganizationSARepository, Engine, SQLAlchemy organization repository configured with OmopDB user models., Encapsulates shared organization persistence with OmopDB SQLAlchemy model types., Initialize shared SQL organization storage with OmopDB model classes.

### Community 434 - "._validate_content"
Cohesion: 0.32
Nodes (5): model_validator, Self, Reserve post-validation for future content-hash verification., Reserve post-validation for future content-hash verification., Reserve post-validation for future content-hash verification.

### Community 435 - "OrganizationService"
Cohesion: 0.33
Nodes (5): OrganizationService, Any, CommonOrganizationService, Encapsulates seqdb organization service behavior., Initialize organization operations with seqdb invitation constraints. Args:…

### Community 436 - "release-please-config.json"
Cohesion: 0.40
Nodes (4): include-component-in-tag, packages, pull-request-title-pattern, $schema

### Community 439 - "app"
Cohesion: 0.67
Nodes (3): app(), mock_client(), fixture

### Community 440 - "test_debug_console_uses_json_formatter"
Cohesion: 0.40
Nodes (4): parametrize, Path, scenario_ids, test_debug_console_uses_json_formatter()

### Community 441 - "command/ontology.py"
Cohesion: 0.18
Nodes (14): ConceptCrudCommand, ConceptRelationCrudCommand, ConceptSetCrudCommand, DiseaseCrudCommand, EtiologicalAgentCrudCommand, EtiologyCrudCommand, CrudCommand, Define casedb commands for concepts, diseases, and etiologies. (+6 more)

### Community 442 - "._filter_users_by_organization"
Cohesion: 0.18
Nodes (10): Any, BaseAbacService, Command, User, UUID, Filter or reject results according to their direct organization IDs. Args:…, Filter or reject results associated with users in visible organizations. Args:…, Initialize role mappings and the command types supported by each filter. Args:… (+2 more)

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

### Community 449 - "UUID"
Cohesion: 0.23
Nodes (9): Any, field_validator, UUID, Normalize the drug concept identifier to UUID form., Normalize dose-era concept identifiers to UUID form., Normalize cohort-definition concept identifiers to UUID form., Normalize episode concept identifiers to UUID form., Normalize the episode-event field concept identifier to UUID form. (+1 more)

### Community 450 - "._validate_state"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate column-type requirements and prohibited linked metadata.

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

### Community 457 - "get_test_client"
Cohesion: 0.50
Nodes (4): get_test_client(), Env, fixture, FixtureRequest

### Community 458 - "TestcasedbEdgeCasesRefDataAccess"
Cohesion: 0.16
Nodes (10): integration, scenario_ids, User, Helper method to retrieve a user by name from the test client environment., Root user should have access to all CaseTypes regardless of policies (superuser…, take first edge case spec as a representative case (since disease access is not…, similar to test_disease_access_matches_all but for etiological agents instead…, Assert that all created CaseTypeSet categories are accessible to any user,… (+2 more)

### Community 459 - "TestOauthIdpClientIntrospection"
Cohesion: 0.25
Nodes (3): Any, scenario_ids, TestOauthIdpClientIntrospection

### Community 460 - "_PytestMockConfig"
Cohesion: 0.50
Nodes (3): Any, _PytestMockConfig, Minimal config shim needed by pytest-mock's backend resolver.

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

### Community 469 - "AuthorizationCodeStore"
Cohesion: 0.18
Nodes (6): AuthorizationCode, AuthorizationCodeStore, datetime, Authorization Code Store In-memory storage for OAuth 2.0 Authorization Codes…, Representation of an OAuth 2.0 authorization code., In-memory store managing authorization codes.

### Community 470 - ".validate_model"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate references and replace all derived ordering fields in place.

### Community 471 - "Any"
Cohesion: 0.14
Nodes (8): Any, Create an OpenID Connect ID Token., Validate only the signature of a JWT token without checking claims., Decode JWT header without verification., Decode JWT payload without verification (use carefully!)., Create a JWT token with the given payload., Verify and decode a JWT token., Get the public keys in JWKS format.

### Community 472 - "CaseTypeSetCaseTypeUpdateAssociationCommand"
Cohesion: 0.18
Nodes (9): CaseTypeSetCaseTypeUpdateAssociationCommand, ColSetColUpdateAssociationCommand, UpdateAssociationCommand, Represent replacement of the case types in a case-type set. The provided…, Represent replacement of the columns in a column set. The provided members keep…, CaseTypeSetMember, ColSetMember, Update case type associations for a case type set. (+1 more)

### Community 473 - "case_service_crud_col_set"
Cohesion: 0.23
Nodes (13): ColSetCrudCommand, Represent CRUD operations for reusable column sets., case_service_crud_col_set(), _crud_col_set_with_abac(), _crud_col_set_without_abac(), BaseCaseService, ColSet, UUID (+5 more)

### Community 475 - "DiseaseEtiologicalAgentUpdateAssociationCommand"
Cohesion: 0.33
Nodes (5): DiseaseEtiologicalAgentUpdateAssociationCommand, UpdateAssociationCommand, Represent replacement of the etiological agents for a disease. Existing…, Etiology, Update etiological agent associations for a disease.

### Community 476 - "CasedbRemoteApp"
Cohesion: 0.10
Nodes (12): CasedbRemoteApp, Any, Case, PhylogeneticTree, Retrieve the full definition of a case type., Encapsulates remote casedb command dispatch over HTTP. Initialization first…, Retrieve cases by their IDs., Retrieve access rights for cases. (+4 more)

### Community 477 - "case_service_crud_ref_dim"
Cohesion: 0.24
Nodes (13): Represent CRUD operations for reusable reference dimensions., RefDimCrudCommand, case_service_crud_ref_dim(), _crud_ref_dim_with_abac(), _crud_ref_dim_without_abac(), BaseCaseService, RefDim, UUID (+5 more)

### Community 478 - "Enum"
Cohesion: 0.19
Nodes (8): Enum, Path, Copy repository files to a new folder and update the configuration.…, Copy repository files to a new folder and update the configuration.…, Copy the repository file for one service type to tgt_dir., Copy a repository file while applying the destination-exists policy. Args:…, Enum class for the service types of this application., Enum class for the repository types of this application.

### Community 484 - "model_validator"
Cohesion: 0.20
Nodes (8): model_validator, Self, Validate consistency between upload status and error logs., Synchronize this upload ID with the contained parent model ID., Validate child-parent references and uniqueness within this parent., Validate unique parent IDs and external identifiers., Validate unique child IDs and external identifiers., Validate that all links between children are within the same parent.

### Community 485 - "._validate_some_criteria"
Cohesion: 0.50
Nodes (3): model_validator, Self, Require at least one last-modified datetime boundary.

### Community 486 - "._validate_state"
Cohesion: 0.50
Nodes (3): model_validator, Self, Ensure tree leaf names and profile identifiers are consistent.

### Community 517 - "ModelFieldProps"
Cohesion: 0.14
Nodes (13): complete_stored_model_field_props(), Any, Command, Domain, Hashable, Model, Complete stored model field properties with defaults for missing fields. Args:…, Register service types, models, and commands with a domain. When models or… (+5 more)

### Community 518 - "KeyedMutex"
Cohesion: 0.16
Nodes (9): KeyedMutex, Acquire the mutex belonging to `key`. Args: key: The cache key being…, Release the mutex belonging to `key`. Args: key: The key whose mutex is held.…, Return whether a regeneration is in progress for `key`., Decrement the user count of `key` and forget an unused mutex., Encapsulates handing out one mutex per key and discarding it when unused.…, Initialize a KeyedMutex instance., A per-key lock registry must not grow with the key space. (+1 more)

### Community 519 - "User"
Cohesion: 0.16
Nodes (9): Command, User, Check if user is authorized via non-RBAC mechanism., Create another test command., Test command for testing. Name starts with _ to avoid warning due to pytest…, Another test command for testing. Name starts with _ to avoid warning due to…, Check if user is root., _TestCommand (+1 more)

### Community 520 - "Role"
Cohesion: 0.17
Nodes (10): Define casedb application roles for command-centric authorization., Role, scenario_ids, Test unsupported command types and non-read operations., Unsupported command type should raise NotImplementedError., Non-read operations should return results unchanged., Test APP_ADMIN users bypass ABAC filtering., APP_ADMIN should receive unmodified results for READ operations. (+2 more)

### Community 521 - "Any"
Cohesion: 0.17
Nodes (7): Any, Response, Invoke the handler, wrapping transport and HTTP errors in ServiceException., Execute a CRUD command by dispatching to the appropriate HTTP method., Return the id kind ('uuid', 'string', 'int', 'float', 'decimal', or 'mixed')., Check existence of each ID via individual GET requests., Deserialize an HTTP response body into the expected model or UUID type.

### Community 524 - "RetrievePersonsByIdCommand"
Cohesion: 0.15
Nodes (10): Command, field_validator, UUID, Represents a request to retrieve all data for a list of person IDs, as a list…, Validate that requested person identifiers are unique., Represents a request to retrieve specimen IDs (equivalent to SEQDB sample IDs)…, RetrievePersonsByIdCommand, RetrieveSpecimenIdsByCohortIdsCommand (+2 more)

### Community 525 - "FakeResponse"
Cohesion: 0.26
Nodes (3): FakeClient, FakeResponse, Any

### Community 526 - "JIRA Issues"
Cohesion: 0.17
Nodes (12): Assigning Issues, Comments and Worklogs, Common Fields, Extended Capabilities, JIRA Issues, Prerequisite: Resolve `cloudId`, Repository Context, Safety Rules (+4 more)

### Community 527 - "casedb/repositories/sa_model/abac.py"
Cohesion: 0.26
Nodes (11): OrganizationAccessCasePolicy, OrganizationShareCasePolicy, Base, RowMetadataMixin, Define SQLAlchemy persistence mappings for casedb ABAC policy models., Persist the casedb OrganizationShareCasePolicy domain model., Persist the casedb UserShareCasePolicy domain model., Persist the casedb OrganizationAccessCasePolicy domain model. (+3 more)

### Community 528 - ".filter"
Cohesion: 0.18
Nodes (7): Any, Command, Return whether the command is allowed by this policy., Return policy content associated with a command., Return the type of content produced by this policy., Filter a command result according to this policy., Determine if a stored value for this field is mutable.

### Community 529 - "OmopdbRemoteApp"
Cohesion: 0.23
Nodes (9): OmopdbRemoteApp, Any, Encapsulates routing of supported OmopDB commands to their remote HTTP…, Register remote OmopDB routes and command handlers., Upload a batch of persons., _fake_app_init(), _make_app(), test_registers_person_retrieval_routes_and_handlers() (+1 more)

### Community 531 - "setup_case_data_operational"
Cohesion: 0.14
Nodes (12): Env, fixture, Create case types, col infrastructure, data collections, cases, and access…, setup_case_data_operational(), Env, fixture, Create reference data (diseases, etiological agents, CaseTypes, CaseTypeSets,…, setup_case_data_reference() (+4 more)

### Community 532 - "TestCaseTypeProps"
Cohesion: 0.17
Nodes (3): parametrize, scenario_ids, TestCaseTypeProps

### Community 533 - "BrokenBackend"
Cohesion: 0.17
Nodes (6): BrokenBackend, Backend that fails every operation, to exercise the failure policy., Fail instead of reading. Args: key: The requested key. Returns: Never returns.…, Fail instead of writing. Args: key: The key to write. value: The envelope to…, Fail instead of deleting. Args: key: The key to remove. Raises:…, Fail instead of clearing. Raises: CacheBackendError: Always.

### Community 534 - "TestDAGAndCycleBehavior"
Cohesion: 0.17
Nodes (5): scenario_ids, Test topological sorting behavior with on_cycle parameter., TestDAGAndCycleBehavior, TestServiceTypeDagSorting, TestStaticUtilities

### Community 535 - "TestJWKSManagerIntegration"
Cohesion: 0.17
Nodes (7): Integration tests for JWKSManager functionality., Test complete JWT creation and verification workflow., Test that JWKS output is compatible with standard libraries., Test that multiple JWKSManager instances are independent., Test complete key rotation workflow., Test complete OpenID Connect ID token workflow., TestJWKSManagerIntegration

### Community 536 - "pr.sh"
Cohesion: 0.25
Nodes (5): generated_body(), print_ready_command(), require_command(), pr.sh script, usage()

### Community 537 - "Issue Templates"
Cohesion: 0.20
Nodes (6): Bug Report Template, Comment Template, Feature Request / Story Template, Issue Templates, Minimal Template, Task Template

### Community 538 - "field_validator"
Cohesion: 0.18
Nodes (6): field_validator, Normalize a supplied user key to lower case., Normalize role input to a set., Convert an empty invitation user key to an omitted key., Normalize invitation role input to a set., Strip leading and trailing whitespace from an external identifier.

### Community 539 - "TestUploadResult"
Cohesion: 0.18
Nodes (3): _make_pending_upload_result(), Construct an UploadResult in PENDING state (no logs required)., TestUploadResult

### Community 540 - ".__init__"
Cohesion: 0.20
Nodes (5): Create prefixed logger name., Initialize application configuration. Args: app_name: Name of the application…, Configure loggers from logging configuration file., Load settings using SettingsManager., Validate settings and apply defaults to all services and repositories.

### Community 541 - "TestPermissionRegistration"
Cohesion: 0.20
Nodes (6): Test permission registration functionality., Test registering a permission without RBAC., Test registering permission without RBAC fails when roles exist., Test unregistering a permission without RBAC., Test unregistering non-registered permission fails., TestPermissionRegistration

### Community 542 - "TestHierarchicalRolePermissions"
Cohesion: 0.20
Nodes (6): Test hierarchical role permission expansion., Test that hierarchical role permissions are expanded correctly., Test that redundant permissions in hierarchy are detected., Test that redundant permissions are allowed when verification is disabled., Test that PermissionTypeSet is properly expanded to individual PermissionTypes., TestHierarchicalRolePermissions

### Community 543 - "TestEdgeCasesAndErrorConditions"
Cohesion: 0.20
Nodes (6): Test edge cases and error conditions., Test that invalid on_missing_root_permissions value raises error., Test that root role is created when missing from role_permissions., Test that empty role hierarchy is handled gracefully., Test that role with no sub-roles returns empty set., TestEdgeCasesAndErrorConditions

### Community 544 - "BaseRemoteAppTestCase"
Cohesion: 0.22
Nodes (4): BaseRemoteAppTestCase, scenario_ids, TestAutoRegistration, TestInitAndProperties

### Community 545 - "Fields, Issue Types, and Transitions"
Cohesion: 0.22
Nodes (9): Clearing and replacing, Discovering fields, Discovering projects and issue types, Field shapes, Fields, Issue Types, and Transitions, Releases instead of milestones, Setting fields, Transition rules (+1 more)

### Community 546 - "case/non_persistable.py"
Cohesion: 0.22
Nodes (8): CaseSetQuery, BaseModel, UUID, Define non-persistable case query, rights, statistics, and result models. These…, Represents labeled filter criteria for querying case sets., Represents a similar-case result with its identifier and date., # TODO: add data_collection_id, SimilarCase

### Community 547 - ".crud"
Cohesion: 0.22
Nodes (6): Any, App, CrudCommand, Forward a CRUD command to seqdb under the configured functional user. The…, Initialize command handlers and the configured seqdb collaborator. Args: app:…, Return the local seqdb application or remote command client.

### Community 548 - ".idp_user_dependency"
Cohesion: 0.25
Nodes (6): Any, computed_field, User, Return the new-user dependency. Returns: Dependency that resolves a newly…, Return the identity-provider user dependency. Returns: Dependency that resolves…, Return the registered-user dependency. Returns: Dependency that resolves a…

### Community 549 - "Logger"
Cohesion: 0.22
Nodes (5): Logger, Logger used during application setup., Logger for API layer messages., Logger for application layer messages., Logger for service layer messages.

### Community 550 - "._validate_int_for_uuid"
Cohesion: 0.33
Nodes (6): Any, field_validator, UUID, Normalize the place-of-service concept identifier to UUID form., Normalize provider concept identifiers to UUID form., Normalize the country concept identifier to UUID form.

### Community 551 - ".create_file"
Cohesion: 0.25
Nodes (5): UUID, Verify a FASTQ payload has valid DNA records and matching quality scores. Args:…, Validate file content and create its persisted file record. Args: cmd: File-…, Decode possibly gzip-compressed UTF-8 content into a text stream. Args:…, Verify a FASTA payload has records containing valid DNA characters. Args:…

### Community 552 - "profile_method"
Cohesion: 0.36
Nodes (8): profile_method(), Path, Profile a callable and write its report to a timestamped log file. The returned…, test_async_returns_value(), test_async_writes_log_file(), test_sync_propagates_exception(), test_sync_returns_value(), test_sync_writes_log_file()

### Community 553 - "_ConcreteResult"
Cohesion: 0.22
Nodes (5): _ConcreteResult, scenario_ids, Minimal Pydantic model used to test BaseResult in isolation., UploadLogItem must be the same class as ResultLogItem (alias)., TestResultLogItem

### Community 554 - "Implement JIRA Issue"
Cohesion: 0.25
Nodes (7): 1. Retrieve and Assess the Issue, 2. Create the Work Branch, 3. Establish the Test Baseline, 4. Implement Incrementally, 5. Final Validation and Delivery, Implement JIRA Issue, Safety Rules

### Community 555 - "Links, Subtasks, and Dependencies"
Cohesion: 0.25
Nodes (8): Common link types, Direction, Epics and parents, Issue links, Links, Subtasks, and Dependencies, Reading links, Remote links, Subtasks

### Community 556 - "RowMetadataMixin"
Cohesion: 0.32
Nodes (8): Base1, Base2, declarative_mixin, RowMetadataMixin, SAModel1_1, SAModel1_2, SAModel2_1, SAModel2_2

### Community 557 - ".set_log_level"
Cohesion: 0.25
Nodes (5): _is_descendant_logger(), Return True when logger_name is a child logger of parent_logger_name., Resolve log level and report where it came from., Emit a structured info log describing the active log level and its source., Set log level for all loggers.

### Community 558 - ".is_allowed"
Cohesion: 0.29
Nodes (6): cached, Command, User, Determine whether a command may proceed under the current outage state. Outage…, Determine whether a user has permission to administer an outage. Args:…, Determine whether no active outage currently restricts requests. Returns: True…

### Community 559 - "._get_target_user_info"
Cohesion: 0.32
Nodes (5): Command, User, Determine whether a user strictly exceeds a target user's permissions. Args:…, Determine whether a user may invite or update the target user. Root users may…, Resolve update target state and early-exit conditions for a user command. Args:…

### Community 560 - "._verify_entity_exists"
Cohesion: 0.25
Nodes (4): Return model for entity., Return crud command for entity., Return permissions for entity., Verify entity exists.

### Community 561 - "._validate_state"
Cohesion: 0.32
Nodes (5): model_validator, Self, Validate the command's operation-specific state., Validate endpoint identifiers and association-object links., Validate compatible mutability settings.

### Community 562 - "TestServiceInitialization"
Cohesion: 0.25
Nodes (5): Test service initialization and basic properties., Test that service initialization creates empty collections., Test that properties return the correct internal collections., Test that register_handlers does nothing in base implementation., TestServiceInitialization

### Community 563 - "TestRoleHierarchy"
Cohesion: 0.25
Nodes (5): Test role hierarchy and sub-role calculations., Test that sub-roles are calculated correctly based on permission subsets., Test that sub-role calculations are cached., Test that sub-role cache is cleared when roles are updated., TestRoleHierarchy

### Community 564 - "TestCommandPermissions"
Cohesion: 0.25
Nodes (5): Test command-related permission functionality., Test getting RBAC permissions for a command class excludes non-RBAC permissions., Test getting command classes that have RBAC permissions., Test that get_root_permissions returns all domain permissions., TestCommandPermissions

### Community 566 - "test_oidc_provider.py"
Cohesion: 0.29
Nodes (4): JSON Web Key Set (JWKS) Manager This module handles JWT token generation,…, OpenID Connect Provider This module implements OpenID Connect (OIDC)…, Unit tests for JWKS Manager This module contains comprehensive unit tests for…, Unit tests for OpenID Connect Provider This module contains comprehensive…

### Community 567 - "ReadSelfResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadSelfResultsOnlyPolicy, Filter casedb user case-policy reads to the current user's records., Register ownership attributes for casedb user case-policy commands. Args:…, ReadSelfResultsOnlyPolicy

### Community 626 - "._serialize_created_at"
Cohesion: 0.29
Nodes (5): Any, datetime, field_serializer, Serialize the creation timestamp as ISO 8601., Omit callable properties from serialized command data.

### Community 629 - ".filter"
Cohesion: 0.29
Nodes (5): Any, BaseAbacService, Command, Initialize role mappings and command attributes that identify ownership. Args:…, Filter or reject read results that are not owned by the current user.…

### Community 630 - "ReadSelfResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadSelfResultsOnlyPolicy, Encapsulates restrictions on shared self-result reads according to OmopDB…, Initialize self-scoped command metadata for OmopDB., ReadSelfResultsOnlyPolicy

### Community 631 - "ReadUserPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadUserPolicy, Encapsulates shared user-read checks with OmopDB role and command mappings., Initialize the user-read policy with OmopDB dependencies., ReadUserPolicy

### Community 632 - "ReadSelfResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadSelfResultsOnlyPolicy, Encapsulates restricting eligible result reads to resources owned by the caller., Initialize the shared policy with seqdb identifier-attribute mappings., ReadSelfResultsOnlyPolicy

### Community 633 - "set_envvar"
Cohesion: 0.33
Nodes (4): Path, set_envvar(), CLI runner to start the local platform and block until Ctrl+C., run_platform()

### Community 634 - "scenario_ids"
Cohesion: 0.29
Nodes (5): scenario_ids, Test RBAC policy registration., Test that RBAC policies are registered for all RBAC command classes., Test registering RBAC policies with custom override functions., TestRbacPolicyRegistration

### Community 635 - "JQL Search"
Cohesion: 0.33
Nodes (6): Calling the tool, Common queries, JQL Search, Operators, Universal search, Values and quoting

### Community 636 - "Creating Issues"
Cohesion: 0.33
Nodes (6): Content format, Creating Issues, Description structure, Issue types, Optional parameters, Summary guidelines

### Community 637 - "Pytest Run (capture once, inspect many times)"
Cohesion: 0.33
Nodes (5): Method, Notes, Pytest Run (capture once, inspect many times), When NOT to use (rerun for real), When to use

### Community 638 - "._serialize_cohort"
Cohesion: 0.40
Nodes (4): field_serializer, UUID, Serialize cohort UUID keys and non-null values as strings., Serialize content UUID keys as strings while retaining values.

### Community 639 - "._serialize_id"
Cohesion: 0.40
Nodes (4): field_serializer, UUID, Serialize UUID identifiers as strings while retaining ``None``., Serialize UUID identifiers as strings while retaining ``None``.

### Community 640 - ".register_retrieve_organization_ids_handler"
Cohesion: 0.40
Nodes (4): Command, UUID, Register an organization-scope resolver for a command class. Args:…, Resolve the organization IDs addressed by a command. Args: cmd: The command to…

### Community 641 - ".filter"
Cohesion: 0.40
Nodes (4): Any, Command, Mask audit fields unless the command user has a privileged role. If the user…, Recursively clear audit metadata on models nested in a result. Args: obj:…

### Community 642 - ".retrieve_user_roles"
Cohesion: 0.33
Nodes (4): Hashable, User, Retrieve the roles assigned directly to a commondb user. Args: user: User whose…, Determine whether a user has the configured root role. Args: user: User whose…

### Community 643 - ".is_invalidated"
Cohesion: 0.33
Nodes (3): Return whether an entry written at `created_at` is affected., Return whether an entry must not be served at all., Return whether an entry may be served while a refresh runs.

### Community 644 - "._validate"
Cohesion: 0.40
Nodes (4): model_validator, Self, Validate claim mappings and public-provider credentials., Validate public-provider credentials.

### Community 645 - ".register_mappers"
Cohesion: 0.22
Nodes (6): Engine, Self, Initialise the repository with the provided SQLAlchemy engine. Registers…, Create and register mappers for a list of entities using the given factory. The…, Default implementation to register standard mappers for a list of entities., Register a mapper, enforcing uniqueness by row class and table.

### Community 646 - "._validate_state"
Cohesion: 0.33
Nodes (4): model_validator, Self, Validate bound presence, ordering, and compatible censor operators. Raises:…, Validate bounds and build the optimized range matching function.

### Community 647 - "crud_read_set.py"
Cohesion: 0.33
Nodes (5): Implement seqdb CRUD service operations for services.seq.crud_read_set., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign…

### Community 649 - ".__init__"
Cohesion: 0.06
Nodes (31): AbacService, App, Any, Command, Domain, Dynaconf, Enum, Logger (+23 more)

### Community 653 - ".setup"
Cohesion: 0.33
Nodes (4): Env, fixture, Print the active edge cases once per class run when VERBOSE is enabled., Auto-inject the env fixture into the class.

### Community 654 - "TestUnauthenticated"
Cohesion: 0.33
Nodes (4): Test unauthenticated user conditions., None user should assert., User without id should assert., TestUnauthenticated

### Community 656 - "Any"
Cohesion: 0.40
Nodes (4): Any, SeqForUpload, Create a sample SeqForUpload with default values and optional overrides., Create a sample SeqForUpload with default values and optional overrides.

### Community 657 - "._generate_key_pair"
Cohesion: 0.33
Nodes (3): Generate a new key pair and return the new key ID., Initialize JWKS manager with a new RSA key pair., Generate a new RSA key pair.

### Community 658 - ".has_read_sets"
Cohesion: 0.40
Nodes (3): computed_field, Indicates whether there are any read sets in the cases., Indicates whether there are any sequences in the cases.

### Community 659 - ".get_content"
Cohesion: 0.40
Nodes (3): Command, Model, Resolve the case access model for a command. Args: cmd: Command for which case…

### Community 661 - "RbacService"
Cohesion: 0.40
Nodes (4): CommonRbacService, Initialize inherited RBAC policy handling with casedb roles. Args: app:…, Encapsulates casedb RBAC using the domain's role enumeration., RbacService

### Community 662 - "._serialize_roles"
Cohesion: 0.40
Nodes (3): field_serializer, Serialize the user's role set as a JSON-compatible list., Serialize the invitation's initial roles as a JSON-compatible list.

### Community 667 - "._invalidate_cache"
Cohesion: 0.40
Nodes (3): Command, Register ABAC policies at their required command lifecycle phases.…, Clear cached user lookups after a command changes ABAC-related state. Args:…

### Community 668 - "CachedError"
Cohesion: 0.40
Nodes (4): CachedError, BaseException, Encapsulates holding an exception that was cached instead of being retried.…, Initialize a CachedError instance.

### Community 669 - ".name"
Cohesion: 0.40
Nodes (3): computed_field, Return the canonical permission name., Return the stable sort key for this permission.

### Community 670 - "omopdb/repositories/sa_model/base.py"
Cohesion: 0.40
Nodes (4): DataLineageMixin, declarative_mixin, Shared SQLAlchemy mixins used by OmopDB table mappings., Encapsulates a SQLAlchemy model mixin for adding a number of standard fields.

### Community 671 - "Examples"
Cohesion: 0.50
Nodes (4): Example 1: Bug report, Example 2: Feature request with priority, Example 3: Mark an issue as blocked, Examples

### Community 676 - "._validate_unit_for_type"
Cohesion: 0.50
Nodes (3): model_validator, Self, Enforce unit presence according to the concept set type.

### Community 681 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseAbacService, Initialize the policy with an ABAC service and policy properties. Args:…

### Community 684 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseAbacService, Initialize the policy with its ABAC service and configuration properties. Args:…

### Community 685 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, App, Initialize role maps and configured root and guest role values. Args: app:…

### Community 686 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseAbacService, Initialize organization-admin query support and configured role mappings. Args:…

### Community 687 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseAbacService, Initialize mapped user type and configured role mappings. Args: abac_service:…

### Community 688 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, App, Initialize configured role mappings and permissions exempt from RBAC. Args:…

### Community 689 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, App, Initialize configured concrete policy classes. Args: app: Application that owns…

### Community 691 - "._validate_locus"
Cohesion: 0.50
Nodes (3): model_validator, Self, Restrict gene-product codes to loci typed as genes.

### Community 692 - "._validate_protocol_type_dependencies"
Cohesion: 0.50
Nodes (3): model_validator, Self, Enforce fields required or disallowed by the selected protocol type.

### Community 693 - "._validate_model"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate mutually exclusive read links and paired-read values.

### Community 694 - "._validate_state"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate sequence links and derive a hash from available contigs.

### Community 695 - "File"
Cohesion: 0.50
Nodes (4): File, Base, RowMetadataMixin, Encapsulates the SQLAlchemy model for the persistable domain model.

### Community 696 - "setup_test_users_and_organizations_operational"
Cohesion: 0.50
Nodes (4): Env, fixture, Set up test users and organizations for operational data edge case tests.…, setup_test_users_and_organizations_operational()

### Community 697 - "Available Tools"
Cohesion: 0.67
Nodes (3): Available Tools, Read operations, Write operations

### Community 719 - "get_test_client"
Cohesion: 0.67
Nodes (3): get_test_client(), Env, fixture

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
- **533 isolated node(s):** `post-pr-comments.sh script`, `docker-entrypoint.sh script`, `PYTHONPATH`, `Gen-EpiX`, `$schema` (+528 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **197 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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