# Graph Report - gen-epix-api  (2026-08-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 14117 nodes · 34014 edges · 639 communities (474 shown, 165 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 1694 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3d81c943`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- commondb/domain/model/__init__.py
- Permission
- casedb/domain/command/__init__.py
- SARepository
- BaseCaseService
- BaseUnitOfWork
- CrudEndpointGenerator
- Client
- commondb/domain/enum.py
- SeqService
- TestClient
- command/seq.py
- _uuid_field_name
- JWKSManager
- AppCfg
- CasedbTestClient
- CrudOperation
- MockRequest
- BaseCaseService
- RequestorApp
- TestUpdate
- log_parser_v2.py
- ObjectAdapter
- entity.py
- BaseRbacServiceTestCase
- casedb/repositories/__init__.py
- JsonFormatter
- BaseAppCfg
- seqdb/domain/enum.py
- CaseService
- Transformer
- App
- OrganizationService
- Run
- .create_claims
- DimLike
- Role
- server.py
- Model
- _crud_cascade_delete
- case_service_create_file_for_read_set_or_seq
- .create_parent_for_upload
- TestTokenStore
- casedb CASE Detailed ERD
- TestCreate
- Any
- test_filter_base_filter.py
- composite.py
- Domain
- DictRepository
- BaseSeqService
- casedb/domain/model/__init__.py
- commondb/domain/literal.py
- omopdb/domain/model/__init__.py
- omopdb/repositories/sa_model/__init__.py
- Token
- .key_generator
- omopdb/domain/command/__init__.py
- test_seqdb_retrieve_best.py
- TransformResult
- commondb/api/exc.py
- UuidSetFilter
- StringSetFilter
- IsoTimeTransformer
- PersonBatchForUpload
- seqdb/domain/model/__init__.py
- .create_person_for_upload
- commondb/repositories/sa_model/__init__.py
- TestcasedbEdgeCasesRefDataAccess
- test_seqdb_distance_optimization_benchmark.py
- CrudCommand
- test_user_manager_auto_create.py
- .create_client
- Policy
- IntervalToIntervalTransformer
- BaseCrudTestCase
- _make_protocol
- casedb/domain/enum.py
- BaseRetrieveCaseTestCase
- auth/__init__.py
- CommondbDictModelModifier
- define_edge_cases_reference.py
- CaseTypeAccessAbac
- TestCreate
- TestClientStore
- CasedbRemoteApp
- SeqProfile
- .create_command_and_result_for_samples
- seqdb/repositories/sa_model/__init__.py
- SeqSARepository
- CaseValidator
- BaseBatchForUpload
- BaseService
- test_casedb_crud_common.py
- test_commondb_upload.py
- make_assoc
- OauthIdpClient
- validate_int_for_uuid_field
- test_get_full_persons_by_person_ids.py
- BaseAbacTestCase
- Person
- CaseTypeCrudCommand
- CaseAbac
- omop/ontology.py
- Entity
- create_client
- seqdb_test_client.py
- Hashable
- ImportGraphAnalyzer
- AuthTestClient
- TypedDatetimeRangeFilter
- retrieve_case.py
- casedb/repositories/sa_model/__init__.py
- case_validator.py
- BaseIsOwnCasesTestCase
- sa_model/util.py
- api/seq.py
- Concept
- Concept (omopdb.omop / OMOP CDM entity)
- RoleGenerator
- DomainException
- calculate_seq_distance.py
- seq_service_calculate_seq_distances_for_new_profiles
- _verify_children_seq_classifications
- OIDCProvider
- ._get_allele_profile_for_ids
- CompositeFilter
- AuthService
- test_casedb_case_validator.py
- Any
- .create_case_for_upload
- .create_child1_for_upload
- UploadCasesCommand
- Filter
- .create_child2_for_upload
- Person
- SeqdbTestClient
- IdentifierForUpload
- .create_crud_cmd
- sa/util.py
- RBACTestClient
- BaseAnonymizer
- Command
- SeqdbEndpointTestClient
- .create_seq_for_upload
- .create_sample_for_upload
- validate_int_enum_value
- Seq
- InMemoryOrganizationRepository
- make_cdb_user
- test_omopdb_upload.py
- TestUpdate
- TestModelBaseSeq
- CaseSet
- Organization
- test_seqdb_calculate_seq_distance.py
- BaseRepository
- TokenIntrospectionManager
- FileCompression
- BaseSimilarCasesTestCase
- test_update_user_policy.py
- api/case.py
- case_service_crud_ref_col
- test_casedb_custom.py
- test_fastapp_rbac_service.py
- TestModelSeq
- .__init__
- .__init__
- Model
- test_casedb_upload.py
- AuthEnv
- TestModelSampleBatchForUpload
- TestModelSeqForUpload
- OAuth2Client
- Protocol (seqdb entity)
- ReadUserPolicy
- EndpointTestClient
- TestRegistrationAndLookups
- _DummyMapper
- BasePersonUploadTestCase
- CaseType
- Protocol
- Any
- ParentUploadResult
- DummyIdpClient
- SeqProfileForUpload
- set_service_repository
- Gen-EpiX README
- case_date.py
- CommondbRemoteApp
- SAMapper
- derived.py
- test_omopdb_model.py
- TestDelete
- BaseUploadTestCase
- TestNumpyAlleleIntegration
- IdentifierIssuer
- DatetimeRangeFilter
- ModelNoId
- TestCreate
- BaseCommondbRemoteAppTestCase
- generate_seq_distances.py
- Case Type
- BaseSeqdbService
- LocusSet
- test_seqdb_upload.py
- test_cfg_log_level.py
- SeqGenerationSettings
- Data Collection
- ErmGenerator
- CaseForUpload
- UserManager
- LogParser2
- TestCreateUserFromToken
- TestInitialization
- ServiceTestClient
- Development Guide
- omop/service.py
- crud_dim.py
- case/non_persistable.py
- model/ontology.py
- BaseEtlResult
- model/omop/upload.py
- RemoteApp
- SeqDictRepository
- TestCaseUpload
- TestCommondbModelProcessMetadata
- test_seqdb_calculate_phylogenetic_tree.py
- scenario_ids
- TestModelSeqProfileForUpload
- fastapp shared application framework
- crud_col_set.py
- OmopdbEndpointTestClient
- gen_epix/util.py
- DummyCommand
- TestDuplicateIds
- UserManager
- TestCreate
- TestBaseResult
- TestRetrieveCompleteCaseType
- .create_local_or_remote_app
- convert
- SeqdbRemoteApp
- .create_measurement_for_upload
- .__init__
- Any
- OmopdbRemoteApp
- TestCasedbMetadataMasking
- test_read_config.py
- DummyCmd
- TestDataLineageMixin
- Organization (commondb.organization entity)
- Sample
- EtlLogItem
- Linter
- test/test_client/util.py
- .create_read_set_for_upload
- Organization
- IdentifierIssuer (omopdb.organization entity)
- Organization
- get_case_abac_from_command
- .get_test_client
- SampleBatchForUpload
- test_logging_runtime_contract.py
- TestCommondbMetadataMasking
- crud_allele.py
- .get_token
- test/conftest.py
- Gen-EpiX Contributor Documentation Index
- Organization
- SAUnitOfWork
- CalculatePhylogeneticTreeCommand
- _encode_to_int32
- TestRead
- test_retrieve_stats.py
- TestOauthIdpClientIntrospection
- TestUserPermissions
- test_get_specimen_ids_by_cohort_ids.py
- AuthorizationCodeStore
- case_service_crud_case_data_collection_link
- abac/__init__.py
- BaseAppComposer
- BaseSAMapper
- omopdb/domain/enum.py
- test_error_code_unicity
- App (command dispatcher / PEP)
- Organization (omopdb.organization entity)
- crud_pcr_measurement.py
- ModelFieldProps
- .__init__
- FakeResponse
- test_general_model_field_properties.py
- TestSeqdbRemoteApp
- BaseUploadTestCase
- JsonFormatter
- CdmSource
- crud_seq_category.py
- crud_ast_prediction.py
- crud_locus_code_map.py
- UUID
- BaseRemoteService
- crud_read_set.py
- crud_read_set_identifier.py
- crud_ref_allele.py
- crud_ref_seq.py
- crud_sample_data_collection_link.py
- crud_seq_classification.py
- crud_seq_distance.py
- crud_seq_identifier.py
- crud_seq_profile.py
- crud_seq_profile_identifier.py
- crud_seq_taxonomy.py
- TestUploadEdgeCases
- crud_taxon_set_member.py
- UUID
- BaseCaseAbacTestCase
- TestCaseTypeProps
- .create_case
- .create_uploader
- Test6Identifiers
- IdpClient hierarchy
- Protocol
- ._validate_model
- BaseLogItem
- PayerPlanPeriod
- Taxon
- Transformer Framework
- rewrite_parametrized_dependency_markers
- test_omopdb_upload_base_result.py
- TestUploadResult
- env
- test_seqdb_remote_app.py
- fixture
- AppComposer (Composition Root)
- Data Collection (doc)
- Region Set
- GraphvizErmGenerator
- MermaidErmGenerator
- Sample
- FullSample
- SeqTaxonomy
- RetrieveSimilarCasesCommand
- RetrievePhylogeneticTreeByCasesCommand
- RetrieveProtocolsCommand
- sa_model/ontology.py
- CommondbSAMapper
- _make_mapper
- .__init__
- renovate.json
- TestSQLInjection
- TestOAuth2Validation
- TestAnonymizeUser
- generate_seqdb_models.py
- patch
- TestOIDCProvider
- PhylogeneticTree
- Concept Relation
- Outage (commondb.system entity)
- _build_diagram
- Protocol
- CaseBatchForUpload
- ._create_remote_app
- dependency
- TestVerifyUserRights
- dependency
- test_logging_yaml.py
- TestDelete
- dependency
- env
- dependency
- RowMetadataMixin
- BaseRepository (abstract)
- Contact (doc)
- seqdb Overview ERD
- IdentifierIssuer
- Taxon
- Locus
- RetrieveGeneticSequenceFastaByCaseCommand
- HandleNoResponseMiddleware
- EngineFactory
- Atlas Agent (Conductor)
- TestRead
- TestUpdate
- OAuth 2.0 Provider with OpenID Connect Support
- Entity descriptor
- DataCollection
- Seq
- OrganizationContacts
- .anonymize_user
- TestDelete
- seq_service_update_seq_distances
- ._validate_content
- ._serialize_int_enums
- Etiology
- Subject
- Concept
- TestDelete
- MeasurementRelation
- ObservationPeriod
- Locus
- ReadSet
- SeqProfile
- EtlLogItem
- CaseAbacPolicy
- .create_unique_values_temp_table
- omopdb/policies/update_user_policy.py
- ._validate_model
- services/user_manager.py
- .__init__
- seqdb/repositories/organization_sa.py
- get_test_client
- TestGetCaseDataCollections
- OAuth Client Credential Flow Test
- init-db one-shot database creation service
- DataCollection (commondb.organization entity)
- DataCollectionSetMember
- Specimen
- DataCollectionSetMember
- TreeAlgorithm
- RetrieveContainingRegionCommand
- casedb/services/organization.py
- .get_row_id_column
- ._validate
- IsOrganizationAdminPolicy
- CalculateSeqDistancesForNewProfilesCommand
- IsOrganizationAdminPolicy
- .__call__
- release-please-config.json
- TestContent
- test_debug_console_uses_json_formatter
- App.handle() command dispatch
- casedb SUBJECT Detailed ERD
- TestRead
- TestRead
- TestUpdate
- NoteNlp
- TreeAlgorithm
- SeqClassificationForUpload
- ._validate_state
- ._validate_state
- .__init__
- .organization_identifier_issuer_link_update_association
- test/enum.py
- ._validate_some_criteria
- .__init__
- ._validate_protocol_type_dependencies
- Test extracting claims from openid scope only.
- .data_collection_set_data_collection_update_association
- docker-entrypoint.sh
- Default App Ports (8000/8001/8002/8010)
- CohortDefinition (omopdb.md)
- Organization
- Locus (seqdb entity)
- SeqCategory
- Locus
- .validate_model
- .__init__
- .update_user_own_organization
- .invite_user
- .retrieve_feature_flags
- .retrieve_outages
- .get_headers
- .invite_user
- .organization_set_organization_update_association
- .retrieve_outages
- .ssl_context
- .__init__
- .__init__
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
- .anonymize_user
- .retrieve_feature_flags
- .retrieve_invite_user_constraints
- .retrieve_own_permissions
- wait_for_mssql.py
- .test_create_discovery_document_supported_claims
- .test_create_discovery_document_auth_methods
- .test_create_discovery_document_signing_algorithms
- .test_create_discovery_document_additional_features
- .test_create_id_token_basic
- .test_create_id_token_with_auth_time
- .test_create_id_token_with_additional_claims
- .test_create_id_token_with_custom_expiry
- .test_validate_id_token
- .test_create_userinfo_response_basic
- .test_create_userinfo_response_with_profile_scope
- .setup_method
- .test_create_userinfo_response_with_email_scope
- .test_create_userinfo_response_with_custom_claims
- .test_provider_initialization
- .test_create_userinfo_response_with_address_scope
- .test_create_userinfo_response_with_phone_scope
- .test_create_discovery_document_basic
- .test_create_userinfo_response_multiple_scopes
- .test_get_supported_algorithms
- .test_create_jwks_response
- .test_validate_nonce_valid
- .test_validate_nonce_invalid
- .test_extract_claims_from_scope_email
- .test_extract_claims_from_scope_unknown_scope
- .test_create_logout_response_basic
- .test_create_discovery_document_response_types
- .test_create_discovery_document_grant_types
- .test_create_discovery_document_supported_scopes
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
- CaseDB RBAC Diagram
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
- BaseCaseService
- BaseException
- Engine
- Hashable
- Self
- Session
- setter
- TypeEngine
- UUID
- Prompt Steering Agent
- Gen-EpiX
- Base
- fixture
- MonkeyPatch
- parametrize
- Path
- gen-epix-api Version 6.1.0
- env
- ProcedureOccurrence
- DataException
- .__init__
- create_root_user_from_claims
- ._validate_content
- ._validate_content
- get_test_client
- _PytestMockConfig
- ._get_user_and_repository
- ._validate_model
- .get_nucleotide_seq
- .is_available

## God Nodes (most connected - your core abstractions)
1. `BaseUnitOfWork` - 241 edges
2. `Entity` - 165 edges
3. `Model` - 153 edges
4. `BaseCaseService` - 147 edges
5. `BaseSeqService` - 135 edges
6. `App` - 126 edges
7. `DictRepository` - 124 edges
8. `CrudOperation` - 122 edges
9. `CasedbTestClient` - 120 edges
10. `SARepository` - 105 edges

## Surprising Connections (you probably didn't know these)
- `PPR Test Docker Compose (Mock OIDC + CASEDB/SEQDB)` --semantically_similar_to--> `SQL + Mock OIDC Docker Compose (SEQDB/OMOPDB/CASEDB)`  [INFERRED] [semantically similar]
  docker-compose.ppr_test.yml → docker-compose.sql.idp.yml
- `casedb-seqdb-omopdb E2E Connection Test Logging Config` --semantically_similar_to--> `casedb Logging Config`  [INFERRED] [semantically similar]
  test/end_to_end/casedb_seqdb_connection/logging.yaml → gen_epix/casedb/config/logging.yaml
- `casedb-seqdb-omopdb E2E Connection Test Logging Config` --semantically_similar_to--> `omopdb Logging Config`  [INFERRED] [semantically similar]
  test/end_to_end/casedb_seqdb_connection/logging.yaml → gen_epix/omopdb/config/logging.yaml
- `casedb-seqdb-omopdb E2E Connection Test Logging Config` --semantically_similar_to--> `seqdb Logging Config`  [INFERRED] [semantically similar]
  test/end_to_end/casedb_seqdb_connection/logging.yaml → gen_epix/seqdb/config/logging.yaml
- `Review Skill` --semantically_similar_to--> `CI: Static Analysis and Testing Workflow`  [INFERRED] [semantically similar]
  .agents/skills/review/SKILL.md → .github/workflows/main.yml

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Gen-EpiX code quality and test toolchain** — dev_requirements_pytest, dev_requirements_isort, dev_requirements_black, dev_requirements_pylint, dev_requirements_mypy, dev_requirements_coverage [EXTRACTED 0.90]
- **Command-centric authorization flow** — agents_transport_adapter_pattern, agents_app_handle, agents_command_centric_authorization, agents_policy_phases [EXTRACTED 0.90]
- **App domains composed on the fastapp framework** — agents_fastapp_framework, agents_commondb, agents_casedb, agents_seqdb, agents_omopdb, agents_filter_transform [EXTRACTED 0.90]
- **Phylogenetic Tree Analysis Flow** — docs_erm_casedb_seqdb_detailed_phylogenetictree, docs_erm_casedb_case_detailed_treealgorithm, docs_erm_casedb_case_detailed_geneticdistanceprotocol [EXTRACTED 0.90]
- **Atlas Multi-Agent Conductor Workflow** — github_agents_atlas_agent, github_agents_oracle_agent, github_agents_sisyphus_agent, github_agents_code_review_agent, github_agents_explorer_agent, github_agents_frontend_engineer_agent [EXTRACTED 1.00]
- **Authentication Pipeline (AuthService -> IdpClient -> UserManager)** — docs_02a_fastapp_framework_authservice, docs_02a_fastapp_framework_idpclient, docs_02a_fastapp_framework_usermanager, docs_02a_fastapp_framework_oauthidpclient [EXTRACTED 1.00]
- **Boot & Composition Sequence (AppCfg -> AppComposer -> create_fast_api)** — docs_08a_app_composition_walkthrough_appcfg, docs_08a_app_composition_walkthrough_appcomposer, docs_08a_app_composition_walkthrough_createfastapi, docs_02_architecture_boot_sequence [EXTRACTED 1.00]
- **CaseType Dimension/Column Data Model** — docs_erm_casedb_case_detailed_casetype, docs_erm_casedb_case_detailed_dim, docs_erm_casedb_case_detailed_col [EXTRACTED 1.00]
- **OMOP CDM Concept/Vocabulary/Domain/ConceptClass standard-vocabulary triangle** — docs_erm_omopdb_omop_detailed_concept, docs_erm_omopdb_omop_detailed_vocabulary, docs_erm_omopdb_omop_detailed_domain, docs_erm_omopdb_omop_detailed_conceptclass [EXTRACTED 1.00]
- **Policy Enforcement Pipeline (BEFORE/DURING/AFTER via PDP and RbacPolicy)** — docs_02_architecture_policy_enforcement_timing, docs_02a_fastapp_framework_pdp, docs_02a_fastapp_framework_app, docs_02a_fastapp_framework_rbacpolicy [EXTRACTED 1.00]
- **seqdb Service ERDs Forming Overview Schema** — docs_erm_seqdb_organization_detailed_doc, docs_erm_seqdb_seq_detailed_doc, docs_erm_seqdb_system_detailed_doc, docs_erm_seqdb_file_doc, docs_erm_seqdb_doc [EXTRACTED 1.00]
- **seqdb Sample x Protocol sequencing/measurement pipeline** — docs_erm_seqdb_detailed_sample, docs_erm_seqdb_detailed_protocol, docs_erm_seqdb_detailed_seq, docs_erm_seqdb_detailed_readset [EXTRACTED 1.00]
- **Explorer-Oracle-Prometheus-Atlas Research/Planning Delegation Pipeline** — github_agents_prometheus_agent, github_agents_atlas_agent, github_agents_explorer_agent, github_agents_oracle_agent [INFERRED 0.85]
- **Org/User Case Access & Share Policy Pattern** — docs_erm_casedb_detailed_organizationaccesscasepolicy, docs_erm_casedb_detailed_useraccesscasepolicy, docs_erm_casedb_case_detailed_casetypeset [INFERRED 0.85]
- **External Identifier Crosswalk Pattern (IdentifierIssuer + *Identifier bridge tables)** — docs_erm_commondb_organization_detailed_identifierissuer, docs_erm_omopdb_omop_detailed_personidentifier, docs_erm_seqdb_detailed_sampleidentifier [INFERRED 0.85]
- **Shared Debug File+Console Logging Pattern (casedb/commondb/omopdb/seqdb)** — gen_epix_casedb_config_logging_debug_logging, gen_epix_commondb_config_logging_debug_logging, gen_epix_omopdb_config_logging_debug_logging, gen_epix_seqdb_config_logging_debug_logging [INFERRED 0.95]
- **Shared Non-Debug JSON Logging Pattern (casedb/commondb/omopdb/seqdb)** — gen_epix_casedb_config_logging_logging, gen_epix_commondb_config_logging_logging, gen_epix_omopdb_config_logging_logging, gen_epix_seqdb_config_logging_logging [INFERRED 0.95]

## Communities (639 total, 165 thin omitted)

### Community 0 - "commondb/domain/model/__init__.py"
Cohesion: 0.02
Nodes (96): Any, BaseAbacService, CommonReadOrganizationResultsOnlyPolicy, ReadOrganizationResultsOnlyPolicy, Any, BaseAbacService, CommonReadSelfResultsOnlyPolicy, ReadSelfResultsOnlyPolicy (+88 more)

### Community 1 - "Permission"
Cohesion: 0.02
Nodes (99): ApiPermission, BaseModel, PermissionType, PermissionTypeSet, LogItem, Permission, computed_field, field_serializer (+91 more)

### Community 2 - "casedb/domain/command/__init__.py"
Cohesion: 0.03
Nodes (124): OrganizationAccessCasePolicyCrudCommand, OrganizationShareCasePolicyCrudCommand, CrudCommand, Manage organization-level access policies to cases and case sets in a data…, Manage per-user maximum access policies to cases and case sets in a data…, Manage which cases or case sets an organization may share from one data…, Manage per-user share permissions for moving cases or case sets between data…, UserAccessCasePolicyCrudCommand (+116 more)

### Community 3 - "SARepository"
Cohesion: 0.05
Nodes (60): Base, BaseException, BaseRepository, BaseSAMapperFactory, CaptureFixture, Engine, Entity, fixture (+52 more)

### Community 4 - "BaseCaseService"
Cohesion: 0.03
Nodes (93): DomainBaseCaseService, BaseCaseAbacPolicy, Any, BaseAbacService, Command, BaseCaseService, Any, Case (+85 more)

### Community 5 - "BaseUnitOfWork"
Cohesion: 0.03
Nodes (80): Extends batch upload to uploading the cases with this service, and the read…, Mixin class for BatchForUpload classes providing common functionality., UploadBatchCommandMixin, EtlStatus, BaseBatchUploadResult, Represents the result of an upload operation for a particular object, including…, Add log items to the upload result. If any of the added log items has severity…, Represents an upload result that also includes upload results for identifiers,… (+72 more)

### Community 6 - "CrudEndpointGenerator"
Cohesion: 0.03
Nodes (119): create_abac_endpoints(), Any, APIRouter, App, Exception, FastAPI, NoReturn, create_geo_endpoints() (+111 more)

### Community 7 - "Client"
Cohesion: 0.02
Nodes (69): RequestValidator, Client, ClientStore, Any, OAuth 2.0 Client Store This module manages OAuth 2.0 client registration and…, Retrieve a client by client ID., Delete a client from the store., Deactivate a client (soft delete). (+61 more)

### Community 8 - "commondb/domain/enum.py"
Cohesion: 0.04
Nodes (81): post-pr-comments.sh Script, Review Skill, ETL (Extract, Transform, Load) script for Gen-EpiX genomic epidemiology…, AppConfigType, AppType, AppTypeSet, DataIssueType, DataIssueTypeSet (+73 more)

### Community 9 - "SeqService"
Cohesion: 0.04
Nodes (39): AstMeasurementCrudCommand, Retrieve the sequences for the given sequence IDs in FASTA format as an…, Retrieve all profiles that match at least one of the given query profiles…, RetrieveSeqFastaCommand, RetrieveSimilarProfilesCommand, SeqCrudCommand, AstMeasurement, Seq (+31 more)

### Community 10 - "TestClient"
Cohesion: 0.04
Nodes (63): Any, Command, DataCollection, datetime, Model, Organization, OrganizationAdminPolicy, OrganizationIdentifierIssuerLink (+55 more)

### Community 11 - "command/seq.py"
Cohesion: 0.03
Nodes (62): LocusCrudCommand, LocusSetCrudCommand, ProtocolCrudCommand, ProtocolSetCrudCommand, ProtocolSetMemberCrudCommand, CrudCommand, # TODO: is a temporary option, to be removed once the memory handling is…, # TODO: is a temporary option, to be removed once the numpy-vectorised ALLELE… (+54 more)

### Community 12 - "_uuid_field_name"
Cohesion: 0.04
Nodes (66): DataLineageMixin, Any, UUID, Mixin class to add fields to a model for data lineage tracking., Validate that the input value is either a UUID or a string that can be…, Validate and synchronize string-based primary key arguments. Mutates ``data``…, Validate and synchronize integer-based primary key arguments. Mutates ``data``…, validate_int_key_args() (+58 more)

### Community 13 - "JWKSManager"
Cohesion: 0.03
Nodes (57): JWKSManager, Any, JSON Web Key Set (JWKS) Manager This module handles JWT token generation,…, Get the current key ID., Generate a new key pair and return the new key ID., Create an OpenID Connect ID Token., Validate only the signature of a JWT token without checking claims., Decode JWT header without verification. (+49 more)

### Community 14 - "AppCfg"
Cohesion: 0.02
Nodes (115): # TODO: app variable added for backwards compatibility with startup code that…, CommonRoleGenerator, RoleGenerator, AppComposer, Any, CommonAppComposer, # TODO: app variable added for backwards compatibility with startup code that…, create_fast_api() (+107 more)

### Community 15 - "CasedbTestClient"
Cohesion: 0.05
Nodes (45): ConceptSet, Contact, Disease, EtiologicalAgent, map_paired_elements(), Any, Hashable, Convert an iterable of paired elements to a dictionary of lists or sets, where… (+37 more)

### Community 16 - "CrudOperation"
Cohesion: 0.04
Nodes (91): _field_marker(), Mermaid-based ERM diagram generator. Produces Mermaid ``erDiagram`` markdown…, Return Mermaid column marker (PK / FK) or empty string., # TODO: remove UPDATE from association objects that do not have properties of…, Command, Domain, Hashable, Register service types, models and commands with a domain. In case some models… (+83 more)

### Community 17 - "MockRequest"
Cohesion: 0.03
Nodes (51): MockRequest, Any, Test OAuth2Validator initialization., Test client authentication requirement for client credentials flow., Test client authentication requirement for other grant types., Test client authentication with valid credentials., Test client authentication with invalid client ID., Test client authentication with missing credentials. (+43 more)

### Community 18 - "BaseCaseService"
Cohesion: 0.03
Nodes (72): CaseCrudCommand, CaseSetCategoryCrudCommand, CaseSetStatusCrudCommand, CaseTypeSetCategoryCrudCommand, GeneticDistanceProtocolCrudCommand, CrudCommand, Manage cases (list/get/create/update/delete) with typed content tied to a…, Maintain the categories used to tag case sets (e.g., outbreak, surveillance,… (+64 more)

### Community 19 - "RequestorApp"
Cohesion: 0.05
Nodes (29): Response, Client application that requests access tokens and calls protected endpoints., Initialize the OIDC client., Get an access token for the specified audience., Call a protected endpoint with the access token., Create a properly formatted but invalid JWT token for testing., RequestorApp, Any (+21 more)

### Community 20 - "TestUpdate"
Cohesion: 0.29
Nodes (5): Env, scenario_ids, skipif, Anonymize and deactivate a user's personal information., TestUpdate

### Community 21 - "log_parser_v2.py"
Cohesion: 0.04
Nodes (55): NoFilter, Any, BaseModel, Hashable, Any, model_validator, Self, RegexFilter (+47 more)

### Community 22 - "ObjectAdapter"
Cohesion: 0.04
Nodes (50): ObjectAdapter, Unified adapter that provides consistent interface for different object types.…, Apply transformation if condition is met., Transform the specified field if it exists., Transform all specified fields., Transform the entire object., Maps a tuple of m source fields to a tuple of n target fields using a provided…, Transform the provided object using the mapping. The object has the target… (+42 more)

### Community 23 - "entity.py"
Cohesion: 0.06
Nodes (88): Model, Key, create_keys(), create_links(), create_multi_links(), Key, Create a dictionary of Key objects from a dictionary of key definitions., Create a dictionary of Link objects from a dictionary of link definitions. (+80 more)

### Community 24 - "BaseRbacServiceTestCase"
Cohesion: 0.02
Nodes (74): BaseRbacServiceTestCase, ConcreteRbacService, Any, App, BaseRbacService, Command, Hashable, scenario_ids (+66 more)

### Community 25 - "casedb/repositories/__init__.py"
Cohesion: 0.04
Nodes (48): CommonBaseAbacRepository, BaseGeoRepository, BaseOntologyRepository, AbacDictRepository, BaseAbacRepository, AbacSARepository, BaseAbacRepository, GeoDictRepository (+40 more)

### Community 26 - "JsonFormatter"
Cohesion: 0.07
Nodes (73): Formatter, _build_sensitive_re(), JsonFormatter, _normalise_sensitive_keys(), Any, LogRecord, Central JSON logging formatter for all GenEpix container applications. Ensures…, Logging filter for the ``uvicorn.access`` logger. Parses the structured args… (+65 more)

### Community 27 - "BaseAppCfg"
Cohesion: 0.03
Nodes (42): BaseAppCfg, _is_descendant_logger(), Dynaconf, Enum, Logger, Path, Refactored configuration management using Strategy Pattern., Logger for API layer messages. (+34 more)

### Community 28 - "seqdb/domain/enum.py"
Cohesion: 0.06
Nodes (48): CoreSchema, AstResultFormat, DnaAmbiguityMap, DnaReverseAmbiguityMap, IdFactory, IntEnumWithJsonSchemaMixin, LocusType, PcrResultFormat (+40 more)

### Community 29 - "CaseService"
Cohesion: 0.05
Nodes (42): CaseService, BaseCaseService, Case, CaseIdentifier, CaseSet, CaseSetCategory, CaseSetMember, CaseSetStatus (+34 more)

### Community 30 - "Transformer"
Cohesion: 0.05
Nodes (53): Object adapters for providing unified interface across different object types., example_conditional_transformation(), example_usage(), Person, BaseModel, Examples demonstrating usage of the transformer framework., Example Pydantic model., Example custom transformer. (+45 more)

### Community 31 - "App"
Cohesion: 0.07
Nodes (26): App, Any, BaseUserManager, Command, datetime, Domain, Hashable, Logger (+18 more)

### Community 32 - "OrganizationService"
Cohesion: 0.04
Nodes (43): Any, App, CrudCommand, Seq, UUID, Generic CRUD operation handler that forwards the command to seqdb while setting…, SeqdbService, RetrieveLicensesCommand (+35 more)

### Community 34 - ".create_claims"
Cohesion: 0.05
Nodes (46): BaseAuthServiceTestCase, Any, scenario_ids, UUID, Test idp_clients property., idp_clients property returns a copy, not the original list., Test scenarios for get_existing_user_from_token., First IDP unauthorized, second IDP succeeds. (+38 more)

### Community 35 - "DimLike"
Cohesion: 0.05
Nodes (38): case_service_crud_dim(), _group_dims_by_key(), Assign a deterministic occurrence value to a Dim. The occurrence must be…, Handle CRUD operations for Dim entities., Group Dims by (case_type_id, ref_dim_id). Each group holds all Dims sharing…, _set_dim_occurrence(), BaseDimTestCase, DimLike (+30 more)

### Community 36 - "Role"
Cohesion: 0.05
Nodes (45): Role, CommonRoleGenerator, RoleGenerator, _make_cmd(), _make_user(), scenario_ids, User, Build a UserCrudCommand bypassing field validation. (+37 more)

### Community 37 - "server.py"
Cohesion: 0.05
Nodes (58): delete, BadRequest400HTTPException, Forbidden403HTTPException, ForeignKeyConstraint409HTTPException, InternalServerError500HTTPException, MethodNotAllowed405HTTPException, NotImplemented501HTTPException, ResourceConflict409HTTPException (+50 more)

### Community 38 - "Model"
Cohesion: 0.06
Nodes (39): Hashable, Get the object IDs, either from the obj_ids field or from the objs field. In…, Get the ID of the model instance. If the ID is not set and raise_on_missing is…, Any, datetime, Hashable, Model, Initialise the repository. extra_data controls behaviour when db contains… (+31 more)

### Community 39 - "_crud_cascade_delete"
Cohesion: 0.05
Nodes (84): CaseTypeSetCrudCommand, CaseTypeSetMemberCrudCommand, ColCrudCommand, ColSetMemberCrudCommand, Manage case-type columns: datatype, vocab/region bindings, and genetic-distance…, Manage which columns belong to a column set used in policies or UI presets., Manage sets of related CaseTypes reused in access policies and presets., Manage which CaseTypes belong to a case-type set. (+76 more)

### Community 40 - "case_service_create_file_for_read_set_or_seq"
Cohesion: 0.04
Nodes (49): CreateFileForReadSetCommand, CreateFileForSeqCommand, Upload a raw reads file (e.g., FASTQ) for a case's read-set column and return…, Upload an assembled sequence file (e.g., FASTA) for a case's sequence column…, case_service_create_file_for_read_set_or_seq(), _create_file(), _get_cases_for_create_file_for_read_sets_or_seqs(), _get_hash_uuid() (+41 more)

### Community 41 - ".create_parent_for_upload"
Cohesion: 0.07
Nodes (37): Parent, ParentUploadResult, Test scenarios related to field mutability for existing objects., Test 5.1.1: Always mutable single value field - should be updated., Test 5.1.2: Always mutable list field - should be updated., Test 5.1.3.1: Dict field - add new key with non-None value., Test 5.1.3.2: Dict field - new key with None value should not be added., Test 5.1.3.3: Dict field - update existing key with new value. (+29 more)

### Community 42 - "TestTokenStore"
Cohesion: 0.03
Nodes (37): Test cases for the TokenStore class., Set up test fixtures before each test method., Test TokenStore initialization., Test storing a basic token., Test storing a token with refresh token creates mapping., Test storing a token without refresh token., Test storing multiple tokens., Test retrieving an existing valid token. (+29 more)

### Community 43 - "casedb CASE Detailed ERD"
Cohesion: 0.06
Nodes (71): Case entity, CaseDataCollectionLink entity, CaseIdentifier entity, CaseSet entity, CaseSetCategory entity, CaseSetDataCollectionLink entity, CaseSetMember entity, CaseSetStatus entity (+63 more)

### Community 44 - "TestCreate"
Cohesion: 0.07
Nodes (4): Env, scenario_ids, skipif, TestCreate

### Community 45 - "Any"
Cohesion: 0.07
Nodes (39): BaseSAMapper, BaseUnitOfWork, Filter, Any, CrudOperation, Model, Read a projection of specific fields, optionally filtered., Split a filter into a SQL where-clause part and a Python remainder. (+31 more)

### Community 46 - "test_filter_base_filter.py"
Cohesion: 0.04
Nodes (31): TypedFilter, AlwaysTrueFilter, BaseFilterTestCase, CompositeFilter, EqualsFilter, Any, BaseModel, scenario_ids (+23 more)

### Community 47 - "composite.py"
Cohesion: 0.10
Nodes (37): # TODO: Add a specific exception for NotImplementedError, # TODO: distinguish between soft and hard delete through hard_delete:, Model, Check existence of multiple IDs using a query-by-IDs endpoint., # TODO: improve performance by not using filter.match_row for nested composite…, TypedCompositeFilter, TypedDateRangeFilter, ComparisonOperator (+29 more)

### Community 48 - "Domain"
Cohesion: 0.07
Nodes (9): Domain, Command, CrudCommand, Hashable, Model, RAISE, Get permissions for all the commands in the domain., For all registered CRUD commands, return a dict where the key is the model… (+1 more)

### Community 49 - "DictRepository"
Cohesion: 0.09
Nodes (58): DictRepository, Load a DictRepository from a zip archive containing per-entity JSON files., Repository that stores models in an in-memory dict, keyed by model class., Return a no-op unit-of-work suitable for the in-memory backend., Return (where_filter, None) — the full filter applies in-memory., Instantiate a DictRepository, optionally loading data from a pkl/zip file., Load a DictRepository from a pickle file (plain or gzip-compressed)., DictUnitOfWork (+50 more)

### Community 50 - "BaseSeqService"
Cohesion: 0.03
Nodes (92): Retrieve sample IDs based on a query. These IDs can then be used to retrieve…, Retrieve all data for a list of sample IDs, as a list of FullSample objects in…, Retrieve the last modified datetime of any SeqDistance for a particular…, RetrieveSamplesByIdCommand, RetrieveSamplesByQueryCommand, RetrieveSeqDistanceLastModifiedCommand, SampleCrudCommand, TaxonCrudCommand (+84 more)

### Community 51 - "casedb/domain/model/__init__.py"
Cohesion: 0.09
Nodes (54): Case, CaseDataCollectionLink, CaseIdentifier, CaseSet, CaseSetDataCollectionLink, CaseSetMember, field_serializer, Model (+46 more)

### Community 52 - "commondb/domain/literal.py"
Cohesion: 0.06
Nodes (46): # TODO: consider full and partial ISO 8601 pattern, The result of uploading a batch of cases., SampleBatchUploadResult, # TODO: 3034 this may have to be updated to allow specifying the protocol…, _handle_locus_allele_pair_mismatch(), Any, UUID, Verify and complete reference data for allele profiles. (+38 more)

### Community 53 - "omopdb/domain/model/__init__.py"
Cohesion: 0.10
Nodes (70): BaseIdentifier, Base class for an identifier generated outside of the system by a particular…, ConditionOccurrence, ConditionOccurrenceIdentifier, Death, DeathIdentifier, DeviceExposure, DeviceExposureIdentifier (+62 more)

### Community 54 - "omopdb/repositories/sa_model/__init__.py"
Cohesion: 0.14
Nodes (64): NoIdRowMetadataMixin, SQLAlchemy model mixin for adding a number of standard fields, but no standard…, IdentifierMixin, DataLineageMixin, declarative_mixin, SQLAlchemy model mixin for adding a number of standard fields., CareSite, CdmSource (+56 more)

### Community 55 - "Token"
Cohesion: 0.04
Nodes (38): Any, patch, Unit tests for OAuth 2.0 Token Store This module contains comprehensive pytest…, Test scopes property with multiple scopes., Test scopes property with single scope., Test scopes property with empty scope., Test scopes property handles extra whitespace., Test has_scope returns True for existing scopes. (+30 more)

### Community 57 - "omopdb/domain/command/__init__.py"
Cohesion: 0.08
Nodes (63): CareSiteCrudCommand, CdmSourceCrudCommand, CohortCrudCommand, CohortDefinitionCrudCommand, ConceptAncestorCrudCommand, ConceptClassCrudCommand, ConceptCrudCommand, ConceptRelationshipCrudCommand (+55 more)

### Community 58 - "test_seqdb_retrieve_best.py"
Cohesion: 0.08
Nodes (38): Command, Retrieve the best Seq ID for each sample among the given sample IDs and…, Retrieve the best SeqProfile ID for each sample among the given sample IDs and…, Retrieve the best SeqClassification ID for each sample among the given sample…, RetrieveBestSeqClassificationPerSampleCommand, RetrieveBestSeqPerSampleCommand, RetrieveBestSeqProfilePerSampleCommand, _get_best_id_per_sample() (+30 more)

### Community 59 - "TransformResult"
Cohesion: 0.05
Nodes (39): Pipeline, Any, Transform with retry logic., Transform with fallback on failure., Chainable pipeline of transformers with comprehensive error handling., Add transformer to pipeline., Enable chaining with | operator., Register error handler for specific transformer. (+31 more)

### Community 60 - "commondb/api/exc.py"
Cohesion: 0.13
Nodes (24): __extract_invalid_ids(), generate_handle_exception_function(), get_logger_fmap(), _handle_auth_exception(), handle_command(), handle_exception(), _handle_invalid_ids_exception(), _handle_service_exception() (+16 more)

### Community 61 - "UuidSetFilter"
Cohesion: 0.05
Nodes (39): ClusterNode, UUID, Describes the reference data that a user has access to. This is a lightweight…, Get a filter for the allowed CaseTypeSets. Returns None if the user has full…, Get a filter for the allowed columns. Returns None if the user has full access…, Get a filter for the allowed dimensions. Returns None if the user has full…, Get a filter for the allowed reference dimensions. Returns None if the user has…, Get a filter for the allowed reference columns. Returns None if the user has… (+31 more)

### Community 62 - "StringSetFilter"
Cohesion: 0.05
Nodes (29): DateRangeFilter, ExistsFilter, Any, Hashable, NumberRangeFilter, PartialDateRangeFilter, datetime, model_validator (+21 more)

### Community 63 - "IsoTimeTransformer"
Cohesion: 0.04
Nodes (33): IsoTimeTransformer, date, Convert from QUARTER to YEAR., Convert from QUARTER to unsupported target unit., Convert from MONTH to QUARTER., Convert from MONTH to YEAR., Convert from MONTH to unsupported target unit., Convert from WEEK to YEAR using exact mode. (+25 more)

### Community 64 - "PersonBatchForUpload"
Cohesion: 0.06
Nodes (39): PersonBatchForUpload, PersonForUpload, Any, computed_field, ParentForUpload, A person, together with any relevant associated data, intended for upload., A set of persons intended for upload, together with any new reference data…, Indicates whether there are any measurements in the person set. (+31 more)

### Community 65 - "seqdb/domain/model/__init__.py"
Cohesion: 0.04
Nodes (56): Contact, DataCollection, DataCollectionSet, DataCollectionSetMember, IdentifierIssuer, Organization, OrganizationIdentifierIssuerLink, OrganizationSet (+48 more)

### Community 66 - ".create_person_for_upload"
Cohesion: 0.09
Nodes (28): ParentUploadResult, Test 8.1: Specimen without Identifiers - should succeed., Create a test PersonForUpload. A default Person is created unless person=None., Upload a batch of persons and return the upload result., Test 1.1: ID not provided or NULL_ID - person does not exist and needs to be…, Test 1.2: ID provided by batch creator (new_id); person does not exist yet -…, Test scenarios related to providing different combinations of child objects., Test 2.1: Person without any child objects. (+20 more)

### Community 67 - "commondb/repositories/sa_model/__init__.py"
Cohesion: 0.13
Nodes (37): declared_attr, Contact, ContactMixin, DataCollection, DataCollectionMixin, DataCollectionSet, DataCollectionSetMember, DataCollectionSetMemberMixin (+29 more)

### Community 68 - "TestcasedbEdgeCasesRefDataAccess"
Cohesion: 0.05
Nodes (38): Manage reusable column definitions (code/label/type) referenced by case-type…, RefColCrudCommand, EdgeCaseSpec, Declarative specification for a single ABAC edge case. Captures all relevant…, get_test_client(), Env, fixture, integration (+30 more)

### Community 69 - "test_seqdb_distance_optimization_benchmark.py"
Cohesion: 0.07
Nodes (53): _extract_protocol_info(), _extract_segments(), _filter(), _fmt_s(), generate_benchmark_charts(), get_test_client(), _grouped_bars(), _init_profile_generator() (+45 more)

### Community 70 - "CrudCommand"
Cohesion: 0.06
Nodes (34): CrudCommand, A command base class for performing a CRUD operation on a model. The command…, Whether the command is a create operation., Whether the command is a read or exists operation. Exists also requires read…, Whether the command is a read all operation., Whether the command is a read one operation., Whether the command is an update operation., Whether the command is an exists operation. (+26 more)

### Community 71 - "test_user_manager_auto_create.py"
Cohesion: 0.08
Nodes (43): claims_basic(), make_user_manager(), mock_organization_service(), mock_rbac_service(), other_org(), other_org_id(), Any, fixture (+35 more)

### Community 72 - ".create_client"
Cohesion: 0.07
Nodes (19): BaseOauthIdpClientTestCase, Any, scenario_ids, Tests for initialization and discovery configuration updates., Base test case with common fixtures and utilities for OauthIdpClient., Test decode raises ExpiredSignatureError and triggers CredentialsAuthError., Test decode raises PyJWTError and triggers CredentialsAuthError., Test decode raises RuntimeError and triggers CredentialsAuthError. (+11 more)

### Community 73 - "Policy"
Cohesion: 0.06
Nodes (35): CommandType, Command, Model, Get the mapped class for a given base class, or return the base class if no…, BaseAbacPolicy, BaseIsOrganizationAdminPolicy, BaseReadOrganizationResultsOnlyPolicy, BaseReadSelfResultsOnlyPolicy (+27 more)

### Community 74 - "IntervalToIntervalTransformer"
Cohesion: 0.06
Nodes (32): Decimal, IntervalDict, IntervalToIntervalTransformer, Hashable, NoReturn, RAISE, TypedDict, Map number to interval. (+24 more)

### Community 75 - "BaseCrudTestCase"
Cohesion: 0.06
Nodes (38): CaseSetCrudCommand, Manage case sets (list/get/create/update/delete) including type, category,…, case_service_crud_case_set(), _crud_case_set_with_abac(), _crud_case_set_without_abac(), BaseCaseService, CaseSet, UUID (+30 more)

### Community 76 - "_make_protocol"
Cohesion: 0.07
Nodes (27): ProtocolType, _create_field_description(), Helper function to create field descriptions based on protocol type…, _make_protocol(), _minimal_protocol_data(), Any, parametrize, Protocol (+19 more)

### Community 77 - "casedb/domain/enum.py"
Cohesion: 0.06
Nodes (33): CaseClassification, CaseRightSet, CaseTypeSetCategoryPurpose, ColRelation, ColTypeOrder, ColTypeSet, ConceptRelationType, ConceptSetType (+25 more)

### Community 78 - "BaseRetrieveCaseTestCase"
Cohesion: 0.10
Nodes (26): case_service_retrieve_cases_by_id(), case_service_retrieve_cases_by_query(), Case, Retrieve case IDs for a query after ABAC, set, and content filtering. The…, Retrieve cases by IDs with ABAC checks and per-case-type max limits., BaseRetrieveCaseTestCase, _FakeCaseAbacPolicy, Any (+18 more)

### Community 79 - "auth/__init__.py"
Cohesion: 0.07
Nodes (34): Retrieve the list of configured identity providers., BaseAuthService, Retrieve a list of available identity providers for authentication., GetIdentityProvidersCommand, Command, # TODO: make async, # TODO: check if this is a security risk, Claims (+26 more)

### Community 80 - "CommondbDictModelModifier"
Cohesion: 0.06
Nodes (24): CommondbDictModelModifier, datetime, Hashable, Model, DictRepository modifier for all databases that use RowMetadataMixin. Mirrors…, BaseDictModelModifier, Hashable, Model (+16 more)

### Community 81 - "define_edge_cases_reference.py"
Cohesion: 0.05
Nodes (44): _build_col_lookup(), _compute_expected_cases_op(), EdgeCaseSpecOp, Setup of edge cases for ABAC-based access to operational data Access to the…, Build (case_type, dc) → union of col codes from all matching policies., Return {case_code: sorted accessible col_codes} for this policy combination.…, Declarative specification for a single operational data access edge case.…, _compute_expected_case_type_sets() (+36 more)

### Community 82 - "CaseTypeAccessAbac"
Cohesion: 0.08
Nodes (24): CaseRight, CaseTypeAccessAbac, CaseTypeShareAbac, BaseModel, UUID, Get the dict[case_type_id, set[data_collection_ids]] combinations for which…, Get the set[case_type_id] for which there is any access or share right in at…, Get the set[case_type_id] for which there is the given right in at least one of… (+16 more)

### Community 83 - "TestCreate"
Cohesion: 0.09
Nodes (4): Env, scenario_ids, skipif, TestCreate

### Community 84 - "TestClientStore"
Cohesion: 0.04
Nodes (27): Any, patch, Test cases for the ClientStore class., Test ClientStore initialization., Test storing a client., Test storing multiple clients., Test that storing a client with same ID overwrites the previous one., Test retrieving an existing active client. (+19 more)

### Community 85 - "CasedbRemoteApp"
Cohesion: 0.09
Nodes (23): CasedbRemoteApp, Any, CaseSet, CaseTypeSetMember, ColSetMember, Etiology, UUID, Remote app client for the casedb service. (+15 more)

### Community 86 - "SeqProfile"
Cohesion: 0.07
Nodes (27): Any, field_serializer, Model, model_validator, ndarray, QualityMixin, Self, UUID (+19 more)

### Community 87 - ".create_command_and_result_for_samples"
Cohesion: 0.13
Nodes (23): Verify SeqProfile specific rules: 1. Replace protocol code by ID when only code…, _verify_children_seq_profiles(), Any, When sample is new, existing-profile checks are skipped., No existing rows means the profile is left untouched., Fallback without seq_id should emit 6b2f8e10., Mismatch with seq_id should emit c4d8a2f7., locus_allele_id_map profile (content_hash=NULL_ID) with seq_id set does not… (+15 more)

### Community 88 - "seqdb/repositories/sa_model/__init__.py"
Cohesion: 0.18
Nodes (44): ContentMixin, ContentMixin, QualityMixin, SQLAlchemy model mixin for adding content-related fields to a model., SQLAlchemy model mixin for adding a number of standard fields., SeqMixin, AstMeasurement, AstPrediction (+36 more)

### Community 89 - "SeqSARepository"
Cohesion: 0.07
Nodes (25): BaseSeqRepository, AbstractSet, Any, datetime, SeqDistance, SeqProfile, UUID, Return profiles that have no SeqDistance record for distance_protocol_id.… (+17 more)

### Community 90 - "CaseValidator"
Cohesion: 0.09
Nodes (21): CaseDataIssue, CaseValidator, BaseCaseService, Concept, NoReturn, Organization, RefCol, Region (+13 more)

### Community 91 - "BaseBatchForUpload"
Cohesion: 0.06
Nodes (29): Get the batch for upload from the command., Get the number of parents in the batch for upload., BaseBatchForUpload, ParentForUpload, Any, field_serializer, field_validator, Model (+21 more)

### Community 92 - "BaseService"
Cohesion: 0.08
Nodes (18): Link, BaseModel, Represents a link between entities. Attributes ---------- link_field_name : str…, Return a unit of work for this repository., BaseService, Any, App, CrudCommand (+10 more)

### Community 93 - "test_casedb_crud_common.py"
Cohesion: 0.07
Nodes (21): EqualsStringFilter, EqualsFilter, DataCmd, DummyCmd, DummyEntity, DummyLink, MetaCmd, NoAbacCmd (+13 more)

### Community 94 - "test_commondb_upload.py"
Cohesion: 0.07
Nodes (35): Child1, Child1ForUpload, Child1UploadResult, Child2, Child2ForUpload, Child2Identifier, ParentBatchForUpload, ParentBatchUploader (+27 more)

### Community 95 - "make_assoc"
Cohesion: 0.07
Nodes (23): AssocModel, BaseRepositoryTestCase, DummyRepository, make_assoc(), Any, Hashable, Model, parametrize (+15 more)

### Community 96 - "OauthIdpClient"
Cohesion: 0.08
Nodes (13): OauthIdpClient, Any, Logger, Request, Response, SSLContext, UUID, Update the OIDC configuration from the discovery URL or, if provided, the… (+5 more)

### Community 97 - "validate_int_for_uuid_field"
Cohesion: 0.11
Nodes (15): Validate that the input value is either a UUID or an integer that can be…, validate_int_for_uuid_field(), Any, field_validator, UUID, Truncate too long values with an ellipsis, as the database field is limited to…, Any, field_validator (+7 more)

### Community 98 - "test_get_full_persons_by_person_ids.py"
Cohesion: 0.08
Nodes (27): BaseOmopRepository, datetime, UUID, Retrieve a list of person IDs for Persons, including their linked data,…, Retrieve all relevant data for the specified person_ids, and construct…, Return a map of cohort_id → list[specimen_id] by joining Cohort (filtered by…, OmopDictRepository, datetime (+19 more)

### Community 99 - "BaseAbacTestCase"
Cohesion: 0.07
Nodes (27): BaseAbacTestCase, OrgPolicyDumpStub, Any, scenario_ids, UUID, Create a command-like object with a .user containing an id., Create a user-like object for get_case_abac cached reads., Create a command-like object for update_user_own_organization. (+19 more)

### Community 100 - "Person"
Cohesion: 0.15
Nodes (27): CareSite, ConditionOccurrence, ConditionOccurrenceIdentifier, DeviceExposure, DrugExposure, Location, CareSite (omopdb.md), ConditionOccurrence (omopdb.md) (+19 more)

### Community 101 - "CaseTypeCrudCommand"
Cohesion: 0.12
Nodes (20): CaseTypeCrudCommand, Manage CaseTypes—the structural and default definitions cases must follow., case_service_crud_case_type(), _crud_case_type_with_abac(), _crud_case_type_without_abac(), BaseCaseService, CaseType, UUID (+12 more)

### Community 102 - "CaseAbac"
Cohesion: 0.13
Nodes (4): CaseAbac, UUID, This test expects is_allowed to return False because the access map does not…, TestCaseAbac

### Community 103 - "omop/ontology.py"
Cohesion: 0.08
Nodes (29): Health economics domain - OMOP CDM v6.0 health economics tables. This module…, Metadata domain - OMOP CDM v6.0 metadata tables. This module contains classes…, Concept, ConceptAncestor, ConceptClass, ConceptRelationship, ConceptSynonym, Domain (+21 more)

### Community 104 - "Entity"
Cohesion: 0.07
Nodes (22): Entity, Get the field names of the entity. Parameters ---------- by_alias : bool,…, Get the ID field name of the entity. Parameters ---------- by_alias : bool,…, Get the link field names of the entity. Parameters ---------- by_alias : bool,…, Get the relationship field names of the entity. Parameters ---------- by_alias…, Get the value field names of the entity. Parameters ---------- by_alias : bool,…, Check if the entity has keys. Returns ------- bool True if the entity has keys,…, Check if the entity has links. Returns ------- bool True if the entity has… (+14 more)

### Community 105 - "create_client"
Cohesion: 0.10
Nodes (19): assert_logged_with_code(), create_client(), DummyLogItem, DummyRequest, make_request(), Any, parametrize, scenario_ids (+11 more)

### Community 106 - "seqdb_test_client.py"
Cohesion: 0.10
Nodes (30): TempPathFactory, fixture, Integration test for SeqSARepository.update_some_seq_distance_content. Verifies…, generate_scale_test_db(), ndarray, Single locus-set / protocol with n_existing pre-seeded profiles. All profiles…, get_test_client(), fixture (+22 more)

### Community 107 - "Hashable"
Cohesion: 0.09
Nodes (15): DictAdapter, PolarsAdapter, Any, BaseModel, Hashable, Protocol, PydanticAdapter, Factory method to create appropriate adapter for object type. (+7 more)

### Community 108 - "ImportGraphAnalyzer"
Cohesion: 0.07
Nodes (30): Import, ImportFrom, analyze_imports(), ImportEdge, ImportGraphAnalyzer, ImportStatementVisitor, ModuleNode, Path (+22 more)

### Community 109 - "AuthTestClient"
Cohesion: 0.08
Nodes (17): AuthTestClient, MockJWKAndToken, get_test_client(), fixture, parametrize, patch, scenario_ids, Test the OidcClient retrieve_jwt_with_client_credentials_flow method. (+9 more)

### Community 110 - "TypedDatetimeRangeFilter"
Cohesion: 0.11
Nodes (21): BaseCaseService, CaseStats, Retrieve statistics for a set of CaseTypes. Each of the parameters, when…, Retrieve statistics for a set of CaseSets. Each of the parameters, when…, RetrieveCaseSetStatsCommand, RetrieveCaseTypeStatsCommand, Retrieve case statistics., case_service_retrieve_case_stats() (+13 more)

### Community 111 - "retrieve_case.py"
Cohesion: 0.09
Nodes (35): CompositeFilter, Retrieve all (case_id, cohort_ids) pairs for a given CaseType. Returns every…, RetrieveCaseCohortLinksByCaseTypeCommand, Retrieve all CaseCohortLinks for a CaseType., case_service_retrieve_case_cohort_links_by_case_type(), _get_map_function_for_col(), _get_map_functions_for_filters(), _get_valid_concepts() (+27 more)

### Community 112 - "casedb/repositories/sa_model/__init__.py"
Cohesion: 0.17
Nodes (37): OrganizationAccessCasePolicy, OrganizationShareCasePolicy, Base, RowMetadataMixin, UserAccessCasePolicy, UserShareCasePolicy, Case, CaseDataCollectionLink (+29 more)

### Community 113 - "case_validator.py"
Cohesion: 0.08
Nodes (27): # TODO: transform any other col_types, # TODO: replace by pre-calculated interval_relation_map for efficiency, IntervalTransformStrategy, Enum, Enum for different types of transformation results., TimeUnit, TimeUnitTransformStrategy, TransformResultType (+19 more)

### Community 114 - "BaseIsOwnCasesTestCase"
Cohesion: 0.10
Nodes (23): BaseIsOwnCasesTestCase, _FakeCaseAbacPolicy, Any, Case, Command, scenario_ids, UUID, Create a Case for tests, defaulting to the common data collection. (+15 more)

### Community 115 - "sa_model/util.py"
Cohesion: 0.07
Nodes (35): OrganizationAdminPolicy, OrganizationAdminPolicyMixin, Base, declarative_mixin, RowMetadataMixin, SQLAlchemy model mixin for derived domain models whose SQLAlchemy models are…, SQLAlchemy model for the corresponding persistable domain model., declarative_mixin (+27 more)

### Community 116 - "api/seq.py"
Cohesion: 0.11
Nodes (27): CreateFileRequestBody, PydanticBaseModel, CalculatePhylogeneticTreeRequestBody, create_seq_endpoints(), Any, APIRouter, App, Exception (+19 more)

### Community 117 - "Concept"
Cohesion: 0.05
Nodes (40): ConceptClass, ConceptSynonym, FactRelationship, ConceptClass (omopdb.md), ConceptSynonym (omopdb.md), EpisodeEvent (omopdb.md), FactRelationship (omopdb.md), Metadata (omopdb.md) (+32 more)

### Community 118 - "Concept (omopdb.omop / OMOP CDM entity)"
Cohesion: 0.13
Nodes (39): CareSite (omopdb.omop / OMOP CDM entity), CdmSource (omopdb.omop / OMOP CDM entity), Cohort (omopdb.omop / OMOP CDM entity), CohortDefinition (omopdb.omop / OMOP CDM entity), Concept (omopdb.omop / OMOP CDM entity), ConceptAncestor (omopdb.omop / OMOP CDM entity), ConceptClass (omopdb.omop / OMOP CDM entity), ConceptRelationship (omopdb.omop / OMOP CDM entity) (+31 more)

### Community 119 - "RoleGenerator"
Cohesion: 0.20
Nodes (9): Command, Enum, Role, Helper method to map common permissions described using the commondb role enum…, Helper method to map common role hierarchy described using the commondb role…, Get a mapping from domain role enum to role string value, whereby the domain…, Get a mapping from domain role set enum to role set string value, whereby the…, Get a mapping from domain role string value to role permissions, whereby the… (+1 more)

### Community 120 - "DomainException"
Cohesion: 0.08
Nodes (18): BaseModel, Self, Set the model class for the entity. Parameters ---------- model_class :…, Check if the entity has a model set. Returns ------- bool True if the entity…, Set the repository model class for the entity, which is intended as the class…, Set the API model class for the entity, which is intended as the request model…, Set the API model class for the entity, which is intended as the model that…, Set the CRUD command class for the entity, which is intended as the class that… (+10 more)

### Community 121 - "calculate_seq_distance.py"
Cohesion: 0.10
Nodes (37): _calculate_and_store_distances(), _calculate_distance_for_decoded_profile_pair(), _calculate_nextclade_snp_hamming_distance(), _calculate_pairwise_profile_distances(), _calculate_profile_distance(), _decode_profile(), _get_matching_seq_profile_protocol_ids(), _nextclade_hamming_from_parsed() (+29 more)

### Community 122 - "seq_service_calculate_seq_distances_for_new_profiles"
Cohesion: 0.15
Nodes (21): For each new SeqProfile find applicable SeqDistance protocols, compute…, seq_service_calculate_seq_distances_for_new_profiles(), _CrudRecorder, _make_allele_profile(), _make_crud_side_effect(), _make_seq_distance(), _make_seq_distance_protocol_for_locus_set(), Any (+13 more)

### Community 123 - "_verify_children_seq_classifications"
Cohesion: 0.13
Nodes (20): Verify SeqClassification specific rules: 1. Replace protocol code by ID when…, _verify_children_seq_classifications(), A seq_id tied to another sample should fail validation., Primary category mismatch with unknown seq should emit f2a84c91., Primary category mismatch with seq_id should emit 9d3a4f1b., Fallback key (protocol, None) resolves identical classification., Temporary SeqClassification IDs are replaced by existing DB IDs., With seq_id=NULL_ID, mismatch is treated as keyed mismatch (9d3a4f1b). (+12 more)

### Community 124 - "OIDCProvider"
Cohesion: 0.06
Nodes (22): OIDCProvider, Any, Create an OpenID Connect ID Token., Validate and decode an ID token., OpenID Connect provider implementation., Create userinfo endpoint response based on scopes., Initialize OIDC provider with JWKS manager., Create OpenID Connect discovery document. (+14 more)

### Community 125 - "._get_allele_profile_for_ids"
Cohesion: 0.09
Nodes (18): Any, SeqForUpload, Test that seqs property maintains proper structure for serialization., Test SampleForUpload without id where seqs can have their own sample_ids., Test SampleForUpload without id where seqs also have NULL_ID sample_ids., Test that samples with seqs follow proper validation rules., Create a sample SeqForUpload with default values and optional overrides., Test valid SampleForUpload with sample_id. (+10 more)

### Community 126 - "CompositeFilter"
Cohesion: 0.12
Nodes (21): case_service_read_association_with_valid_ids(), BaseCaseService, CrudCommand, Model, User, UUID, # TODO: this can be a generic service/repository method (ids should be Hashable…, cached (+13 more)

### Community 127 - "AuthService"
Cohesion: 0.06
Nodes (26): IdpClient, SSLContext, UUID, Get identity provider configuration., Extract claims from userinfo endpoint using access token., MockIDPClient, Request, UUID (+18 more)

### Community 128 - "test_casedb_case_validator.py"
Cohesion: 0.12
Nodes (19): BaseCaseValidatorTestCase, Concept, Organization, Region, scenario_ids, UUID, Unit tests for CaseValidator in casedb case transformer. The tests follow the…, Base test case with common fixtures and helpers for CaseValidator tests. (+11 more)

### Community 129 - "Any"
Cohesion: 0.06
Nodes (18): Any, Save authorization code (not used in client credentials flow)., Validate authorization code (not used in client credentials flow)., Confirm redirect URI (not used in client credentials flow)., Validate that the grant type is supported by the client., Validate bearer token and scopes., Get default redirect URI for a client., Validate redirect URI. (+10 more)

### Community 130 - ".create_case_for_upload"
Cohesion: 0.15
Nodes (9): Batch can contain cases from different DCs., Tests for ABAC column and creation-right verification in verify_abac_rights., Tests for CaseBatchForUpload.has_samples (the pure predicate on the batch…, When new case has NULL_ID and no default, should add error., When case explicitly sets created_in_data_collection_id, don't override., Existing cases should not be modified by default setting., New case with explicit DC ID should use that DC for ABAC., TestCaseBatchHasSamples (+1 more)

### Community 131 - ".create_child1_for_upload"
Cohesion: 0.09
Nodes (19): Test combinations of different scenarios., Test parent with both children and Identifiers., Test updating an existing parent with new child objects., Test complex reference data resolution across multiple children., Test Child2 with Identifiers in combination with parent relationships and other…, verify_only=True and verify_only=False must agree on batch outcome., Create a test child1 for upload., Create a test Ref1 object. (+11 more)

### Community 132 - "UploadCasesCommand"
Cohesion: 0.11
Nodes (21): Upload a batch of cases along with their associated data and return an upload…, UploadCasesCommand, CaseBatchUploadResult, The result of uploading a batch of cases., Upload cases in batch., case_service_upload_cases(), CaseBatchUploader, BaseCaseService (+13 more)

### Community 133 - "Filter"
Cohesion: 0.13
Nodes (20): _default_validate_query_filter(), Filter, Any, BaseModel, Hashable, Self, Base class for filters. Attributes: invert (bool): Whether to invert the…, Check if a row matches the filter. Args: row (dict[Hashable, Any | None]): The… (+12 more)

### Community 134 - ".create_child2_for_upload"
Cohesion: 0.12
Nodes (16): Test scenarios related to Identifiers for Child2 objects., Test 9.2.1.1: Existing Identifier with NULL child2 ID - should set child2 ID., Test 9.2.1.2.1: Existing Identifier with same child2 ID - should succeed., Test 9.2.1.2.2: Existing Identifier with different child2 ID - should fail., Test 9.2.2: New Identifier for new child2 - should succeed., Test 9.2.3.1: Multiple Identifiers, some existing for same child2 - should…, Test 9.2.3.1: Multiple Identifiers, some existing for different child2 - should…, Test 9.2.3.2: Multiple Identifiers all new but same issuer - should fail. (+8 more)

### Community 135 - "Person"
Cohesion: 0.10
Nodes (34): ConditionOccurrenceIdentifier (omopdb.md), Observation (omopdb.md), VisitOccurrence (omopdb.md), CareSite, ConditionOccurrence, ConditionOccurrenceIdentifier, DeviceExposure, DeviceExposureIdentifier (+26 more)

### Community 136 - "SeqdbTestClient"
Cohesion: 0.15
Nodes (15): FileFormat, Any, DataCollection, File, Model, Protocol, ReadSet, Sample (+7 more)

### Community 137 - "IdentifierForUpload"
Cohesion: 0.09
Nodes (21): IdentifierForUpload, An external identifier, defined as the combination of (identifier issuer,…, Check equality based on identifier_issuer_id, identifier_issuer_code, and…, SpecimenIdentifier, Test scenarios related to Identifiers for Specimen objects., Test 8.2.1.1: Existing Identifier with NULL specimen ID - should set specimen…, Test 8.2.1.2.1: Existing Identifier with same specimen ID - should succeed., Test 8.2.1.2.2: Existing Identifier with different specimen ID - should fail. (+13 more)

### Community 138 - ".create_crud_cmd"
Cohesion: 0.11
Nodes (17): BasePolicyTestCase, CrudCommand, Model, OrganizationAdminPolicy, scenario_ids, User, UUID, Create a user with optional roles and organization. (+9 more)

### Community 139 - "sa/util.py"
Cohesion: 0.12
Nodes (29): compiles, ComputedFieldInfo, get_mixin_mapped_column(), Any, Mapped, TypeEngine, Helper function to create a mapped column for a field in a model mixin class,…, get_type_from_annotation() (+21 more)

### Community 140 - "RBACTestClient"
Cohesion: 0.10
Nodes (16): ServiceUser, get_test_client(), Any, BaseRbacService, CrudCommand, Enum, fixture, Hashable (+8 more)

### Community 141 - "BaseAnonymizer"
Cohesion: 0.09
Nodes (20): Collection, BaseAnonymizer, ModelAnonymizer, ABC, Any, date, Domain, Model (+12 more)

### Community 142 - "Command"
Cohesion: 0.10
Nodes (19): Command, field_validator, UUID, Retrieve cases by their IDs., Retrieve access rights for a set of cases., RetrieveCaseRightsCommand, RetrieveCasesByIdCommand, RetrieveCaseSetRightsCommand (+11 more)

### Community 143 - "SeqdbEndpointTestClient"
Cohesion: 0.08
Nodes (22): field_validator, UUID, Retrieve only the SampleIdentifier records for a list of sample IDs. Lighter…, RetrieveSampleIdentifiersByIdCommand, SampleIdentifierCrudCommand, SampleIdentifier, Retrieve only sample identifiers for the given sample IDs., Handle CRUD operations for SampleIdentifier entities. (+14 more)

### Community 144 - ".create_seq_for_upload"
Cohesion: 0.15
Nodes (17): Verify Seq specific rules: 1. Replace protocol code by ID when only code is…, _verify_children_seqs(), SeqForUpload, Helper to create a SeqForUpload with default or specified properties., A non-ASSEMBLY protocol for Seq should be flagged with code a4c9e18b., Test the _verify_children_seqs function., When sample is new, seq conflict checks are skipped., No matching seq rows means function leaves the seq untouched. (+9 more)

### Community 145 - ".create_sample_for_upload"
Cohesion: 0.10
Nodes (18): Verify and complete reference data., _verify_sample_refdata(), SeqTaxonomy, Test the _verify_batch_sample_refdata function., Test that _verify_batch_sample_refdata succeeds with empty samples., Test successful verification when no allele profiles are provided., Test that _verify_refdata fails when new alleles are missing from batch., Helper to create a SampleForUpload with default or specified properties. (+10 more)

### Community 146 - "validate_int_enum_value"
Cohesion: 0.08
Nodes (17): FormatType, IntEnum, Validate that the given value is a valid member of the given IntEnum class., Validate that the given value is a valid member of the given IntEnum class or…, validate_int_enum_value(), validate_int_enum_value_or_none(), SeqDistanceType, field_validator (+9 more)

### Community 147 - "Seq"
Cohesion: 0.12
Nodes (12): Contig, computed_field, field_serializer, field_validator, Model, model_validator, QualityMixin, Self (+4 more)

### Community 148 - "InMemoryOrganizationRepository"
Cohesion: 0.08
Nodes (19): NoResultsError, InMemoryOrganizationRepository, make_commondb_user_manager(), make_idps_cfg(), make_mock_organization_service(), make_mock_rbac_service(), make_root_cfg(), Any (+11 more)

### Community 149 - "make_cdb_user"
Cohesion: 0.11
Nodes (11): get_name_from_claims(), Any, Get the name from the claims, checking against a list of possible name claims., make_cdb_user(), Pure unit tests for claim name-extraction helpers and update_user_name., Verify the real UserManager writes the name change to the repo., Verify the root-token time-to-live enforcement. A *very* short TTL (1 second)…, Build an AuthEnv with a pre-stored root user. (+3 more)

### Community 150 - "test_omopdb_upload.py"
Cohesion: 0.10
Nodes (19): Upload a batch of persons along with their associated data. The data are…, UploadPersonsCommand, PersonBatchUploadResult, The result of uploading a batch of persons., Upload persons in batch., PersonValidator, BaseOmopService, UUID (+11 more)

### Community 151 - "TestUpdate"
Cohesion: 0.15
Nodes (4): Env, scenario_ids, skipif, TestUpdate

### Community 152 - "TestModelBaseSeq"
Cohesion: 0.08
Nodes (17): UUID, Test cases for BaseSeq model validation and functionality., Return a valid DNA sequence for testing., Return an invalid DNA sequence for testing., Compute the expected sequence hash for a given sequence., Test creating BaseSeq with valid DNA sequence., Test that DNA sequences are normalized to lowercase., Test that length is automatically calculated when set to 0. (+9 more)

### Community 153 - "CaseSet"
Cohesion: 0.08
Nodes (30): Case, Case, CaseAccessAbac, CaseRights, CaseSet, CaseSetAccessAbac, CaseSetForUpload, CaseSetRights (+22 more)

### Community 154 - "Organization"
Cohesion: 0.11
Nodes (30): Organization (doc), Organization Set (doc), User (doc), User Invitation (doc), Organization, Organization Identifier Issuer Link, IdentifierIssuer, Organization (+22 more)

### Community 155 - "test_seqdb_calculate_seq_distance.py"
Cohesion: 0.13
Nodes (21): InvalidArgumentsError, BaseCalculateSeqDistanceTestCase, _iterable(), _make_mlva_profile(), _make_nextclade_content(), _make_seq_distance_protocol_for_snp(), _make_snp_profile_for_upload(), ndarray (+13 more)

### Community 156 - "BaseRepository"
Cohesion: 0.15
Nodes (11): BaseRepository, Any, Hashable, Model, Update association objects of the given model class that represent an…, Factory method to create a repository instance with the given parameters., Remove all contents of the repository., Verify that the given object ids are valid for the given model class, which… (+3 more)

### Community 157 - "TokenIntrospectionManager"
Cohesion: 0.12
Nodes (11): Any, Logger, SSLContext, TokenIntrospectionManager, DummyResponse, make_dummy_client(), Any, MonkeyPatch (+3 more)

### Community 158 - "FileCompression"
Cohesion: 0.11
Nodes (18): FileCompression, field_serializer, BaseFileService, File, UUID, Create a new file and return its unique identifier., Perform CRUD operations on files based on the command., FileService (+10 more)

### Community 159 - "BaseSimilarCasesTestCase"
Cohesion: 0.14
Nodes (15): BaseSimilarCasesTestCase, Case, Col, GeneticDistanceProtocol, RefCol, scenario_ids, UUID, Set the tuple return value of _retrieve_cases_with_content_right. (+7 more)

### Community 160 - "test_update_user_policy.py"
Cohesion: 0.27
Nodes (14): _make_abac_service(), _make_invite_cmd(), _make_policy(), _make_role_set_map(), _make_update_cmd(), _make_user(), scenario_ids, User (+6 more)

### Community 161 - "api/case.py"
Cohesion: 0.08
Nodes (47): CaseTypeSetCaseTypeUpdateAssociationRequestBody, ColSetColUpdateAssociationRequestBody, create_case_endpoints(), CreateCaseSetRequestBody, CreateFileForReadSetRequestBody, CreateFileForSeqRequestBody, Any, APIRouter (+39 more)

### Community 162 - "case_service_crud_ref_col"
Cohesion: 0.11
Nodes (17): case_service_crud_ref_col(), BaseCaseService, RefCol, UUID, Handle CRUD operations for RefCol entities., BaseRefColTestCase, parametrize, RefCol (+9 more)

### Community 163 - "test_casedb_custom.py"
Cohesion: 0.26
Nodes (9): get_test_client(), Env, fixture, skip, User, UUID, # TODO: move to test_build_db, # TODO: add to test_build_db (+1 more)

### Community 164 - "test_fastapp_rbac_service.py"
Cohesion: 0.26
Nodes (17): Model1_1CrudCommand, Model1_2CrudCommand, Model2_1CrudCommand, Model2_2CrudCommand, CrudCommand, Enum, ServiceType, TestType (+9 more)

### Community 165 - "TestModelSeq"
Cohesion: 0.09
Nodes (16): Seq, Test cases for Seq model functionality and inheritance., Create a valid Contig for testing., Create a sample Seq with default values and optional overrides., Test creating Seq with contigs., Test creating Seq without contigs (not available)., Test that Seq inherits HasSampleMixin properties., Test that Seq inherits CodeMixin properties. (+8 more)

### Community 166 - ".__init__"
Cohesion: 0.10
Nodes (18): AbacService, Any, Command, Domain, Dynaconf, Enum, Logger, Model (+10 more)

### Community 167 - ".__init__"
Cohesion: 0.18
Nodes (12): AuthException, ConcurrentModificationError, CredentialsAuthError, FeatureDisabledServiceError, InvalidIdsError, Any, RequestLimitExceededAuthError, ServiceException (+4 more)

### Community 168 - "Model"
Cohesion: 0.12
Nodes (14): Any, Hashable, Model, Get row ID from row object or row class., Dump model object to SQLAlchemy row object., Update row with model object values., Load model object from SQLAlchemy row., Get the schema name from the row class __table_args__. (+6 more)

### Community 169 - "test_casedb_upload.py"
Cohesion: 0.13
Nodes (23): BaseUploadTestCase, _mock_uow(), scenario_ids, Unit tests for casedb case upload functionality., Tests for existing case data collection handling, including NULL_ID edge case.…, Map commondb role enums to casedb role strings with CASEDB_ prefix., Base test case with common fixtures and utility methods., LSP-3647 regression: CaseBatchUploader.upsert_batch merges incoming content… (+15 more)

### Community 170 - "AuthEnv"
Cohesion: 0.12
Nodes (8): AuthEnv, scenario_ids, Self-contained, per-test auth environment built around the real…, Verify that unknown users are auto-created when the flag is on, and rejected…, Verify that a root user can log in for the first time (triggering…, Drive get_existing_user_from_claims directly (no HTTP stack)., TestAutoCreateUser, TestRootUserLogin

### Community 171 - "TestModelSampleBatchForUpload"
Cohesion: 0.08
Nodes (14): Create a SampleForUpload with specified number of SeqForUpload instances., Test reading sample_batch_for_upload1.json as SampleBatchForUpload model., Test reading sample_batch_for_upload2.json as SampleBatchForUpload model., Test valid SampleBatchForUpload with minimal data., Test valid SampleBatchForUpload with alleles., Test valid SampleBatchForUpload with multiple samples including seqs., Test valid SampleBatchForUpload with empty samples list., Test SampleBatchForUpload where all samples contain SeqForUpload instances. (+6 more)

### Community 172 - "TestModelSeqForUpload"
Cohesion: 0.07
Nodes (15): Test cases for SeqForUpload model functionality and upload-specific features., Test creating SeqForUpload with basic fields., Test that SeqForUpload inherits all Seq properties., Test SeqForUpload with NULL_ID for sample_id., Test that sample_id serialization handles NULL_ID correctly., Test upload-specific field handling., Test JSON serialization structure of SeqForUpload., Test that quality fields are properly inherited. (+7 more)

### Community 173 - "OAuth2Client"
Cohesion: 0.10
Nodes (16): demo_client_credentials_flow(), OAuth2Client, Any, OAuth 2.0 Client Test Script This script demonstrates how to use the OAuth 2.0…, Create a new OAuth client., Delete an OAuth client., List all OAuth clients., Simple OAuth 2.0 client for testing. (+8 more)

### Community 174 - "Protocol (seqdb entity)"
Cohesion: 0.13
Nodes (27): AstMeasurement (seqdb entity), AstPrediction (seqdb entity), File (seqdb entity), IdentifierIssuer (seqdb entity), LocusSet (seqdb entity), OrganizationIdentifierIssuerLink (seqdb entity), PcrMeasurement (seqdb entity), Protocol (seqdb entity) (+19 more)

### Community 175 - "ReadUserPolicy"
Cohesion: 0.13
Nodes (14): Any, BaseAbacService, Command, User, UUID, ReadUserPolicy, Any, BaseAbacService (+6 more)

### Community 176 - "EndpointTestClient"
Cohesion: 0.17
Nodes (10): EndpointTestClient, Any, Command, CrudCommand, Response, CasedbEndpointTestClient, Any, App (+2 more)

### Community 177 - "TestRegistrationAndLookups"
Cohesion: 0.07
Nodes (5): scenario_ids, Test topological sorting behavior with on_cycle parameter., TestDAGAndCycleBehavior, TestRegistrationAndLookups, TestStaticUtilities

### Community 178 - "_DummyMapper"
Cohesion: 0.13
Nodes (9): BaseMapperTestCase, _DummyMapper, _make_row_class(), _Model, Any, Hashable, Base fixtures and helpers for mapper tests., _RowBase (+1 more)

### Community 179 - "BasePersonUploadTestCase"
Cohesion: 0.10
Nodes (19): BasePersonUploadTestCase, scenario_ids, Base test case with common fixtures and utilities for person upload tests., Set up test fixtures., Create a test UploadPersonsCommand., Test scenarios related to person existence in repository., Test scenarios related to person_id links in child objects., Test scenarios related to field mutability for existing Person objects. (+11 more)

### Community 180 - "CaseType"
Cohesion: 0.09
Nodes (26): CaseQuery, CaseQueryResult, CaseSetQuery, CaseType, CaseTypeAccessAbac, CaseTypeCategory, CaseTypeCol, CaseTypeSet (+18 more)

### Community 181 - "Protocol"
Cohesion: 0.14
Nodes (26): Identifier Issuer, File, AstMeasurement, AstPrediction, LocusSet, PcrMeasurement, Protocol, ProtocolSet (+18 more)

### Community 182 - "Any"
Cohesion: 0.11
Nodes (10): DimType, TreeAlgorithmType, CaseTypeProps, Any, BaseModel, field_serializer, field_validator, Ensure that the code is always a string. (+2 more)

### Community 183 - "ParentUploadResult"
Cohesion: 0.15
Nodes (9): ParentUploadResult, Represents the upload result for a Parent model upload. This class must be…, Count the number of occurrences of each EtlStatus in this result (if…, Mark this result, and each of its own children, as FAILED if any nested child…, Update the upload status of this result based on the data issues found, adding…, Convert all occurrences of from_status to to_status in this result and all its…, Get the list of field names in this result class that contain lists of child…, Get the list of parent upload results in this batch upload result. (+1 more)

### Community 184 - "DummyIdpClient"
Cohesion: 0.09
Nodes (13): Request, Extract claims from JWT token., Returns the claims of the user from the request or None if claims cannot be…, DummyIdpClient, Any, Request, scenario_ids, Unit tests for IdpClient base class. Follows the reference test style for… (+5 more)

### Community 185 - "SeqProfileForUpload"
Cohesion: 0.11
Nodes (17): Generate and return the MLVA profile in ORDERED_REPEAT_NUMBERS format based on…, model_validator, ReadSet, Self, Seq, SeqClassification, SeqProfile, A sequence profile record intended for upload. Equal to a SeqProfile, with… (+9 more)

### Community 186 - "set_service_repository"
Cohesion: 0.19
Nodes (14): _build_snp_upload_command(), _build_upload_command(), Any, Env, parametrize, RepositoryType, UUID, Given a created dict dataset, build a UploadSamplesCommand. db_index selects… (+6 more)

### Community 187 - "Gen-EpiX README"
Cohesion: 0.11
Nodes (25): pr.sh Helper Script, PR Skill, CASEDB Service, COMMONDB Service, FASTAPP Shared Framework, lsp-data Repository, OMOPDB Service, SEQDB Service (+17 more)

### Community 188 - "case_date.py"
Cohesion: 0.17
Nodes (19): case_service_calculate_case_date(), case_service_get_case_date_col_mappers(), case_service_get_case_date_col_mappers_from_cols(), convert_iso_date_to_datetime(), convert_iso_month_to_first_day_datetime(), convert_iso_quarter_to_first_day_datetime(), convert_iso_week_to_first_day_datetime(), convert_iso_year_to_first_day_datetime() (+11 more)

### Community 189 - "CommondbRemoteApp"
Cohesion: 0.24
Nodes (7): CommondbRemoteApp, Remote app client for the commondb service with OAuth2/NONE authentication., _mock_response(), Any, fixture, Test the hand-written (non-CRUD) command handlers., TestNonCrudHandlers

### Community 190 - "SAMapper"
Cohesion: 0.11
Nodes (11): Standard SAMapper implementation that provides default mapping logic between…, The order of field names is guaranteed to be the same as the order of the row…, The order of field names is guaranteed to be the same as the order of the model…, Initialize field name mappings between model and row classes. Validates that…, Retrieve and validate field names for service metadata, db metadata, and actual…, Check that the provided field names are valid. If field names is None, return…, Initialize relationship field name mappings between model and row classes.…, Initialize functions to extract the primary key values from model and row… (+3 more)

### Community 191 - "derived.py"
Cohesion: 0.15
Nodes (20): Cohort, CohortDefinition, ConditionEra, DoseEra, DrugEra, Episode, EpisodeEvent, Any (+12 more)

### Community 192 - "test_omopdb_model.py"
Cohesion: 0.36
Nodes (9): common_data(), Encoder, location_data(), measurement_data(), observation_data(), person_data(), Any, fixture (+1 more)

### Community 193 - "TestDelete"
Cohesion: 0.17
Nodes (4): Env, scenario_ids, skipif, TestDelete

### Community 194 - "BaseUploadTestCase"
Cohesion: 0.17
Nodes (12): BaseUploadTestCase, scenario_ids, Base test case with common fixtures and utilities., Set up test fixtures., Test upload with varying batch sizes., Test 8.1: Upload batch of n new parent objects., Test 8.2: Upload parent with varying number of Child1 objects., Test scenarios related to object existence in repository. (+4 more)

### Community 195 - "TestNumpyAlleleIntegration"
Cohesion: 0.10
Nodes (15): _make_user(), _mock_uow(), fixture, parametrize, Protocol, User, Unit tests for all new numpy ALLELE distance code paths (LSP-3529)., Run _calculate_and_store_distances directly for ALLELE profiles. Returns… (+7 more)

### Community 196 - "IdentifierIssuer"
Cohesion: 0.08
Nodes (24): Death, DeathIdentifier, DeviceExposureIdentifier, DrugExposureIdentifier, IdentifierIssuer, Death (omopdb.md), DeathIdentifier (omopdb.md), DeviceExposureIdentifier (omopdb.md) (+16 more)

### Community 197 - "DatetimeRangeFilter"
Cohesion: 0.15
Nodes (15): field_serializer, Serialize dim-type keys and col-type sets to plain string dicts., ColType, CaseStats, model_validator, Self, BaseCaseRepository, datetime (+7 more)

### Community 198 - "ModelNoId"
Cohesion: 0.11
Nodes (10): ModelNoId, UUID, Model, scenario_ids, Unit tests for ModelNoId.set_modified and ModelNoId.set_created. Test coverage:…, # TODO: check scenario ids, how are they determined?, TestSetCreated, TestSetModified (+2 more)

### Community 199 - "TestCreate"
Cohesion: 0.17
Nodes (4): Env, scenario_ids, skipif, TestCreate

### Community 200 - "BaseCommondbRemoteAppTestCase"
Cohesion: 0.09
Nodes (16): BaseCommondbRemoteAppTestCase, DerivedRemoteApp, scenario_ids, Minimal subclass of CommondbRemoteApp for testing timeout configuration., Test create_local_or_remote_app class method., Raise error for invalid app_setup_type., app_setup_type is case-insensitive., Test HTTP timeout configuration per command class. (+8 more)

### Community 201 - "generate_seq_distances.py"
Cohesion: 0.18
Nodes (22): create_seq_distance_database(), get_allele_profile_ids(), get_allele_profiles(), get_data_collection(), get_locus_detection_protocol(), get_locus_set(), get_random_sequences(), get_sample() (+14 more)

### Community 202 - "Case Type"
Cohesion: 0.10
Nodes (23): ColSet, Disease, Etiology, ColSet (doc), ColSetMember (doc), Case Type, Col, Col Set Member (+15 more)

### Community 203 - "BaseSeqdbService"
Cohesion: 0.09
Nodes (16): Command, Retrieve a genetic sequence by its ID., Retrieve a set of genetic sequences in FASTA format based on a set of sequence…, RetrieveGeneticSequenceByIdCommand, RetrieveGeneticSequenceFastaByIdCommand, BaseSeqdbService, PhylogeneticTree, UUID (+8 more)

### Community 204 - "LocusSet"
Cohesion: 0.11
Nodes (15): Locus, LocusCodeMap, LocusSet, computed_field, field_serializer, field_validator, Model, model_validator (+7 more)

### Community 205 - "test_seqdb_upload.py"
Cohesion: 0.11
Nodes (17): Model, Verify that protocols provided by ID or code exist, and resolve codes to IDs., _verify_protocol(), create_allele_profile_base64(), scenario_ids, Unit tests for seqdb sample upload functionality. Tests the…, # TODO: replace with actual log code rather than log message, Test that ConcurrentModificationError in distance calculation is a soft failure. (+9 more)

### Community 206 - "test_cfg_log_level.py"
Cohesion: 0.20
Nodes (16): _build_test_fixture(), _DummyHandler, _DummyLogger, _extract_diagnostic_payload(), _patch_logging_get_logger(), _patch_runtime_logger_dict(), MonkeyPatch, scenario_ids (+8 more)

### Community 207 - "SeqGenerationSettings"
Cohesion: 0.15
Nodes (7): BaseModel, computed_field, field_validator, Random, SeqGenerationSettings, scenario_ids, TestGenerateRandomSequences

### Community 208 - "Data Collection"
Cohesion: 0.15
Nodes (22): ColSet, DataCollection, Organization, OrganizationAdminPolicy, User, Case Type Set, Case Type Set Category, Col Set (+14 more)

### Community 209 - "ErmGenerator"
Cohesion: 0.11
Nodes (14): ErmGenerator, Graphviz / erdantic-based ERM diagram generator. Produces PNG Entity-…, generate_hash_for_domain_models(), Domain, Path, Generates a SHA-256 hash for a list of sorted classes by pickling them to a…, ABC, Domain (+6 more)

### Community 210 - "CaseForUpload"
Cohesion: 0.13
Nodes (15): CaseForUpload, field_serializer, Model, model_validator, ParentForUpload, Self, UUID, Validate sample ID and assembly protocol. (+7 more)

### Community 211 - "UserManager"
Cohesion: 0.19
Nodes (7): Any, BaseRbacService, BaseUserManager, User, UUID, UserManager, get_email_from_claims()

### Community 212 - "LogParser2"
Cohesion: 0.24
Nodes (4): LogParser2, A class to parse and export logsas produced directly by the application or as…, Parses the log file and sorts the user journey logs. This method reads the log…, Exports the sorted user journey logs to a CSV and a pickle file. This method…

### Community 213 - "TestCreateUserFromToken"
Cohesion: 0.20
Nodes (11): make_cdb_invitation(), make_cdb_organization(), parametrize, UserInvitation, UUID, Return a valid future-expiring UserInvitation., Verify that the commondb UserManager correctly creates a user from an…, Build an AuthEnv with a pre-stored creator (inviting) user. (+3 more)

### Community 214 - "TestInitialization"
Cohesion: 0.09
Nodes (12): Test CommondbRemoteApp initialization with various configurations., Initialize with NONE auth protocol as enum., Initialize with NONE auth protocol as string., Initialize with OAUTH2 auth protocol as enum., Initialize with OAUTH2 auth protocol as string., Initialize with OAuthFlow as enum., Initialize with OAuthFlow as string., Verify default route prefix is /v1. (+4 more)

### Community 215 - "ServiceTestClient"
Cohesion: 0.13
Nodes (10): env(), fixture, FixtureRequest, TestRepository, Service1, Service2, Any, Model (+2 more)

### Community 216 - "Development Guide"
Cohesion: 0.16
Nodes (21): Python & Pytest Conventions, Diagnose-before-editing workflow, test.util.mock_compat, pytest-run skill, Test behavior, not implementation details, Gen-EpiX Agent Guide, Graphify architecture query workflow, Claude Code Root Config (+13 more)

### Community 217 - "omop/service.py"
Cohesion: 0.14
Nodes (13): DomainBaseOmopService, BaseOmopService, Any, Abstract base class for OMOP services defining the interface contract. This…, # TODO: initialise members, # TODO: implement, omop_service_retrieve_persons_by_id(), omop_service_retrieve_persons_by_query() (+5 more)

### Community 218 - "crud_dim.py"
Cohesion: 0.24
Nodes (20): DimCrudCommand, Manage dimensions that group case-type columns (e.g., demographics, sample,…, _crud_create_dim(), _crud_dim_with_abac(), _crud_dim_without_abac(), _crud_update_dim(), _get_existing_dim(), _load_existing_dims() (+12 more)

### Community 219 - "case/non_persistable.py"
Cohesion: 0.12
Nodes (16): Retrieve cases based on a query., RetrieveCasesByQueryCommand, BaseCaseRights, CaseCohortLink, CaseQuery, CaseQueryResult, CaseSetQuery, BaseModel (+8 more)

### Community 220 - "model/ontology.py"
Cohesion: 0.15
Nodes (14): Concept, ConceptRelation, ConceptSet, Disease, EtiologicalAgent, Etiology, Any, field_serializer (+6 more)

### Community 221 - "BaseEtlResult"
Cohesion: 0.10
Nodes (12): BaseEtlResult, BaseModel, Append an ERROR-severity log item and update the status., Override to set the concrete class's error status value., Append a WARN-severity log item., Return True if any log item has ERROR severity., Return True if any log item has WARN severity., Return True if any log item has INFO severity. (+4 more)

### Community 222 - "model/omop/upload.py"
Cohesion: 0.12
Nodes (19): DataIssue, IdentifiersMixin, PydanticBaseModel, Mixin that adds identifiers fields and validation. Assumes that the inheriting…, Get all data issues that are errors., Describes an issue with a single value, MeasurementForUpload, MeasurementRelationForUpload (+11 more)

### Community 223 - "RemoteApp"
Cohesion: 0.07
Nodes (28): Any, App, Command, CrudCommand, PydanticBaseModel, Response, Remote port, or None if not specified., HTTP protocol (HTTP or HTTPS). (+20 more)

### Community 224 - "SeqDictRepository"
Cohesion: 0.13
Nodes (15): AbstractSet, Any, datetime, SeqDistance, SeqProfile, UUID, See parent class method, SeqDictRepository (+7 more)

### Community 225 - "TestCaseUpload"
Cohesion: 0.14
Nodes (13): CaseUploadSetup, get_test_client(), Any, Case, Env, fixture, scenario_ids, skip (+5 more)

### Community 226 - "TestCommondbModelProcessMetadata"
Cohesion: 0.10
Nodes (15): get_test_client(), Env, fixture, integration, scenario_ids, modified_at must be set by the backend on creation., modified_by must be set to the creating user's id., created_at must not change when a record is updated. (+7 more)

### Community 227 - "test_seqdb_calculate_phylogenetic_tree.py"
Cohesion: 0.16
Nodes (13): scenario_ids, Verify update_some_seq_distance_content against a real SA_SQLITE database., TestBulkUpdateSeqDistanceContentSA, _make_protocol(), _make_seq_distance(), _mock_uow(), Any, Protocol (+5 more)

### Community 228 - "scenario_ids"
Cohesion: 0.10
Nodes (12): scenario_ids, Test ValidationError when id doesn't match computed seq_hash., Test valid Identifier with identifier_issuer_code., Test valid Identifier with identifier_issuer_id., Test valid Identifier with both issuer fields., Test ValidationError when both issuer fields are missing., Test field length validation., Test valid AlleleForUpload with locus_id. (+4 more)

### Community 229 - "TestModelSeqProfileForUpload"
Cohesion: 0.11
Nodes (9): Test JSON serialization of AlleleProfileForUpload., Test valid AlleleProfileForUpload with codes., Test valid AlleleProfileForUpload with locus_code_map when using allele_ids., Test ValidationError when both protocol fields are missing., Test ValidationError when both locus_set fields are missing., Test ValidationError when all allele data fields are missing., Test ValidationError when locus_code_map is missing but alleles have locus_code., Test that AlleleProfileForUpload inherits QualityMixin properties. (+1 more)

### Community 230 - "fastapp shared application framework"
Cohesion: 0.13
Nodes (20): casedb domain, commondb shared package, Dynaconf-based configuration, fastapp shared application framework, filter and transform support packages, IDP modes (IDPS, MOCK, NONE), omopdb domain, Repository mode parity (DICT, SA_SQLITE, SA_SQL) (+12 more)

### Community 231 - "crud_col_set.py"
Cohesion: 0.22
Nodes (14): ColSetCrudCommand, Manage column sets used for read/write scopes and default column groupings., case_service_crud_col_set(), _crud_col_set_with_abac(), _crud_col_set_without_abac(), BaseCaseService, ColSet, UUID (+6 more)

### Community 232 - "OmopdbEndpointTestClient"
Cohesion: 0.14
Nodes (11): Retrieve person IDs based on a query. These IDs can then be used to retrieve…, RetrievePersonsByQueryCommand, BaseOmopService, Retrieve persons by their IDs., Retrieve persons matching query criteria., Retrieve specimen IDs grouped by cohort ID., OmopdbEndpointTestClient, Any (+3 more)

### Community 233 - "gen_epix/util.py"
Cohesion: 0.17
Nodes (18): get_package_root(), profile_method(), Path, Get the root path of the project by looking for pyproject.toml. Searches upward…, Decorator method to profile a method using Pyinstrument. The profiling output…, _parse_pyproject_dependency(), _parse_requirements_line(), Path (+10 more)

### Community 234 - "DummyCommand"
Cohesion: 0.12
Nodes (13): DummyCommand, Command, Test get_headers method for different auth protocols., get_headers returns default headers with NONE protocol., get_headers caches token when not expired., get_headers refreshes token past refresh margin., Minimal command for testing., get_headers caches long-lived tokens correctly. Note: Tokens without an 'exp'… (+5 more)

### Community 235 - "TestDuplicateIds"
Cohesion: 0.21
Nodes (10): ParentForUpload, Duplicate-ID detection converts per-item hard failures into soft FAILED results., Construct a Child1ForUpload bypassing Pydantic validators (for dup-ID tests)., Construct a ParentForUpload bypassing Pydantic validators., Build an UploadParentsCommand bypassing all Pydantic batch validators., Duplicate parent UUID → both occurrences FAILED, distinct parent unaffected., Two children with the same UUID inside one parent → parent FAILED., Same child UUID in two distinct parents → both parents FAILED, message names… (+2 more)

### Community 236 - "UserManager"
Cohesion: 0.18
Nodes (7): MockUser, Any, BaseModel, BaseUserManager, Hashable, User, UserManager

### Community 237 - "TestCreate"
Cohesion: 0.21
Nodes (4): Env, scenario_ids, skipif, TestCreate

### Community 239 - "TestRetrieveCompleteCaseType"
Cohesion: 0.15
Nodes (8): Retrieve a complete CaseType., RetrieveCompleteCaseTypeCommand, Retrieve complete case type with all associated data., cached, Retrieve the full definition of a case type., Any, User, TestRetrieveCompleteCaseType

### Community 240 - ".create_local_or_remote_app"
Cohesion: 0.14
Nodes (13): Any, App, Domain, Enum, Logger, User, Register an invited user using their invitation token., Update a user's active status, roles, or organization. (+5 more)

### Community 241 - "convert"
Cohesion: 0.20
Nodes (5): Any, Convert a sequence represented in Nextclade format versus a particular…, convert(), parametrize, TestNextcladeSequenceConversion

### Community 242 - "SeqdbRemoteApp"
Cohesion: 0.11
Nodes (12): Any, datetime, SampleIdentifier, Remote app client for the seqdb service., Retrieve full sample records by their IDs., Retrieve sample identifiers by sample IDs., Retrieve samples matching the given query., Trigger sequence distance calculation and return results. (+4 more)

### Community 243 - ".create_measurement_for_upload"
Cohesion: 0.11
Nodes (17): PersonIdentifier, date, datetime, Person, UUID, Test combinations of different scenarios., Test person with all child types and Identifiers., Test batch with multiple persons having different child type combinations. (+9 more)

### Community 244 - ".__init__"
Cohesion: 0.11
Nodes (12): User, UserInvitation, Retrieve a user by their unique key (e.g., email)., Any, Hashable, Model, User, UserInvitation (+4 more)

### Community 245 - "Any"
Cohesion: 0.12
Nodes (10): Any, Enum, field_validator, Hashable, Key, model_validator, Validate and convert links to Link objs., Get the linked entity, if any. Parameters ---------- link_field_name : str The… (+2 more)

### Community 246 - "OmopdbRemoteApp"
Cohesion: 0.13
Nodes (12): OmopdbRemoteApp, Any, Retrieve specimen IDs for the given cohort IDs., Remote app client for the omopdb service., Register all omopdb routes and command handlers., Retrieve persons matching the given query., Retrieve full person records by their IDs., Set up test fixtures by mocking dependencies to avoid side effects. (+4 more)

### Community 247 - "TestCasedbMetadataMasking"
Cohesion: 0.13
Nodes (14): get_test_client(), CaseType, Env, fixture, integration, scenario_ids, User, Verifies that MaskModelProcessMetadataPolicy is correctly wired in casedb. Root… (+6 more)

### Community 248 - "test_read_config.py"
Cohesion: 0.29
Nodes (17): _assert_default_import_payload(), _assert_string_override_payload(), override_tmp_dir(), fixture, parametrize, Path, scenario_ids, Construct and compose an app config, returning key config/auth values. (+9 more)

### Community 249 - "DummyCmd"
Cohesion: 0.14
Nodes (8): BaseRemoteAppTestCase, DummyCmd, Command, scenario_ids, TestAutoRegistration, TestHeadersAndApplyHandler, TestInitAndProperties, TestRouteRegistration

### Community 250 - "TestDataLineageMixin"
Cohesion: 0.14
Nodes (10): FieldInfo, Tests for the DataLineageMixin class. DataLineageMixin is a plain mixin (not a…, DataLineageMixin should declare a provenance_id annotation., DataLineageMixin should declare a source_traceback annotation., The provenance_id Field should have a default of None., The source_traceback Field should have a default of None., The source_traceback Field should enforce max_length=255., The provenance_id annotation should allow UUID | None. (+2 more)

### Community 251 - "Organization (commondb.organization entity)"
Cohesion: 0.22
Nodes (17): Contact (commondb.organization entity), IdentifierIssuer (commondb.organization entity), Organization (commondb.organization entity), OrganizationIdentifierIssuerLink (commondb.organization entity), Site (commondb.organization entity), User (commondb.organization entity), UserInvitation (commondb.organization entity), commondb / ORGANIZATION — Simplified ERD (+9 more)

### Community 252 - "Sample"
Cohesion: 0.21
Nodes (17): AstMeasurement, DataCollection, File, IdentifierForUpload, AstMeasurement (seqdb.seq.md), PcrMeasurement (seqdb.seq.md), ReadSet (seqdb.seq.md), Sample (seqdb.seq.md) (+9 more)

### Community 253 - "EtlLogItem"
Cohesion: 0.12
Nodes (9): Get all data issues that are errors., EtlLogItem, field_serializer, field_validator, Append an INFO-severity log item., Return a list of log items with INFO severity., Represents a log item for an ETL result accumulator, containing a timestamp,…, Get all data issues that are errors. (+1 more)

### Community 254 - "Linter"
Cohesion: 0.21
Nodes (5): Linter, Path, Runs the specified linting tool with the provided command-line arguments. This…, Runs a series of linting and formatting tools on the gen-epix project. This…, This class provides an interface to run linting tools like mypy, pylint, isort,…

### Community 255 - "test/test_client/util.py"
Cohesion: 0.26
Nodes (7): This module contains the `Linter` class which is used to enforce code quality…, generate_hex_strings(), generate_uuids(), get_test_name(), get_test_root_output_dir(), Enum, Path

### Community 256 - ".create_read_set_for_upload"
Cohesion: 0.16
Nodes (6): ReadSetForUpload, SeqForUpload, Tests for the has_case guard added to _get_upload_samples_command., Tests for the casedb-to-seqdb upload bridge in CaseBatchUploader., TestCaseUploadSeqdbBridge, TestGetUploadSamplesCommandNoCaseGuard

### Community 257 - "Organization"
Cohesion: 0.15
Nodes (16): Contact, Contact (omopdb.md), Organization (omopdb.md), OrganizationAdminPolicy (omopdb.md), OrganizationSet (omopdb.md), Site (omopdb.md), User (omopdb.md), UserInvitation (omopdb.md) (+8 more)

### Community 258 - "IdentifierIssuer (omopdb.organization entity)"
Cohesion: 0.12
Nodes (16): ConditionOccurrenceIdentifier (omopdb.omop / OMOP CDM entity), Death (omopdb.omop / OMOP CDM entity), DeathIdentifier (omopdb.omop / OMOP CDM entity), DeviceExposureIdentifier (omopdb.omop / OMOP CDM entity), DrugExposureIdentifier (omopdb.omop / OMOP CDM entity), MeasurementIdentifier (omopdb.omop / OMOP CDM entity), NoteIdentifier (omopdb.omop / OMOP CDM entity), NoteNlp (omopdb.omop / OMOP CDM entity) (+8 more)

### Community 259 - "Organization"
Cohesion: 0.14
Nodes (16): Contact, IdentifierIssuer, Contact (omopdb.organization.md), IdentifierIssuer (omopdb.organization.md), Organization (omopdb.organization.md), OrganizationSetMember (omopdb.organization.md), Site (omopdb.organization.md), User (omopdb.organization.md) (+8 more)

### Community 260 - "get_case_abac_from_command"
Cohesion: 0.08
Nodes (44): CaseIdentifierCrudCommand, CaseSetDataCollectionLinkCrudCommand, CaseSetMemberCrudCommand, Manage case identifiers that link cases to external systems or provide…, Manage links that share case sets into additional data collections for cross-…, Manage membership of cases in a case set, including per-member classification…, case_service_crud_case_identifier(), _crud_case_identifier_with_abac() (+36 more)

### Community 261 - ".get_test_client"
Cohesion: 0.12
Nodes (9): parse_stats(), Any, Any, Path, Create a test environment for the given test type and repository type. A single…, scenario_ids, TestRead, scenario_ids (+1 more)

### Community 262 - "SampleBatchForUpload"
Cohesion: 0.18
Nodes (9): computed_field, A set of samples intended for upload, together with any new reference data…, Indicates whether there are any read sets in the sample set., Indicates whether there are any sequences in the sample set., Indicates whether there are any seq taxonomies in the sample set., Indicates whether there are any seq classifications in the sample set., Indicates whether there are any PCR measurements in the sample set., Indicates whether there are any AST measurements in the sample set. (+1 more)

### Community 263 - "test_logging_runtime_contract.py"
Cohesion: 0.28
Nodes (15): JSONDict, _emit_log_level_resolution_payloads(), _emit_log_level_resolution_payloads_for_both_modes(), _emit_runtime_payloads_for_all_yaml_paths(), _emit_runtime_payloads_via_dictconfig(), _has_message(), _load_class(), parametrize (+7 more)

### Community 264 - "TestCommondbMetadataMasking"
Cohesion: 0.15
Nodes (13): get_test_client(), DataCollection, Env, fixture, FixtureRequest, integration, scenario_ids, User (+5 more)

### Community 265 - "crud_allele.py"
Cohesion: 0.15
Nodes (12): AlleleCrudCommand, Allele, Handle CRUD operations for Allele entities., Allele, UUID, Handle CRUD operations for Allele entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 266 - ".get_token"
Cohesion: 0.12
Nodes (8): Delete a refresh token and its associated access token., Revoke all tokens for a specific client., Remove all expired tokens from the store., Check if a token exists and is not expired., Get token information without the actual token value., Retrieve a token by access token., Retrieve a token by refresh token., Delete a token and its refresh token mapping.

### Community 267 - "test/conftest.py"
Cohesion: 0.18
Nodes (14): CallInfo, Config, Item, generate_excel_report(), Any, Session, pytest_collection_modifyitems(), pytest_runtest_makereport() (+6 more)

### Community 268 - "Gen-EpiX Contributor Documentation Index"
Cohesion: 0.14
Nodes (15): Gen-EpiX Contributor Documentation Index, Getting Started, Boot Sequence (AppCfg -> AppComposer -> create_fast_api), Request Lifecycle (endpoint -> app.handle -> policies -> handler), API Surface, Logging (namespaces, command-object summarization), Startup Lifecycle (run.py -> AppCfg -> AppComposer -> create_fast_api), Mutation Testing (pytest-gremlins) (+7 more)

### Community 269 - "Organization"
Cohesion: 0.16
Nodes (15): Contact, Contact (seqdb.md), Organization (seqdb.md), OrganizationAdminPolicy (seqdb.md), OrganizationSetMember (seqdb.md), Site (seqdb.md), User (seqdb.md), UserInvitation (seqdb.md) (+7 more)

### Community 270 - "SAUnitOfWork"
Cohesion: 0.19
Nodes (7): Exception, Self, Session, TracebackType, Unit of work class wrapping the SQLAlchemy session. The context stack that can…, Handle exceptions raised during a unit of work, converting them into a domain…, SAUnitOfWork

### Community 271 - "CalculatePhylogeneticTreeCommand"
Cohesion: 0.13
Nodes (10): CalculatePhylogeneticTreeCommand, model_validator, Self, Calculate a phylogenetic tree based on the given protocol, tree algorithm, and…, PhylogeneticTree, Calculate phylogenetic tree for given parameters., PhylogeneticTree, Request phylogenetic tree calculation and return the result. (+2 more)

### Community 272 - "_encode_to_int32"
Cohesion: 0.22
Nodes (10): _encode_to_int32(), _hamming_allele_int32_batch(), _hamming_allele_numpy(), _hamming_allele_numpy_batch(), ndarray, Hamming distances from one existing int32 profile to all M new int32 profiles.…, Hamming distance between two (n_loci,) S16 allele arrays. S16 is a no-uint128…, Hamming distances from one existing S16 profile to all M new profiles.… (+2 more)

### Community 273 - "TestRead"
Cohesion: 0.28
Nodes (4): Env, scenario_ids, skipif, TestRead

### Community 274 - "test_retrieve_stats.py"
Cohesion: 0.31
Nodes (14): get_all_case_type_ids(), get_test_client(), get_user_for_test(), Env, fixture, parametrize, User, UUID (+6 more)

### Community 275 - "TestOauthIdpClientIntrospection"
Cohesion: 0.25
Nodes (3): Any, scenario_ids, TestOauthIdpClientIntrospection

### Community 276 - "TestUserPermissions"
Cohesion: 0.14
Nodes (8): Test user permission retrieval and authorization checks., Test that user permissions are union of all their role permissions., Test that user with no roles has no permissions., Test that user has all RBAC permissions when they actually do., Test that user doesn't have all RBAC permissions when missing some., Test checking if user has more permissions than another user., Test that user doesn't have more permissions when they're a subset., TestUserPermissions

### Community 277 - "test_get_specimen_ids_by_cohort_ids.py"
Cohesion: 0.18
Nodes (11): _make_dict_repo(), _make_sa_repo(), fixture, Session, Unit tests for get_specimen_ids_by_cohort_ids. Scenario: one person with two…, Create an in-memory SQLite DB with Cohort and Specimen tables populated. The SA…, Bypass SARepository.__init__ and wire uow() to the provided session., Bypass __init__ and set _db directly. (+3 more)

### Community 278 - "AuthorizationCodeStore"
Cohesion: 0.18
Nodes (6): AuthorizationCode, AuthorizationCodeStore, datetime, Authorization Code Store In-memory storage for OAuth 2.0 Authorization Codes…, Representation of an OAuth 2.0 authorization code., In-memory store managing authorization codes.

### Community 279 - "case_service_crud_case_data_collection_link"
Cohesion: 0.24
Nodes (13): CaseDataCollectionLinkCrudCommand, Manage links that associate cases with additional data collections to widen or…, case_service_crud_case_data_collection_link(), _crud_case_data_collection_link_with_abac(), _crud_case_data_collection_link_without_abac(), BaseCaseService, CaseDataCollectionLink, UUID (+5 more)

### Community 280 - "abac/__init__.py"
Cohesion: 0.23
Nodes (12): BaseCasePolicy, OrganizationAccessCasePolicy, OrganizationShareCasePolicy, Stores the maximum access rights of a user to a particular data collection,…, Stores any additional case or case set share rights of an organization to a…, Stores the maximum share rights of a user to a particular data collection,…, Stores the access rights of an organization to a particular data collection. If…, UserAccessCasePolicy (+4 more)

### Community 281 - "BaseAppComposer"
Cohesion: 0.18
Nodes (5): BaseAppComposer, Any, App, Dynaconf, Enum

### Community 282 - "BaseSAMapper"
Cohesion: 0.14
Nodes (7): BaseSAMapper, BaseSAMapper is an abstract base class for mappers between SQLAlchemy models…, Create a SAMapper instance for model and row classes., Get field names by field type., Get field names by field type set., Get row field names by field type., Get row field names by field type set.

### Community 283 - "omopdb/domain/enum.py"
Cohesion: 0.24
Nodes (11): AnonMethod, AnonStrictness, Enum, RepositoryType, Role, ServiceType, CommonRoleGenerator, # TODO: fill in permissions (+3 more)

### Community 284 - "test_error_code_unicity"
Cohesion: 0.25
Nodes (13): _extract_hex_strings_from_file(), _get_all_seen_codes(), _get_python_files(), _get_repo_root(), _hanlde_duplicate_hex_codes(), _is_long_hex_string(), Path, scenario_ids (+5 more)

### Community 285 - "App (command dispatcher / PEP)"
Cohesion: 0.17
Nodes (13): Command-Based Execution Model, Policy Enforcement Timing (BEFORE/DURING/AFTER), App (command dispatcher / PEP), BaseRbacService, CrudEndpointGenerator, PolicyDecisionPoint, Policy (is_allowed/get_content/filter hooks), RbacPolicy (+5 more)

### Community 286 - "Organization (omopdb.organization entity)"
Cohesion: 0.29
Nodes (13): OrganizationAdminPolicy (omopdb.abac entity), omopdb / ABAC — Simplified ERD, omopdb — Full Database ERD (detailed, 69 entities), omopdb — Full Database ERD (simplified, 69 entities), Contact (omopdb.organization entity), Organization (omopdb.organization entity), OrganizationIdentifierIssuerLink (omopdb.organization entity), Site (omopdb.organization entity) (+5 more)

### Community 287 - "crud_pcr_measurement.py"
Cohesion: 0.15
Nodes (12): PcrMeasurementCrudCommand, PcrMeasurement, Handle CRUD operations for PcrMeasurement entities., PcrMeasurement, UUID, Handle CRUD operations for PcrMeasurement entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 288 - "ModelFieldProps"
Cohesion: 0.16
Nodes (10): complete_stored_model_field_props(), Any, Model, Complete the stored_model_field_props with default props for all other…, ModelFieldProps, BaseModel, model_validator, Self (+2 more)

### Community 289 - ".__init__"
Cohesion: 0.40
Nodes (4): Domain, Path, Initialize connection parameters, SSL context, routes, and optional CRUD…, Configure the SSL context based on protocol and certificate settings.

### Community 290 - "FakeResponse"
Cohesion: 0.26
Nodes (3): FakeClient, FakeResponse, Any

### Community 291 - "test_general_model_field_properties.py"
Cohesion: 0.21
Nodes (11): _is_iterable_type(), Any, scenario_ids, Check if the given field type is an iterable type (like List, Set, Tuple, etc.), test if domain and request body models have a max_length for all iterable…, test_model_field_properties(), is_model_class(), Any (+3 more)

### Community 292 - "TestSeqdbRemoteApp"
Cohesion: 0.15
Nodes (8): scenario_ids, Test the SeqdbRemoteApp class with focus on…, Test that the ROUTE_MAP contains the expected mapping., Test that the calculate_phylogenetic_tree method exists and is callable., Test that base URL is constructed correctly., Test that the remote app initializes correctly with default values., Test that the handler registers the correct route., TestSeqdbRemoteApp

### Community 293 - "BaseUploadTestCase"
Cohesion: 0.15
Nodes (7): BaseUploadTestCase, ParentUploadResult, ReadSetForUpload, UUID, Helper to create a ReadSetForUpload with default or specified properties., Base test case with common fixtures and utilities., Set up test fixtures.

### Community 294 - "JsonFormatter"
Cohesion: 0.41
Nodes (12): casedb Debug Logging Config, casedb Logging Config, commondb Debug Logging Config, JsonFormatter, commondb Logging Config, Log Level Tuning Rationale (sqlalchemy/httpx/asyncio), UvicornAccessLogFilter, omopdb Debug Logging Config (+4 more)

### Community 295 - "CdmSource"
Cohesion: 0.27
Nodes (8): CdmSource, Metadata, Any, field_validator, Model, UUID, The CDM_SOURCE table contains detail about the source database and the process…, The METADATA table contains metadata information about a dataset that has been…

### Community 296 - "crud_seq_category.py"
Cohesion: 0.20
Nodes (10): SeqCategoryCrudCommand, SeqCategory, UUID, Handle CRUD operations for SeqCategory entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added, # TODO: Specific logic for update operation to be added, # TODO: Specific logic for delete operation to be added, e.g. check for foreign… (+2 more)

### Community 297 - "crud_ast_prediction.py"
Cohesion: 0.15
Nodes (12): AstPredictionCrudCommand, AstPrediction, Handle CRUD operations for AstPrediction entities., AstPrediction, UUID, Handle CRUD operations for AstPrediction entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 298 - "crud_locus_code_map.py"
Cohesion: 0.15
Nodes (12): LocusCodeMapCrudCommand, LocusCodeMap, Handle CRUD operations for LocusCodeMap entities., LocusCodeMap, UUID, Handle CRUD operations for LocusCodeMap entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 299 - "UUID"
Cohesion: 0.20
Nodes (7): UUID, Create a test Ref2 object., Test scenarios related to providing different combinations of child objects., Test 2.2: Parent with Child1 objects only., Test 2.3: Parent with Child2 objects only., Test 2.4: Parent with both Child1 and Child2 objects., Test2ChildObjectProvision

### Community 300 - "BaseRemoteService"
Cohesion: 0.22
Nodes (5): BaseRemoteService, Any, App, Command, setter

### Community 301 - "crud_read_set.py"
Cohesion: 0.15
Nodes (12): ReadSetCrudCommand, ReadSet, Handle CRUD operations for ReadSet entities., ReadSet, UUID, Handle CRUD operations for ReadSet entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 302 - "crud_read_set_identifier.py"
Cohesion: 0.15
Nodes (12): ReadSetIdentifierCrudCommand, ReadSetIdentifier, Handle CRUD operations for ReadSetIdentifier entities., ReadSetIdentifier, UUID, Handle CRUD operations for ReadSetIdentifier entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 303 - "crud_ref_allele.py"
Cohesion: 0.15
Nodes (12): RefAlleleCrudCommand, RefAllele, Handle CRUD operations for RefAllele entities., RefAllele, UUID, Handle CRUD operations for RefAllele entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 304 - "crud_ref_seq.py"
Cohesion: 0.15
Nodes (12): RefSeqCrudCommand, RefSeq, Handle CRUD operations for RefSeq entities., RefSeq, UUID, Handle CRUD operations for RefSeq entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 305 - "crud_sample_data_collection_link.py"
Cohesion: 0.15
Nodes (12): SampleDataCollectionLinkCrudCommand, SampleDataCollectionLink, Handle CRUD operations for SampleDataCollectionLink entities., SampleDataCollectionLink, UUID, Handle CRUD operations for SampleDataCollectionLink entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 306 - "crud_seq_classification.py"
Cohesion: 0.15
Nodes (12): SeqClassificationCrudCommand, SeqClassification, Handle CRUD operations for SeqClassification entities., SeqClassification, UUID, Handle CRUD operations for SeqClassification entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 307 - "crud_seq_distance.py"
Cohesion: 0.15
Nodes (12): SeqDistanceCrudCommand, SeqDistance, Handle CRUD operations for SeqDistance entities., SeqDistance, UUID, Handle CRUD operations for SeqDistance entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 308 - "crud_seq_identifier.py"
Cohesion: 0.15
Nodes (12): SeqIdentifierCrudCommand, SeqIdentifier, Handle CRUD operations for SeqIdentifier entities., SeqIdentifier, UUID, Handle CRUD operations for SeqIdentifier entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 309 - "crud_seq_profile.py"
Cohesion: 0.16
Nodes (12): SeqProfileCrudCommand, SeqProfile, Handle CRUD operations for SeqProfile entities., _get_not_implemented_message(), CrudCommand, SeqProfile, UUID, Handle CRUD operations for SeqProfile entities. (+4 more)

### Community 310 - "crud_seq_profile_identifier.py"
Cohesion: 0.15
Nodes (12): SeqProfileIdentifierCrudCommand, SeqProfileIdentifier, Handle CRUD operations for SeqProfileIdentifier entities., SeqProfileIdentifier, UUID, Handle CRUD operations for SeqProfileIdentifier entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 311 - "crud_seq_taxonomy.py"
Cohesion: 0.15
Nodes (12): SeqTaxonomyCrudCommand, SeqTaxonomy, Handle CRUD operations for SeqTaxonomy entities., SeqTaxonomy, UUID, Handle CRUD operations for SeqTaxonomy entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 312 - "TestUploadEdgeCases"
Cohesion: 0.20
Nodes (6): Focused edge-case tests for upload consistency and null semantics., Multiple existing identifiers for one parent must resolve to one internal ID., Same-service link verification should support user=None without crashing., Different non-null parent IDs across children in one parent should fail., NULL_ID internal_id should be treated as unresolved and skipped., TestUploadEdgeCases

### Community 313 - "crud_taxon_set_member.py"
Cohesion: 0.15
Nodes (12): TaxonSetMemberCrudCommand, TaxonSetMember, Handle CRUD operations for TaxonSetMember entities., TaxonSetMember, UUID, Handle CRUD operations for TaxonSetMember entities., # TODO: Specific logic for create operation to be added, # TODO: Specific logic for read operation to be added (+4 more)

### Community 314 - "UUID"
Cohesion: 0.18
Nodes (6): UUID, Upload a file and return its assigned UUID., Retrieve profile IDs similar to the given profiles within a distance threshold., Return IDs of all seq distance protocols., Retrieve the best sequence ID per sample ID., Retrieve the best sequence classification ID per sample ID.

### Community 315 - "BaseCaseAbacTestCase"
Cohesion: 0.18
Nodes (5): BaseCaseAbacTestCase, scenario_ids, Base test case with common fixtures for ABAC rights., TestCaseTypeAccessAbac, TestCaseTypeShareAbac

### Community 316 - "TestCaseTypeProps"
Cohesion: 0.17
Nodes (3): parametrize, scenario_ids, TestCaseTypeProps

### Community 317 - ".create_case"
Cohesion: 0.27
Nodes (6): Case, datetime, parametrize, UUID, Existing case should maintain its created_in_data_collection_id., Existing cases must not be changed to a different created_in_data_collection_id.

### Community 318 - ".create_uploader"
Cohesion: 0.23
Nodes (3): After re-validation, case_date set by calculate_case_date must not be reset to…, read_fields row[1] keys may be UUID objects (DICT) or strings (SQL); both must…, TestExistingContentKeyNormalization

### Community 319 - "Test6Identifiers"
Cohesion: 0.20
Nodes (7): Test scenarios related to Identifiers for parent objects., Test 6.2.1.2.2: Existing Identifier with different parent ID - should fail., Test 6.2.2: New Identifier for new parent - should succeed., Test 6.2.3.1: Multiple Identifiers, some existing for different parent - should…, Test 6.2.3.2: Multiple Identifiers, all new but same issuer - should fail., Get the ParentIdentifier model corresponding to an IdentifierForUpload model,…, Test6Identifiers

### Community 320 - "IdpClient hierarchy"
Cohesion: 0.20
Nodes (11): AuthService (concrete), IdpClient hierarchy, MockIDPClient (no-auth dev/CI), OauthIdpClient (real OIDC), BaseUserManager, Authentication (Identity Resolution Layer), User Resolution (claims -> local User), Add New IDP Configuration (+3 more)

### Community 321 - "Protocol"
Cohesion: 0.20
Nodes (11): AstMeasurement, LocusSet, AstMeasurement (seqdb.md), LocusSet (seqdb.md), PcrMeasurement (seqdb.md), Protocol (seqdb.md), ProtocolSetMember (seqdb.md), PcrMeasurement (+3 more)

### Community 322 - "._validate_model"
Cohesion: 0.40
Nodes (4): model_validator, Self, Derive the id, if not provided, or otherwise verify that it is correctly…, Ensure that either identifier_issuer_id or identifier_issuer_code is set.

### Community 323 - "BaseLogItem"
Cohesion: 0.20
Nodes (6): BaseLogItem, Any, Convert the log item to a JSON string., BaseLogItem class for creating log messages. Defined as a regular class instead…, Any, Logger

### Community 324 - "PayerPlanPeriod"
Cohesion: 0.25
Nodes (9): Cost, PayerPlanPeriod, Any, DataLineageMixin, field_validator, Model, UUID, The COST table captures records containing the cost of any medical event… (+1 more)

### Community 325 - "Taxon"
Cohesion: 0.16
Nodes (11): field_serializer, field_validator, Model, UUID, A member of a taxon set, representing the inclusion of a specific taxon in a…, A taxonomic unit (taxon) in the taxonomic hierarchy. A single unified taxonomy…, Validate and convert rank representation to a TaxonRank enum value. When given…, A set of taxa, for example a set of taxa that are relevant for a specific… (+3 more)

### Community 326 - "Transformer Framework"
Cohesion: 0.25
Nodes (11): FallbackTransformer, FieldTransformer, ObjectAdapter, RetryTransformer, Streaming Pipeline Performance Rationale, StreamingPipeline, Transformer, Transformer Framework (+3 more)

### Community 327 - "rewrite_parametrized_dependency_markers"
Cohesion: 0.33
Nodes (6): pytest_collection_modifyitems(), pytest_collection_modifyitems(), pytest_collection_modifyitems(), pytest_collection_modifyitems(), Rewrite class-level dependency 'depends' markers to include parametrize IDs.…, rewrite_parametrized_dependency_markers()

### Community 328 - "test_omopdb_upload_base_result.py"
Cohesion: 0.20
Nodes (6): _ConcreteResult, scenario_ids, Unit tests for BaseResult and ResultLogItem. Verifies that: - add_error /…, Minimal Pydantic model used to test BaseResult in isolation., UploadLogItem must be the same class as ResultLogItem (alias)., TestResultLogItem

### Community 329 - "TestUploadResult"
Cohesion: 0.18
Nodes (3): _make_pending_upload_result(), Construct an UploadResult in PENDING state (no logs required)., TestUploadResult

### Community 330 - "env"
Cohesion: 0.31
Nodes (5): env(), fixture, FixtureRequest, Return a test client configured for either DICT or SA_SQLITE demo repos. The…, TestRetrieveSamples

### Community 331 - "test_seqdb_remote_app.py"
Cohesion: 0.20
Nodes (6): Any, Unit tests for SeqdbRemoteApp create_calculate_phylogenetic_tree_handler…, Test the retrieve_seq_distance_last_modified handler., Create sample response data for testing., Test successful HTTP request with complete response data., TestRetrieveSeqDistanceLastModified

### Community 332 - "fixture"
Cohesion: 0.20
Nodes (6): fixture, User, Test successful HTTP request with response data missing leaf_ids., Create a mock user for testing., Create a SeqdbRemoteApp instance for testing., Create a sample command for testing.

### Community 333 - "AppComposer (Composition Root)"
Cohesion: 0.22
Nodes (10): System Composition (four FastAPI apps sharing a model), AppCfg (logger init, settings load, settings validation), AppComposer (Composition Root), AppImplDetails (state bag), create_fast_api Assembly (lifespan, middleware, routers, OpenAPI), Entry Point app.py (SCHEMA_KWARGS, APP_CFG, APP_COMPOSER, FAST_API), Exception Handling (api/exc.py, handle_exception/handle_command), Repository + Service Loop (compose_application/_initialize_repository) (+2 more)

### Community 334 - "Data Collection (doc)"
Cohesion: 0.27
Nodes (10): Data Collection Set, Data Collection Set Member, Data Collection (doc), DataCollection, DataCollectionSet, DataCollectionSetMember, DataCollection, DataCollectionSet (+2 more)

### Community 335 - "Region Set"
Cohesion: 0.22
Nodes (10): Region, RegionSet, Region (doc), Region Relation (doc), Region Set (doc), Region Set Shape (doc), Region, Region Relation (+2 more)

### Community 336 - "GraphvizErmGenerator"
Cohesion: 0.33
Nodes (5): GraphvizErmGenerator, Domain, Path, Generates Entity-Relationship Model diagrams as PNG files via ``erdantic`` /…, Generate ERM diagrams (PNG) for every domain and its services. Also writes an…

### Community 337 - "MermaidErmGenerator"
Cohesion: 0.36
Nodes (7): MermaidErmGenerator, Domain, Path, Write a Markdown file wrapping a Mermaid diagram., Generates Mermaid ``erDiagram`` markdown files from domain model definitions.…, Generate Mermaid ERD markdown files into *dir*., _write_md()

### Community 338 - "Sample"
Cohesion: 0.27
Nodes (10): AstPrediction, AstPrediction (seqdb.md), Sample (seqdb.md), Seq (seqdb.md), SeqClassification (seqdb.md), SeqTaxonomy (seqdb.md), Sample, Seq (+2 more)

### Community 339 - "FullSample"
Cohesion: 0.27
Nodes (10): FullSample, IdentifierIssuer, ReadSetIdentifier (seqdb.seq.md), SampleIdentifier (seqdb.seq.md), SeqIdentifier (seqdb.seq.md), SeqProfileIdentifier (seqdb.seq.md), ReadSetIdentifier, SampleIdentifier (+2 more)

### Community 340 - "SeqTaxonomy"
Cohesion: 0.20
Nodes (10): RefSeq (seqdb.seq.md), SeqTaxonomy (seqdb.seq.md), Taxon (seqdb.seq.md), TaxonSet (seqdb.seq.md), TaxonSetMember (seqdb.seq.md), RefSeq, SeqTaxonomy, Taxon (+2 more)

### Community 341 - "RetrieveSimilarCasesCommand"
Cohesion: 0.24
Nodes (7): BaseModel, Retrieve cases that are (genetically) similar to a given list of case_ids,…, The return value for the RetrieveSimilarCasesCommand., RetrieveSimilarCasesCommand, RetrieveSimilarCasesReturnValue, Retrieve UUIDs of cases similar to specified case., Retrieve cases similar to the given cases within a distance threshold.

### Community 342 - "RetrievePhylogeneticTreeByCasesCommand"
Cohesion: 0.20
Nodes (7): Retrieve a phylogenetic tree based on a set of case IDs, a tree algorithm, and…, RetrievePhylogeneticTreeByCasesCommand, PhylogeneticTree, Retrieve phylogenetic tree for specified cases., PhylogeneticTree, PhylogeneticTree, Compute and retrieve a phylogenetic tree for the given cases.

### Community 343 - "RetrieveProtocolsCommand"
Cohesion: 0.20
Nodes (7): Retrieve the protocols registered in seqdb for downstream sequence processing…, RetrieveProtocolsCommand, Protocol, Retrieve available protocols., Protocol, Protocol, Retrieve sequencing or assembly protocols.

### Community 344 - "sa_model/ontology.py"
Cohesion: 0.53
Nodes (9): Concept, ConceptRelation, ConceptSet, Disease, EtiologicalAgent, Etiology, Base, RowMetadataMixin (+1 more)

### Community 345 - "CommondbSAMapper"
Cohesion: 0.29
Nodes (7): CommondbSAMapper, Any, Hashable, Model, SAMapper subclass for all databases that use RowMetadataMixin. Overrides…, Update `row` from `obj`, applying commondb metadata-field rules. Returns True…, Dump `obj` to a dict, applying commondb metadata-field rules. For users without…

### Community 346 - "_make_mapper"
Cohesion: 0.29
Nodes (4): _make_entity(), _make_mapper(), scenario_ids, TestSAMapper

### Community 347 - ".__init__"
Cohesion: 0.31
Nodes (4): Any, Hashable, Update the row source and target fields. This allows for changing the field…, Initialise the transformer with the provided mapping and field specifications.…

### Community 348 - "renovate.json"
Cohesion: 0.20
Nodes (9): config:best-practices, dev, automerge, baseBranchPatterns, extends, packageRules, prConcurrentLimit, prHourlyLimit (+1 more)

### Community 349 - "TestSQLInjection"
Cohesion: 0.31
Nodes (6): get_test_client(), Env, fixture, scenario_ids, Session, TestSQLInjection

### Community 350 - "TestOAuth2Validation"
Cohesion: 0.20
Nodes (6): Test OAuth2 configuration validation during initialization., Raise error when OAuth2 requires discovery URL., Raise error when OAuth2 requires client ID., Raise error when OAuth2 requires scope., Raise error for OIDC auth protocol (not yet supported)., TestOAuth2Validation

### Community 351 - "TestAnonymizeUser"
Cohesion: 0.22
Nodes (6): scenario_ids, Include each user ID so forgotten users in one organization remain unique., Verify anonymization of the target user., Set up test fixtures., Anonymize personal fields and deactivate the anonymized user., TestAnonymizeUser

### Community 352 - "generate_seqdb_models.py"
Cohesion: 0.33
Nodes (9): build_random_nextclade_fields(), generate_demo_seqdb_models(), _generate_snp_objects(), Any, Random, Sample, UUID, Generate demo seqdb models. When snp_seq_length > 0, SNP-specific reference… (+1 more)

### Community 353 - "patch"
Cohesion: 0.20
Nodes (5): patch, Test that empty/null response data returns None., Test that empty dict response returns None., Test that HTTP errors are properly propagated., Test that RetrievePhylogeneticTreeRequestBody is constructed correctly.

### Community 354 - "TestOIDCProvider"
Cohesion: 0.20
Nodes (6): Test creating ID token with nonce., Test cases for the OIDCProvider class., Test extracting claims from address scope., Test extracting claims from multiple scopes., Test creating logout response with redirect URI., TestOIDCProvider

### Community 355 - "PhylogeneticTree"
Cohesion: 0.25
Nodes (9): TreeAlgorithm, TreeAlgorithmClass, Tree Algorithm (doc), Tree Algorithm Class (doc), GeneticDistanceProtocol, PhylogeneticTree (casedb.seqdb.md concept), PhylogeneticTree, Tree Algorithm (+1 more)

### Community 356 - "Concept Relation"
Cohesion: 0.28
Nodes (9): Concept, Concept Relation, Concept Set, Concept (doc), Concept Relation (doc), Concept, ConceptSet, Concept (doc concept) (+1 more)

### Community 357 - "Outage (commondb.system entity)"
Cohesion: 0.25
Nodes (9): Outage (commondb.system entity), commondb / SYSTEM — Simplified ERD, IdentityProvider (omopdb.auth entity), IDPUser (omopdb.auth entity), omopdb / AUTH — Simplified ERD, IdentityProvider (seqdb.auth entity), IDPUser (seqdb.auth entity), seqdb / AUTH — Simplified ERD (+1 more)

### Community 358 - "_build_diagram"
Cohesion: 0.28
Nodes (9): _annotation_to_mermaid_type(), _build_diagram(), BaseModel, Return the Mermaid lines for a single entity block **with** attributes. Example…, Generate Mermaid relationship lines for a set of model classes. Each Link in an…, Build a complete Mermaid erDiagram string. Parameters ---------- model_classes…, Convert a Python / Pydantic type annotation to a short Mermaid-friendly type…, _render_entity_block() (+1 more)

### Community 359 - "Protocol"
Cohesion: 0.28
Nodes (9): Protocol (seqdb.seq.md), ProtocolSetMember (seqdb.seq.md), SeqDistance (seqdb.seq.md), SeqProfile (seqdb.seq.md), Protocol, ProtocolSet, ProtocolSetMember, SeqDistance (+1 more)

### Community 360 - "CaseBatchForUpload"
Cohesion: 0.25
Nodes (6): CaseBatchForUpload, computed_field, A number of unique cases intended for upload., Indicates whether there are any read sets in the cases., Indicates whether there are any sequences in the cases., Determine if there are any seqdb samples in the cases to be uploaded.

### Community 361 - "._create_remote_app"
Cohesion: 0.31
Nodes (5): Instantiate a remote app from a module path and class name., Test error handling in _create_remote_app., _create_remote_app raises error when remote_app_props is None., _create_remote_app raises error when module key is missing., TestCreateRemoteAppErrors

### Community 362 - "dependency"
Cohesion: 0.22
Nodes (9): dependency, ModuleTestCreate, ModuleTestDelete, ModuleTestRead, ModuleTestUpdate, TestCreate, TestDelete, TestRead (+1 more)

### Community 363 - "TestVerifyUserRights"
Cohesion: 0.36
Nodes (4): Role, User, Tests for RBAC verification in CaseBatchUploader.verify_user_rights., TestVerifyUserRights

### Community 364 - "dependency"
Cohesion: 0.22
Nodes (9): dependency, ModuleTestCreate, ModuleTestDelete, ModuleTestRead, ModuleTestUpdate, TestCreate, TestDelete, TestRead (+1 more)

### Community 365 - "test_logging_yaml.py"
Cohesion: 0.47
Nodes (8): parametrize, Path, scenario_ids, Contract tests for all production logging.yaml configuration files. These tests…, test_console_handler_uses_json_formatter(), test_root_logger_is_present_and_uses_console_handler(), test_third_party_loggers_explicitly_configured(), test_uvicorn_access_has_structured_filter()

### Community 366 - "TestDelete"
Cohesion: 0.33
Nodes (5): Env, scenario_ids, skipif, RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…, TestDelete

### Community 367 - "dependency"
Cohesion: 0.22
Nodes (9): dependency, ModuleTestCreate, ModuleTestDelete, ModuleTestRead, ModuleTestUpdate, TestCreate, TestDelete, TestRead (+1 more)

### Community 368 - "env"
Cohesion: 0.36
Nodes (5): env(), fixture, FixtureRequest, Return a test client configured for either DICT or SA_SQLITE demo repos. The…, TestRetrievePersons

### Community 369 - "dependency"
Cohesion: 0.22
Nodes (9): dependency, ModuleTestCreate, ModuleTestDelete, ModuleTestRead, ModuleTestUpdate, TestCreate, TestDelete, TestRead (+1 more)

### Community 370 - "RowMetadataMixin"
Cohesion: 0.32
Nodes (8): Base1, Base2, declarative_mixin, RowMetadataMixin, SAModel1_1, SAModel1_2, SAModel2_1, SAModel2_2

### Community 371 - "BaseRepository (abstract)"
Cohesion: 0.25
Nodes (8): Layer Boundaries principle, BaseRepository (abstract), BaseService, DictRepository (in-memory backend), SARepository (SQLAlchemy backend), Repository Modes (DICT_DEMO/EMPTY, SA_SQLITE_DEMO/EMPTY, SA_SQL), Architectural Constraints table, Copilot Chat + Repo Docs Guide

### Community 372 - "Contact (doc)"
Cohesion: 0.32
Nodes (8): Contact, Contact (doc), Site (doc), Contact, Site, Site, Contact, Site

### Community 373 - "seqdb Overview ERD"
Cohesion: 0.25
Nodes (8): seqdb Overview ERD, seqdb FILE Service ERD, seqdb ORGANIZATION Service ERD (Detailed), seqdb ORGANIZATION Service ERD (Simplified), seqdb SEQ Service ERD (Detailed), seqdb SEQ Service ERD (Simplified), seqdb SYSTEM Service ERD (Detailed), seqdb SYSTEM Service ERD (Simplified)

### Community 374 - "IdentifierIssuer"
Cohesion: 0.25
Nodes (8): IdentifierIssuer, IdentifierIssuer (seqdb.md), OrganizationIdentifierIssuerLink (seqdb.md), SampleIdentifier (seqdb.md), SeqIdentifier (seqdb.md), OrganizationIdentifierIssuerLink, SampleIdentifier, SeqIdentifier

### Community 375 - "Taxon"
Cohesion: 0.25
Nodes (8): RefSeq (seqdb.md), Taxon (seqdb.md), TaxonSet (seqdb.md), TaxonSetMember (seqdb.md), RefSeq, Taxon, TaxonSet, TaxonSetMember

### Community 376 - "Locus"
Cohesion: 0.25
Nodes (8): Allele, AlleleForUpload, Locus, Allele (seqdb.seq.md), Locus (seqdb.seq.md), RefAllele (seqdb.seq.md), RefAllele, SampleBatchForUpload

### Community 377 - "RetrieveGeneticSequenceFastaByCaseCommand"
Cohesion: 0.25
Nodes (5): Retrieve a set of genetic sequences in FASTA format based on a set of case IDs…, RetrieveGeneticSequenceFastaByCaseCommand, Retrieve genetic sequence data in FASTA format for case., Return a streaming iterable of FASTA formatted lines. Path: HTTP client ->…, Stream genetic sequence FASTA data for cases.

### Community 378 - "HandleNoResponseMiddleware"
Cohesion: 0.29
Nodes (6): HandleNoResponseMiddleware, App, BaseHTTPMiddleware, FastAPI, Logger, Middleware to handle cases where no response is returned from the endpoint.…

### Community 379 - "EngineFactory"
Cohesion: 0.29
Nodes (4): EngineFactory, Engine, Static factory class to create and manage SQLAlchemy engine objs., Create a new SQLAlchemy engine or return an existing one for the given…

### Community 380 - "Atlas Agent (Conductor)"
Cohesion: 0.43
Nodes (8): Atlas Agent (Conductor), Code-Review Agent, Explorer Agent, Frontend-Engineer Agent, Oracle Agent (Planner/Researcher), Prometheus Agent (Autonomous Planner), Scripter GOTCHAS Reference, Sisyphus Agent (Implementer)

### Community 381 - "TestRead"
Cohesion: 0.39
Nodes (4): Env, scenario_ids, skipif, TestRead

### Community 382 - "TestUpdate"
Cohesion: 0.36
Nodes (4): Env, scenario_ids, skipif, TestUpdate

### Community 383 - "OAuth 2.0 Provider with OpenID Connect Support"
Cohesion: 0.43
Nodes (8): client_store.py, demo_client.py, OAuth 2.0 Provider with OpenID Connect Support, jwks.py, oidc_provider.py, server.py (OAuth FastAPI app), token_store.py, validators.py

### Community 384 - "Entity descriptor"
Cohesion: 0.29
Nodes (7): Domain (registry), Entity descriptor, Key (unique constraint), Link (foreign key descriptor), Domain Registration (register_domain_entities), casedb ABAC Simplified ERD, casedb ABAC Detailed ERD

### Community 385 - "DataCollection"
Cohesion: 0.33
Nodes (7): DataCollection, DataCollectionSet, DataCollectionSetMember, DataCollection (seqdb.md), DataCollectionSetMember (seqdb.md), SampleDataCollectionLink (seqdb.md), SampleDataCollectionLink

### Community 386 - "Seq"
Cohesion: 0.29
Nodes (7): AstPrediction, Contig, AstPrediction (seqdb.seq.md), Seq (seqdb.seq.md), SeqClassification (seqdb.seq.md), Seq, SeqClassification

### Community 387 - "OrganizationContacts"
Cohesion: 0.29
Nodes (4): OrganizationContacts, BaseModel, Retrieve organization contact information., Retrieve contact information for an organization.

### Community 388 - ".anonymize_user"
Cohesion: 0.29
Nodes (3): cached, User, Forget user information.

### Community 389 - "TestDelete"
Cohesion: 0.33
Nodes (5): Env, scenario_ids, skipif, RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…, TestDelete

### Community 390 - "seq_service_update_seq_distances"
Cohesion: 0.33
Nodes (5): For a given distance protocol, find all profiles that don't yet have a…, UpdateSeqDistancesCommand, Update sequence distance calculations., For a given distance protocol, find all profiles that don't yet have a…, seq_service_update_seq_distances()

### Community 391 - "._validate_content"
Cohesion: 0.29
Nodes (5): model_validator, Self, UUID, Validate that the content representation is valid., Get the profile distance map from the content.

### Community 392 - "._serialize_int_enums"
Cohesion: 0.29
Nodes (5): field_serializer, IntEnum, UUID, Serializes the IntEnums to their int value., Serializes UUID fields as strings. If the value is None, it returns None.

### Community 393 - "Etiology"
Cohesion: 0.33
Nodes (6): Disease, EtiologicalAgent, Etiology, Disease (doc concept), EtiologicalAgent (doc concept), Etiology (doc concept)

### Community 394 - "Subject"
Cohesion: 0.40
Nodes (6): DataCollection, IdentifierIssuer, Subject (doc concept), SubjectIdentifier (doc concept), Subject, SubjectIdentifier

### Community 395 - "Concept"
Cohesion: 0.07
Nodes (32): Concept, ConceptAncestor, ConceptRelationship, ConditionEra, Cost, Domain, DoseEra, DrugEra (+24 more)

### Community 396 - "TestDelete"
Cohesion: 0.33
Nodes (5): Env, scenario_ids, skipif, RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…, TestDelete

### Community 397 - "MeasurementRelation"
Cohesion: 0.40
Nodes (6): MeasurementRelation (omopdb.md), MeasurementRelationIdentifier (omopdb.md), MeasurementRelation, MeasurementRelationIdentifier, MeasurementRelation, MeasurementRelationIdentifier

### Community 398 - "ObservationPeriod"
Cohesion: 0.40
Nodes (6): ObservationPeriod (omopdb.md), ObservationPeriodIdentifier (omopdb.md), ObservationPeriod, ObservationPeriodIdentifier, ObservationPeriod, ObservationPeriodIdentifier

### Community 399 - "Locus"
Cohesion: 0.33
Nodes (6): Allele, Locus, Allele (seqdb.md), Locus (seqdb.md), RefAllele (seqdb.md), RefAllele

### Community 400 - "ReadSet"
Cohesion: 0.33
Nodes (6): File, File (seqdb.md), ReadSet (seqdb.md), ReadSetIdentifier (seqdb.md), ReadSet, ReadSetIdentifier

### Community 401 - "SeqProfile"
Cohesion: 0.33
Nodes (6): SeqDistance (seqdb.md), SeqProfile (seqdb.md), SeqProfileIdentifier (seqdb.md), SeqDistance, SeqProfile, SeqProfileIdentifier

### Community 402 - "EtlLogItem"
Cohesion: 0.53
Nodes (6): CalculateSeqDistancesResult, EtlLogItem, SampleBatchUploadResult, SampleDataIssue, SampleUploadResult, UploadResult

### Community 403 - "CaseAbacPolicy"
Cohesion: 0.50
Nodes (3): CaseAbacPolicy, Command, Model

### Community 404 - ".create_unique_values_temp_table"
Cohesion: 0.33
Nodes (5): Create an SQL temp table with a single columns with unique values. This can be…, MetaData, Table, TypeEngine, UUID

### Community 405 - "omopdb/policies/update_user_policy.py"
Cohesion: 0.33
Nodes (4): Any, BaseAbacService, CommonUpdateUserPolicy, UpdateUserPolicy

### Community 406 - "._validate_model"
Cohesion: 0.40
Nodes (4): model_validator, Self, Derive the sequence hash as the first 128 bits of the SHA256 hash of the lower…, Validate that the content hash matches the content.

### Community 407 - "services/user_manager.py"
Cohesion: 0.05
Nodes (29): ServiceType, Any, BaseOrganizationService, Any, User, Retrieve user by their unique key., Register user from invitation., Update user information. (+21 more)

### Community 408 - ".__init__"
Cohesion: 0.33
Nodes (5): OrganizationDictRepository, Any, CommonOrganizationDictRepository, Hashable, Model

### Community 409 - "seqdb/repositories/organization_sa.py"
Cohesion: 0.33
Nodes (4): OrganizationSARepository, Any, CommonOrganizationSARepository, Engine

### Community 410 - "get_test_client"
Cohesion: 0.47
Nodes (5): get_test_client(), Env, fixture, Register root1_1 + org1, invite root1_2, and create minimum CaseType…, setup_reference_data()

### Community 412 - "OAuth Client Credential Flow Test"
Cohesion: 0.53
Nodes (6): OAuth Client Credential Flow Test, OAuthServerManager, ReceiverApp, ReceiverAppCLI, ReceiverAppManager, RequestorApp

### Community 413 - "init-db one-shot database creation service"
Cohesion: 0.50
Nodes (5): casedb service (SA_SQL mode, embedded LOCAL seqdb), init-db one-shot database creation service, lsp_sql SQL Server service, omopdb service (SA_SQL mode), seqdb service (SA_SQL mode)

### Community 414 - "DataCollection (commondb.organization entity)"
Cohesion: 0.50
Nodes (5): DataCollection (commondb.organization entity), DataCollection (omopdb.organization entity), DataCollection (seqdb entity), DataCollectionSetMember (seqdb entity), SampleDataCollectionLink (seqdb entity)

### Community 415 - "DataCollectionSetMember"
Cohesion: 0.50
Nodes (5): DataCollection, DataCollectionSet, DataCollectionSetMember, DataCollection (omopdb.md), DataCollectionSetMember (omopdb.md)

### Community 416 - "Specimen"
Cohesion: 0.29
Nodes (7): Specimen (omopdb.md), SpecimenIdentifier (omopdb.md), Specimen (omopdb.omop.md), Specimen, SpecimenIdentifier, Specimen, SpecimenIdentifier

### Community 417 - "DataCollectionSetMember"
Cohesion: 0.50
Nodes (5): DataCollection, DataCollectionSet, DataCollectionSetMember, DataCollection (omopdb.organization.md), DataCollectionSetMember (omopdb.organization.md)

### Community 418 - "TreeAlgorithm"
Cohesion: 0.40
Nodes (5): TreeAlgorithm (seqdb.seq.md), TreeAlgorithmClass (seqdb.seq.md), PhylogeneticTree, TreeAlgorithm, TreeAlgorithmClass

### Community 419 - "RetrieveContainingRegionCommand"
Cohesion: 0.40
Nodes (4): Command, Retrieve the regions that contain the specified regions., RetrieveContainingRegionCommand, Region

### Community 420 - "casedb/services/organization.py"
Cohesion: 0.40
Nodes (3): OrganizationService, Any, CommonOrganizationService

### Community 421 - ".get_row_id_column"
Cohesion: 0.40
Nodes (3): MappedColumn, Get the row ID column., Return the row ID column.

### Community 422 - "._validate"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate that all required fields are set after model initialization.

### Community 423 - "IsOrganizationAdminPolicy"
Cohesion: 0.40
Nodes (4): IsOrganizationAdminPolicy, Any, BaseAbacService, CommonIsOrganizationAdminPolicy

### Community 424 - "CalculateSeqDistancesForNewProfilesCommand"
Cohesion: 0.40
Nodes (3): CalculateSeqDistancesForNewProfilesCommand, Calculate sequence distances between the given new profiles and all existing…, Calculate sequence distances for new profiles.

### Community 425 - "IsOrganizationAdminPolicy"
Cohesion: 0.40
Nodes (4): IsOrganizationAdminPolicy, Any, BaseAbacService, CommonIsOrganizationAdminPolicy

### Community 426 - ".__call__"
Cohesion: 0.40
Nodes (3): Any, Transform a single object. Args: obj: Object adapter wrapping the object to…, Transform an object with error handling. Args: obj: Object to transform…

### Community 427 - "release-please-config.json"
Cohesion: 0.40
Nodes (4): include-component-in-tag, packages, pull-request-title-pattern, $schema

### Community 428 - "TestContent"
Cohesion: 0.29
Nodes (6): get_test_client(), Env, fixture, scenario_ids, Happy-path test for RetrieveIsOwnCasesCommand. Finds an org user whose…, TestContent

### Community 429 - "test_debug_console_uses_json_formatter"
Cohesion: 0.40
Nodes (4): parametrize, Path, scenario_ids, test_debug_console_uses_json_formatter()

### Community 430 - "App.handle() command dispatch"
Cohesion: 0.83
Nodes (4): App.handle() command dispatch, Command-centric authorization, BEFORE/DURING/AFTER policy phases, API functions as transport adapters

### Community 431 - "casedb SUBJECT Detailed ERD"
Cohesion: 0.67
Nodes (4): casedb SUBJECT Detailed ERD, Subject entity, SubjectIdentifier entity, casedb SUBJECT Simplified ERD

### Community 432 - "TestRead"
Cohesion: 0.39
Nodes (4): Env, scenario_ids, skipif, TestRead

### Community 433 - "TestRead"
Cohesion: 0.39
Nodes (4): Env, scenario_ids, skipif, TestRead

### Community 434 - "TestUpdate"
Cohesion: 0.36
Nodes (4): Env, scenario_ids, skipif, TestUpdate

### Community 435 - "NoteNlp"
Cohesion: 0.50
Nodes (4): NoteNlp (omopdb.omop.md), NoteNlpIdentifier (omopdb.omop.md), NoteNlp, NoteNlpIdentifier

### Community 436 - "TreeAlgorithm"
Cohesion: 0.50
Nodes (4): TreeAlgorithm (seqdb.md), TreeAlgorithmClass (seqdb.md), TreeAlgorithm, TreeAlgorithmClass

### Community 437 - "SeqClassificationForUpload"
Cohesion: 0.67
Nodes (4): SeqCategory (seqdb.seq.md), SeqCategory, SeqCategorySet, SeqClassificationForUpload

### Community 439 - "._validate_state"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate the consistency of the RefCol based on its type and linked entities.

### Community 440 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, Hashable, Model

### Community 441 - ".organization_identifier_issuer_link_update_association"
Cohesion: 0.50
Nodes (3): OrganizationIdentifierIssuerLink, Update identifier issuer links for an organization., OrganizationIdentifierIssuerUpdateAssociationCommand

### Community 442 - "test/enum.py"
Cohesion: 0.83
Nodes (3): Enum, RepositoryType, TestType

### Community 443 - "._validate_some_criteria"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validate that at least some criteria are provided, to avoid accidentally…

### Community 444 - ".__init__"
Cohesion: 0.50
Nodes (3): Any, Hashable, Model

### Community 445 - "._validate_protocol_type_dependencies"
Cohesion: 0.50
Nodes (3): model_validator, Self, Validates that the fields required for the specified protocol type are…

### Community 449 - "Default App Ports (8000/8001/8002/8010)"
Cohesion: 0.67
Nodes (3): Default App Ports (8000/8001/8002/8010), run.py quickstart command (app_type/idp_mode/repo_mode), api subcommand group (api, api_platform_local_mock_*)

### Community 450 - "CohortDefinition (omopdb.md)"
Cohesion: 0.67
Nodes (3): CohortDefinition, CohortDefinition (omopdb.md), CohortDefinition

### Community 451 - "Organization"
Cohesion: 1.00
Nodes (3): Organization, OrganizationAdminPolicy, User

### Community 452 - "Locus (seqdb entity)"
Cohesion: 0.67
Nodes (3): Allele (seqdb entity), Locus (seqdb entity), RefAllele (seqdb entity)

### Community 453 - "SeqCategory"
Cohesion: 1.00
Nodes (3): SeqCategory (seqdb.md), SeqCategory, SeqCategorySet

### Community 454 - "Locus"
Cohesion: 0.67
Nodes (3): Allele, Locus, RefAllele

### Community 626 - "env"
Cohesion: 0.33
Nodes (5): env(), fixture, FixtureRequest, scenario_ids, TestRepository

### Community 627 - "ProcedureOccurrence"
Cohesion: 0.40
Nodes (6): ProcedureOccurrence (omopdb.md), ProcedureOccurrenceIdentifier (omopdb.md), ProcedureOccurrence, ProcedureOccurrenceIdentifier, ProcedureOccurrence, ProcedureOccurrenceIdentifier

### Community 628 - "DataException"
Cohesion: 0.33
Nodes (3): DataException, NotNullConstraintViolationError, UniqueConstraintViolationError

### Community 629 - ".__init__"
Cohesion: 0.40
Nodes (4): Any, App, BaseAbacRepository, Logger

### Community 630 - "create_root_user_from_claims"
Cohesion: 0.50
Nodes (5): create_root_user_from_claims(), get_existing_root_user(), App, Dynaconf, User

### Community 633 - "get_test_client"
Cohesion: 0.50
Nodes (4): get_test_client(), Env, fixture, FixtureRequest

### Community 634 - "_PytestMockConfig"
Cohesion: 0.50
Nodes (3): Any, _PytestMockConfig, Minimal config shim needed by pytest-mock's backend resolver.

## Ambiguous Edges - Review These
- `commondb AUTH Simplified ERD` → `commondb Simplified ERD`  [AMBIGUOUS]
  docs/erm/commondb.md · relation: conceptually_related_to
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
- **421 isolated node(s):** `RetrieveSimilarCasesResponseBody`, `UnsupportedModel`, `OrganismType`, `TestPersonUpload`, `DataCmd` (+416 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **165 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `commondb AUTH Simplified ERD` and `commondb Simplified ERD`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
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