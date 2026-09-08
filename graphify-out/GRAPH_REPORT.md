# Graph Report - gen-epix-api  (2026-09-08)

## Corpus Check
- 859 files · ~1,164,699 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 17668 nodes · 38424 edges · 739 communities (578 shown, 161 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 1574 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2ef6b146`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- commondb/domain/util.py
- AppType
- casedb/domain/command/__init__.py
- commondb/domain/enum.py
- .filter
- TestRoleRegistration
- .create_person_for_upload
- App
- AppCfg
- Client
- omop/ontology.py
- BaseSeqService
- AppImplDetails
- command/seq.py
- omopdb/domain/model/__init__.py
- JWKSManager
- MockRequest
- CaseService
- crud_dim.py
- case_service_crud_case_set
- crud_case_type_set.py
- CrudOperation
- .create_log_message
- seq/service.py
- IsoTimeTransformer
- BaseAbacRepository
- JsonFormatter
- validate_int_for_uuid_field
- BaseUnitOfWork
- TupleMapTransformer
- TestSeqdbRemoteApp
- seqdb/domain/model/__init__.py
- transform/__init__.py
- casedb/domain/model/__init__.py
- BaseCaseService
- test_user_manager_auto_create.py
- Run
- case/service.py
- TestBaseResult
- TokenIntrospectionManager
- .create_claims
- case_service_create_file_for_read_set_or_seq
- Token
- test_docs_model_field_descriptions.py
- ObjectAdapter
- casedb CASE Simplified ERD
- ._validate_args
- .__call__
- TestCreate
- Model
- test_filter_base_filter.py
- .__init__
- UUID
- omopdb/repositories/sa_model/__init__.py
- profile_method
- Any
- Entity
- omopdb/domain/command/__init__.py
- test_seqdb_retrieve_best.py
- TestTokenStore
- test_fastapp_rbac_service.py
- Domain
- sa/repository.py
- DictRepository
- OauthIdpClient
- .__init__
- RemoteApp
- omopdb/repositories/__init__.py
- SARepository
- retrieve_case.py
- Filter
- Role
- .create_command_and_result_for_samples
- person_validator.py
- .create_client
- BaseAbacTestCase
- ErmGenerator
- TestcasedbEdgeCasesRefDataAccess
- ._validate_state
- RbacService
- _make_protocol
- server.py
- .create_seq_classification_for_upload
- define_edge_cases_reference.py
- IntervalToIntervalTransformer
- TestCreate
- .is_allowed
- _verify_batch_refdata_snp_profiles
- TestClientStore
- sa_model/seq/__init__.py
- SampleBatchUploader
- EqualsUuidFilter
- casedb/repositories/sa_model/__init__.py
- calculate_seq_distance.py
- BaseUploadTestCase
- .create_parent_for_upload
- test_seqdb_distance_optimization_benchmark.py
- sa_model/case.py
- ._serialize_int_enums
- BaseSeqRepository
- Hashable
- ._make_child_parent_id_mismatch_cmd
- CasedbTestClient
- IntEnumWithJsonSchemaMixin
- CaseAbac
- make_assoc
- OIDCProvider
- TestCrudWithAccessFilter
- CaseBatchUploader
- test_seqdb_calculate_seq_distances_performance.py
- sa/util.py
- TestClient
- ImportGraphAnalyzer
- CaseValidator
- .crud
- case_service_retrieve_is_own_cases
- Concept
- .upload_batch
- Concept (omopdb.omop / OMOP CDM entity)
- test_update_user_policy.py
- seq_service_calculate_seq_distances_for_new_profiles
- test_fastapp_repository_performance.py
- DummyCommand
- CacheRegion
- BaseCaseValidatorTestCase
- OAuth2Validator
- .create_case_for_upload
- cache/__init__.py
- SAMapper
- Person
- PersonForUpload
- TestRegistrationAndLookups
- ._get_allele_profile_for_ids
- RBACTestClient
- model_anonymizer.py
- Concept
- .retrieve_case_rights
- .__init__
- BaseRepository
- api/seq.py
- .create_crud_cmd
- .create_child2_for_upload
- TestModelSampleBatchForUpload
- case/non_persistable.py
- crud_file.py
- TestUpdate
- SeqdbTestClient
- TestModelBaseSeq
- CacheStatistics
- Case Type
- case_service_retrieve_similar_cases
- command/case.py
- .__init__
- Data Collection
- test_fastapp_cache_region.py
- Any
- .name
- ServerManager
- test_fastapp_cache_support.py
- .expectStatusCount
- TestModelSeq
- CaseSet
- CaseType
- UUID
- .create_local_or_remote_app
- InMemoryOrganizationRepository
- omopdb/domain/enum.py
- test_casedb_upload.py
- create_client
- DummyCmd
- ._create_sample_seq_for_upload
- OAuth2Client
- test_seqdb_calculate_phylogenetic_tree.py
- create_mapped_column
- Protocol
- Person
- Protocol (seqdb entity)
- RetrieveOutagesCommand
- TestCommondbDictModelModifier
- EndpointTestClient
- User
- AuthEnv
- _DummyMapper
- UUID
- FakeResponse
- Gen-EpiX README
- casedb.organization.md
- ._validate_model
- case_date.py
- .anonymize_user
- CommondbRemoteApp
- computed_field
- TestDelete
- IdentifierIssuer
- case_service_crud_ref_col
- CasedbRemoteApp
- CompositeFilter
- IntervalTransformer
- test_casedb_user_journey_performance.py
- map_paired_elements
- TestCreate
- BaseUploadTestCase
- TestNumpyAlleleIntegration
- DummyIdpClient
- UUID
- Registry
- test_cfg_log_level.py
- generate_seq_distances.py
- scenario_ids
- ._validate_case_for_upload
- EvictionStrategy
- TestCreateUserFromToken
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
- SeqdbRemoteApp
- convert
- BaseSeqDistancePerformance
- CrudCommand
- sa_model/geo.py
- .__init__
- test_seqdb_calculate_seq_distance.py
- Any
- TestAuth
- TestCasedbMetadataMasking
- CircuitBreaker
- test_read_config.py
- TestDataLineageMixin
- ClientStore
- Organization (commondb.organization entity)
- crud_case_data_collection_link.py
- check_docstrings.py
- BaseCaseService
- .upload_batch
- UUID
- BasePersonUploadTestCase
- `gen_epix.fastapp.cache`
- Organization
- IdentifierIssuer (omopdb.organization entity)
- Organization
- derived.py
- User
- CaseTypeCrudCommand
- MemoryTagIndex
- test_logging_runtime_contract.py
- ReceiverApp
- TokenStore
- test/conftest.py
- Gen-EpiX Contributor Documentation Index
- Organization
- Sample
- PersonBatchForUpload
- ._make_user_cmd
- SAUnitOfWork
- _encode_to_int32
- TestCasedbCaseCreateSeq
- TestRead
- _make_cmd
- UUID
- _get_cases_for_create_file_for_read_sets_or_seqs
- Test6Identifiers
- test_retrieve_stats.py
- TestCommondbMetadataMasking
- ModelNoId
- TestHttpTimeoutConfiguration
- test_error_code_unicity
- omop/service.py
- ReadOrganizationResultsOnlyPolicy
- App (command dispatcher / PEP)
- Organization (omopdb.organization entity)
- Unit
- RetrieveGeneticSequenceFastaByIdCommand
- casedb/domain/command/abac.py
- .dispatch
- omopdb/policies/read_organization_results_only_policy.py
- BaseAbacService
- seq/crud_tree_algorithm.py
- CacheConfigurationError
- FullSample
- JsonFormatter
- .__init__
- CalculatePhylogeneticTreeCommand
- data_access/conftest.py
- AuthTestClient
- make_cdb_user
- OmopdbRemoteApp
- case_service_crud_col_set
- handle_command
- IdpClient hierarchy
- Protocol
- .retrieve_case_set_stats
- RetrieveContainingRegionCommand
- .retrieve_organization_ids
- sa_model/ontology.py
- .handle
- PayerPlanPeriod
- Transformer Framework
- test_casedb_custom.py
- rewrite_parametrized_dependency_markers
- TestRetrieveCompleteCaseType
- Any
- TestOidcClientCredentials
- env
- BaseRbacServiceTestCase
- LogParser2
- AppComposer (Composition Root)
- Region Set
- Sample
- SeqTaxonomy
- ConcreteRbacService
- CommondbSAMapper
- TestUserPermissions
- TestOIDCProviderIntegration
- metadata.py
- renovate.json
- TestUpdate
- TestSQLInjection
- BaseCommondbRemoteAppTestCase
- TestAnonymizeUser
- generate_seqdb_models.py
- TestOIDCProvider
- Ref Col
- Outage (commondb.system entity)
- Protocol
- 3.8 Comments and Docstrings
- calculate_phylogenetic_tree.py
- crud_ast_measurement.py
- IdsError
- crud_seq_profile.py
- crud_locus.py
- crud_locus_set.py
- crud_pcr_measurement.py
- crud_protocol_set.py
- crud_protocol_set_member.py
- crud_ref_seq.py
- patch
- crud_read_set_identifier.py
- crud_seq.py
- crud_seq_category.py
- crud_seq_category_set.py
- crud_seq_distance.py
- crud_seq_taxonomy.py
- crud_taxon.py
- crud_taxon_set.py
- crud_taxon_set_member.py
- dependency
- TestVerifyUserRights
- TestDelete
- dependency
- test_logging_yaml.py
- test_omopdb_build.py
- dependency
- OmopdbTestClient
- test_seqdb_build.py
- dependency
- Any
- TestOauthIdpClientIntrospection
- .extract_security_callable
- .make_idp_client
- AuthorizationCodeStore
- BaseRepository (abstract)
- Contact (doc)
- seqdb Overview ERD
- IdentifierIssuer
- Taxon
- Locus
- Any
- .__init__
- UpdateUserPolicy
- .create_sa_repository
- .__init__
- .__init__
- TestRead
- KeyedMutex
- User
- BaseAuthServiceTestCase
- scenario_ids
- OAuth 2.0 Provider with OpenID Connect Support
- .get_mapped_class
- Entity descriptor
- Specimen
- DataCollection
- Seq
- fixture
- JIRA Issues
- casedb/repositories/sa_model/abac.py
- ._validate_content
- AuthException
- DataException
- Self
- Subject
- MeasurementRelation
- ObservationPeriod
- ProcedureOccurrence
- Locus
- ReadSet
- SeqProfile
- EtlLogItem
- CreateFileForSeqCommand
- ._validate_model
- BaseSAMapper
- .__init__
- IsOrganizationAdminPolicy
- BaseAbacService
- IsOrganizationAdminPolicy
- ReadUserPolicy
- BaseFileRepository
- OrganizationSARepository
- _parse_nextclade_profile_content
- OAuth Client Credential Flow Test
- TestCaseTypeProps
- init-db one-shot database creation service
- DataCollection (commondb.organization entity)
- DataCollectionSetMember
- DataCollectionSetMember
- TreeAlgorithm
- EtlLogItem
- BrokenBackend
- TestJWKSManagerIntegration
- pr.sh
- OrganizationService
- Issue Templates
- .default_isolation_level
- omopdb/repositories/organization_sa.py
- ._validate_content
- OrganizationService
- release-please-config.json
- get_test_client
- command/geo.py
- field_validator
- test_debug_console_uses_json_formatter
- PersonBatchUploader
- DummyLogItem
- App.handle() command dispatch
- casedb SUBJECT Simplified ERD
- NoteNlp
- TreeAlgorithm
- SeqClassificationForUpload
- ._validate_state
- TestUploadResult
- ._validate_state
- .organization_identifier_issuer_link_update_association
- test/enum.py
- ._validate_some_criteria
- ._validate_content
- .__init__
- .__init__
- get_test_client
- MermaidErmGenerator
- .__init__
- _PytestMockConfig
- .data_collection_set_data_collection_update_association
- docker-entrypoint.sh
- Default App Ports (8000/8001/8002/8010)
- CohortDefinition (omopdb.md)
- Organization
- Locus (seqdb entity)
- SeqCategory
- Locus
- .__init__
- .validate_model
- crud_read_set.py
- CaseTypeSetCaseTypeUpdateAssociationCommand
- crud_ref_allele.py
- .create_case_set
- .disease_etiological_agent_update_association
- .__init__
- .retrieve_cases_by_id
- .retrieve_phylogenetic_tree_by_cases
- .retrieve_protocols
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
- crud_seq_identifier.py
- TestPermissionRegistration
- .retrieve_cases_by_query
- TestHierarchicalRolePermissions
- .retrieve_genetic_sequence_fasta_by_case
- .anonymize_user
- .retrieve_feature_flags
- .retrieve_invite_user_constraints
- .retrieve_licenses
- .retrieve_organization_admin_name_emails
- .retrieve_own_permissions
- TestEdgeCasesAndErrorConditions
- OmopdbEndpointTestClient
- wait_for_mssql.py
- Test5FieldMutability
- Fields, Issue Types, and Transitions
- test/fastapp/model.py
- .crud
- .idp_user_dependency
- .anonymize_user
- ._parse_and_get_package_metadata
- openapi.py
- ._validate_state
- ._validate_int_for_uuid
- MockJWKAndToken
- _ConcreteResult
- Implement JIRA Issue
- Links, Subtasks, and Dependencies
- .logger
- .__exit__
- create_seq_endpoints
- ._validate_content
- TestServiceInitialization
- TestRoleHierarchy
- TestCommandPermissions
- TestGetNewUserFromClaims
- test_oidc_provider.py
- ReadOrganizationResultsOnlyPolicy
- ReadSelfResultsOnlyPolicy
- OrganizationSARepository
- case_service_crud_genetic_distance_protocol
- .filter
- .crud
- create_root_user_from_claims
- Hashable
- ._custom_json_encoder
- ReadSelfResultsOnlyPolicy
- ReadSelfResultsOnlyPolicy
- Commit Skill
- TokenRetrieval
- scenario_ids
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
- JQL Search
- casedb/config/__init__.py
- casedb/__init__.py
- Creating Issues
- Pytest Run (capture once, inspect many times)
- ConditionOccurrence
- case_service_crud_tree_algorithm_class
- ._serialize_cohort
- case_service_crud_tree_algorithm
- ._serialize_id
- .get_status_count
- .register_retrieve_organization_ids_handler
- .is_existing_user_by_key
- .filter
- .retrieve_user_roles
- .is_invalidated
- ._validate
- OrganizationService
- ._validate_sample_ids
- .register_mappers
- ._validate_allele_profile_upload
- ._validate_mlva_profile_upload
- fastapp/services/__init__.py
- ._validate_exactly_one_representation
- omopdb/config/__init__.py
- gen_epix/omopdb/__init__.py
- seqdb/config/__init__.py
- TestRootUserTokenTimeToLive
- TestInitializationValidation
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
- omopdb/repositories/sa_model/base.py
- omop_service_retrieve_persons_by_id
- _FakeCaseAbacPolicy
- Examples
- gen-epix-api Version 6.1.0
- Death
- ._validate_unit_for_type
- .__init__
- .get_batch_for_upload
- .add_error
- .__init__
- .__init__
- .__init__
- .__init__
- .__init__
- InvalidIdsError
- InvalidLinkIdsError
- InvalidModelIdsError
- LinkConstraintViolationError
- ._validate_state
- .validate_limit
- ._validate_locus
- ._validate_protocol_type_dependencies
- ._validate_model
- ._validate_state
- File
- ._validate_ref1_fields
- Available Tools
- .seqdb_user
- ._serialize_severity
- ._validate_severity
- .retrieve_user_is_non_rbac_authorized
- .__enter__
- ._serialize_seq_profile_type
- ._validate_seq_profile_type
- .__init__
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
- .retrieve_case_type_stats
- .is_existing_user_by_key
- .is_existing_user_by_key
- .__del__
- .set_auto_invalidate_cache
- .__init__
- .flush
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

## Communities (739 total, 161 thin omitted)

### Community 0 - "commondb/domain/util.py"
Cohesion: 0.02
Nodes (115): AbacService, Compose and expose the configured casedb FastAPI application. This module forms…, # TODO: app variable added for backwards compatibility with startup code that…, Create and populate the casedb domain registry. Command exports provide…, CommonRoleGenerator, Encapsulates Casedb role inheritance and command permission expansion. The…, RoleGenerator, Compose casedb application dependencies from the configured environment.… (+107 more)

### Community 1 - "AppType"
Cohesion: 0.05
Nodes (55): post-pr-comments.sh Script, Review Skill, ETL (Extract, Transform, Load) script for Gen-EpiX genomic epidemiology…, AppType, AppTypeSet, DevIdpConfig, DevRepositoryConfig, Encapsulates a Gen-EpiX application domain or the aggregate domain set. (+47 more)

### Community 2 - "casedb/domain/command/__init__.py"
Cohesion: 0.03
Nodes (112): Expose and group casedb and shared commands for domain registration. ABAC…, ConceptCrudCommand, ConceptRelationCrudCommand, ConceptSetCrudCommand, DiseaseCrudCommand, DiseaseEtiologicalAgentUpdateAssociationCommand, EtiologicalAgentCrudCommand, EtiologyCrudCommand (+104 more)

### Community 3 - "commondb/domain/enum.py"
Cohesion: 0.01
Nodes (213): CaseBatchForUpload, Define case, sequence, and read-set upload request and result models. The…, Represents a batch of unique cases intended for upload., Return whether any case has read sets or sequences for a seqdb sample., Validate and normalize uploaded case content against case-type metadata. The…, # TODO: transform any other col_types, # TODO: replace by pre-calculated interval_relation_map for efficiency, Verify and persist case batches and their linked seqdb samples. The module… (+205 more)

### Community 4 - ".filter"
Cohesion: 0.18
Nodes (7): Any, Command, Return whether the command is allowed by this policy., Return policy content associated with a command., Return the type of content produced by this policy., Filter a command result according to this policy., Determine if a stored value for this field is mutable.

### Community 5 - "TestRoleRegistration"
Cohesion: 0.08
Nodes (13): Test role registration and management., Test registering a new role with permissions., Test registering role with invalid permissions fails., Test registering existing role without update fails., Test updating existing role succeeds., Test registering multiple roles at once., Test registering roles with root role adds all missing permissions., Test registering roles with root role and missing permissions raises error. (+5 more)

### Community 6 - ".create_person_for_upload"
Cohesion: 0.10
Nodes (22): ParentUploadResult, Create a test PersonForUpload. A default Person is created unless person=None., Test scenarios related to person existence in repository., Test 1.1: ID not provided or NULL_ID - person does not exist and needs to be…, Test 1.2: ID provided by batch creator (new_id); person does not exist yet -…, Test scenarios related to providing different combinations of child objects., Test 2.1: Person without any child objects., Test 2.2: Person with measurements only. (+14 more)

### Community 7 - "App"
Cohesion: 0.01
Nodes (332): Define casedb API representations for organization permissions., Expose concrete casedb and shared services for application composition. Casedb…, Encapsulates the commondb service responsible for a domain operation., ServiceType, Define commondb role permissions and mappings for application domains. The…, # TODO: remove UPDATE from association objects that do not have properties of…, Provide an RBAC policy contract for role creation and updates., BaseHasSystemOutagePolicy (+324 more)

### Community 8 - "AppCfg"
Cohesion: 0.03
Nodes (52): AppCfg, BaseAppCfg, _is_descendant_logger(), Dynaconf, Enum, Logger, Path, Refactored configuration management using Strategy Pattern. (+44 more)

### Community 9 - "Client"
Cohesion: 0.04
Nodes (35): Client, OAuth 2.0 Client representation., Hash the client secret for security., Hash a client secret using SHA-256., Verify a client secret against the stored hash., Validate and filter requested scopes against allowed scopes., Check if the client supports a specific grant type., Check if the redirect URI is registered for this client. (+27 more)

### Community 10 - "omop/ontology.py"
Cohesion: 0.04
Nodes (69): DataLineageMixin, Any, UUID, Shared OMOP model mixins and primary-key normalization helpers., Encapsulates optional provenance and source-traceback fields to an OMOP model., Validate that the input value is either a UUID or a string that can be…, Validate and synchronize string-based primary key arguments. Mutates ``data``…, Validate and synchronize integer-based primary key arguments. Mutates ``data``… (+61 more)

### Community 11 - "BaseSeqService"
Cohesion: 0.02
Nodes (119): CalculateSeqDistancesForNewProfilesCommand, Command, Represents calculating and storing distances between new and existing sequence…, Represents creating missing distances for profiles under a distance protocol.…, Represents retrieval of sample identifiers matching a query. These identifiers…, Represents retrieval of complete data for sample identifiers. The result…, Represents retrieval of only SampleIdentifier records for sample identifiers.…, Represents retrieval of sequences in FASTA format. as an iterable that yields… (+111 more)

### Community 12 - "AppImplDetails"
Cohesion: 0.01
Nodes (308): create_abac_endpoints(), Any, APIRouter, App, Exception, FastAPI, NoReturn, Register casedb ABAC endpoints through the shared commondb API adapter. (+300 more)

### Community 13 - "command/seq.py"
Cohesion: 0.02
Nodes (120): Define commondb commands for organization-administration policies., Command, CrudCommand, Any, datetime, field_serializer, Represents commondb user context, audit metadata, and serializable properties., Serialize the creation timestamp as ISO 8601. (+112 more)

### Community 14 - "omopdb/domain/model/__init__.py"
Cohesion: 0.05
Nodes (104): BaseIdentifier, Represents an identifier generated outside the system for an entity. It records…, Expose shared and OMOP model types plus their domain registration metadata. The…, ConditionOccurrence, ConditionOccurrenceIdentifier, Death, DeathIdentifier, DeviceExposure (+96 more)

### Community 15 - "JWKSManager"
Cohesion: 0.05
Nodes (34): JWKSManager, Get the public key in PEM format., Get the private key in PEM format (use with caution!)., Manages JSON Web Keys for JWT token operations., Test verification of a valid JWT token., Test verification of an invalid JWT token., Test verification fails with token signed by different key., Test getting public keys in JWKS format. (+26 more)

### Community 16 - "MockRequest"
Cohesion: 0.03
Nodes (52): MockRequest, Any, Test client authentication requirement for client credentials flow., Test client authentication requirement for other grant types., Test client authentication with valid credentials., Test client authentication with invalid client ID., Test client authentication with invalid secret., Test client authentication with missing credentials. (+44 more)

### Community 17 - "CaseService"
Cohesion: 0.03
Nodes (56): Expose the concrete service that handles casedb case-domain commands.…, CaseService, BaseCaseService, CaseIdentifier, CaseSet, CaseSetCategory, CaseSetDataCollectionLink, CaseSetMember (+48 more)

### Community 18 - "crud_dim.py"
Cohesion: 0.04
Nodes (61): DimCrudCommand, Represent CRUD operations for dimensions that group case-type columns., case_service_crud_dim(), _crud_create_dim(), _crud_dim_with_abac(), _crud_dim_without_abac(), _crud_update_dim(), _get_existing_dim() (+53 more)

### Community 19 - "case_service_crud_case_set"
Cohesion: 0.08
Nodes (29): CaseSetCrudCommand, Represent CRUD operations for case sets and their context., case_service_crud_case_set(), _crud_case_set_with_abac(), _crud_case_set_without_abac(), BaseCaseService, CaseSet, UUID (+21 more)

### Community 20 - "crud_case_type_set.py"
Cohesion: 0.08
Nodes (34): CaseTypeSetCrudCommand, ColSetMemberCrudCommand, Represent CRUD operations for column-set membership., Represent CRUD operations for reusable sets of related case types., CaseTypeSet, ColSetMember, Handle a CRUD command for column-set members. Args: cmd: Column-set member CRUD…, Handle a CRUD command for case-type sets. Args: cmd: Case-type-set CRUD command… (+26 more)

### Community 21 - "CrudOperation"
Cohesion: 0.02
Nodes (156): CaseClassification, CaseRightSet, CaseTypeSetCategoryPurpose, ColConceptSetType, ColRelation, ColTypeOrder, ColTypeSet, ConceptRelationType (+148 more)

### Community 22 - ".create_log_message"
Cohesion: 0.16
Nodes (9): Command, Register a lifecycle listener for a command class and timing. Listeners receive…, Register a cache invalidator for successful commands of an exact type. Args:…, Remove a previously registered command lifecycle listener. Args: command_class:…, Register the handler that executes a command class. The handler is resolved for…, Return the nearest registered handler for a command class. Searches the class…, Dispatch a command through its complete application lifecycle. For the initial…, Resolve a command handler while logging and unwinding a failed dispatch. Args:… (+1 more)

### Community 23 - "seq/service.py"
Cohesion: 0.02
Nodes (92): Represents retrieval of the last modified datetime for a SeqDistance protocol.…, RetrieveSeqDistanceLastModifiedCommand, datetime, Retrieve the latest sequence-distance modification time. Args: cmd: Last-…, Return the latest distance-record update for a sequence-distance protocol.…, seq_service_retrieve_seq_distance_last_modified(), Allele, UUID (+84 more)

### Community 24 - "IsoTimeTransformer"
Cohesion: 0.03
Nodes (49): IntervalTransformStrategy, Enum, Enumerations for temporal granularity, interval mapping, and result status., Encapsulates strategies for reducing ISO time granularity., Encapsulates strategies for mapping interval categorizations., Encapsulates high-level transformation categories., Encapsulates transformation outcome classifications., Encapsulates supported ISO time granularities. (+41 more)

### Community 25 - "BaseAbacRepository"
Cohesion: 0.05
Nodes (39): BaseGeoRepository, Define the repository contract for Casedb geographic reference data., Provide the shared repository base for geographic persistence., Expose backend-independent repository contracts used by casedb services. Casedb…, BaseOntologyRepository, Define the repository contract for Casedb ontology reference data., Provide the shared repository base for ontology persistence., AbacDictRepository (+31 more)

### Community 26 - "JsonFormatter"
Cohesion: 0.05
Nodes (89): Formatter, _build_sensitive_re(), JsonFormatter, _normalise_sensitive_keys(), Any, LogRecord, Central JSON logging formatter for all GenEpix container applications. Ensures…, Format a Unix timestamp as a millisecond-precision UTC ISO 8601 value. Args:… (+81 more)

### Community 27 - "validate_int_for_uuid_field"
Cohesion: 0.06
Nodes (35): Validate that the input value is either a UUID or an integer that can be…, validate_int_for_uuid_field(), Any, field_validator, UUID, Normalize measurement concept identifiers to UUID form., Truncate too long values with an ellipsis, as the database field is limited to…, Normalize observation concept identifiers to UUID form. (+27 more)

### Community 28 - "BaseUnitOfWork"
Cohesion: 0.04
Nodes (86): Upload a batch of sequence samples. Implementations may persist samples and…, Upsert cases and then their linked read sets and sequences. The method mutates…, Upload samples to seqdb under the configured functional user. The command's…, Encapsulates batch-upload options and payload access for upload commands., UploadBatchCommandMixin, BaseBatchUploadResult, Represents the result for an atomic batch upload. Subclasses use field names…, BatchUploader (+78 more)

### Community 29 - "TupleMapTransformer"
Cohesion: 0.03
Nodes (57): Any, Hashable, Replace the lookup map used by subsequent row transformations. Only active rows…, Encapsulates mapping source-field tuples to target-field tuples. The mapping is…, Update the row source and target fields. This allows row field names to change…, Transform an adapted object using the configured tuple mapping. Target fields…, Transform a dictionary row in place and return the same dictionary. This is the…, Return the configured source-field values for a row without transforming it.… (+49 more)

### Community 30 - "TestSeqdbRemoteApp"
Cohesion: 0.12
Nodes (10): scenario_ids, Test the SeqdbRemoteApp class with focus on…, Test that HTTP errors are properly propagated., Test that the ROUTE_MAP contains the expected mapping., Test that the calculate_phylogenetic_tree method exists and is callable., Test that base URL is constructed correctly., Test that the remote app initializes correctly with default values., Use the extended timeout for large Locus CRUD batches. (+2 more)

### Community 31 - "seqdb/domain/model/__init__.py"
Cohesion: 0.01
Nodes (281): Provide an HTTP command client for remote casedb applications. The client…, Model, IntEnum, Normalize a value to a member of an integer enumeration. Args: enum_class: The…, Normalize an optional value to a member of an integer enumeration. Args:…, Represents an optional persistent identifier to commondb audit-aware models., validate_int_enum_value(), validate_int_enum_value_or_none() (+273 more)

### Community 32 - "transform/__init__.py"
Cohesion: 0.04
Nodes (50): Expose the public API for the transformation framework. `DictAdapter`,…, FallbackTransformer, Pipeline, Any, Synchronous transformer pipeline with ordered execution and error recovery., Run the wrapped transformer until it succeeds or retries are exhausted. Retries…, Encapsulates fallback transformation after a primary exception., Store the primary transformer and fallback transformer. (+42 more)

### Community 33 - "casedb/domain/model/__init__.py"
Cohesion: 0.03
Nodes (126): Expose case ABAC policy records, rights models, and shared admin policy types.…, BaseCasePolicy, OrganizationAccessCasePolicy, OrganizationShareCasePolicy, Define persistent organization and user ABAC policy records for cases. Access…, Represents a user's maximum access rights in one data collection. The rights…, Represents common case and case-set rights for a case-type set., Represents an organization's additional source-to-target share rights. Rights… (+118 more)

### Community 34 - "BaseCaseService"
Cohesion: 0.03
Nodes (56): CaseSetCategoryCrudCommand, CaseSetStatusCrudCommand, GeneticDistanceProtocolCrudCommand, Represent CRUD operations for categories used to tag case sets., Represent CRUD operations for case-set lifecycle statuses., Represent CRUD operations for genetic-distance protocols., BaseCaseService, Any (+48 more)

### Community 35 - "test_user_manager_auto_create.py"
Cohesion: 0.08
Nodes (43): claims_basic(), make_user_manager(), mock_organization_service(), mock_rbac_service(), other_org(), other_org_id(), Any, fixture (+35 more)

### Community 37 - "case/service.py"
Cohesion: 0.04
Nodes (67): Decimal, case_service_read_association_with_valid_ids(), BaseCaseService, CrudCommand, Model, User, UUID, Read association models with endpoint constraints and selectable return shapes. (+59 more)

### Community 39 - "TokenIntrospectionManager"
Cohesion: 0.08
Nodes (23): Any, Logger, SSLContext, Return cached introspection endpoint., Prune expired introspection cache., Encapsulates managing token introspection and discovery-endpoint caching., Return whether cached introspection token inactive., Return whether recheck introspection. (+15 more)

### Community 40 - ".create_claims"
Cohesion: 0.16
Nodes (11): Test scenarios for get_existing_user_from_claims., No user manager -> UnauthorizedAuthError., User found, name updated -> returns updated user., Update user name raises DomainException -> returns original user., No user key initially; after userinfo, key resolves -> returns user., User not found; claims match root -> create root user., User not found; auto-create -> success., User not found; auto-create returns None -> Unauthorized. (+3 more)

### Community 41 - "case_service_create_file_for_read_set_or_seq"
Cohesion: 0.09
Nodes (22): CreateFileForReadSetCommand, Represent upload of a raw-reads file for a case read-set column. The command…, case_service_create_file_for_read_set_or_seq(), _create_file(), _get_hash_uuid(), BaseCaseService, UUID, Create or reuse a file for a case-linked read set or sequence. The handler… (+14 more)

### Community 42 - "Token"
Cohesion: 0.05
Nodes (34): Any, patch, Unit tests for OAuth 2.0 Token Store This module contains comprehensive pytest…, Test scopes property with multiple scopes., Test scopes property with single scope., Test scopes property with empty scope., Test scopes property handles extra whitespace., Test has_scope returns True for existing scopes. (+26 more)

### Community 43 - "test_docs_model_field_descriptions.py"
Cohesion: 0.18
Nodes (11): _is_iterable_type(), Any, scenario_ids, Check if the given field type is an iterable type (like List, Set, Tuple, etc.), test if domain and request body models have a max_length for all iterable…, test_model_field_properties(), is_model_class(), Any (+3 more)

### Community 44 - "ObjectAdapter"
Cohesion: 0.05
Nodes (52): ObjectAdapter, Adapters that expose a common field interface for row-like objects. The…, Encapsulates adapter selection for supported object representations. Supported…, example_conditional_transformation(), example_usage(), Person, BaseModel, Executable examples of composing field, validation, and streaming transforms. (+44 more)

### Community 46 - "._validate_args"
Cohesion: 0.50
Nodes (3): Any, model_validator, Normalize endpoint-set initialization data.

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
Nodes (30): AlwaysTrueFilter, BaseFilterTestCase, BaseTrueFilter, CompositeFilter, EqualsFilter, Any, BaseModel, scenario_ids (+22 more)

### Community 51 - ".__init__"
Cohesion: 0.13
Nodes (14): Any, Initialize a NoResultsError instance., Initialize a ServiceException instance., Return http other props., Initialize http props., Initialize a FeatureDisabledServiceError instance., Initialize a CredentialsAuthError instance., Initialize a UnauthorizedAuthError instance. (+6 more)

### Community 52 - "UUID"
Cohesion: 0.16
Nodes (9): UUID, Validate SNP content and derive its hash. Returns: The derived SNP profile…, Validate the k-mer profile content., Validate the MLVA profile content., Validate allele content and derive its hash. Returns: The derived allele…, Return the deterministic content hash for ordered MLVA repeat numbers., Return the deterministic content hash for a k-mer frequency map., Return a deterministic hash for SNPs in position-sorted order. (+1 more)

### Community 53 - "omopdb/repositories/sa_model/__init__.py"
Cohesion: 0.04
Nodes (119): NoIdRowMetadataMixin, declarative_mixin, Encapsulates audit metadata fields to a row with a nonstandard primary key., IdentifierMixin, Encapsulates SQLAlchemy columns for external identifier-derived row models., Register and expose SQLAlchemy mappings for shared and OmopDB model types. The…, CareSite, CdmSource (+111 more)

### Community 54 - "profile_method"
Cohesion: 0.16
Nodes (18): get_package_root(), profile_method(), Path, Profile a callable and write its report to a timestamped log file. The returned…, Return the repository root located from this module's source path. Searches…, _parse_pyproject_dependency(), _parse_requirements_line(), Path (+10 more)

### Community 55 - "Any"
Cohesion: 0.10
Nodes (27): Any, Hashable, Model, Return a per-id existence flag list in the same order as obj_ids., Read a projection of specific fields, optionally filtered., Split a filter into a SQL where-clause part and a Python remainder., Helper method for debugging., Verify that obj_ids are unique and/or exist in the database. (+19 more)

### Community 56 - "Entity"
Cohesion: 0.02
Nodes (142): _annotation_to_mermaid_type(), _build_diagram(), _field_marker(), BaseModel, Mermaid-based ERM diagram generator. Produces Mermaid ``erDiagram`` markdown…, Return Mermaid column marker (PK / FK) or empty string., Return the Mermaid lines for a single entity block **with** attributes. Example…, Generate Mermaid relationship lines for a set of model classes. Each Link in an… (+134 more)

### Community 57 - "omopdb/domain/command/__init__.py"
Cohesion: 0.03
Nodes (125): Expose shared and OMOP command types plus command-registration metadata.…, CareSiteCrudCommand, CdmSourceCrudCommand, CohortCrudCommand, CohortDefinitionCrudCommand, ConceptAncestorCrudCommand, ConceptClassCrudCommand, ConceptCrudCommand (+117 more)

### Community 58 - "test_seqdb_retrieve_best.py"
Cohesion: 0.12
Nodes (24): _get_best_id_per_sample(), Retrieve the best result identifier for each requested sample. Retrieves the…, _classification_cmd(), _make_user(), _mock_service(), _mock_uow(), _profile_cmd(), Any (+16 more)

### Community 59 - "TestTokenStore"
Cohesion: 0.03
Nodes (35): Test cases for the TokenStore class., Test storing a basic token., Test storing a token with refresh token creates mapping., Test storing a token without refresh token., Test storing multiple tokens., Test retrieving an existing valid token., Test retrieving a non-existent token returns None., Test that retrieving expired token auto-cleans it. (+27 more)

### Community 60 - "test_fastapp_rbac_service.py"
Cohesion: 0.13
Nodes (27): Model1_1CrudCommand, Model1_2CrudCommand, Model2_1CrudCommand, Model2_2CrudCommand, CrudCommand, Enum, ServiceType, TestType (+19 more)

### Community 61 - "Domain"
Cohesion: 0.02
Nodes (110): Define Casedb role permissions and their shared-role mappings., # TODO: remove UPDATE from association objects that do not have properties of…, Retrieve effective permissions for the command's current user. Args: cmd:…, Retrieve effective permissions for the command's authenticated user. Args: cmd:…, Retrieve effective permissions through the commondb RBAC service. Args: user:…, Domain, Command, CrudCommand (+102 more)

### Community 62 - "sa/repository.py"
Cohesion: 0.03
Nodes (56): Model, Check existence of multiple IDs using a query-by-IDs endpoint., SQLAlchemy repository implementation., # TODO: determine invalid obj_ids and pass them to the exception, # NOTE: Only tested with MS SQL Server, # TODO: check if temp table exists and take a different name in that case, # TODO: finalize this part, # TODO: finalize this part, remove the example (+48 more)

### Community 63 - "DictRepository"
Cohesion: 0.08
Nodes (63): In-memory dictionary-backed repository exports., DictRepository, Load a DictRepository from a pickle file (plain or gzip-compressed)., Load a DictRepository from a zip archive containing per-entity JSON files., Encapsulates a repository that stores models in an in-memory dict, keyed by…, Return a no-op unit-of-work suitable for the in-memory backend., Return (where_filter, None) — the full filter applies in-memory., Instantiate a DictRepository, optionally loading data from a pkl/zip file. (+55 more)

### Community 64 - "OauthIdpClient"
Cohesion: 0.07
Nodes (23): OauthIdpClient, Any, Request, Response, Issuer the requested value., Audience the requested value., Scope the requested value., Log keys fetch success. (+15 more)

### Community 65 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseRbacService, Initialize the policy with its RBAC service and configuration properties. Args:…

### Community 66 - "RemoteApp"
Cohesion: 0.02
Nodes (82): BaseIsPermissionSubsetNewRolePolicy, Encapsulates prevention of creation or updates that would elevate a role's…, Return the policy decision point configured for command execution. Returns: The…, EventTiming, Encapsulates identifying a phase in command execution., FeatureDisabledServiceError, Base service error with HTTP response properties., Return http status code. (+74 more)

### Community 67 - "omopdb/repositories/__init__.py"
Cohesion: 0.04
Nodes (62): CommonBaseAbacRepository, BaseAbacRepository, OmopDB specialization of the shared attribute-based access repository., Encapsulates the commondb ABAC repository contract for OmopDB composition., Expose OmopDB repository contracts for shared and OMOP persistence.…, BaseOmopRepository, datetime, UUID (+54 more)

### Community 68 - "SARepository"
Cohesion: 0.05
Nodes (54): CaptureFixture, AbacSARepository, BaseAbacRepository, Provide casedb SQLAlchemy persistence behavior for ABAC policy data., Provide SQLAlchemy-backed persistence for casedb ABAC policy data., GeoSARepository, Provide SQLAlchemy-backed persistence for casedb geographic data., Provide SQLAlchemy-backed persistence for casedb geographic data. (+46 more)

### Community 69 - "retrieve_case.py"
Cohesion: 0.05
Nodes (65): CaseQueryResult, Represents the case identifiers returned for an executed query., case_service_retrieve_case_cohort_links_by_case_type(), case_service_retrieve_cases_by_id(), case_service_retrieve_cases_by_query(), _get_map_function_for_col(), _get_map_functions_for_filters(), _get_valid_concepts() (+57 more)

### Community 70 - "Filter"
Cohesion: 0.11
Nodes (23): _default_validate_query_filter(), Allow query filters with at most one level of composite filters., Filter, Any, BaseModel, Hashable, Self, Yield column values that match the filter. (+15 more)

### Community 71 - "Role"
Cohesion: 0.10
Nodes (25): Define casedb application roles for command-centric authorization., Role, BaseReadUserPolicyTestCase, scenario_ids, User, UUID, Unit tests for ReadUserPolicy.filter. The tests cover all branches in…, Test unsupported command types and non-read operations. (+17 more)

### Community 72 - ".create_command_and_result_for_samples"
Cohesion: 0.06
Nodes (51): Verify SeqProfile-specific rules. 1. Replace protocol code by ID when only code…, _verify_children_seq_profiles(), create_allele_profile_base64(), Any, ReadSetForUpload, SeqTaxonomy, UUID, Test the _verify_children_seq_profiles function. (+43 more)

### Community 73 - "person_validator.py"
Cohesion: 0.11
Nodes (17): PersonDataIssue, Represents a validation or processing issue in an OMOP person upload., PersonValidator, BaseOmopService, UUID, Person-upload validation and transformation extension points., Encapsulates validation and transformation of person-upload content., Initialize validation state for the service and submitting user. (+9 more)

### Community 74 - ".create_client"
Cohesion: 0.07
Nodes (19): BaseOauthIdpClientTestCase, Any, scenario_ids, Tests for initialization and discovery configuration updates., Base test case with common fixtures and utilities for OauthIdpClient., Test decode raises ExpiredSignatureError and triggers CredentialsAuthError., Test decode raises PyJWTError and triggers CredentialsAuthError., Test decode raises RuntimeError and triggers CredentialsAuthError. (+11 more)

### Community 75 - "BaseAbacTestCase"
Cohesion: 0.07
Nodes (28): BaseAbacTestCase, OrgPolicyDumpStub, Any, scenario_ids, UUID, Create a command-like object with a .user containing an id., Create a user-like object for get_case_abac cached reads., Create a command-like object for update_user_own_organization. (+20 more)

### Community 76 - "ErmGenerator"
Cohesion: 0.09
Nodes (19): ErmGenerator, GraphvizErmGenerator, Domain, Path, Graphviz / erdantic-based ERM diagram generator. Produces PNG Entity-…, Generates Entity-Relationship Model diagrams as PNG files via ``erdantic`` /…, Generate ERM diagrams (PNG) for every domain and its services. Also writes an…, generate_hash_for_domain_models() (+11 more)

### Community 77 - "TestcasedbEdgeCasesRefDataAccess"
Cohesion: 0.06
Nodes (36): CaseTypeSetCategoryCrudCommand, Represent CRUD operations for case-type-set categories., CaseTypeSetCategory, Handle a CRUD command for case-type-set categories. Args: cmd: Case-type-set…, case_service_crud_case_type_set_category(), BaseCaseService, CaseTypeSetCategory, UUID (+28 more)

### Community 78 - "._validate_state"
Cohesion: 0.32
Nodes (5): model_validator, Self, Validate the command's operation-specific state., Validate endpoint identifiers and association-object links., Validate compatible mutability settings.

### Community 79 - "RbacService"
Cohesion: 0.40
Nodes (4): CommonRbacService, Initialize RBAC operations using the seqdb role enumeration. Args: app:…, Encapsulates seqdb RBAC service behavior., RbacService

### Community 80 - "_make_protocol"
Cohesion: 0.07
Nodes (28): ProtocolType, Encapsulates the laboratory or analytical purpose of a protocol., _create_field_description(), Helper function to create field descriptions based on protocol type…, _make_protocol(), _minimal_protocol_data(), Any, parametrize (+20 more)

### Community 81 - "server.py"
Cohesion: 0.03
Nodes (81): delete, BadRequest400HTTPException, Forbidden403HTTPException, ForeignKeyConstraint409HTTPException, InternalServerError500HTTPException, MethodNotAllowed405HTTPException, NotImplemented501HTTPException, Construct an HTTP 409 exception with optional headers. (+73 more)

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

### Community 86 - ".is_allowed"
Cohesion: 0.29
Nodes (6): cached, Command, User, Determine whether a command may proceed under the current outage state. Outage…, Determine whether a user has permission to administer an outage. Args:…, Determine whether no active outage currently restricts requests. Returns: True…

### Community 87 - "_verify_batch_refdata_snp_profiles"
Cohesion: 0.09
Nodes (30): Verify SNP profiles specific rules., _verify_batch_refdata_snp_profiles(), BaseSnpUploadTestCase, scenario_ids, UUID, Create command and result for profiles. Uses model_construct to bypass pydantic…, Create a mock Protocol with ref_seq_id., Set up repository.crud side_effect. (+22 more)

### Community 88 - "TestClientStore"
Cohesion: 0.04
Nodes (27): Any, patch, Test cases for the ClientStore class., Test storing a client., Test storing multiple clients., Test that storing a client with same ID overwrites the previous one., Test retrieving an existing active client., Test retrieving an existing but inactive client returns None. (+19 more)

### Community 89 - "sa_model/seq/__init__.py"
Cohesion: 0.05
Nodes (83): ContentMixin, get_mixin_mapped_column(), Any, Mapped, TypeEngine, Create a mapped column from a Pydantic model-mixin field. The helper derives…, ContentMixin, QualityMixin (+75 more)

### Community 90 - "SampleBatchUploader"
Cohesion: 0.20
Nodes (6): Encapsulates validation and persistence of seqdb sample upload batches., Configure upload processing for seqdb stored model fields., Verify that the command user may upload the supplied sample batch. Args: cmd:…, SampleBatchUploader, Set up test fixtures., Set up test fixtures.

### Community 91 - "EqualsUuidFilter"
Cohesion: 0.04
Nodes (51): AbacService, BaseAbacService, cached, Command, OrganizationAccessCasePolicy, OrganizationShareCasePolicy, User, UserAccessCasePolicy (+43 more)

### Community 92 - "casedb/repositories/sa_model/__init__.py"
Cohesion: 0.05
Nodes (90): Expose and register SQLAlchemy persistence models for casedb entities. The ABAC…, OrganizationAdminPolicy, OrganizationAdminPolicyMixin, Base, declarative_mixin, RowMetadataMixin, Define SQLAlchemy rows and mixins for commondb ABAC policy persistence., Encapsulates SQLAlchemy columns for OrganizationAdminPolicy-derived row models.… (+82 more)

### Community 93 - "calculate_seq_distance.py"
Cohesion: 0.07
Nodes (45): Encapsulates the biological representation used by a sequence profile., SeqProfileType, Return the sequence-profile type used by this distance protocol. Returns: The…, CalculateSeqDistancesResult, Represents the result of calculating distances between existing profiles and…, _calculate_and_store_distances(), _calculate_distance_for_decoded_profile_pair(), _calculate_nextclade_snp_hamming_distance() (+37 more)

### Community 94 - "BaseUploadTestCase"
Cohesion: 0.08
Nodes (28): BaseUploadTestCase, ParentUploadResult, scenario_ids, SeqForUpload, Test that ConcurrentModificationError in distance calculation is a soft failure., Helper to create a SeqForUpload with default or specified properties., Base test case with common fixtures and utilities., Test the _verify_protocol helper. (+20 more)

### Community 95 - ".create_parent_for_upload"
Cohesion: 0.13
Nodes (15): Parent, Test scenarios related to field mutability for existing objects., Test 5.1.1: Always mutable single value field - should be updated., Test 5.1.2: Always mutable list field - should be updated., Test 5.1.3.1: Dict field - add new key with non-None value., Test 5.1.3.2: Dict field - new key with None value should not be added., Test 5.1.3.3: Dict field - update existing key with new value., Test 5.1.3.4: Dict field - remove existing key when new value is None. (+7 more)

### Community 96 - "test_seqdb_distance_optimization_benchmark.py"
Cohesion: 0.07
Nodes (53): _extract_protocol_info(), _extract_segments(), _filter(), _fmt_s(), generate_benchmark_charts(), get_test_client(), _grouped_bars(), _init_profile_generator() (+45 more)

### Community 97 - "sa_model/case.py"
Cohesion: 0.08
Nodes (45): Case, CaseDataCollectionLink, CaseIdentifier, CaseSet, CaseSetCategory, CaseSetDataCollectionLink, CaseSetMember, CaseSetStatus (+37 more)

### Community 98 - "._serialize_int_enums"
Cohesion: 0.29
Nodes (5): field_serializer, IntEnum, UUID, Serializes the IntEnums to their int value., Serializes UUID fields as strings. If the value is None, it returns None.

### Community 99 - "BaseSeqRepository"
Cohesion: 0.07
Nodes (25): BaseSeqRepository, AbstractSet, Any, datetime, SeqDistance, SeqProfile, UUID, Define seqdb domain interfaces and policies for domain.repository.seq. (+17 more)

### Community 100 - "Hashable"
Cohesion: 0.06
Nodes (27): DictAdapter, PolarsAdapter, Any, BaseModel, Hashable, Protocol, PydanticAdapter, Encapsulates adapting a Pydantic model to the field interface. (+19 more)

### Community 101 - "._make_child_parent_id_mismatch_cmd"
Cohesion: 0.14
Nodes (10): ParentBatchUploader, Any, Service to handle batch upload of Parent models., Verify and complete reference data for allele profiles., UploadParentsCommand, LSP-3655: a child-level failure must be visible on its own parent's status (not…, Build a fresh command whose only problem is a child/parent ID mismatch., A FAILED child result must also mark its own parent result FAILED. (+2 more)

### Community 102 - "CasedbTestClient"
Cohesion: 0.07
Nodes (32): Contact, Disease, EtiologicalAgent, RegionSet, RegionSetShape, Site, CasedbTestClient, Case (+24 more)

### Community 103 - "IntEnumWithJsonSchemaMixin"
Cohesion: 0.05
Nodes (42): CoreSchema, FormatType, AstResultFormat, IntEnumWithJsonSchemaMixin, PcrResultFormat, IntEnum, QualityControlResult, Encapsulates ordered quality-control outcomes for sequence data. (+34 more)

### Community 104 - "CaseAbac"
Cohesion: 0.03
Nodes (63): CaseRight, Identify access rights granted for cases and case sets., CaseAbac, CaseTypeAccessAbac, CaseTypeShareAbac, BaseModel, UUID, Compute effective case and case-set rights from resolved ABAC records. Access… (+55 more)

### Community 105 - "make_assoc"
Cohesion: 0.08
Nodes (18): Raise an error when the iterable contains duplicate identifiers., BaseRepositoryTestCase, DummyRepository, make_assoc(), Any, Hashable, Model, scenario_ids (+10 more)

### Community 106 - "OIDCProvider"
Cohesion: 0.10
Nodes (14): OIDCProvider, Any, Create an OpenID Connect ID Token., Validate and decode an ID token., OpenID Connect provider implementation., Create userinfo endpoint response based on scopes., Initialize OIDC provider with JWKS manager., Create OpenID Connect discovery document. (+6 more)

### Community 107 - "TestCrudWithAccessFilter"
Cohesion: 0.07
Nodes (18): DataCmd, DummyCmd, DummyEntity, DummyLink, MetaCmd, NoAbacCmd, OtherCmd, scenario_ids (+10 more)

### Community 108 - "CaseBatchUploader"
Cohesion: 0.11
Nodes (15): CaseBatchUploader, Model, UUID, Re-validate content merged with each case's stored content. This catches…, Verify or upload seqdb samples and map results back to cases. The method…, Encapsulates verification and persistence of case upload batches. The uploader…, Initialize a case batch uploader for a case service. Args: service: Service…, Filter uploaded values according to per-case ABAC rights. This requires knowing… (+7 more)

### Community 109 - "test_seqdb_calculate_seq_distances_performance.py"
Cohesion: 0.07
Nodes (51): Expose seqdb repository implementations for application composition., Provide seqdb persistence behavior for repositories.seq_dict., Encapsulates seqdb persistence behavior for sequence repositories using in-…, SeqDictRepository, Provide seqdb persistence behavior for repositories.seq_sa., Encapsulates seqdb persistence behavior for sequence repositories using…, SeqSARepository, TempPathFactory (+43 more)

### Community 110 - "sa/util.py"
Cohesion: 0.09
Nodes (36): compiles, ComputedFieldInfo, get_type_from_annotation(), Any, Adapted from https://github.com/fastapi/sqlmodel v0.0.24., Repository implementations and unit-of-work exports., SQLAlchemy repository, mapper, and unit-of-work exports., create_sa_type_from_field_info() (+28 more)

### Community 111 - "TestClient"
Cohesion: 0.04
Nodes (63): Any, Command, DataCollection, datetime, Model, Organization, OrganizationAdminPolicy, OrganizationIdentifierIssuerLink (+55 more)

### Community 112 - "ImportGraphAnalyzer"
Cohesion: 0.07
Nodes (30): Import, ImportFrom, analyze_imports(), ImportEdge, ImportGraphAnalyzer, ImportStatementVisitor, ModuleNode, Path (+22 more)

### Community 113 - "CaseValidator"
Cohesion: 0.05
Nodes (46): Represent an atomic batch upload of cases and associated data. The upload…, UploadCasesCommand, CaseBatchUploadResult, CaseDataIssue, Represents a case-content issue associated with a column., Represents the results of uploading a batch of cases., Upload a batch of cases and related data. Implementations may persist cases,…, CaseValidator (+38 more)

### Community 114 - ".crud"
Cohesion: 0.06
Nodes (25): Return a unit of work for this repository., Any, App, CrudCommand, datetime, Hashable, Logger, Model (+17 more)

### Community 115 - "case_service_retrieve_is_own_cases"
Cohesion: 0.12
Nodes (24): case_service_retrieve_is_own_cases(), BaseCaseService, UUID, Map accessible requested cases to private-collection ownership flags. Invalid…, BaseIsOwnCasesTestCase, Case, Command, scenario_ids (+16 more)

### Community 116 - "Concept"
Cohesion: 0.08
Nodes (30): ConceptClass, ConceptRelationship, FactRelationship, ConceptClass (omopdb.md), ConceptRelationship (omopdb.md), EpisodeEvent (omopdb.md), FactRelationship (omopdb.md), Relationship (omopdb.md) (+22 more)

### Community 117 - ".upload_batch"
Cohesion: 0.08
Nodes (25): Test combinations of different scenarios., Test parent with both children and Identifiers., Test updating an existing parent with new child objects., Test complex reference data resolution across multiple children., Test Child2 with Identifiers in combination with parent relationships and other…, verify_only=True and verify_only=False must agree on batch outcome., Create a test child1 for upload., Create a test Ref1 object. (+17 more)

### Community 118 - "Concept (omopdb.omop / OMOP CDM entity)"
Cohesion: 0.13
Nodes (39): CareSite (omopdb.omop / OMOP CDM entity), CdmSource (omopdb.omop / OMOP CDM entity), Cohort (omopdb.omop / OMOP CDM entity), CohortDefinition (omopdb.omop / OMOP CDM entity), Concept (omopdb.omop / OMOP CDM entity), ConceptAncestor (omopdb.omop / OMOP CDM entity), ConceptClass (omopdb.omop / OMOP CDM entity), ConceptRelationship (omopdb.omop / OMOP CDM entity) (+31 more)

### Community 119 - "test_update_user_policy.py"
Cohesion: 0.27
Nodes (14): _make_abac_service(), _make_invite_cmd(), _make_policy(), _make_role_set_map(), _make_update_cmd(), _make_user(), scenario_ids, User (+6 more)

### Community 120 - "seq_service_calculate_seq_distances_for_new_profiles"
Cohesion: 0.11
Nodes (32): Calculate and persist distances for newly supplied sequence profiles. For each…, seq_service_calculate_seq_distances_for_new_profiles(), _CrudRecorder, _make_allele_profile(), _make_crud_side_effect(), _make_mlva_profile(), _make_nextclade_content(), _make_seq_distance() (+24 more)

### Community 121 - "test_fastapp_repository_performance.py"
Cohesion: 0.08
Nodes (22): parse_stats(), Any, Append profiler function statistics to a row-oriented result list. Args: df:…, Create a test environment for the given test type and repository type. A single…, scenario_ids, TestRead, scenario_ids, TestStartup (+14 more)

### Community 122 - "DummyCommand"
Cohesion: 0.12
Nodes (13): DummyCommand, Command, Test get_headers method for different auth protocols., get_headers returns default headers with NONE protocol., get_headers caches token when not expired., get_headers refreshes token past refresh margin., Minimal command for testing., get_headers caches long-lived tokens correctly. Note: Tokens without an 'exp'… (+5 more)

### Community 123 - "CacheRegion"
Cohesion: 0.01
Nodes (140): CacheBackend, ProxyBackend, ABC, Abstract cache store contract. A backend is a dumb key-to-envelope store. It…, Return a store-provided mutex for regenerating `key`. Returns: A mutex when the…, Release the resources held by the store., Encapsulates altering the behavior of another backend without subclassing it.…, Initialize a ProxyBackend instance. (+132 more)

### Community 124 - "BaseCaseValidatorTestCase"
Cohesion: 0.10
Nodes (18): BaseCaseValidatorTestCase, Concept, Organization, Region, scenario_ids, UUID, Base test case with common fixtures and helpers for CaseValidator tests., Regression test for LSP-3417. ``_get_col_pairs`` generates both directions, so… (+10 more)

### Community 125 - "OAuth2Validator"
Cohesion: 0.07
Nodes (22): RequestValidator, Test OAuth2Validator initialization., OAuth2Validator, Any, Save authorization code (not used in client credentials flow)., Validate authorization code (not used in client credentials flow)., Confirm redirect URI (not used in client credentials flow)., Validate that the grant type is supported by the client. (+14 more)

### Community 126 - ".create_case_for_upload"
Cohesion: 0.09
Nodes (15): ReadSetForUpload, SeqForUpload, Batch can contain cases from different DCs., Tests for ABAC column and creation-right verification in verify_abac_rights., Tests for the has_case guard added to _get_upload_samples_command., Tests for CaseBatchForUpload.has_samples (the pure predicate on the batch…, Tests for default_created_in_data_collection_id behavior. NOTE: Direct unit…, When new case has NULL_ID and no default, should add error. (+7 more)

### Community 127 - "cache/__init__.py"
Cohesion: 0.02
Nodes (169): Clock, Protocol, Time sources used by the cache framework. Every expiry decision in this package…, Encapsulates supplying the monotonic and wall-clock readings a cache needs., Return a strictly non-decreasing reading in seconds., Return the current wall-clock time as a Unix timestamp., Encapsulates reading time from the operating system. Expiry uses `monotonic` so…, SystemClock (+161 more)

### Community 128 - "SAMapper"
Cohesion: 0.06
Nodes (31): Any, Hashable, Model, Get row ID from row object or row class., Dump model object to SQLAlchemy row object., Update row with model object values., Load model object from SQLAlchemy row., Get the schema name from the row class __table_args__. (+23 more)

### Community 129 - "Person"
Cohesion: 0.08
Nodes (40): ConditionEra, ConditionEra (omopdb.md), Observation (omopdb.md), VisitOccurrence (omopdb.md), CareSite, ConditionEra, DeviceExposure, DeviceExposureIdentifier (+32 more)

### Community 130 - "PersonForUpload"
Cohesion: 0.09
Nodes (26): PersonForUpload, ParentForUpload, Represents a person, together with any relevant associated data, intended for…, get_test_client(), _make_person(), Env, fixture, MonkeyPatch (+18 more)

### Community 132 - "._get_allele_profile_for_ids"
Cohesion: 0.08
Nodes (17): Test that seqs property maintains proper structure for serialization., Test SampleForUpload without id where seqs can have their own sample_ids., Test SampleForUpload without id where seqs also have NULL_ID sample_ids., Test has_seqs computed field returns False when no samples have seqs., Test valid SampleForUpload with sample_id., Test valid SampleForUpload with Identifiers., Test valid SampleForUpload with both sample_id and sample_ids., Test valid SampleForUpload with multiple identifiers. (+9 more)

### Community 133 - "RBACTestClient"
Cohesion: 0.10
Nodes (16): ServiceUser, get_test_client(), Any, BaseRbacService, CrudCommand, Enum, fixture, Hashable (+8 more)

### Community 134 - "model_anonymizer.py"
Cohesion: 0.08
Nodes (26): Collection, AnonMethod, AnonStrictness, Encapsulates the enforcement level for anonymization requirements., Encapsulates available anonymization transformations., BaseAnonymizer, ModelAnonymizer, ABC (+18 more)

### Community 135 - "Concept"
Cohesion: 0.08
Nodes (29): Concept, ConceptAncestor, ConceptSynonym, Cost, Domain, DoseEra, DrugEra, DrugStrength (+21 more)

### Community 137 - ".__init__"
Cohesion: 0.22
Nodes (6): BaseRbacService, User, UserInvitation, Validate optional defaults used to create previously unknown users. Args:…, Initialize identity claim settings and user creation configuration. Args:…, Validate and construct the root organization and root user. Args: root_cfg:…

### Community 138 - "BaseRepository"
Cohesion: 0.08
Nodes (24): Any, Enum, Return services keyed by their service type., Return repositories keyed by their service type., Create a repository using the configured persistence backend. Args: cls:…, BaseRepository, Any, Hashable (+16 more)

### Community 139 - "api/seq.py"
Cohesion: 0.10
Nodes (25): PydanticBaseModel, Expose seqdb api.seq API adapters and request representations., # TODO: remove max_new_profiles usage and replace by limit, Docstring assigned automatically., Docstring assigned automatically., Docstring assigned automatically., Docstring assigned automatically., Docstring assigned automatically. (+17 more)

### Community 140 - ".create_crud_cmd"
Cohesion: 0.11
Nodes (17): BasePolicyTestCase, CrudCommand, Model, OrganizationAdminPolicy, scenario_ids, User, UUID, Create a user with optional roles and organization. (+9 more)

### Community 141 - ".create_child2_for_upload"
Cohesion: 0.11
Nodes (17): Test scenarios related to Identifiers for Child2 objects., Test 9.1: No Identifiers provided for Child2 - should succeed., Test 9.2.1.1: Existing Identifier with NULL child2 ID - should set child2 ID., Test 9.2.1.2.1: Existing Identifier with same child2 ID - should succeed., Test 9.2.1.2.2: Existing Identifier with different child2 ID - should fail., Test 9.2.2: New Identifier for new child2 - should succeed., Test 9.2.3.1: Multiple Identifiers, some existing for same child2 - should…, Test 9.2.3.1: Multiple Identifiers, some existing for different child2 - should… (+9 more)

### Community 142 - "TestModelSampleBatchForUpload"
Cohesion: 0.08
Nodes (14): Create a SampleForUpload with specified number of SeqForUpload instances., Test reading sample_batch_for_upload1.json as SampleBatchForUpload model., Test reading sample_batch_for_upload2.json as SampleBatchForUpload model., Test valid SampleBatchForUpload with minimal data., Test valid SampleBatchForUpload with alleles., Test valid SampleBatchForUpload with multiple samples including seqs., Test valid SampleBatchForUpload with empty samples list., Test SampleBatchForUpload where all samples contain SeqForUpload instances. (+6 more)

### Community 143 - "case/non_persistable.py"
Cohesion: 0.06
Nodes (31): CaseCohortLink, CaseQuery, CaseSetQuery, BaseModel, Model, UUID, Define non-persistable case query, rights, statistics, and result models. These…, Represents labeled filter criteria for querying case sets. (+23 more)

### Community 144 - "crud_file.py"
Cohesion: 0.05
Nodes (32): UUID, Create a sequence file and return its identifier. Implementations persist file…, Retrieve profiles similar to a specified profile. Args: cmd: Similarity command…, Seq, UUID, Retrieve sequence objects from seqdb by ID., Create a seqdb file under the configured functional user. The command's…, Retrieve similar profile IDs under the configured functional user. The… (+24 more)

### Community 145 - "TestUpdate"
Cohesion: 0.15
Nodes (4): Env, scenario_ids, skipif, TestUpdate

### Community 146 - "SeqdbTestClient"
Cohesion: 0.09
Nodes (23): FileCompression, FileFormat, Encapsulates all supported biological file formats., Encapsulates supported compression methods for biological files., UUID, Verify a FASTQ payload has valid DNA records and matching quality scores. Args:…, Validate file content and create its persisted file record. Args: cmd: File-…, Decode possibly gzip-compressed UTF-8 content into a text stream. Args:… (+15 more)

### Community 147 - "TestModelBaseSeq"
Cohesion: 0.08
Nodes (17): UUID, Test cases for BaseSeq model validation and functionality., Return a valid DNA sequence for testing., Return an invalid DNA sequence for testing., Compute the expected sequence hash for a given sequence., Test creating BaseSeq with valid DNA sequence., Test that DNA sequences are normalized to lowercase., Test that length is automatically calculated when set to 0. (+9 more)

### Community 148 - "CacheStatistics"
Cohesion: 0.02
Nodes (143): Return the counters observed by this store., AsyncCachedFunction, BoundCachedFunction, CachedFunction, make_cached_function(), Any, Declarative caching of function results. `CachedFunction` is what makes…, Return the logical cache key for one argument combination. A writer that wants… (+135 more)

### Community 149 - "Case Type"
Cohesion: 0.08
Nodes (26): ColSet, Disease, Etiology, CaseTypeSetMember (doc), ColSet (doc), ColSetMember (doc), Case Type, Case Type Set Member (+18 more)

### Community 150 - "case_service_retrieve_similar_cases"
Cohesion: 0.11
Nodes (21): case_service_retrieve_similar_cases(), BaseCaseService, Retrieve accessible cases genetically similar to the query cases. Profiles are…, Run `operation`, giving up after the configured timeout. Args: operation: The…, Return the worker pool, creating it on first use., BaseSimilarCasesTestCase, Case, Col (+13 more)

### Community 151 - "command/case.py"
Cohesion: 0.03
Nodes (92): CreateCaseSetCommand, BaseModel, Command, field_validator, UUID, Define casedb commands for case schemas, content, sets, and sequence links., Represent a request for statistics about case types. Optional parameters…, Represent a request for statistics about case sets. Optional parameters further… (+84 more)

### Community 152 - ".__init__"
Cohesion: 0.09
Nodes (17): User, UserInvitation, Initialize the repository with its user and invitation model classes. Args:…, Retrieve the user associated with a normalized unique key. Args: uow: Unit of…, Any, Hashable, Model, User (+9 more)

### Community 153 - "Data Collection"
Cohesion: 0.12
Nodes (28): ColSet, DataCollection, Organization, OrganizationAdminPolicy, User, CaseTypeSet (doc), Case Type Set, Col Set (+20 more)

### Community 154 - "test_fastapp_cache_region.py"
Cohesion: 0.02
Nodes (138): ManualClock, Encapsulates advancing only when a test tells it to. Both readings start at…, Initialize a ManualClock instance., Move the clock forward and return the new reading. Args: seconds: A non-…, Set both readings to an absolute value. Args: value: The new reading. Raises:…, InlineRefreshRunner, Encapsulates refreshing stale entries on the calling thread. This makes a stale…, Random (+130 more)

### Community 155 - "Any"
Cohesion: 0.06
Nodes (27): field_serializer, Serialize dim-type keys and col-type sets to plain string dicts., DimType, Classify the kind of data grouped by a case-type dimension., Define supported phylogenetic-tree and clustering algorithms., TreeAlgorithmType, Any, field_serializer (+19 more)

### Community 156 - ".name"
Cohesion: 0.40
Nodes (3): computed_field, Return the canonical permission name., Return the stable sort key for this permission.

### Community 157 - "ServerManager"
Cohesion: 0.04
Nodes (61): AppComposer, Any, CommonAppComposer, Encapsulates casedb registrations for shared application composition. The…, Initialize and run casedb application composition. Construction delegates…, create_fast_api(), Any, App (+53 more)

### Community 158 - "test_fastapp_cache_support.py"
Cohesion: 0.03
Nodes (93): CantDeserializeError, Error for a value that could not be converted to its stored form., Error for a stored value that the current code can no longer read. A region…, SerializationError, compute_etag(), HttpCachePolicy, matches_etag(), HTTP-level caching helpers. Caching at the transport boundary is a different… (+85 more)

### Community 159 - ".expectStatusCount"
Cohesion: 0.10
Nodes (17): ParentUploadResult, Test 6.1: No Identifiers provided - should succeed., Test scenarios related to the on_exists and on_new command parameters., Test 7.1: on_exists=ERROR with existing object - should fail., Test 7.2: on_exists=SKIP with existing object - should skip., Test 7.3: on_exists=UPDATE with existing object - should update., Test 7.4: on_new=CREATE with new object having provided ID - should create., Test 7.5: on_new=SKIP with new object having provided ID - should skip. (+9 more)

### Community 160 - "TestModelSeq"
Cohesion: 0.09
Nodes (16): Seq, Test cases for Seq model functionality and inheritance., Create a valid Contig for testing., Create a sample Seq with default values and optional overrides., Test creating Seq with contigs., Test creating Seq without contigs (not available)., Test that Seq inherits HasSampleMixin properties., Test that Seq inherits CodeMixin properties. (+8 more)

### Community 161 - "CaseSet"
Cohesion: 0.09
Nodes (28): Case, Case, CaseAccessAbac, CaseRights, CaseSet, CaseSetAccessAbac, CaseSetForUpload, CaseSetRights (+20 more)

### Community 162 - "CaseType"
Cohesion: 0.11
Nodes (21): CaseQuery, CaseQueryResult, CaseSetQuery, CaseType, CaseTypeAccessAbac, CaseTypeCategory, CaseTypeCol, Col (+13 more)

### Community 163 - "UUID"
Cohesion: 0.07
Nodes (19): Case, CaseSet, CaseSetMember, Col, CrudCommand, Model, RefCol, User (+11 more)

### Community 164 - ".create_local_or_remote_app"
Cohesion: 0.09
Nodes (19): Any, App, Domain, Enum, Logger, User, Register an invited user using their invitation token., Update a user's active status, roles, or organization. (+11 more)

### Community 165 - "InMemoryOrganizationRepository"
Cohesion: 0.09
Nodes (18): NoResultsError, Error for an operation that expected matching data but found none., InMemoryOrganizationRepository, make_commondb_user_manager(), make_mock_organization_service(), make_mock_rbac_service(), make_root_cfg(), Any (+10 more)

### Community 166 - "omopdb/domain/enum.py"
Cohesion: 0.06
Nodes (30): Command, Enum, Role, Map commondb role permissions to equivalent domain roles and commands. The…, Map the commondb role hierarchy to equivalent domain roles. The mapping…, Return string values for commondb and mapped domain roles. The mapping returns…, Return string role sets for commondb and mapped domain role sets. The mapping…, Return permissions indexed by commondb or mapped domain role values. The… (+22 more)

### Community 167 - "test_casedb_upload.py"
Cohesion: 0.08
Nodes (34): BaseUploadTestCase, _mock_uow(), Case, datetime, parametrize, scenario_ids, UUID, Unit tests for casedb case upload functionality. (+26 more)

### Community 168 - "create_client"
Cohesion: 0.12
Nodes (15): assert_logged_with_code(), create_client(), DummyRequest, make_request(), parametrize, scenario_ids, UUID, Authorization header parsing and scheme handling. (+7 more)

### Community 169 - "DummyCmd"
Cohesion: 0.22
Nodes (4): DummyCmd, Command, TestHeadersAndApplyHandler, TestRouteRegistration

### Community 170 - "._create_sample_seq_for_upload"
Cohesion: 0.09
Nodes (16): Create a sample SeqForUpload with default values and optional overrides., Test cases for SeqForUpload model functionality and upload-specific features., Test creating SeqForUpload with basic fields., Test that SeqForUpload inherits all Seq properties., Test SeqForUpload with NULL_ID for sample_id., Test that sample_id serialization handles NULL_ID correctly., Test upload-specific field handling., Test JSON serialization structure of SeqForUpload. (+8 more)

### Community 171 - "OAuth2Client"
Cohesion: 0.10
Nodes (16): demo_client_credentials_flow(), OAuth2Client, Any, OAuth 2.0 Client Test Script This script demonstrates how to use the OAuth 2.0…, Create a new OAuth client., Delete an OAuth client., List all OAuth clients., Simple OAuth 2.0 client for testing. (+8 more)

### Community 172 - "test_seqdb_calculate_phylogenetic_tree.py"
Cohesion: 0.16
Nodes (13): scenario_ids, Verify update_some_seq_distance_content against a real SA_SQLITE database., TestBulkUpdateSeqDistanceContentSA, _make_protocol(), _make_seq_distance(), _mock_uow(), Any, Protocol (+5 more)

### Community 173 - "create_mapped_column"
Cohesion: 0.09
Nodes (26): declared_attr, Mapped, Organization, UUID, Map the owning organization ID column., Map the owning organization relationship., Map the optional site ID column., Map the optional site relationship. (+18 more)

### Community 174 - "Protocol"
Cohesion: 0.12
Nodes (28): Identifier Issuer, IdentifierIssuer, File, AstMeasurement, AstPrediction, LocusSet, PcrMeasurement, Protocol (+20 more)

### Community 175 - "Person"
Cohesion: 0.16
Nodes (24): CareSite, DeviceExposure, DrugExposure, Location, CareSite (omopdb.md), DeviceExposure (omopdb.md), DrugExposure (omopdb.md), Location (omopdb.md) (+16 more)

### Community 176 - "Protocol (seqdb entity)"
Cohesion: 0.13
Nodes (27): AstMeasurement (seqdb entity), AstPrediction (seqdb entity), File (seqdb entity), IdentifierIssuer (seqdb entity), LocusSet (seqdb entity), OrganizationIdentifierIssuerLink (seqdb entity), PcrMeasurement (seqdb entity), Protocol (seqdb entity) (+19 more)

### Community 177 - "RetrieveOutagesCommand"
Cohesion: 0.11
Nodes (15): Command, Represents a request to retrieve current and scheduled system outages for…, Represents a request to retrieve license metadata for installed application…, Represents a request to retrieve feature flags exposed by the composed…, RetrieveFeatureFlagsCommand, RetrieveLicensesCommand, RetrieveOutagesCommand, Hashable (+7 more)

### Community 178 - "TestCommondbDictModelModifier"
Cohesion: 0.06
Nodes (26): CommondbDictModelModifier, datetime, Hashable, Model, Encapsulates a DictRepository modifier for all databases that use…, Initialize the source of timezone-aware audit timestamps. Args:…, Stamp a new commondb model with creation and modification metadata. Args:…, Refresh modification metadata while preserving the stored creation time. Args:… (+18 more)

### Community 179 - "EndpointTestClient"
Cohesion: 0.07
Nodes (28): EndpointTestClient, Any, Command, CrudCommand, Response, Register a command class with its endpoint-dispatch handler. Args:…, Dispatch a supported command to its corresponding API endpoint. Args: cmd:…, Request identity providers and deserialize the returned list. Args: cmd:… (+20 more)

### Community 180 - "User"
Cohesion: 0.09
Nodes (14): Any, Hashable, User, Update the user's name in the user manager., Get the user key, which uniquely identifies the user across systems, from the…, Construct user instance from identity claims., Create root user from identity claims., Check if claims belong to root user. (+6 more)

### Community 181 - "AuthEnv"
Cohesion: 0.12
Nodes (8): AuthEnv, scenario_ids, Self-contained, per-test auth environment built around the real…, Verify that unknown users are auto-created when the flag is on, and rejected…, Verify that a root user can log in for the first time (triggering…, Drive get_existing_user_from_claims directly (no HTTP stack)., TestAutoCreateUser, TestRootUserLogin

### Community 182 - "_DummyMapper"
Cohesion: 0.11
Nodes (10): _DummyMapper, _make_mapper(), _make_row_class(), _Model, Any, Hashable, scenario_ids, _RowBase (+2 more)

### Community 183 - "UUID"
Cohesion: 0.10
Nodes (13): datetime, SeqDistance, SeqProfile, UUID, Yield requested sequences and their DNA contigs for FASTA generation. Args:…, Yield distance records for a protocol, optionally limited to profile IDs., Yield unique profile IDs that have distance records for a protocol., Return the latest modification time among a protocol's distance records. (+5 more)

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
Cohesion: 0.40
Nodes (4): model_validator, Self, Normalize and validate the sequence representation, length, and hash. Derives…, Validate that the content hash matches the content.

### Community 188 - "case_date.py"
Cohesion: 0.11
Nodes (26): case_service_calculate_case_date(), case_service_get_case_date_col_mappers(), case_service_get_case_date_col_mappers_from_cols(), convert_iso_date_to_datetime(), convert_iso_month_to_first_day_datetime(), convert_iso_quarter_to_first_day_datetime(), convert_iso_week_to_first_day_datetime(), convert_iso_year_to_first_day_datetime() (+18 more)

### Community 189 - ".anonymize_user"
Cohesion: 0.20
Nodes (6): cached, User, Retrieve and cache a user by normalized key. Args: user_key: User key to…, Register an invited user and consume related active and expired invitations.…, Update a user's active state, roles, and organization membership. Args: cmd:…, Anonymize a target user and deactivate their account. Args: cmd: Command…

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

### Community 194 - "case_service_crud_ref_col"
Cohesion: 0.06
Nodes (28): Represent CRUD operations for reusable reference-column definitions., RefColCrudCommand, ColType, Classify the representation and semantics of a case-data column., datetime, UUID, Build temporal-resolution date normalization functions. Returns: A mapper for…, Read aggregate statistics for a case type within a unit of work.… (+20 more)

### Community 195 - "CasedbRemoteApp"
Cohesion: 0.16
Nodes (12): CasedbRemoteApp, Retrieve cohort links for a given case type., Retrieve the full definition of a case type., Encapsulates remote casedb command dispatch over HTTP. Initialization first…, Retrieve access rights for case sets., app(), mock_client(), _mock_response() (+4 more)

### Community 196 - "CompositeFilter"
Cohesion: 0.13
Nodes (21): Recursively partition a filter into a SQL-expressible subtree and a remainder…, CompositeFilter, Any, BaseModel, Hashable, model_validator, Self, Match a value using the function generated during validation. Args: value: The… (+13 more)

### Community 197 - "IntervalTransformer"
Cohesion: 0.13
Nodes (13): IntervalTransformer, Return whether `value` matches an interval without mutating an object., Encapsulates mapping a numeric field to its configured interval. Bounds may be…, scenario_ids, Test transform_value method for direct value transformation., Test with Decimal input values., Test cases for IntervalTransformer., Test basic number to interval mapping. (+5 more)

### Community 198 - "test_casedb_user_journey_performance.py"
Cohesion: 0.03
Nodes (67): NoFilter, Any, BaseModel, Hashable, Represents a filter retaining every value unless explicitly inverted., Return the non-inverted pass-through result., Yield a pass-through match for every column value., Yield every column value when the filter is not inverted. (+59 more)

### Community 199 - "map_paired_elements"
Cohesion: 0.18
Nodes (5): map_paired_elements(), Any, Hashable, Group paired values by key while preserving input order for lists. With…, datetime

### Community 200 - "TestCreate"
Cohesion: 0.17
Nodes (4): Env, scenario_ids, skipif, TestCreate

### Community 201 - "BaseUploadTestCase"
Cohesion: 0.07
Nodes (23): BaseUploadTestCase, scenario_ids, Base test case with common fixtures and utilities., Set up test fixtures., Test upload with varying batch sizes., Test 8.1: Upload batch of n new parent objects., Test 8.2: Upload parent with varying number of Child1 objects., Focused edge-case tests for upload consistency and null semantics. (+15 more)

### Community 202 - "TestNumpyAlleleIntegration"
Cohesion: 0.14
Nodes (10): parametrize, Unit tests for all new numpy ALLELE distance code paths (LSP-3529)., Run _calculate_and_store_distances directly for ALLELE profiles. Returns…, _decode_profile with use_numpy_allele=True returns (n_loci,) S16 array; null…, The isinstance(np.ndarray) branch in…, Each invalid variant-flag combination raises ValueError., numpy_batch path stores correct cross and intra-batch distances., int32_vocab path produces identical distances to numpy_batch. (+2 more)

### Community 203 - "DummyIdpClient"
Cohesion: 0.10
Nodes (12): Request, Extract claims from JWT token., Returns the claims of the user from the request or None if claims cannot be…, DummyIdpClient, Any, Request, scenario_ids, Test abstract method behavior exposed via base class. (+4 more)

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

### Community 210 - "EvictionStrategy"
Cohesion: 0.02
Nodes (52): Initialize a MemoryBackend instance. Args: max_weight: Total weight the store…, CountMinSketch, create_eviction_strategy(), EvictionStrategy, FIFOEviction, LFUEviction, LRUEviction, ABC (+44 more)

### Community 211 - "TestCreateUserFromToken"
Cohesion: 0.20
Nodes (11): make_cdb_invitation(), make_cdb_organization(), parametrize, UserInvitation, UUID, Return a valid future-expiring UserInvitation., Verify that the commondb UserManager correctly creates a user from an…, Build an AuthEnv with a pre-stored creator (inviting) user. (+3 more)

### Community 212 - "TestInitialization"
Cohesion: 0.09
Nodes (12): Test CommondbRemoteApp initialization with various configurations., Initialize with NONE auth protocol as enum., Initialize with NONE auth protocol as string., Initialize with OAUTH2 auth protocol as enum., Initialize with OAUTH2 auth protocol as string., Initialize with OAuthFlow as enum., Initialize with OAuthFlow as string., Verify default route prefix is /v1. (+4 more)

### Community 213 - "RequestorApp"
Cohesion: 0.05
Nodes (30): Response, RequestorApp Module This module contains the RequestorApp client that requests…, Client application that requests access tokens and calls protected endpoints., Initialize the OIDC client., Get an access token for the specified audience., Call a protected endpoint with the access token., Create a properly formatted but invalid JWT token for testing., RequestorApp (+22 more)

### Community 214 - "SeqGenerationSettings"
Cohesion: 0.18
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
Nodes (14): Env, fixture, integration, scenario_ids, modified_at must be set by the backend on creation., modified_by must be set to the creating user's id., created_at must not change when a record is updated., modified_by must be stamped with the updating user, not the creating user. (+6 more)

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

### Community 225 - "SeqdbRemoteApp"
Cohesion: 0.07
Nodes (19): Any, datetime, SampleIdentifier, UUID, Stream genetic sequence FASTA data by sequence IDs., Upload a file and return its assigned UUID., Retrieve profile IDs similar to the given profiles within a distance threshold., Encapsulates the remote app client for the seqdb service. (+11 more)

### Community 226 - "convert"
Cohesion: 0.20
Nodes (5): Any, Reconstruct a nucleotide sequence from a NextClade representation. Args:…, convert(), parametrize, TestNextcladeSequenceConversion

### Community 227 - "BaseSeqDistancePerformance"
Cohesion: 0.27
Nodes (7): BaseSeqDistancePerformance, ensure_datasets_exist_and_valid(), get_test_client(), Env, fixture, parametrize, RepositoryType

### Community 228 - "CrudCommand"
Cohesion: 0.08
Nodes (38): ColCrudCommand, CrudCommand, Represent CRUD operations for typed case-data columns., Represent CRUD operations for reusable reference dimensions., Represent CRUD operations for phylogenetic algorithm categories., Represent CRUD operations for phylogenetic-tree algorithms., RefDimCrudCommand, TreeAlgorithmClassCrudCommand (+30 more)

### Community 229 - "sa_model/geo.py"
Cohesion: 0.26
Nodes (11): Base, RowMetadataMixin, Define SQLAlchemy persistence mappings for casedb geographic models., Persist the casedb RegionSet domain model., Persist the casedb RegionSetShape domain model., Persist the casedb Region domain model., Persist the casedb RegionRelation domain model., Region (+3 more)

### Community 230 - ".__init__"
Cohesion: 0.33
Nodes (5): Any, App, BaseAbacRepository, Logger, Initialize ABAC model, command, policy, and role mappings. Args: app:…

### Community 231 - "test_seqdb_calculate_seq_distance.py"
Cohesion: 0.15
Nodes (16): InvalidArgumentsError, Error for command arguments that fail validation., BaseCalculateSeqDistanceTestCase, _iterable(), _make_user(), _mock_uow(), fixture, ndarray (+8 more)

### Community 232 - "Any"
Cohesion: 0.07
Nodes (36): Concept, ConceptAncestor, ConceptClass, ConceptRelationship, ConceptSynonym, Domain, DrugStrength, Any (+28 more)

### Community 233 - "TestAuth"
Cohesion: 0.20
Nodes (5): get_name_from_claims(), Get the name from the claims, checking against a list of possible name claims., Pure unit tests for claim name-extraction helpers and update_user_name., Verify the real UserManager writes the name change to the repo., TestAuth

### Community 234 - "TestCasedbMetadataMasking"
Cohesion: 0.19
Nodes (9): CaseType, integration, scenario_ids, User, Verifies that MaskModelProcessMetadataPolicy is correctly wired in casedb. Root…, Root user must see all three metadata fields populated — superusers bypass…, Org admin must see all three metadata fields masked to None by…, Org user must see all three metadata fields masked to None by… (+1 more)

### Community 235 - "CircuitBreaker"
Cohesion: 0.04
Nodes (40): Return the default failure policy implied by the configuration. A configured…, CircuitBreaker, FailurePolicy, BaseException, Return the state, moving an expired open breaker to half open., Open the breaker and start its reset timer., Encapsulates bounding the wall-clock duration of a backend call. The call runs…, Initialize a TimeoutGuard instance. Args: timeout: Seconds allowed for one… (+32 more)

### Community 236 - "test_read_config.py"
Cohesion: 0.29
Nodes (17): _assert_default_import_payload(), _assert_string_override_payload(), override_tmp_dir(), fixture, parametrize, Path, scenario_ids, Construct and compose an app config, returning key config/auth values. (+9 more)

### Community 237 - "TestDataLineageMixin"
Cohesion: 0.14
Nodes (10): FieldInfo, Tests for the DataLineageMixin class. DataLineageMixin is a plain mixin (not a…, DataLineageMixin should declare a provenance_id annotation., DataLineageMixin should declare a source_traceback annotation., The provenance_id Field should have a default of None., The source_traceback Field should have a default of None., The source_traceback Field should enforce max_length=255., The provenance_id annotation should allow UUID | None. (+2 more)

### Community 238 - "ClientStore"
Cohesion: 0.06
Nodes (23): ClientStore, Any, OAuth 2.0 Client Store This module manages OAuth 2.0 client registration and…, Retrieve a client by client ID., Delete a client from the store., Deactivate a client (soft delete)., List all active clients., Check if a client exists and is active. (+15 more)

### Community 239 - "Organization (commondb.organization entity)"
Cohesion: 0.22
Nodes (17): Contact (commondb.organization entity), IdentifierIssuer (commondb.organization entity), Organization (commondb.organization entity), OrganizationIdentifierIssuerLink (commondb.organization entity), Site (commondb.organization entity), User (commondb.organization entity), UserInvitation (commondb.organization entity), commondb / ORGANIZATION — Simplified ERD (+9 more)

### Community 240 - "crud_case_data_collection_link.py"
Cohesion: 0.16
Nodes (17): CaseDataCollectionLinkCrudCommand, Represent CRUD operations for case-to-data-collection links., CaseDataCollectionLink, Handle a CRUD command for case data-collection links. Args: cmd: Case data-…, case_service_crud_case_data_collection_link(), _crud_case_data_collection_link_with_abac(), _crud_case_data_collection_link_without_abac(), BaseCaseService (+9 more)

### Community 241 - "check_docstrings.py"
Cohesion: 0.09
Nodes (37): audit_file(), check_coverage(), check_exception_classes(), check_package(), check_pydantic(), check_raises(), decorator_name(), has_decorator() (+29 more)

### Community 242 - "BaseCaseService"
Cohesion: 0.04
Nodes (110): DomainBaseCaseService, CaseCrudCommand, CaseIdentifierCrudCommand, CaseSetDataCollectionLinkCrudCommand, CaseSetMemberCrudCommand, CaseTypeSetMemberCrudCommand, Represent CRUD operations for typed cases in data collections., Represent CRUD operations for alternate and external case identifiers. (+102 more)

### Community 243 - ".upload_batch"
Cohesion: 0.11
Nodes (20): SpecimenIdentifier, Test scenarios related to Identifiers for Specimen objects., Test 8.1: Specimen without Identifiers - should succeed., Test 8.2.1.1: Existing Identifier with NULL specimen ID - should set specimen…, Test 8.2.1.2.1: Existing Identifier with same specimen ID - should succeed., Test 8.2.1.2.2: Existing Identifier with different specimen ID - should fail., A retried derived-specimen chain (e.g. a repeat culture attempt) that carries…, Test 8.2.2: New Identifier for new specimen - should succeed. (+12 more)

### Community 244 - "UUID"
Cohesion: 0.17
Nodes (12): ParentForUpload, UUID, Duplicate-ID detection converts per-item hard failures into soft FAILED results., Construct a Child1ForUpload bypassing Pydantic validators (for dup-ID tests)., Construct a ParentForUpload bypassing Pydantic validators., Build an UploadParentsCommand bypassing all Pydantic batch validators., Duplicate parent UUID → both occurrences FAILED, distinct parent unaffected., Two children with the same UUID inside one parent → parent FAILED. (+4 more)

### Community 245 - "BasePersonUploadTestCase"
Cohesion: 0.09
Nodes (24): PersonIdentifier, BasePersonUploadTestCase, date, datetime, Person, UUID, Base test case with common fixtures and utilities for person upload tests., Test combinations of different scenarios. (+16 more)

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

### Community 250 - "derived.py"
Cohesion: 0.11
Nodes (26): Cohort, CohortDefinition, ConditionEra, DoseEra, DrugEra, Episode, EpisodeEvent, Any (+18 more)

### Community 251 - "User"
Cohesion: 0.08
Nodes (19): Any, User, UUID, Construct a user from claims and configured automatic-user defaults. Args:…, Determine whether identity claims belong to the configured root user. Args:…, Determine whether a user has the configured root role. Args: user: User whose…, Create or retrieve the configured root organization and user. The operation is…, Create a user from configured defaults when automatic provisioning is enabled.… (+11 more)

### Community 252 - "CaseTypeCrudCommand"
Cohesion: 0.10
Nodes (22): CaseTypeCrudCommand, Represent CRUD operations for structural case-type definitions., case_service_crud_case_type(), _crud_case_type_with_abac(), _crud_case_type_without_abac(), BaseCaseService, CaseType, UUID (+14 more)

### Community 253 - "MemoryTagIndex"
Cohesion: 0.07
Nodes (16): MemoryTagIndex, ABC, Forget `key` and remove it from every tag., Remove `tag` and return the keys that carried it., Forget every association., Return the tags currently known to the index., Encapsulates keeping tag associations in process memory. The index holds both…, Initialize a MemoryTagIndex instance. (+8 more)

### Community 254 - "test_logging_runtime_contract.py"
Cohesion: 0.28
Nodes (15): JSONDict, _emit_log_level_resolution_payloads(), _emit_log_level_resolution_payloads_for_both_modes(), _emit_runtime_payloads_for_all_yaml_paths(), _emit_runtime_payloads_via_dictconfig(), _has_message(), _load_class(), parametrize (+7 more)

### Community 255 - "ReceiverApp"
Cohesion: 0.16
Nodes (11): main(), ReceiverApp CLI Module This module provides a command-line interface for…, Command-line interface for ReceiverApp., Start the ReceiverApp server. Args: port: Port to run the server on (default:…, Main entry point for the CLI., ReceiverAppCLI, FastAPI, FastAPI app that receives and validates access tokens. (+3 more)

### Community 256 - "TokenStore"
Cohesion: 0.05
Nodes (26): Set up test fixtures before each test method., Test TokenStore initialization., Integration tests for OAuth2Validator with real stores., Set up test fixtures., Test complete client credentials flow validation., Test scope validation with various edge cases., Test complete token lifecycle: create, validate, revoke., Test comprehensive redirect URI validation scenarios. (+18 more)

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

### Community 261 - "PersonBatchForUpload"
Cohesion: 0.10
Nodes (16): PersonBatchForUpload, Any, computed_field, Represents a set of persons intended for upload, together with any new…, Indicates whether there are any measurements in the person set., Indicates whether there are any observations in the person set., Indicates whether there are any specimens in the person set., Total number of persons in the batch. (+8 more)

### Community 262 - "._make_user_cmd"
Cohesion: 0.11
Nodes (13): Any, None user should assert., READ_ALL for org admin should include users in admin orgs and admins, including…, READ_SOME for org admin should authorize when all users are within admin orgs., READ_SOME should raise when any user is outside admin orgs., READ_ONE for org admin allows inactive user in admin orgs., READ_ALL for regular user should include self and active admins of own org., READ_SOME for regular user should allow self and active admins only. (+5 more)

### Community 263 - "SAUnitOfWork"
Cohesion: 0.12
Nodes (14): Exception, Self, Session, TracebackType, Enter the managed context., Exit the managed context., Encapsulates a unit of work class wrapping the SQLAlchemy session. The context…, Initialize a SAUnitOfWork instance. (+6 more)

### Community 264 - "_encode_to_int32"
Cohesion: 0.22
Nodes (10): _encode_to_int32(), _hamming_allele_int32_batch(), _hamming_allele_numpy(), _hamming_allele_numpy_batch(), ndarray, Hamming distances from one existing int32 profile to all M new int32 profiles.…, Hamming distance between two (n_loci,) S16 allele arrays. S16 is a no-uint128…, Hamming distances from one existing S16 profile to all M new profiles.… (+2 more)

### Community 265 - "TestCasedbCaseCreateSeq"
Cohesion: 0.10
Nodes (14): fixture, scenario_ids, Comprehensive test suite for the create_seq.py module in…, Create a mock user for testing., Create a mock UnitOfWork for testing., Create a mock repository for testing., Create sample RefCol objects with GENETIC_READS type for testing., Create sample RefCol objects with GENETIC_SEQUENCE type for testing. (+6 more)

### Community 266 - "TestRead"
Cohesion: 0.28
Nodes (4): Env, scenario_ids, skipif, TestRead

### Community 267 - "_make_cmd"
Cohesion: 0.29
Nodes (5): _make_cmd(), scenario_ids, User, Build a UserCrudCommand bypassing field validation., TestModelMetadataPolicy

### Community 268 - "UUID"
Cohesion: 0.11
Nodes (13): datetime, SeqDistance, SeqProfile, UUID, Yield distance records for a protocol, optionally limited to profile IDs., Yield unique profile IDs that have distance records for a protocol., Return the latest modification time among a protocol's distance records., Persist changed distance records and update their modification metadata. (+5 more)

### Community 269 - "_get_cases_for_create_file_for_read_sets_or_seqs"
Cohesion: 0.14
Nodes (13): _get_cases_for_create_file_for_read_sets_or_seqs(), Case, Load cases and validate genetic column compatibility and write access. Args:…, UUID, Test _get_cases_for_create_file_for_read_sets_or_seqs function., Create sample Col objects for testing., Test successful retrieval of cases for ReadSets creation., Test successful retrieval of cases for Seqs creation. (+5 more)

### Community 270 - "Test6Identifiers"
Cohesion: 0.13
Nodes (11): Test scenarios related to Identifiers for parent objects., Test 6.2.1.1: Existing Identifier with NULL parent ID - should set parent ID., Test 6.2.1.2.1: Existing Identifier with same parent ID - should succeed., Test 6.2.1.2.2: Existing Identifier with different parent ID - should fail., Test 6.2.2: New Identifier for new parent - should succeed., Test 6.2.3.1: Multiple Identifiers, some existing for same parent - should…, Test 6.2.3.1: Multiple Identifiers, some existing for different parent - should…, Test 6.2.3.2: Multiple Identifiers, all new but same issuer - should fail. (+3 more)

### Community 271 - "test_retrieve_stats.py"
Cohesion: 0.19
Nodes (19): CaseStats, model_validator, Self, Represents aggregate statistics for cases or a case set. Model validation: Own…, Validate count and case-date invariants., get_all_case_type_ids(), get_test_client(), get_user_for_test() (+11 more)

### Community 272 - "TestCommondbMetadataMasking"
Cohesion: 0.16
Nodes (11): DataCollection, Env, fixture, integration, scenario_ids, User, Only APP_ADMIN or ROOT users can see created_at, modified_at, and modified_by,…, Register root1_1 + org1, then invite an org_user and an org_admin. (+3 more)

### Community 273 - "ModelNoId"
Cohesion: 0.08
Nodes (16): ModelNoId, UUID, Represents creation and modification metadata to a FastApp domain model. This…, Record the current UTC time and user as the latest modification., Record the current UTC time and user as both creation and modification., Model, OmopDB base model with optional UUID identity metadata., Represents the shared model contract with an optional OmopDB object ID. (+8 more)

### Community 274 - "TestHttpTimeoutConfiguration"
Cohesion: 0.15
Nodes (9): DerivedRemoteApp, Minimal subclass of CommondbRemoteApp for testing timeout configuration., Test HTTP timeout configuration per command class., DerivedRemoteApp has DEFAULT_HTTP_TIMEOUTS configured., DerivedRemoteApp can be initialized., _create_remote_app applies DEFAULT_HTTP_TIMEOUTS to remote app., Base CommondbRemoteApp has empty DEFAULT_HTTP_TIMEOUTS., Timeout configuration works independently of auth protocol. (+1 more)

### Community 275 - "test_error_code_unicity"
Cohesion: 0.25
Nodes (13): _extract_hex_strings_from_file(), _get_all_seen_codes(), _get_python_files(), _get_repo_root(), _hanlde_duplicate_hex_codes(), _is_long_hex_string(), Path, scenario_ids (+5 more)

### Community 276 - "omop/service.py"
Cohesion: 0.13
Nodes (14): DomainBaseOmopService, BaseOmopService, Any, Encapsulates an omopdb service, by providing additional implementation details…, Initialize the domain service and expose application role mappings., Expose the concrete service handling OmopDB OMOP commands., omop_service_retrieve_persons_by_query(), Repository-backed workflows for retrieving OMOP persons and identifiers. (+6 more)

### Community 277 - "ReadOrganizationResultsOnlyPolicy"
Cohesion: 0.16
Nodes (13): Any, BaseAbacService, Command, User, UUID, Filter or reject results according to their direct organization IDs. Args:…, Encapsulates AFTER-phase organization-scope filtering to supported read…, Filter or reject results associated with users in visible organizations. Args:… (+5 more)

### Community 278 - "App (command dispatcher / PEP)"
Cohesion: 0.17
Nodes (13): Command-Based Execution Model, Policy Enforcement Timing (BEFORE/DURING/AFTER), App (command dispatcher / PEP), BaseRbacService, CrudEndpointGenerator, PolicyDecisionPoint, Policy (is_allowed/get_content/filter hooks), RbacPolicy (+5 more)

### Community 279 - "Organization (omopdb.organization entity)"
Cohesion: 0.29
Nodes (13): OrganizationAdminPolicy (omopdb.abac entity), omopdb / ABAC — Simplified ERD, omopdb — Full Database ERD (detailed, 69 entities), omopdb — Full Database ERD (simplified, 69 entities), Contact (omopdb.organization entity), Organization (omopdb.organization entity), OrganizationIdentifierIssuerLink (omopdb.organization entity), Site (omopdb.organization entity) (+5 more)

### Community 280 - "Unit"
Cohesion: 0.09
Nodes (19): ConceptSet, ConceptSetType, Classify the language or value scale represented by a concept set., Identify units supported by casedb column and concept metadata., Unit, Any, field_serializer, field_validator (+11 more)

### Community 281 - "RetrieveGeneticSequenceFastaByIdCommand"
Cohesion: 0.20
Nodes (8): Command, Define casedb commands that retrieve sequence data from seqdb., Represent a request for genetic sequences identified by ID., Represent a request for genetic sequences in FASTA format. The response is an…, RetrieveGeneticSequenceByIdCommand, RetrieveGeneticSequenceFastaByIdCommand, Retrieve genetic sequence data in FASTA format by identifier. Args: cmd: FASTA…, Return seqdb's FASTA iterator for the requested sequence IDs. Args: cmd: Casedb…

### Community 282 - "casedb/domain/command/abac.py"
Cohesion: 0.11
Nodes (19): OrganizationAccessCasePolicyCrudCommand, OrganizationShareCasePolicyCrudCommand, CrudCommand, Define casedb commands for case access and sharing policies., Represent CRUD operations for organization-level case access policies. Policies…, Represent CRUD operations for per-user case access policies. Effective rights…, Represent CRUD operations for organization case-sharing policies. Policies…, Represent CRUD operations for per-user case-sharing policies. User permissions… (+11 more)

### Community 283 - ".dispatch"
Cohesion: 0.29
Nodes (5): Exception, Request, Response, Log an authentication exception through the configured application logger., Process a request and translate authentication exception groups to HTTP 401.

### Community 284 - "omopdb/policies/read_organization_results_only_policy.py"
Cohesion: 0.22
Nodes (7): Any, BaseAbacService, CommonReadOrganizationResultsOnlyPolicy, Configure organization-scoped result reads for OmopDB commands., Encapsulates restrictions on shared organization results according to OmopDB…, Initialize organization-scoped command metadata for OmopDB., ReadOrganizationResultsOnlyPolicy

### Community 285 - "BaseAbacService"
Cohesion: 0.09
Nodes (18): BaseAbacService, CommonAbacService, Encapsulates seqdb handlers implemented by concrete ABAC services., Any, BaseAbacService, CommonReadOrganizationResultsOnlyPolicy, Implement seqdb authorization policy behavior for…, Encapsulates restricting result reads to the caller's authorized organization… (+10 more)

### Community 286 - "seq/crud_tree_algorithm.py"
Cohesion: 0.14
Nodes (13): TreeAlgorithm, TreeAlgorithmCrudCommand, UUID, Implement seqdb CRUD service operations for services.seq.crud_tree_algorithm., Handle CRUD operations for tree-algorithm entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added (+5 more)

### Community 287 - "CacheConfigurationError"
Cohesion: 0.13
Nodes (16): CacheConfigurationError, Error for an invalid or contradictory cache configuration., Return the field names referenced by a format string. Args: template: The…, _template_field_names(), _as_scope_parts(), Any, Build a region, register it and return it. Args: config: The declarative policy…, Create every region described by a settings mapping. Args: settings: Region… (+8 more)

### Community 288 - "FullSample"
Cohesion: 0.21
Nodes (12): AstMeasurement, FullSample, IdentifierIssuer, AstMeasurement (seqdb.seq.md), ReadSetIdentifier (seqdb.seq.md), SampleIdentifier (seqdb.seq.md), SeqIdentifier (seqdb.seq.md), SeqProfileIdentifier (seqdb.seq.md) (+4 more)

### Community 289 - "JsonFormatter"
Cohesion: 0.41
Nodes (12): casedb Debug Logging Config, casedb Logging Config, commondb Debug Logging Config, JsonFormatter, commondb Logging Config, Log Level Tuning Rationale (sqlalchemy/httpx/asyncio), UvicornAccessLogFilter, omopdb Debug Logging Config (+4 more)

### Community 290 - ".__init__"
Cohesion: 0.11
Nodes (11): Logger, SSLContext, UUID, Update the OIDC configuration from the discovery URL or, if provided, the…, Call server to get token through OAuth Client Credentials flow., Request token with retries., Log failed token retrieval attempts., Helper method to build token data / request body for client credentials flow. (+3 more)

### Community 291 - "CalculatePhylogeneticTreeCommand"
Cohesion: 0.11
Nodes (13): CalculatePhylogeneticTreeCommand, model_validator, Self, Represents calculating a phylogenetic tree from query profiles and a configured…, Require custom leaf names to align with the queried profile identifiers., PhylogeneticTree, Calculate a phylogenetic tree. Args: cmd: Tree-calculation command to execute.…, PhylogeneticTree (+5 more)

### Community 292 - "data_access/conftest.py"
Cohesion: 0.12
Nodes (16): Env, fixture, Create case types, col infrastructure, data collections, cases, and access…, setup_case_data_operational(), Env, fixture, Create reference data (diseases, etiological agents, CaseTypes, CaseTypeSets,…, setup_case_data_reference() (+8 more)

### Community 293 - "AuthTestClient"
Cohesion: 0.18
Nodes (6): AuthTestClient, get_test_client(), fixture, parametrize, Get an OidcClient instance from the test environment., TestAuth

### Community 294 - "make_cdb_user"
Cohesion: 0.23
Nodes (5): make_cdb_user(), Verify the root-token time-to-live enforcement. A *very* short TTL (1 second)…, Build an AuthEnv with a pre-stored root user., Return a fresh commondb User with the given attributes., TestRootTokenTTL

### Community 295 - "OmopdbRemoteApp"
Cohesion: 0.14
Nodes (12): OmopdbRemoteApp, Any, Retrieve specimen IDs for the given cohort IDs., Encapsulates routing of supported OmopDB commands to their remote HTTP…, Register remote OmopDB routes and command handlers., Upload a batch of persons., Retrieve persons matching the given query., Retrieve full person records by their IDs. (+4 more)

### Community 296 - "case_service_crud_col_set"
Cohesion: 0.18
Nodes (15): ColSetCrudCommand, Represent CRUD operations for reusable column sets., ColSet, Handle a CRUD command for column sets. Args: cmd: Column-set CRUD command to…, case_service_crud_col_set(), _crud_col_set_with_abac(), _crud_col_set_without_abac(), BaseCaseService (+7 more)

### Community 297 - "handle_command"
Cohesion: 0.21
Nodes (17): generate_handle_exception_function(), _handle_auth_exception(), handle_command(), handle_exception(), _handle_service_exception(), Any, App, Command (+9 more)

### Community 298 - "IdpClient hierarchy"
Cohesion: 0.20
Nodes (11): AuthService (concrete), IdpClient hierarchy, MockIDPClient (no-auth dev/CI), OauthIdpClient (real OIDC), BaseUserManager, Authentication (Identity Resolution Layer), User Resolution (claims -> local User), Add New IDP Configuration (+3 more)

### Community 299 - "Protocol"
Cohesion: 0.20
Nodes (11): AstMeasurement, LocusSet, AstMeasurement (seqdb.md), LocusSet (seqdb.md), PcrMeasurement (seqdb.md), Protocol (seqdb.md), ProtocolSetMember (seqdb.md), PcrMeasurement (+3 more)

### Community 301 - "RetrieveContainingRegionCommand"
Cohesion: 0.25
Nodes (6): Command, Represent a request for regions containing specified regions., RetrieveContainingRegionCommand, Region, Retrieve the containing region for each location in a command. Args: cmd:…, Region

### Community 302 - ".retrieve_organization_ids"
Cohesion: 0.20
Nodes (7): Command, UUID, Extract affected organization IDs from site CRUD command objects., Retrieve organizations affected by site-linked contact command objects., Determine whether a user may manage every organization affected by a command.…, Register a resolver for organizations affected by a command type. Args:…, Resolve organizations affected by a command, caching inherited resolvers. Args:…

### Community 303 - "sa_model/ontology.py"
Cohesion: 0.21
Nodes (15): Concept, ConceptRelation, ConceptSet, Disease, EtiologicalAgent, Etiology, Base, RowMetadataMixin (+7 more)

### Community 304 - ".handle"
Cohesion: 0.50
Nodes (3): Any, Command, Handle the requested value.

### Community 305 - "PayerPlanPeriod"
Cohesion: 0.21
Nodes (11): Cost, PayerPlanPeriod, Any, DataLineageMixin, field_validator, Model, UUID, Normalize payer-plan-period concept identifiers to UUID form. (+3 more)

### Community 306 - "Transformer Framework"
Cohesion: 0.25
Nodes (11): FallbackTransformer, FieldTransformer, ObjectAdapter, RetryTransformer, Streaming Pipeline Performance Rationale, StreamingPipeline, Transformer, Transformer Framework (+3 more)

### Community 307 - "test_casedb_custom.py"
Cohesion: 0.12
Nodes (19): Set the configured level on commondb and HTTP client loggers. Args: prefix:…, set_log_level(), get_test_client(), Env, fixture, skip, User, UUID (+11 more)

### Community 308 - "rewrite_parametrized_dependency_markers"
Cohesion: 0.33
Nodes (6): pytest_collection_modifyitems(), pytest_collection_modifyitems(), pytest_collection_modifyitems(), pytest_collection_modifyitems(), Rewrite class-level dependency 'depends' markers to include parametrize IDs.…, rewrite_parametrized_dependency_markers()

### Community 309 - "TestRetrieveCompleteCaseType"
Cohesion: 0.31
Nodes (3): Any, User, TestRetrieveCompleteCaseType

### Community 310 - "Any"
Cohesion: 0.13
Nodes (8): Any, Return application configuration required by configured services. Returns: The…, Return application-specific implementation details. Returns: The configured…, Execute cache invalidators registered for the exact command type., Execute a resolved command handler and its remaining lifecycle phases. Runs…, Recursively walk *data* and replace any list or mapping longer than their…, Parse a boolean command-log configuration value. Args: value: Boolean or case-…, Parse an integer command-log configuration value. Args: value: Value accepted…

### Community 311 - "TestOidcClientCredentials"
Cohesion: 0.17
Nodes (10): patch, scenario_ids, Test the OidcClient retrieve_jwt_with_client_credentials_flow method., Test successful JWT token retrieval with client credentials flow., Test that HTTP errors trigger retries and eventually raise…, Test that missing token endpoint raises ServiceUnavailableError., Test handling of invalid response format (missing access_token)., Test handling of network failures during token retrieval. (+2 more)

### Community 312 - "env"
Cohesion: 0.31
Nodes (5): env(), fixture, FixtureRequest, Return a test client configured for either DICT or SA_SQLITE demo repos. The…, TestRetrieveSamples

### Community 313 - "BaseRbacServiceTestCase"
Cohesion: 0.14
Nodes (10): BaseRbacServiceTestCase, Base test case with common fixtures and utilities., Set up test fixtures., Create a test command., Test user authorization behavior methods., Test that retrieve_user_is_root returns False by default., Test that retrieve_user_is_root can be overridden in concrete implementation., Test that retrieve_user_is_non_rbac_authorized returns False by default in… (+2 more)

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

### Community 319 - "ConcreteRbacService"
Cohesion: 0.17
Nodes (11): ConcreteRbacService, Any, App, BaseRbacService, Hashable, UUID, Concrete implementation of BaseRbacService for testing., Retrieve roles for a user. (+3 more)

### Community 320 - "CommondbSAMapper"
Cohesion: 0.25
Nodes (8): CommondbSAMapper, Any, Hashable, Model, Create a mapper that enforces commondb audit metadata behavior. Args:…, Encapsulates a SAMapper subclass for all databases that use RowMetadataMixin.…, Update a SQLAlchemy row from a domain model using commondb metadata rules.…, Dump a domain model while hiding protected audit metadata. For users without…

### Community 321 - "TestUserPermissions"
Cohesion: 0.12
Nodes (9): Test user permission retrieval and authorization checks., Test that user permissions are union of all their role permissions., Test that user with no roles has no permissions., Test that user has all RBAC permissions when they actually do., Test that user doesn't have all RBAC permissions when missing some., Test checking if user has more permissions than another user., Test checking if user has more permissions than a set of roles., Test that user doesn't have more permissions when they're a subset. (+1 more)

### Community 322 - "TestOIDCProviderIntegration"
Cohesion: 0.12
Nodes (9): Integration tests for OIDCProvider with real JWKSManager., Set up test fixtures., Test complete ID token creation and validation workflow., Test discovery document and JWKS endpoint integration., Test userinfo endpoint with scope-based claim filtering., Test nonce validation integrated with ID token workflow., Test claims extraction integrated with userinfo response., Test logout workflow integration. (+1 more)

### Community 323 - "metadata.py"
Cohesion: 0.20
Nodes (11): CdmSource, Metadata, Any, field_validator, Model, UUID, Metadata domain - OMOP CDM v6.0 metadata tables. This module contains classes…, Normalize metadata concept identifiers to UUID form. (+3 more)

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

### Community 329 - "generate_seqdb_models.py"
Cohesion: 0.33
Nodes (9): build_random_nextclade_fields(), generate_demo_seqdb_models(), _generate_snp_objects(), Any, Random, Sample, UUID, Generate demo seqdb models. When snp_seq_length > 0, SNP-specific reference… (+1 more)

### Community 330 - "TestOIDCProvider"
Cohesion: 0.03
Nodes (37): Test discovery document includes correct supported claims., Test discovery document includes correct authentication methods., Test discovery document includes correct signing algorithms., Test discovery document includes additional OIDC features., Test creating a basic ID token., Test creating ID token with nonce., Test creating ID token with explicit auth_time., Test creating ID token with additional claims. (+29 more)

### Community 331 - "Ref Col"
Cohesion: 0.11
Nodes (20): Concept, Concept Relation, Concept Set, Genetic Distance Protocol, Concept (doc), Concept Relation (doc), Ref Col (doc), Ref Dim (doc) (+12 more)

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
Cohesion: 0.15
Nodes (14): ClusterNode, _correct_nj_tree_negative_branch_lengths_recursion(), _get_newick_repr_recursion(), Any, PhylogeneticTree, Implement seqdb sequence service behavior for…, # TODO: this should be parameterised, so that such higher, # TODO: convert condensed distance matrix directly to lower triangle (+6 more)

### Community 336 - "crud_ast_measurement.py"
Cohesion: 0.22
Nodes (9): AstMeasurement, UUID, Implement seqdb CRUD service operations for services.seq.crud_ast_measurement., Handle CRUD operations for AST measurement entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 337 - "IdsError"
Cohesion: 0.17
Nodes (13): __extract_invalid_ids(), _handle_invalid_ids_exception(), log_and_raise_invalid_ids_exception(), Hashable, Translate an ID exception into a validation or conflict HTTP response. Args:…, Log invalid IDs and raise an HTTP response with their public details. Args:…, Return request IDs that are also reported by an ID exception. Args: exception:…, AlreadyExistingIdsError (+5 more)

### Community 338 - "crud_seq_profile.py"
Cohesion: 0.22
Nodes (10): _get_not_implemented_message(), CrudCommand, Format an unsupported CRUD-operation message including the caller's roles., SeqProfile, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_profile., Handle CRUD operations for sequence-profile entities. Args: self: Sequence…, # TODO: 3034 Check if seq_profile.seq_profile_type and… (+2 more)

### Community 339 - "crud_locus.py"
Cohesion: 0.14
Nodes (13): LocusCrudCommand, Represents CRUD command metadata for locus records., Locus, Handle a CRUD command for locus entities. Args: cmd: Typed locus CRUD command…, Locus, UUID, Implement seqdb CRUD service operations for services.seq.crud_locus., Handle CRUD operations for locus entities. Args: self: Sequence service… (+5 more)

### Community 340 - "crud_locus_set.py"
Cohesion: 0.22
Nodes (9): LocusSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_locus_set., Handle CRUD operations for locus-set entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 341 - "crud_pcr_measurement.py"
Cohesion: 0.22
Nodes (9): PcrMeasurement, UUID, Implement seqdb CRUD service operations for services.seq.crud_pcr_measurement., Handle CRUD operations for PCR measurement entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 342 - "crud_protocol_set.py"
Cohesion: 0.22
Nodes (9): ProtocolSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_protocol_set., Handle CRUD operations for protocol-set entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 343 - "crud_protocol_set_member.py"
Cohesion: 0.22
Nodes (9): ProtocolSetMember, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for protocol-set membership entities. Args: self:…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 344 - "crud_ref_seq.py"
Cohesion: 0.22
Nodes (9): RefSeq, UUID, Implement seqdb CRUD service operations for services.seq.crud_ref_seq., Handle CRUD operations for reference-sequence entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 345 - "patch"
Cohesion: 0.19
Nodes (9): CalculatePhylogeneticTreeRequestBody, Docstring assigned automatically., Any, patch, Test that authentication headers are properly included in requests., Test that RetrievePhylogeneticTreeRequestBody is constructed correctly., Test the retrieve_seq_distance_last_modified handler., Test successful HTTP request with complete response data. (+1 more)

### Community 346 - "crud_read_set_identifier.py"
Cohesion: 0.14
Nodes (13): Represents CRUD command metadata for read-set identifier records., ReadSetIdentifierCrudCommand, ReadSetIdentifier, Handle a CRUD command for read-set identifier entities. Args: cmd: Typed read-…, ReadSetIdentifier, UUID, Implement seqdb CRUD service operations for…, Handle CRUD operations for read-set identifier entities. Args: self: Sequence… (+5 more)

### Community 347 - "crud_seq.py"
Cohesion: 0.22
Nodes (9): Seq, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq., Handle CRUD operations for sequence entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 348 - "crud_seq_category.py"
Cohesion: 0.22
Nodes (9): SeqCategory, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_category., Handle CRUD operations for sequence-category entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 349 - "crud_seq_category_set.py"
Cohesion: 0.12
Nodes (15): Represents CRUD command metadata for sequence category-set records., SeqCategorySetCrudCommand, SeqCategorySet, Handle a CRUD command for sequence-category-set entities. Args: cmd: Typed…, SeqCategorySet, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_category_set., Handle CRUD operations for sequence-category-set entities. Args: self: Sequence… (+7 more)

### Community 350 - "crud_seq_distance.py"
Cohesion: 0.22
Nodes (9): SeqDistance, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_distance., Handle CRUD operations for sequence-distance entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 351 - "crud_seq_taxonomy.py"
Cohesion: 0.14
Nodes (13): Represents CRUD command metadata for sequence taxonomy records., SeqTaxonomyCrudCommand, SeqTaxonomy, Handle a CRUD command for sequence-taxonomy entities. Args: cmd: Typed…, SeqTaxonomy, UUID, Implement seqdb CRUD service operations for services.seq.crud_seq_taxonomy., Handle CRUD operations for sequence-taxonomy entities. Args: self: Sequence… (+5 more)

### Community 352 - "crud_taxon.py"
Cohesion: 0.14
Nodes (13): Represents CRUD command metadata for taxon records., TaxonCrudCommand, Taxon, Handle a CRUD command for taxon entities. Args: cmd: Typed taxon CRUD command…, Taxon, UUID, Implement seqdb CRUD service operations for services.seq.crud_taxon., Handle CRUD operations for taxon entities. Args: self: Sequence service… (+5 more)

### Community 353 - "crud_taxon_set.py"
Cohesion: 0.22
Nodes (9): TaxonSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_taxon_set., Handle CRUD operations for taxon-set entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 354 - "crud_taxon_set_member.py"
Cohesion: 0.22
Nodes (9): TaxonSetMember, UUID, Implement seqdb CRUD service operations for services.seq.crud_taxon_set_member., Handle CRUD operations for taxon-set membership entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

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

### Community 360 - "test_omopdb_build.py"
Cohesion: 0.08
Nodes (21): # TODO: test_create_site, # TODO: test_create_site_raise, # TODO: test_create_contact, # TODO: test_create_contact_raise, # TODO: OrganizationAdminPolicy.user does not exist, Env, scenario_ids, skipif (+13 more)

### Community 361 - "dependency"
Cohesion: 0.22
Nodes (9): dependency, ModuleTestCreate, ModuleTestDelete, ModuleTestRead, ModuleTestUpdate, TestCreate, TestDelete, TestRead (+1 more)

### Community 362 - "OmopdbTestClient"
Cohesion: 0.12
Nodes (16): get_test_client(), Env, fixture, # TODO: annotate test with correct test scenario…, # TODO: add setup to create Organizations, Users, Concepts, Domains, ..., TestPersonUpload, env(), fixture (+8 more)

### Community 363 - "test_seqdb_build.py"
Cohesion: 0.08
Nodes (18): Provide seqdb functionality for domain.exc., # TODO: OrganizationAdminPolicy.user does not exist, Env, scenario_ids, skipif, RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…, TestDelete, Env (+10 more)

### Community 364 - "dependency"
Cohesion: 0.22
Nodes (9): dependency, ModuleTestCreate, ModuleTestDelete, ModuleTestRead, ModuleTestUpdate, TestCreate, TestDelete, TestRead (+1 more)

### Community 365 - "Any"
Cohesion: 0.13
Nodes (8): Any, Return the lower-case aligned nucleotide sequence for an SNP profile. Args:…, Return ordered allele IDs as raw 16-byte chunks. Args: **kwargs: Reserved…, Return ordered allele identifiers from this profile. Args: **kwargs: Reserved…, Return the number of non-null loci in this allele profile. Args: **kwargs:…, Return MLVA repeat numbers from this profile. Args: **kwargs: Reserved…, Return the k-mer frequency map from this profile. Args: **kwargs: Reserved…, Return ordered, lower-case SNP substitutions from NextClade content. Args:…

### Community 366 - "TestOauthIdpClientIntrospection"
Cohesion: 0.25
Nodes (3): Any, scenario_ids, TestOauthIdpClientIntrospection

### Community 367 - ".extract_security_callable"
Cohesion: 0.15
Nodes (10): Any, Test create_user_dependencies with no IDP clients configured., Dummy deps return user or new user, and fallback to no-auth user., Dummy new-user dep raises when claims missing., Test create_user_dependencies with IDP clients configured., Resolve current user via first and second IDPs, and IDP user from claims., No claims provided -> UnauthorizedAuthError., Extract the callable function from Annotated[*, Security(...)] (+2 more)

### Community 368 - ".make_idp_client"
Cohesion: 0.15
Nodes (10): UUID, Test scenarios for get_existing_user_from_token., First IDP unauthorized, second IDP succeeds., No IDP yields a valid user -> UnauthorizedAuthError., Test scenarios for get_identity_providers., Filter public providers and ignore retry errors., Retry initializes a pending client and adds it to service., Create an IdpClient mock with minimal interface. (+2 more)

### Community 369 - "AuthorizationCodeStore"
Cohesion: 0.18
Nodes (6): AuthorizationCode, AuthorizationCodeStore, datetime, Authorization Code Store In-memory storage for OAuth 2.0 Authorization Codes…, Representation of an OAuth 2.0 authorization code., In-memory store managing authorization codes.

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

### Community 376 - "Any"
Cohesion: 0.14
Nodes (8): Any, Create an OpenID Connect ID Token., Validate only the signature of a JWT token without checking claims., Decode JWT header without verification., Decode JWT payload without verification (use carefully!)., Create a JWT token with the given payload., Verify and decode a JWT token., Get the public keys in JWKS format.

### Community 377 - ".__init__"
Cohesion: 0.25
Nodes (7): OrganizationDictRepository, Any, CommonOrganizationDictRepository, Hashable, Model, Encapsulates casedb persistence behavior for organization dictionaries., Initialize the repository with casedb user and invitation model types. Args:…

### Community 378 - "UpdateUserPolicy"
Cohesion: 0.19
Nodes (10): Any, BaseAbacService, Command, User, Determine whether a user strictly exceeds a target user's permissions. Args:…, Encapsulates BEFORE-phase role and organization checks to user mutations., Initialize mapped user type and configured role mappings. Args: abac_service:…, Determine whether a user may invite or update the target user. Root users may… (+2 more)

### Community 379 - ".create_sa_repository"
Cohesion: 0.09
Nodes (19): EngineFactory, Engine, Thread-safe SQLAlchemy engine factory., Encapsulates creation and management of SQLAlchemy engines., Initialize a EngineFactory instance., Create a new SQLAlchemy engine or return an existing one for the given…, Create an SARepository, setting up engine, schemas, and DDL. When…, Helper method to process common repository parameters and handle connection… (+11 more)

### Community 380 - ".__init__"
Cohesion: 0.25
Nodes (7): OrganizationDictRepository, Any, CommonOrganizationDictRepository, Hashable, Model, Encapsulates shared organization persistence with OmopDB user model types., Initialize shared organization storage with OmopDB model classes.

### Community 381 - ".__init__"
Cohesion: 0.25
Nodes (7): OrganizationDictRepository, Any, CommonOrganizationDictRepository, Hashable, Model, Encapsulates seqdb persistence behavior for organization dictionaries., Initialize the repository with seqdb user and invitation model types. Args:…

### Community 382 - "TestRead"
Cohesion: 0.39
Nodes (4): Env, scenario_ids, skipif, TestRead

### Community 383 - "KeyedMutex"
Cohesion: 0.16
Nodes (9): KeyedMutex, Acquire the mutex belonging to `key`. Args: key: The cache key being…, Release the mutex belonging to `key`. Args: key: The key whose mutex is held.…, Return whether a regeneration is in progress for `key`., Decrement the user count of `key` and forget an unused mutex., Encapsulates handing out one mutex per key and discarding it when unused.…, Initialize a KeyedMutex instance., A per-key lock registry must not grow with the key space. (+1 more)

### Community 384 - "User"
Cohesion: 0.16
Nodes (9): Command, User, Check if user is authorized via non-RBAC mechanism., Create another test command., Test command for testing. Name starts with _ to avoid warning due to pytest…, Another test command for testing. Name starts with _ to avoid warning due to…, Check if user is root., _TestCommand (+1 more)

### Community 385 - "BaseAuthServiceTestCase"
Cohesion: 0.15
Nodes (10): BaseAuthServiceTestCase, scenario_ids, Test idp_clients property., idp_clients property returns a copy, not the original list., Base test case with common fixtures and utilities., Set up test fixtures., Test get_idp_user_from_claims., Should parse issuer and sub from claims. (+2 more)

### Community 386 - "scenario_ids"
Cohesion: 0.17
Nodes (9): scenario_ids, Set up test fixtures., Test scenarios related to Identifiers for persons., Test 6.3: New Identifier created on upload., Test upload with varying batch sizes., Test 8: Upload batch of n new persons., Test 8: Upload person with varying number of measurements., Test6Identifiers (+1 more)

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

### Community 393 - "fixture"
Cohesion: 0.17
Nodes (7): fixture, User, Test successful HTTP request with response data missing leaf_ids., Create a mock user for testing., Create a SeqdbRemoteApp instance for testing., Create a sample command for testing., Create sample response data for testing.

### Community 394 - "JIRA Issues"
Cohesion: 0.17
Nodes (12): Assigning Issues, Comments and Worklogs, Common Fields, Extended Capabilities, JIRA Issues, Prerequisite: Resolve `cloudId`, Repository Context, Safety Rules (+4 more)

### Community 395 - "casedb/repositories/sa_model/abac.py"
Cohesion: 0.26
Nodes (11): OrganizationAccessCasePolicy, OrganizationShareCasePolicy, Base, RowMetadataMixin, Define SQLAlchemy persistence mappings for casedb ABAC policy models., Persist the casedb OrganizationShareCasePolicy domain model., Persist the casedb UserShareCasePolicy domain model., Persist the casedb OrganizationAccessCasePolicy domain model. (+3 more)

### Community 396 - "._validate_content"
Cohesion: 0.29
Nodes (5): model_validator, Self, UUID, Validate the profile-distance-map content and reset its unused hash., Decode the stored JSON profile-distance map. Returns: Distances keyed by…

### Community 397 - "AuthException"
Cohesion: 0.17
Nodes (12): AuthException, CredentialsAuthError, Base error for authentication and authorization failures., HTTP 401 error for credentials that cannot be validated., HTTP 403 error for credentials without the required authorization., HTTP 404 error for an identity with no application user., HTTP 409 error for an identity that already has an application user., HTTP 429 error for an authentication request that exceeds its limit. (+4 more)

### Community 398 - "DataException"
Cohesion: 0.17
Nodes (9): DataException, NotNullConstraintViolationError, Initialize a UniqueConstraintViolationError instance., Error for data that omits a required field., Initialize a NotNullConstraintViolationError instance., Domain error associated with one or more data identifiers., Initialize a DataException instance., Error for data that violates a unique constraint. (+1 more)

### Community 399 - "Self"
Cohesion: 0.20
Nodes (7): model_validator, Self, Require non-empty content for a locus profile upload. Returns: The validated…, Require content or an aligned sequence for an SNP profile upload. Returns: The…, Apply validation for the selected sequence-profile type., Reserve post-validation for future classification-content verification., Require a code or non-null ID for every configured reference-data pair.

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

### Community 408 - "CreateFileForSeqCommand"
Cohesion: 0.15
Nodes (8): CreateFileForSeqCommand, Represent upload of an assembled file for a case sequence column. The command…, Create a file for a case-linked sequence. Implementations persist file metadata…, Create or reuse a seqdb file for a case-linked sequence. casedb access…, UUID, Create a file associated with a read set column., Create a file associated with a sequence column., Check whether the user owns each of the given cases.

### Community 409 - "._validate_model"
Cohesion: 0.40
Nodes (4): model_validator, Self, Derive or validate the deterministic identifier UUID., Require an issuer UUID or code.

### Community 410 - "BaseSAMapper"
Cohesion: 0.05
Nodes (24): BaseSAMapper, MappedColumn, Get row field names by field type., Get row field names by field type set., Get the row ID column., Encapsulates an abstract mapper between SQLAlchemy rows and Pydantic models. It…, Create a SAMapper instance for model and row classes., Get a field name map between model and row fields. If one of the fields does… (+16 more)

### Community 411 - ".__init__"
Cohesion: 0.29
Nodes (5): Command, Hashable, User, Initialize a RbacPolicy instance., Return whether allowed.

### Community 412 - "IsOrganizationAdminPolicy"
Cohesion: 0.29
Nodes (6): IsOrganizationAdminPolicy, Any, BaseAbacService, CommonIsOrganizationAdminPolicy, Encapsulates organization-administrator checks using the OmopDB role map., Initialize the policy with OmopDB users and role mappings.

### Community 413 - "BaseAbacService"
Cohesion: 0.10
Nodes (17): BaseAbacService, CommonAbacService, Encapsulates mapping of shared ABAC command groups to their OmopDB command…, Any, BaseAbacService, CommonReadUserPolicy, Configure shared user-read policy behavior for OmopDB roles and commands., Encapsulates shared user-read checks with OmopDB role and command mappings. (+9 more)

### Community 414 - "IsOrganizationAdminPolicy"
Cohesion: 0.29
Nodes (6): IsOrganizationAdminPolicy, Any, BaseAbacService, CommonIsOrganizationAdminPolicy, Encapsulates organization-admin checks using seqdb roles and user models., Configure the shared policy with seqdb role and user mappings.

### Community 415 - "ReadUserPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadUserPolicy, Encapsulates authorizing user reads with seqdb roles and organization-admin…, Configure the shared policy with seqdb authorization dependencies., ReadUserPolicy

### Community 416 - "BaseFileRepository"
Cohesion: 0.23
Nodes (9): BaseFileRepository, Define seqdb domain interfaces and policies for domain.repository.file., Encapsulates the shared repository base for seqdb file persistence., FileDictRepository, Provide seqdb persistence behavior for repositories.file_dict., Encapsulates dictionary-backed persistence for seqdb uploaded files., FileSARepository, Provide seqdb persistence behavior for repositories.file_sa. (+1 more)

### Community 417 - "OrganizationSARepository"
Cohesion: 0.29
Nodes (6): OrganizationSARepository, Any, CommonOrganizationSARepository, Engine, Encapsulates seqdb persistence behavior for SQL-based organization repositories., Initialize the repository with seqdb SQLAlchemy model types. Args: engine:…

### Community 418 - "_parse_nextclade_profile_content"
Cohesion: 0.21
Nodes (12): _parse_nextclade_non_acgtns(), _parse_nextclade_position_token(), _parse_nextclade_profile_content(), _parse_nextclade_ranges(), _parse_nextclade_substitutions(), Split a comma-separated Nextclade field into trimmed nonempty tokens., Parse one Nextclade position or inclusive position range. Args: token: Position…, Parse Nextclade substitution tokens into normalized bases by position. Args:… (+4 more)

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

### Community 426 - "EtlLogItem"
Cohesion: 0.10
Nodes (11): Get all data issues that are errors., EtlLogItem, BaseModel, Append a WARN-severity log item., Append an INFO-severity log item., Return a list of log items with ERROR severity., Return a list of log items with WARN severity., Return a list of log items with INFO severity. (+3 more)

### Community 427 - "BrokenBackend"
Cohesion: 0.17
Nodes (6): BrokenBackend, Backend that fails every operation, to exercise the failure policy., Fail instead of reading. Args: key: The requested key. Returns: Never returns.…, Fail instead of writing. Args: key: The key to write. value: The envelope to…, Fail instead of deleting. Args: key: The key to remove. Raises:…, Fail instead of clearing. Raises: CacheBackendError: Always.

### Community 428 - "TestJWKSManagerIntegration"
Cohesion: 0.17
Nodes (7): Integration tests for JWKSManager functionality., Test complete JWT creation and verification workflow., Test that JWKS output is compatible with standard libraries., Test that multiple JWKSManager instances are independent., Test complete key rotation workflow., Test complete OpenID Connect ID token workflow., TestJWKSManagerIntegration

### Community 429 - "pr.sh"
Cohesion: 0.25
Nodes (5): generated_body(), print_ready_command(), require_command(), pr.sh script, usage()

### Community 430 - "OrganizationService"
Cohesion: 0.33
Nodes (5): OrganizationService, Any, CommonOrganizationService, Encapsulates organization operations using casedb user model types., Initialize organization handling with casedb model specializations. Args:…

### Community 431 - "Issue Templates"
Cohesion: 0.20
Nodes (6): Bug Report Template, Comment Template, Feature Request / Story Template, Issue Templates, Minimal Template, Task Template

### Community 432 - ".default_isolation_level"
Cohesion: 0.50
Nodes (3): setter, Return the default isolation level for new sessions., Set the default isolation level for new sessions.

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

### Community 437 - "get_test_client"
Cohesion: 0.40
Nodes (4): get_test_client(), Env, fixture, TestCaseUploadContentDeletion

### Community 438 - "command/geo.py"
Cohesion: 0.24
Nodes (10): CrudCommand, Define casedb commands for geographic regions and region sets., Represent CRUD operations for geographic region sets., Represent CRUD operations for geographic regions., Represent CRUD operations for relationships between regions., Represent CRUD operations for shapes associated with region sets., RegionCrudCommand, RegionRelationCrudCommand (+2 more)

### Community 439 - "field_validator"
Cohesion: 0.18
Nodes (6): field_validator, Normalize a supplied user key to lower case., Normalize role input to a set., Convert an empty invitation user key to an omitted key., Normalize invitation role input to a set., Strip leading and trailing whitespace from an external identifier.

### Community 440 - "test_debug_console_uses_json_formatter"
Cohesion: 0.40
Nodes (4): parametrize, Path, scenario_ids, test_debug_console_uses_json_formatter()

### Community 441 - "PersonBatchUploader"
Cohesion: 0.20
Nodes (7): PersonBatchUploader, UUID, Verify the person content and add any derived values., Get person validator for the given complete person type, Encapsulates validation and persistence of person batches and associated data., Initialize the uploader for an OMOP service. Args: service: Service that owns…, Verify rights for a person-upload command. Args: cmd: Batch command whose user…

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

### Community 449 - "TestUploadResult"
Cohesion: 0.18
Nodes (3): _make_pending_upload_result(), Construct an UploadResult in PENDING state (no logs required)., TestUploadResult

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

### Community 458 - "MermaidErmGenerator"
Cohesion: 0.36
Nodes (7): MermaidErmGenerator, Domain, Path, Write a Markdown file wrapping a Mermaid diagram., Generates Mermaid ``erDiagram`` markdown files from domain model definitions.…, Generate Mermaid ERD markdown files into *dir*., _write_md()

### Community 459 - ".__init__"
Cohesion: 0.22
Nodes (5): datetime, Domain, Domain the requested value., Initialize command-object log summarization from runtime configuration. Uses…, Initialize an application command mediator and its runtime dependencies.…

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

### Community 469 - ".__init__"
Cohesion: 0.27
Nodes (7): Any, App, Logger, SSLContext, Validate that configured provider names and labels are unique. Args: app:…, Initialize authentication, identity-provider clients, and API dependencies.…, Initialize configured identity-provider clients and queue retryable failures.…

### Community 470 - ".validate_model"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate references and replace all derived ordering fields in place.

### Community 471 - "crud_read_set.py"
Cohesion: 0.22
Nodes (9): ReadSet, UUID, Implement seqdb CRUD service operations for services.seq.crud_read_set., Handle CRUD operations for read-set entities. Args: self: Sequence service…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

### Community 472 - "CaseTypeSetCaseTypeUpdateAssociationCommand"
Cohesion: 0.18
Nodes (9): CaseTypeSetCaseTypeUpdateAssociationCommand, ColSetColUpdateAssociationCommand, UpdateAssociationCommand, Represent replacement of the case types in a case-type set. The provided…, Represent replacement of the columns in a column set. The provided members keep…, CaseTypeSetMember, ColSetMember, Update case type associations for a case type set. (+1 more)

### Community 473 - "crud_ref_allele.py"
Cohesion: 0.22
Nodes (9): RefAllele, UUID, Implement seqdb CRUD service operations for services.seq.crud_ref_allele., Handle CRUD operations for reference-allele entities. Args: self: Sequence…, # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+1 more)

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

### Community 518 - "TestPermissionRegistration"
Cohesion: 0.20
Nodes (6): Test permission registration functionality., Test registering a permission without RBAC., Test registering permission without RBAC fails when roles exist., Test unregistering a permission without RBAC., Test unregistering non-registered permission fails., TestPermissionRegistration

### Community 520 - "TestHierarchicalRolePermissions"
Cohesion: 0.20
Nodes (6): Test hierarchical role permission expansion., Test that hierarchical role permissions are expanded correctly., Test that redundant permissions in hierarchy are detected., Test that redundant permissions are allowed when verification is disabled., Test that PermissionTypeSet is properly expanded to individual PermissionTypes., TestHierarchicalRolePermissions

### Community 528 - "TestEdgeCasesAndErrorConditions"
Cohesion: 0.20
Nodes (6): Test edge cases and error conditions., Test that invalid on_missing_root_permissions value raises error., Test that root role is created when missing from role_permissions., Test that empty role hierarchy is handled gracefully., Test that role with no sub-roles returns empty set., TestEdgeCasesAndErrorConditions

### Community 529 - "OmopdbEndpointTestClient"
Cohesion: 0.36
Nodes (5): OmopdbEndpointTestClient, Any, App, FastAPI, Response

### Community 531 - "Test5FieldMutability"
Cohesion: 0.20
Nodes (6): Test scenarios related to field mutability for existing Person objects., Test 5.1.1: Always mutable single value field (person_source_value) - should be…, Test 5.2.1: Mutable if empty field - stored value is empty, should succeed., Test 5.2.2: Mutable if empty field - stored not empty, new empty, should…, Test 5.2.3: Mutable if empty field - stored not empty, new not empty, should…, Test5FieldMutability

### Community 532 - "Fields, Issue Types, and Transitions"
Cohesion: 0.22
Nodes (9): Clearing and replacing, Discovering fields, Discovering projects and issue types, Field shapes, Fields, Issue Types, and Transitions, Releases instead of milestones, Setting fields, Transition rules (+1 more)

### Community 533 - "test/fastapp/model.py"
Cohesion: 0.39
Nodes (8): Base1, Base2, declarative_mixin, RowMetadataMixin, SAModel1_1, SAModel1_2, SAModel2_1, SAModel2_2

### Community 534 - ".crud"
Cohesion: 0.22
Nodes (6): Any, App, CrudCommand, Forward a CRUD command to seqdb under the configured functional user. The…, Initialize command handlers and the configured seqdb collaborator. Args: app:…, Return the local seqdb application or remote command client.

### Community 535 - ".idp_user_dependency"
Cohesion: 0.25
Nodes (6): Any, computed_field, User, Return the new-user dependency. Returns: Dependency that resolves a newly…, Return the identity-provider user dependency. Returns: Dependency that resolves…, Return the registered-user dependency. Returns: Dependency that resolves a…

### Community 536 - ".anonymize_user"
Cohesion: 0.22
Nodes (5): User, Register a user from an invitation. Args: cmd: Command carrying the invitation…, Update user information. Args: cmd: Command identifying the user and requested…, Anonymize user information. Args: cmd: Command identifying the user to…, Retrieve a user by their unique key. Args: user_key: Normalized user key to…

### Community 537 - "._parse_and_get_package_metadata"
Cohesion: 0.22
Nodes (5): cached, Retrieve metadata for the application and installed dependencies. Args: cmd:…, Parse package metadata from pyproject.toml and installed dependencies., Normalize project URL label according to PEP 753., Extract a homepage URL using well-known Project-URL labels. Labels follow the…

### Community 538 - "openapi.py"
Cohesion: 0.22
Nodes (8): create_custom_openapi_function(), fix_schema_nullable_and_single_element(), Any, OpenAPI schema generation and compatibility fixes., # TODO: add a function to fix read-only fields, Create a cached OpenAPI schema factory with optional schema fixes., # TODO: add a fix for read-only fields, Fixes the schema by handling 'anyOf' constructs and setting the 'nullable'…

### Community 539 - "._validate_state"
Cohesion: 0.22
Nodes (7): _enum_to_str(), Any, model_validator, Self, Return an enum member name or the supplied string-like value., Normalize members and build the optimized membership matcher., Match a value using the function generated during validation. Args: value: The…

### Community 540 - "._validate_int_for_uuid"
Cohesion: 0.33
Nodes (6): Any, field_validator, UUID, Normalize the place-of-service concept identifier to UUID form., Normalize provider concept identifiers to UUID form., Normalize the country concept identifier to UUID form.

### Community 541 - "MockJWKAndToken"
Cohesion: 0.33
Nodes (3): make_idps_cfg(), Return IDP config list derived from the given mock JWK/token., MockJWKAndToken

### Community 542 - "_ConcreteResult"
Cohesion: 0.22
Nodes (5): _ConcreteResult, scenario_ids, Minimal Pydantic model used to test BaseResult in isolation., UploadLogItem must be the same class as ResultLogItem (alias)., TestResultLogItem

### Community 543 - "Implement JIRA Issue"
Cohesion: 0.25
Nodes (7): 1. Retrieve and Assess the Issue, 2. Create the Work Branch, 3. Establish the Test Baseline, 4. Implement Incrementally, 5. Final Validation and Delivery, Implement JIRA Issue, Safety Rules

### Community 544 - "Links, Subtasks, and Dependencies"
Cohesion: 0.25
Nodes (8): Common link types, Direction, Epics and parents, Issue links, Links, Subtasks, and Dependencies, Reading links, Remote links, Subtasks

### Community 545 - ".logger"
Cohesion: 0.25
Nodes (6): BaseUserManager, Logger, setter, Return the user manager used by authorization policies. Returns: The user…, Logger the requested value., Logger the requested value.

### Community 546 - ".__exit__"
Cohesion: 0.25
Nodes (5): Exception, TracebackType, Commit the transaction managed by this unit of work. Subclasses implement…, Roll back the transaction managed by this unit of work. Subclasses implement…, Finish the managed transaction context. Commits when the context exits…

### Community 547 - "create_seq_endpoints"
Cohesion: 0.25
Nodes (8): create_seq_endpoints(), Any, APIRouter, App, Exception, FastAPI, NoReturn, Register all non-CRUD seqdb endpoints on the given router.

### Community 548 - "._validate_content"
Cohesion: 0.29
Nodes (5): model_validator, Self, Validate that the content format matches the sequence profile type., Verify profile content and derive or validate its content hash. Upload-only…, Report that locus-profile hash validation is not implemented. Returns: A…

### Community 549 - "TestServiceInitialization"
Cohesion: 0.25
Nodes (5): Test service initialization and basic properties., Test that service initialization creates empty collections., Test that properties return the correct internal collections., Test that register_handlers does nothing in base implementation., TestServiceInitialization

### Community 550 - "TestRoleHierarchy"
Cohesion: 0.25
Nodes (5): Test role hierarchy and sub-role calculations., Test that sub-roles are calculated correctly based on permission subsets., Test that sub-role calculations are cached., Test that sub-role cache is cleared when roles are updated., TestRoleHierarchy

### Community 551 - "TestCommandPermissions"
Cohesion: 0.25
Nodes (5): Test command-related permission functionality., Test getting RBAC permissions for a command class excludes non-RBAC permissions., Test getting command classes that have RBAC permissions., Test that get_root_permissions returns all domain permissions., TestCommandPermissions

### Community 552 - "TestGetNewUserFromClaims"
Cohesion: 0.25
Nodes (5): Test scenarios for get_new_user_from_claims., With userinfo and user manager -> returns instance., User manager unable to create -> UnauthorizedAuthError., No user manager -> construct model.User from claims., TestGetNewUserFromClaims

### Community 553 - "test_oidc_provider.py"
Cohesion: 0.29
Nodes (4): JSON Web Key Set (JWKS) Manager This module handles JWT token generation,…, OpenID Connect Provider This module implements OpenID Connect (OIDC)…, Unit tests for JWKS Manager This module contains comprehensive unit tests for…, Unit tests for OpenID Connect Provider This module contains comprehensive…

### Community 554 - "ReadOrganizationResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadOrganizationResultsOnlyPolicy, Filter casedb case-policy reads to visible organizations., Register casedb case-policy commands for organization filtering. Args:…, ReadOrganizationResultsOnlyPolicy

### Community 555 - "ReadSelfResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadSelfResultsOnlyPolicy, Filter casedb user case-policy reads to the current user's records., Register ownership attributes for casedb user case-policy commands. Args:…, ReadSelfResultsOnlyPolicy

### Community 556 - "OrganizationSARepository"
Cohesion: 0.29
Nodes (6): OrganizationSARepository, Any, CommonOrganizationSARepository, Engine, Encapsulates casedb persistence behavior for SQL organization data., Initialize the repository with casedb SQLAlchemy model types. Args: engine:…

### Community 557 - "case_service_crud_genetic_distance_protocol"
Cohesion: 0.33
Nodes (6): case_service_crud_genetic_distance_protocol(), BaseCaseService, GeneticDistanceProtocol, UUID, Handle CRUD operations for genetic-distance protocol entities. This is a simple…, Handle CRUD operations for GeneticDistanceProtocol entities.

### Community 558 - ".filter"
Cohesion: 0.29
Nodes (5): Any, BaseAbacService, Command, Initialize role mappings and command attributes that identify ownership. Args:…, Filter or reject read results that are not owned by the current user.…

### Community 559 - ".crud"
Cohesion: 0.29
Nodes (5): Any, App, CrudCommand, Initialize mapped user models and cache invalidation handlers. Args: app:…, Execute CRUD while preventing root users from deleting themselves or home.…

### Community 560 - "create_root_user_from_claims"
Cohesion: 0.33
Nodes (7): create_root_user_from_claims(), get_existing_root_user(), App, Dynaconf, User, Retrieve the configured root user from an initialized application. Args: cfg:…, Create the configured root user through the application's claim workflow. Args:…

### Community 561 - "Hashable"
Cohesion: 0.29
Nodes (3): Hashable, Return a copy of the feature flags dict to prevent external mutation., Set the enabled state for a feature flag. Args: key: Identifier used to…

### Community 562 - "._custom_json_encoder"
Cohesion: 0.29
Nodes (4): Any, Initialize a BaseLogItem instance., Serialize exceptions, datetimes, and other unsupported objects as strings., Initialize a LogItem instance.

### Community 563 - "ReadSelfResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadSelfResultsOnlyPolicy, Encapsulates restrictions on shared self-result reads according to OmopDB…, Initialize self-scoped command metadata for OmopDB., ReadSelfResultsOnlyPolicy

### Community 564 - "ReadSelfResultsOnlyPolicy"
Cohesion: 0.29
Nodes (6): Any, BaseAbacService, CommonReadSelfResultsOnlyPolicy, Encapsulates restricting eligible result reads to resources owned by the caller., Initialize the shared policy with seqdb identifier-attribute mappings., ReadSelfResultsOnlyPolicy

### Community 566 - "TokenRetrieval"
Cohesion: 0.33
Nodes (3): Response, Simple client for the retrieval of tokens Input variables are passed to the…, TokenRetrieval

### Community 567 - "scenario_ids"
Cohesion: 0.29
Nodes (5): scenario_ids, Test RBAC policy registration., Test that RBAC policies are registered for all RBAC command classes., Test registering RBAC policies with custom override functions., TestRbacPolicyRegistration

### Community 626 - "JQL Search"
Cohesion: 0.33
Nodes (6): Calling the tool, Common queries, JQL Search, Operators, Universal search, Values and quoting

### Community 629 - "Creating Issues"
Cohesion: 0.33
Nodes (6): Content format, Creating Issues, Description structure, Issue types, Optional parameters, Summary guidelines

### Community 630 - "Pytest Run (capture once, inspect many times)"
Cohesion: 0.33
Nodes (5): Method, Notes, Pytest Run (capture once, inspect many times), When NOT to use (rerun for real), When to use

### Community 631 - "ConditionOccurrence"
Cohesion: 0.40
Nodes (6): ConditionOccurrence, ConditionOccurrenceIdentifier, ConditionOccurrence (omopdb.md), ConditionOccurrenceIdentifier (omopdb.md), ConditionOccurrence, ConditionOccurrenceIdentifier

### Community 632 - "case_service_crud_tree_algorithm_class"
Cohesion: 0.29
Nodes (7): case_service_crud_tree_algorithm_class(), BaseCaseService, TreeAlgorithmClass, TreeAlgorithmClassCrudCommand, UUID, Handle CRUD operations for tree-algorithm-class entities. This is a simple…, Handle CRUD operations for TreeAlgorithmClass entities.

### Community 633 - "._serialize_cohort"
Cohesion: 0.40
Nodes (4): field_serializer, UUID, Serialize cohort UUID keys and non-null values as strings., Serialize content UUID keys as strings while retaining values.

### Community 634 - "case_service_crud_tree_algorithm"
Cohesion: 0.29
Nodes (7): case_service_crud_tree_algorithm(), BaseCaseService, TreeAlgorithm, TreeAlgorithmCrudCommand, UUID, Handle CRUD operations for tree-algorithm entities. This is a simple metadata…, Handle CRUD operations for TreeAlgorithm entities.

### Community 635 - "._serialize_id"
Cohesion: 0.40
Nodes (4): field_serializer, UUID, Serialize UUID identifiers as strings while retaining ``None``., Serialize UUID identifiers as strings while retaining ``None``.

### Community 636 - ".get_status_count"
Cohesion: 0.33
Nodes (3): Get the list of parent upload results in this batch upload result., Count statuses across this batch result and its parent results. Args:…, Set this batch result's status based on the aggregate of its children. Only has…

### Community 637 - ".register_retrieve_organization_ids_handler"
Cohesion: 0.40
Nodes (4): Command, UUID, Register an organization-scope resolver for a command class. Args:…, Resolve the organization IDs addressed by a command. Args: cmd: The command to…

### Community 638 - ".is_existing_user_by_key"
Cohesion: 0.20
Nodes (3): Determine whether a user exists for a normalized unique key. Args: uow: Unit of…, Initialize a BaseUnitOfWork instance., Return whether managing context.

### Community 639 - ".filter"
Cohesion: 0.40
Nodes (4): Any, Command, Mask audit fields unless the command user has a privileged role. If the user…, Recursively clear audit metadata on models nested in a result. Args: obj:…

### Community 640 - ".retrieve_user_roles"
Cohesion: 0.33
Nodes (4): Hashable, User, Retrieve the roles assigned directly to a commondb user. Args: user: User whose…, Determine whether a user has the configured root role. Args: user: User whose…

### Community 641 - ".is_invalidated"
Cohesion: 0.33
Nodes (3): Return whether an entry written at `created_at` is affected., Return whether an entry must not be served at all., Return whether an entry may be served while a refresh runs.

### Community 642 - "._validate"
Cohesion: 0.40
Nodes (4): model_validator, Self, Validate claim mappings and public-provider credentials., Validate public-provider credentials.

### Community 643 - "OrganizationService"
Cohesion: 0.33
Nodes (5): OrganizationService, Any, CommonOrganizationService, Encapsulates handling of organization commands using OmopDB user and invitation…, Initialize the shared service with OmopDB model classes.

### Community 644 - "._validate_sample_ids"
Cohesion: 0.40
Nodes (4): field_validator, UUID, Require every requested sample identifier to occur at most once., Require every requested sample identifier to occur at most once.

### Community 645 - ".register_mappers"
Cohesion: 0.22
Nodes (6): Engine, Self, Initialise the repository with the provided SQLAlchemy engine. Registers…, Create and register mappers for a list of entities using the given factory. The…, Default implementation to register standard mappers for a list of entities., Register a mapper, enforcing uniqueness by row class and table.

### Community 646 - "._validate_allele_profile_upload"
Cohesion: 0.33
Nodes (3): Return ordered allele identifiers in their encoded profile representation., Return the deterministic content hash for ordered allele identifiers., Validate and normalize an allele-profile upload representation. Returns: The…

### Community 647 - "._validate_mlva_profile_upload"
Cohesion: 0.33
Nodes (3): Return ordered MLVA repeat numbers in their JSON profile representation., Require a locus code map for a map-based profile representation. Args:…, Validate and normalize an MLVA-profile upload representation. Returns: The…

### Community 649 - "._validate_exactly_one_representation"
Cohesion: 0.33
Nodes (3): Format representation names for a validation error message., Require exactly one named profile representation. Args: representations:…, Validate and normalize a k-mer-profile upload representation. Returns: The…

### Community 653 - "TestRootUserTokenTimeToLive"
Cohesion: 0.33
Nodes (4): Test root token TTL enforcement helper., Root token younger than configured TTL should pass., Root token older than configured TTL should raise UnauthorizedAuthError., TestRootUserTokenTimeToLive

### Community 654 - "TestInitializationValidation"
Cohesion: 0.33
Nodes (4): Test IDP configuration validation during initialization., Duplicate names raise InitializationServiceError., If IDP init returns None, it is added to pending list., TestInitializationValidation

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

### Community 669 - "omopdb/repositories/sa_model/base.py"
Cohesion: 0.40
Nodes (4): DataLineageMixin, declarative_mixin, Shared SQLAlchemy mixins used by OmopDB table mappings., Encapsulates a SQLAlchemy model mixin for adding a number of standard fields.

### Community 670 - "omop_service_retrieve_persons_by_id"
Cohesion: 0.40
Nodes (4): omop_service_retrieve_persons_by_id(), BaseOmopService, Retrieve all relevant FullPersons, containing all Person-linked data. The…, Retrieve full persons identified by the command.

### Community 671 - "_FakeCaseAbacPolicy"
Cohesion: 0.50
Nodes (3): _FakeCaseAbacPolicy, Any, Lightweight policy to inject a case ABAC object into commands.

### Community 676 - "Examples"
Cohesion: 0.50
Nodes (4): Example 1: Bug report, Example 2: Feature request with priority, Example 3: Mark an issue as blocked, Examples

### Community 681 - "Death"
Cohesion: 0.50
Nodes (4): Death, DeathIdentifier, Death (omopdb.omop.md), DeathIdentifier (omopdb.omop.md)

### Community 682 - "._validate_unit_for_type"
Cohesion: 0.50
Nodes (3): model_validator, Self, Enforce unit presence according to the concept set type.

### Community 683 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseAbacService, Initialize the policy with an ABAC service and policy properties. Args:…

### Community 686 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseAbacService, Initialize the policy with its ABAC service and configuration properties. Args:…

### Community 687 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, App, Initialize role maps and configured root and guest role values. Args: app:…

### Community 688 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, BaseAbacService, Initialize role mappings and organization-ID resolvers. Args: abac_service:…

### Community 689 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, App, Initialize configured role mappings and permissions exempt from RBAC. Args:…

### Community 690 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, App, Initialize configured concrete policy classes. Args: app: Application that owns…

### Community 691 - "InvalidIdsError"
Cohesion: 0.50
Nodes (3): InvalidIdsError, Error for malformed or unknown object identifiers., Initialize a InvalidIdsError instance.

### Community 692 - "InvalidLinkIdsError"
Cohesion: 0.50
Nodes (3): InvalidLinkIdsError, Error for identifiers that violate a model relationship., Initialize a InvalidLinkIdsError instance.

### Community 693 - "InvalidModelIdsError"
Cohesion: 0.50
Nodes (3): InvalidModelIdsError, Error for identifiers belonging to an unexpected model., Initialize a InvalidModelIdsError instance.

### Community 694 - "LinkConstraintViolationError"
Cohesion: 0.50
Nodes (3): LinkConstraintViolationError, Error for a relationship constraint violation between model instances., Initialize a LinkConstraintViolationError instance.

### Community 695 - "._validate_state"
Cohesion: 0.50
Nodes (3): model_validator, Self, Build the optimized UUID membership matcher.

### Community 696 - ".validate_limit"
Cohesion: 0.50
Nodes (3): model_validator, Self, Normalize the deprecated maximum-profile field into ``limit``.

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

### Community 701 - "File"
Cohesion: 0.50
Nodes (4): File, Base, RowMetadataMixin, Encapsulates the SQLAlchemy model for the persistable domain model.

### Community 702 - "._validate_ref1_fields"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate that either ref1_id or ref1_code is provided.

### Community 703 - "Available Tools"
Cohesion: 0.67
Nodes (3): Available Tools, Read operations, Write operations

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
- **515 isolated node(s):** `post-pr-comments.sh script`, `docker-entrypoint.sh script`, `PYTHONPATH`, `Gen-EpiX`, `$schema` (+510 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **161 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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