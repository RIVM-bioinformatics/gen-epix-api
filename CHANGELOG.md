# CHANGELOG

## [9.0.1](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v9.0.0...v9.0.1) (2026-07-15)


### Bug Fixes

* **deps:** update dependency slowapi to v0.1.10 ([#572](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/572)) ([b1b16eb](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b1b16eb2105d2c3050c773a591315a487556a228))

## [9.0.0](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v8.1.0...v9.0.0) (2026-07-15)


### ⚠ BREAKING CHANGES

* Lsp 3474 make upload work end to end ([#536](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/536))

### Features

* Add profiling decorator for methods ([#547](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/547)) ([27e0ff6](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/27e0ff6f7cd2633f90cf1d6664abee417e44d8a5))
* auto-create root organization in user auto-creation flow ([#557](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/557)) ([6173881](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/61738815d758f2abf206ba40af4d91f55e5ebc08))
* **caches:** add app-level cache invalidator registry (LSP-1829) ([#576](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/576)) ([2fe65c3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2fe65c3d188c0913c3c58a1c8329284eea185fe4))
* Lsp 3474 make upload work end to end ([#536](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/536)) ([c0f26f3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c0f26f3913317669017f883f3e649fe793036af1))
* **LSP-911:** Implement new endpoint to check is_own_cases for multiple case_ids ([#567](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/567)) ([4e87c54](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/4e87c54baea378eb3fe8aebe481e7b2237b47c7d))


### Bug Fixes

* **casedb:** prevent derived values from being overwritten during age-category update (LSP-3417) ([#566](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/566)) ([3f9acc7](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3f9acc7c3ed8924c82455874fff6289756dbcf9b))
* **casedb:** use highest-resolution date available for case_date ([#545](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/545)) ([d3a969b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d3a969bcc5feecc33e6f64c2b2ec417cd07ea4ed))
* **ci:** always start from a clean venv on cache miss ([#549](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/549)) ([eae0550](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/eae0550ad5f10b3452ee30d951d75a102dbda02e))
* **deps:** remove outdated cryptography dependency ([8ddac28](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8ddac28c6306f9cded890e960f971f444f219fff))
* **deps:** update dependency cryptography to v48 [security] ([#542](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/542)) ([ca6a29f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ca6a29f712156f1481c5d2ac9eb8d13102c0639f))
* **deps:** update dependency pyjwt to v2.13.0 [security] ([#539](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/539)) ([dde6d19](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/dde6d1983b76ca951871f28b80d98315c38652c2))
* **deps:** update dependency python-multipart to v0.0.31 [security] ([#538](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/538)) ([4c3b7d1](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/4c3b7d17fffbe4e9125965e3b4dfeff4adbe1fac))
* **deps:** update dependency starlette to ==1.3.* [security] ([#540](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/540)) ([f220e8f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f220e8fd03ac4dc26a2dde38573bddc5af40f086))
* **deps:** update dependency urllib3 to v2.7.0 [security] ([#541](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/541)) ([d695b02](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d695b024ce7057ac603203dc95ca3cfaca07e321))
* Resolved error in phylogenetic tree construction ([#565](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/565)) ([2df76f4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2df76f4c6ecd9e31255fde389c8547efdfaee7aa))
* **seqdb:** skip content_hash check when hash is server-computed (NULL_ID) ([#546](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/546)) ([c4fcbc3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c4fcbc34303673b061a7d3f8b858624cc8b857e8))
* Update operation type for data collection check ([feb6222](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/feb6222c8eb07a07691ad612561e9bd1f4f2f717))
* use checkfirst=True in SARepository.create_all ([8daad11](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8daad119e824b48c0f587919cb265aee15ec1d60))
* use checkfirst=True in SARepository.create_all ([#556](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/556)) ([6433445](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6433445b7425e8dbd98b6ad3b4c2fd4d7331749e))

## [8.1.0](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v8.0.0...v8.1.0) (2026-06-15)


### Features

* Add case_set_date field to CaseSet model ([170e42e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/170e42e2962337db9e44f02bb87bfe92009249bf))
* Add default timeout for CalculatePhylogeneticTreeCommand and RetrieveSimilarProfilesCommand ([#534](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/534)) ([3b52408](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3b52408e6e574d06154137b2f0ba5f72f753a2e0))
* Add method to filter SeqProfiles by quality control result ([#495](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/495)) ([310fad2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/310fad2c4b6b869b378070ed88cc284eef0f06dd))
* add permission types for RegionRelation and TreeAlgorithm commands ([#492](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/492)) ([724672b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/724672b022d591c0bb82c7b8a8c7509ae946cab7))
* Add unique code to DomainException and derivatives ([#503](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/503)) ([b426292](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b426292414406e330ccff39b2ac278eb2734ceda))
* added abac commondb endpoints; WIP not tested ([#517](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/517)) ([841d6d9](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/841d6d9258441280290f0e2502c2bd2498014903))
* **casedb:** LSP-3206 added Case.cohort property and corresponding functionality ([#526](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/526)) ([28b12d7](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/28b12d79004288f02782fff4d07473cb1f0f7975))
* commondb EtlLogItem source and target trace variables added; WIP ([4f96bef](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/4f96befacd7045582cbe98167d1d362cd071ffa5))
* commondb EtlLogItem source and target trace variables added; WIP ([c51a27b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c51a27b6d99ff4309e69b824c174b57c1453649d))
* **commondb:** intra-parent link functionality added ([e3041f3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e3041f38e70e62225bcdcda3c5e35abbdceee15e))
* fastapp Domain.get_dag_sorted_services and Entity.topological_sort added ([#504](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/504)) ([fb226b9](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/fb226b98e7c822050f28b3857276ad8e273324c9))
* fastapp RemoteApp added mechanism to set timeout per handler ([#507](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/507)) ([a27c5c4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a27c5c4e6bf3b6376b517225a7516e30e1fd591c))
* **fastapp:** log_cmd_object_on_error property added to App ([e3041f3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e3041f38e70e62225bcdcda3c5e35abbdceee15e))
* Implement RetrieveFullPersonsCommand and related service methods ([#494](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/494)) ([41c3a1a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/41c3a1a27952d1184fea0eac4188e68ab681302f))
* Implement SNP Profile support for uploading and calculating seq-distances ([#508](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/508)) ([03c342a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/03c342a83fa4b256bcdb5da9db40a8db46fc0df4))
* Incremental processing: limit and existing_chunk_size parameters for bounded memory and HTTP timeout control ([e3041f3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e3041f38e70e62225bcdcda3c5e35abbdceee15e))
* Introduced new UpdateSeqDistancesCommand and refactor SeqDistance calculation ([#493](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/493)) ([0e4afc0](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0e4afc069b767cddbc645d9a9f37e6622a5deb1b))
* Lsp 2348 add pagination to standard crud get all endpoints ([#527](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/527)) ([aa6a386](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/aa6a3862a597bcac15f54f6588c3d5a189e76e4f))
* Lsp 2914 create omop geo data ([#489](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/489)) ([704d0d0](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/704d0d025a038d8ef0c2b0efe16102138c286bfb))
* Lsp 3213 create local dockercompose setup for testing batch uploads with lsp data ([#502](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/502)) ([8469669](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8469669ca89ba908f18b39b452f49ae82604d9f0))
* Lsp 3213 upload batch to casedb ([#501](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/501)) ([e9e3478](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e9e3478e7905bac2f13350b0e9127b42061b5f4e))
* Lsp 3229 add salmonella order type 43 part 2 ([#511](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/511)) ([4f96bef](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/4f96befacd7045582cbe98167d1d362cd071ffa5))
* LSP-3298 Fix end to end data flow in DEV ([#521](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/521)) ([e659a71](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e659a713420fac633f0a262e43900e371c5a4fdf))
* omopdb Measurement added field validator; minor fix in TupleTransformer ([#486](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/486)) ([e290bf5](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e290bf5453b1b0257b29acd75d457fcee5730284))
* seqdb added /retrieve/samples_by_ids and _by_query endpoints ([#499](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/499)) ([04bb8d4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/04bb8d484139674fb8eb2e77b51c4120e459b6e6))
* seqdb added RetrieveBestSeqPerSampleCommand, RetrieveBestSeqProfilePerSampleCommand; not tested ([bc9950a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/bc9950a689546f605fee61713a3fa452c1c7e250))
* seqdb added RetrieveBestSeqPerSampleCommand, RetrieveBestSeqProfilePerSampleCommand; WIP ([626557d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/626557da162d61fee59e03c1ec3da9ba7c139bfb))
* **seqdb:** add RetrieveBestSeq{,Profile}PerSample handlers to SeqdbRemoteApp ([619ee7f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/619ee7fcd765dcb498c9d1d10bf85ffd47a3b613))
* **seqdb:** upload adds verification of intra-parent links and possibility for temporary IDs to allow within-batch intra-parent links; child objects are matched on their natural key as well ([e3041f3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e3041f38e70e62225bcdcda3c5e35abbdceee15e))
* transform TupleMapTransformer.get_row_key added ([4f96bef](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/4f96befacd7045582cbe98167d1d362cd071ffa5))
* transform TupleMapTransformer.get_row_key added ([c51a27b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c51a27b6d99ff4309e69b824c174b57c1453649d))


### Bug Fixes

* add best_seq_per_sample methods to service ([ae83e1c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ae83e1c761b748f7b472e0d9cf8288fb3999bc38))
* added stubs for missing _validate_content implementations ([31e3bb9](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31e3bb943df493f33a280a67ef25f4038c2497b8))
* allow deletion of SeqProfile; prevent DNA sequences from flooding logs on errors ([e3041f3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e3041f38e70e62225bcdcda3c5e35abbdceee15e))
* **casedb:** look up existing case content by id when merging on update ([48ca140](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/48ca140becd21fdfd800ac95f1cb9a474b039ee2))
* continue if parent_id is null or null_id ([23b5aeb](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/23b5aebca9cf9bd7cbf31c783d3c618d8ca4b445))
* cryptography==46.0.6 to solve conflicting requirements. ([ac385a2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ac385a275f8224ca7318a0d1e32b8d292a31169f))
* **deps:** update dependency biopython to v1.87 ([#487](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/487)) ([e904812](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e9048120942ff96e45a0b4225374fed5daa4f57f))
* **deps:** update dependency numpy to v2.4.4 ([#485](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/485)) ([d203c42](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d203c4252da05c7b34d72d8d76c124d51c9e7ff7))
* Disable early max results limit in case_service_retrieve_cases_by_query ([0278579](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0278579401c8785d2fa4b96a1372e1e952d0a0d2))
* disable rate limiting with env var RATELIMIT_ENABLED ([1fc11d1](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/1fc11d13ac0e88485cd010921061dc4f8d6368a3))
* duplicate key user in UploadSamplesCommand construction ([b224fb0](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b224fb020e77c70e1056abc1a5bb6729c16841fd))
* error message referenced non-existent attribute ([52e8a4c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/52e8a4c770521b160c3f1dac0e1f7db640114e5c))
* fix case abac check in upload.py ([96d6a3d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/96d6a3de34c4f2a017cf54c42cbcc0b53011e474))
* fix case abac during upload ([3f0597b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3f0597b300d07682b51c8cc2c8f655820db45467))
* fix typo in HealthResponseBody ([7d3206e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/7d3206ee5af40edb83e86decfc5d0840934dac92))
* **LSP-3225:** fixes for uploading SampleForUploadBatch to SEQDB ([#506](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/506)) ([85cecb3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/85cecb3367b913df203459e5e1eb0e1396c9f966))
* **LSP-3275:** enforce immutability of case created_in_data_collection_id on upload ([#524](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/524)) ([04f4f91](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/04f4f91516c9fe72172a1020675fb1b02e8bf700))
* **LSP-3356:** make case_date mutable and remove None reset on update ([#522](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/522)) ([9c7792f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/9c7792fca09113cb5545512c7400739e0f387647))
* **LSP-3367:** pre-validate SeqCategory FK before SeqClassification INSERT ([#525](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/525)) ([172ddc2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/172ddc23f4be39a9d71a930f8d67f003511b81c3))
* missed one location to skip null parent ([a2a9ff3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a2a9ff3818b26b422205c896bd3197e076df9ab7))
* overwrite in loop caused always empty return value ([b241817](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b241817066584bf86e6e21506baa485a9a4604e2))
* replaced NumberSetFilter for StringSetFilter for string column ([d23a76a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d23a76a7eb75d433836cb927166897f19a9c95d6))
* Resolved bug in upload process where the child-id was not being passed to the ForUpload class ([e04e1a4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e04e1a42d006151a4867ba9ac97f3d367c7b3463))
* return as dict which the casebuilder expects. ([83a8254](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/83a8254822442630aacf91fa7c2ebba9e7e5c06a))
* seqdb SeqProfile key removed ([4979333](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/4979333cdf7688c53bed40caa952ad4a9d358ee2))
* **seqdb:** treat protocol_ids=None as "any protocol" in retrieve_best ([724bca4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/724bca40775f7f00a4cbd3d1b000bc3212750958))
* set_envvar() for api_platform_local ([6052b2d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6052b2ddfa13f544327da02d05b8722df43055da))
* space got introduced in merge ([8b00269](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8b00269efeab789685860732d85bda027cf47cf4))
* SQL NOT EXISTS scan: push missing-distance profile lookup into DB, eliminating Python set-difference over 10k+ UUIDs ([e3041f3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e3041f38e70e62225bcdcda3c5e35abbdceee15e))
* Temp-table JOINs: fix ODBC 07002 on uniqueidentifier IN() for iter_seq_distances, get_profiles_by_protocol_ids, and retrieve_similar_profiles ([e3041f3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e3041f38e70e62225bcdcda3c5e35abbdceee15e))
* upload of seqdb sample batches ([85cecb3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/85cecb3367b913df203459e5e1eb0e1396c9f966))
* warning that was annoying me ([#512](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/512)) ([2af2c2e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2af2c2ef9ca15fb5bd3296aec6093695844677a9))
* when qc_result, set default (PENDING) if it is None ([fb7458e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/fb7458e929af95b71b4cd3fbb0ba570d6af61695))

## [8.0.0](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v7.1.2...v8.0.0) (2026-03-30)


### ⚠ BREAKING CHANGES

* Lsp 3031, 3032, 3045 minor fixes and adjustments to data model ([#450](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/450))
* lsp-2971 rename dim/col to ref dim/ref col and case type dim/col to dim/col ([#425](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/425))
* LSP-2730 casedb retrieve commands now consistently require case_type_id ([#342](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/342))
* casedb retrieve commands now consistently require case_type_id
* add general framework for upload with implementations for seqdb and casedb ([#313](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/313))
* major update to seqdb models and other functionality ([#234](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/234)); many other feature branches also merged first through this branch
* add case type dim persistable model ([#269](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/269))

### Features

* add case type dim persistable model ([#269](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/269)) ([faf3870](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/faf38705db58500cb8d8fc71e84958ec1d374b56))
* Add file hash computation for ReadSet/Seq objects on File creation ([#247](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/247)) ([56ba268](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/56ba2684f4a96b8ea26b27182c5cd37fae2643df))
* add general framework for upload with implementations for seqdb and casedb ([#313](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/313)) ([059ef4f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/059ef4fc98c70d82b08c92f26cab96a2176b1080))
* add gzip middleware ([9290af0](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/9290af0fccc3cbf6647bd4b594be5877c797c880))
* add hard timeout for root ([#408](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/408)) ([cc30e71](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/cc30e71c0e02e445711d17e729a98007ec8240a5))
* Add org-specific abac rules for Crud Col and Dim ([#420](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/420)) ([107ff4b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/107ff4b25f05362ac37bccfc248c92bf7d5c2ac9))
* add tls ingress settings ([#308](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/308)) ([972b67c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/972b67c15c32c4cfc73a8a0c29fa393f91f752f4))
* added /organizations/{organization_id}/identifier_issuers endpoint ([#277](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/277)) ([996a2c9](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/996a2c94fbcf7f2d7adbc87d9796548d209d8ff9))
* **auth:** Created retry mechanism for IDP client initialization ([#235](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/235)) ([85d86f9](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/85d86f96031f9a146b3a9d7c3e0c8b6d609f0040))
* casedb CompleteCaseType extra settings; some fixes and refactoring ([#242](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/242)) ([46d0e5b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/46d0e5b06f4047bc064a5401075ec3fca489247d))
* casedb retrieve commands now consistently require case_type_id ([4d26698](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/4d266987928ecbc0ab040339e6d7727b4f00d291))
* create platform-level launch configs to start multiple services ([#351](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/351)) ([724a223](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/724a2236702afa488a5c5c7c3de1584f1a019ba8))
* feature flags ([#435](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/435)) ([6d84c3f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6d84c3f5cff25fc7dec673576fb43f8847c682d0))
* Implement TokenIntrospectionManager for OauthIdpClient ([#245](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/245)) ([b19d665](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b19d6655712f6a73f8f0cbe631349ac6bbd964ab))
* Implemented GetSimilarCases functionality ([#362](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/362)) ([697c90d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/697c90da095a3892ca4418af21a53b6612207a1d))
* initial upload models added ([#289](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/289)) ([8340692](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/83406926be33cab1a712823a6ce4b14ccc6214cd))
* Introduced new CommonServerManager ([#243](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/243)) ([0093a36](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0093a36ed71443ae31e9f1f63328e84cd123aab8))
* Introduced new Protocol model to replace all existing protocols ([#467](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/467)) ([cdec47d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/cdec47de04b14d1fbbc146d184c2d5491cef228c))
* Introduced SeqDistance update logic for uploading new profiles ([#388](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/388)) ([0572b21](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0572b21019b625e78908546ab1fbae4b4f228cc7))
* Key optional in UserInvitation and other related models (backup) ([#421](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/421)) ([99d2a92](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/99d2a921d1172249b69b0721febee4afe59e7ed7))
* **logging:** Add Uvicorn loggers to logging configuration ([52049ee](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/52049eebbc4fdd2453577689f9aa79a5829f9ebf))
* **logging:** Add Uvicorn loggers to logging configuration ([#396](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/396)) ([6679aeb](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6679aebb41a4295a5ec5f4d7cc50934398900e70))
* **logging:** Add UvicornAccessLogFilter for structured HTTP logging ([9d43741](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/9d43741e9c3db7291d0efa8797eaed3482f0986d))
* **logging:** Add UvicornAccessLogFilter for structured HTTP logging ([#398](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/398)) ([75a08e2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/75a08e2bc63dad3c93027f670271f410b9e7b417))
* **logging:** Enhance JSON formatter for improved logging ([022d991](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/022d991ff0f22f454f3a038601517b8e964ae3f8))
* **logging:** Enhance JSON formatter for improved logging ([#397](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/397)) ([3ec396b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3ec396badd1f1646fe0cdbfa83ecde60fc7ddeb7))
* **logging:** Enhance JSON logging to redact nested claims ([dbe4886](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/dbe4886650f1823bd506b6306b2d10eb23bb145f))
* **logging:** Enhance JsonFormatter to support app lifecycle messages and operational ID aliases ([d043e52](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d043e520244b6e65bb88a883410960f7c1893c2d))
* **logging:** Enhance logging configuration for third-party loggers ([58c27dd](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/58c27dd4f415fda483ae3608cbd468d25d59a7bd))
* **logging:** Enhance Uvicorn access log message formatting ([133e480](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/133e480732b7f96aa7b856495376d08bd2da75e6))
* **logging:** Enhance UvicornAccessLogFilter to enforce JSON formatting ([e86074d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e86074dc88f65a9bf6242488381a9445f3fefc27))
* **logging:** Enhance UvicornAccessLogFilter to enforce JSON formatting ([#414](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/414)) ([822db20](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/822db208eb200ef650fe59591e3409f75df8c725))
* **logging:** Implement JSON logging formatter for structured logging ([8fb9cc4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8fb9cc43cf2486ab45bab09cad5154d4e3ce0b0e))
* **logging:** Implement JSON logging formatter for structured logging ([#394](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/394)) ([c30e4ed](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c30e4ed52a87f6d833867f6b1d7e9b94318bdc04))
* **logging:** Update logging configuration for third-party loggers ([61a3f5c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/61a3f5c4b094b950902415ce3ac83f91e93f5007))
* Lsp 2730 genetic sequence download functionality failing ([#352](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/352)) ([617e474](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/617e47464768b0be502010258df9bf09d5d50b94))
* Lsp 2886 update design of iles transformer class ([#411](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/411)) ([d5a5a09](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d5a5a09a5a055c34a38e682c5bd3644d9cd04f8e))
* Lsp 2974 replace is new id by cmd.on new ([#419](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/419)) ([d678b45](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d678b454489773e9ac0b7e773a9a8e7731dd58e6))
* Lsp 3015 replace external identifier with identifier models ([#429](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/429)) ([8d706d6](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8d706d60eb590befbe4bca3117641e7391b8f20f))
* Lsp 3031, 3032, 3045 minor fixes and adjustments to data model ([#450](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/450)) ([980b760](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/980b760cf52dcd4e6187c295e437b845a471aa6d))
* LSP-2730 casedb retrieve commands now consistently require case_type_id ([#342](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/342)) ([af80162](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/af8016211c5bfd5395bc73f5f86a130bb3d6d69a))
* LSP-2750 improve case type stats performance ([#346](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/346)) ([e2f1258](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e2f125871c2a8f404cff635d2fab3cad28e7fe15))
* LSP-2961-improve-http.access-logging-for-Grafana ([#403](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/403)) ([bf5138d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/bf5138dd944888a2e6b01f1ddeb2960548312808))
* LSP-2962 add provided_by_organization_id to omop entities ([#454](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/454)) ([1d602a8](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/1d602a859aefdba848abd085fd9ddaf11adf022d))
* lsp-2971 rename dim/col to ref dim/ref col and case type dim/col to dim/col ([#425](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/425)) ([21a7a97](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/21a7a97cdd4dfadb166433d30a95e61639bc68a5))
* LSP-2985 omopdb returns SKIPPED for empty batch and verification_only ([#434](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/434)) ([b27d720](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b27d720f4e804dddcdd2525771f6db9810adfe6f))
* made Person.person_id immutable and skipped attempts to update it ([b8af867](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b8af867b2523d08de3842fcaee58c5ed109ac246))
* major update to seqdb models and other functionality ([#234](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/234)); many other feature branches also merged first through this branch ([8089945](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/808994516f9caccab93da4804c636c9222622cd3))
* move retrieve_organization_contacts to commondb and refactor to only read contacts by organization_id ([#392](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/392)) ([bfcbca6](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/bfcbca675f7fa77189b2267bbeba55571ef8bd62))
* omopdb OmopdbRemoteApp added ([6007e4a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6007e4a845d25fce9d7ad160aec59049a83f3c20))
* **omopdb:** Implement person upload functionality ([#377](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/377)) ([a1602f4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a1602f40c8598762753610ae73a4b315c97d25cf))
* remove ABAC from case_type_set, case_type_set_members, col_set and col_set_members ([ba434bc](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ba434bc577dd7eb7a8917ecbf96063277f6187af))
* seqdb added UpsertCompleteSamplesCommand stub ([ee9d17e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ee9d17e6c24a38812b2da4efaf38f6ad8328fdcd))
* **test:** Add smoke tests for app import functionality ([640e66c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/640e66c8b42739e3bc1b9b29661fcecf478e59bd))
* **test:** Add smoke tests for app import functionality ([#437](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/437)) ([592c6f9](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/592c6f92f129749e2605cf57b7ab0027f0478e85))
* **testing:** LSP-2926 add pytest gremlins for mutation testing ([#382](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/382)) ([d4164f3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d4164f3eea77a4fbb82f20827428d181f1c8a55b))
* transform updated TupleMapTransformer to make it more generically applicable ([#380](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/380)) ([ce86902](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ce8690246208fc07a1c6d309da9b7e2934604c55))
* **upload:** cascade status conversion to child and identifier results ([2364293](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/23642930f7483f9dc6f0aacf1a6b518c910cf01a))
* Uvicorn to use same logging strategy as FastAPI ([#395](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/395)) ([d7aae5e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d7aae5e4d16407598da994713650e9129b88053a))


### Bug Fixes

* ! unpack SA row before loading Seq mapper in retrieve_seq_fasta ([cea15a2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/cea15a24dbabb1b039816a4cb374e4b3bf09ba36))
* add command.RetrieveFeatureFlagsCommand to NO_RBAC_PERMISSIONS ([49e2243](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/49e2243659343a8d6fb9d5c1e0b953073579fe8e))
* add Content-Security-Policy-Report-Only ([6ebcda4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6ebcda46a050ad361a6567a3cc390ce060e9f7ba))
* add parent id to parent class in upload.py ([7f7ef3c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/7f7ef3c624a748a8aa3305edb1dce0416bb9656d))
* add token_time_to_live for root users in get_existing_user_from_token ([f1ab471](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f1ab47193df1bd82ab6c72be8af930480de1e9ab))
* add UserInvitation.key field validator that sets the key to None if an empty string was provided ([b02f5f4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b02f5f4709fb48d3b8defd7653d6222598681b0a))
* Added pytest-xdist to prevent internal error during testing ([155dfa7](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/155dfa7e4dbf10f76e50f18be8615c89e9a04120))
* allow to configure ssl_context in idp config ([3821f06](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3821f06663d12350773903d4b6be12ca83c48c93))
* casedb case type and case set stats fixed ([#295](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/295)) ([ae1ff53](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ae1ff53a9ed6bad1a950509f3c006740f1ddee9c))
* casedb some read permission fixes ([#347](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/347)) ([b9f690d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b9f690d645f50e8f6ee30e74eeb0deb3e5f744e7))
* casting HttpProtocol from string ([6c30b9f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6c30b9f3828f86b75ebe0d86919fc49b72f2a5d0))
* commondb circular import with util module ([#370](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/370)) ([640f32c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/640f32c86f66f62e81997073c44284c2d901a751))
* commondb oauth IDP client init correctly receives ssl_context ([2fa8b89](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2fa8b89a72ad9738ea6de0166247a6e1078c9816))
* commondb only relevant user invitations are deleted ([#476](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/476)) ([fe6eb79](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/fe6eb79b24b59f840c31e565c8d7544c2dee0a18))
* convert dynaconf values to correct types ([54ce9dd](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/54ce9dd2ccc084693aacad3799ff6fd780d97118))
* convert dynaconf values to correct types ([66e6672](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/66e667260818953e25771c64ccc801a720a51a7d))
* Corrected import statement for ParentUploadResult that caused a bug in idsdb repo ([a059104](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a059104910e749d07c2c71deabfddf8b30bda2eb))
* create IntEnumWithJsonSchemaMixin and appy to all IntEnum's ([96b3dd8](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/96b3dd8a7ed5119c273f22ad772e9d53b795ceb1))
* create_sec:_create_file returns ID instead of file object ([6e14d84](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6e14d84a9039d01e0eca89747bfa88fa58ea0962))
* **deps:** update dependency cachetools to v7 ([#376](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/376)) ([f213730](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f213730686647347d36be00e4c71bd9ead48a417))
* **deps:** update dependency cachetools to v7.0.2 ([#405](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/405)) ([3e2f47a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3e2f47a02605baa2a973104dc62556378404a50b))
* **deps:** update dependency cachetools to v7.0.3 ([#418](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/418)) ([c1d3e5e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c1d3e5efa383b0916b380ca0d89854922924e31f))
* **deps:** update dependency cachetools to v7.0.5 ([#426](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/426)) ([6d7acfb](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6d7acfbccb68767c6a358e5904c7b1869aa6bf6d))
* **deps:** update dependency dynaconf to v3.2.13 ([#464](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/464)) ([e3af9a8](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e3af9a8ee8591399a9d0c15b79d902dcba98dc0f))
* **deps:** update dependency fastapi to v0.129.0 ([#374](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/374)) ([72b35eb](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/72b35ebaac924544978c0f1e5fe86aa172924133))
* **deps:** update dependency fastapi to v0.134.0 ([#389](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/389)) ([9bb8247](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/9bb8247aa7916bf0036c43c95297f526c1e8ba19))
* **deps:** update dependency fastapi to v0.135.1 ([#401](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/401)) ([ad19597](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ad195977cc9774289922704ab86852c706b528c8))
* **deps:** update dependency fastapi to v0.135.2 ([#472](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/472)) ([2480c7c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2480c7cec17a9ac302f1c54e3c393cce25338305))
* **deps:** update dependency gunicorn to ==25.2.* ([#474](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/474)) ([9a7ebfb](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/9a7ebfb1d8d86fd7611568981703dbf9bc86d2a1))
* **deps:** update dependency gunicorn to ==25.3.* ([#479](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/479)) ([cba0daf](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/cba0daf17fced97b58294b1c98150b488f95bbe6))
* **deps:** update dependency gunicorn to v25 ([#357](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/357)) ([b6fbb16](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b6fbb160f5386840fcf95a19502f6e92d7b6df2b))
* **deps:** update dependency numpy to v2.4.2 ([#356](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/356)) ([8dcf833](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8dcf833310b4dc02a4d8a6d9d4490de798688738))
* **deps:** update dependency numpy to v2.4.3 ([#427](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/427)) ([b7f9fcc](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b7f9fcc04c90a7c6fff340b3dd47ae6a9bdab0ee))
* **deps:** update dependency pyjwt to v2.11.0 ([#355](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/355)) ([07b419e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/07b419eabccc8844a3f28b5baeaeb1b2fce704f7))
* **deps:** update dependency pyjwt to v2.12.1 ([#480](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/480)) ([899cd14](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/899cd14559d90d1cab4db4f74b801c9f15f77208))
* **deps:** update dependency scipy to v1.17.1 ([#390](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/390)) ([11ffade](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/11ffadece00037c4f91640e54cd082b433560650))
* **deps:** update dependency sqlalchemy to v2.0.47 ([#391](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/391)) ([118a57a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/118a57a23bbb6eceb5bebddb17c49b56d81ed688))
* **deps:** update dependency sqlalchemy to v2.0.48 ([#404](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/404)) ([8580801](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/858080193693d95f78b566fdef48f95aefcd7b68))
* **deps:** update dependency starlette to ==0.52.* ([#339](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/339)) ([b055e3a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b055e3adf74da1cb8849dfdd53f53089cf093d05))
* **deps:** update dependency starlette to v1 ([#470](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/470)) ([e8095f8](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e8095f804322aff714134d646ea0af42a6f3267d))
* **deps:** update dependency types-setuptools to v82 ([#386](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/386)) ([2ab6892](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2ab68923b878035b8239424f96ceb779b1606226))
* **Dockerfile:** Security issue with OpenSSL ([#443](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/443)) ([a926e7d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a926e7d906c5420cb14dfeabba79f9cb5e64b3ee))
* empty fasta files when downloading sequences ([#248](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/248)) ([78899f9](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/78899f9066cca428f99e03fb6357c76af3eea064))
* Enhanced http(s) protocol property to correctly handle enum and strings ([eee4ad4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/eee4ad467a81184e0ffe22720017fb966907ae9e))
* fastapp.Domain.register_command minor fix ([6007e4a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6007e4a845d25fce9d7ad160aec59049a83f3c20))
* filter case_sets correctly ([fe338e0](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/fe338e0c35175b059703f40f120ed31122f4bdac))
* fix _retrieve_case_sets_with_content_right signature and remove invalid_case_set_ids check in case_service_retrieve_cases_by_query ([8e00e5b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8e00e5b146179b8bafa1c7e10b5433a29cb795b4))
* fix case type props in case type model ([3691013](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3691013cea5008aa6e54da0e593f6b795e73a180))
* fix DimColTypeSet - add NOMINAL to NUMBER set ([19eb5d4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/19eb5d40a04d2899f4cdeace9f977fb754e95aff))
* fix DimColTypeSet - expand OTHER ([1589642](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/1589642c088c785f98902e0f788964cf7bce77b4))
* fix etl by dropping tables and schemas ([#329](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/329)) ([1eb7d20](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/1eb7d20d525b05c2117ee82eef800bfe7f97f377))
* fix loading case type stats for abac full access ([5652504](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/5652504483cf4d4030ba6113220a5de6481f711e))
* fix loading the automatic_new_user config when config is epty ([3f17b92](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3f17b92eb5cc7cba7feb20de07670e7022d3b027))
* fix omop etl by fixing NoIdRowMetadataMixin id (primary_key=False) ([66b9685](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/66b9685c40b3f60cd0d259ee1286d1207811930c))
* fix retrieving case type stats ([065b556](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/065b5569c76bc8a515936b133a652f71a56f5c01))
* fix unit tests after feature flags merge ([#442](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/442)) ([65f340a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/65f340a5632bfcaf502f54ac4c174435ef6ac368))
* Fix url construction for fastapp remote_app ([0d767d9](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0d767d94c18e5a53b34cddb029f774c5d9f872bd))
* Fixed a bug in SeqdbRemoteApp where fasta files where empty on retrieval ([#244](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/244)) ([dac1a20](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/dac1a2090ed3b06e73ac0feb944b82faf6e9b9ed))
* handle seqdb_command.CreateFileCommand correctly ([5a3c4da](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/5a3c4da4564de20443bc71bf38c6b936c0dc0f76))
* in retrieve_case_set stats, filter out  unauthorised cases ([bad4a8c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/bad4a8cba49019466cd0a9bd766efd694dc063c1))
* in user invitations a key with an empty string and a key with None should be handled as the same ([1d3a2b3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/1d3a2b3b5503516e6e0c6b3eb52cec04ea9c59ce))
* insert read_set id and seq id into content after uploading samples to seqdb ([430ef1c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/430ef1c9191e060c9aab7f5568f3799381919ea6))
* Invalidate retrieve complete case type cache on CaseType CRUD ([b6c3800](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b6c3800cca05d4c796014191f535180dc0212a01))
* log ServiceException with stack traces in command mediator ([#369](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/369)) ([10413cf](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/10413cf380e8587384b3e22f970e576865638f55))
* **logging:** Correct logger names in logging configuration. Fixed typos in logger names from 'opomdb' to 'omopdb' ([e7e7976](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e7e7976c27a68df4cfd09a743566019fcd694a79))
* **logging:** fully redact sensitive bearer authorization in logs ([0e8d6b4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0e8d6b4658f36bef807eeff685a3e4d5495508cf))
* **logging:** preserve service metadata and redact auth-sensitive fields ([3f640b4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3f640b44d430a75ee54ed27c3abc330ef917b3ac))
* LSP 2644 fix sonarcloud issues ([#319](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/319)) ([79556b5](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/79556b50f9004fffe0e07f8f46022190e8b89986))
* Lsp 2811 fix retrieve stats ([#402](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/402)) ([348e82c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/348e82c92ee91981e29cfa947c3ca41dec255680))
* make client_id and scope optional when public=false, add validator for when public=true ([7dede9d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/7dede9d2878fe1170b5b0f2af1c27ac05a0b7e8f))
* **mypy:** resolve duplicate module resolution for docs.erm.erm_hash ([7049ab9](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/7049ab937e70085ca0237320d999c72e1be371b0))
* permission for OrganizationSetCrudCommand ([#484](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/484)) ([2016522](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20165220d5b40af84a4777d9179d20717265ada7))
* prevent key error in retrieve_stats.py ([3d2e708](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3d2e7080c84f214990e87be6121d8d75ce5c1c1b))
* propagate cmd.on_exists from case upload to sample upload verification ([a553aff](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a553afffb5fe0f85c57884cba51339efc3ba2b35))
* **remote_app:** Correct route handling for command registration ([00651fa](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/00651fa776f485b1bd624eb58bbc7dccb6a06ee2))
* remove command.RetrieveOutagesCommand from permissions (doesn't require RBAC) ([12e3f59](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/12e3f5941ea21992dbca5b1f9634929d24a7e221))
* Remove SSL context max/min TLS that caused a bug ([d14be7c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d14be7c88b201d5812037f2fef50ae8f37e9652f))
* rename profile_id to seq_profile_Id ([beea2ff](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/beea2ff58ea45c7c2ff19e5f88d46da68cc841b7))
* Resolved all test failures after sonarcloud branch merge in dev ([#348](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/348)) ([e3f53fb](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e3f53fb46c8de670ea42f828c630ff01e3bc5c04))
* retrieve case type sets correctly in _crud_case_type_set_with_abac ([e1b8bb0](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e1b8bb036e0cf7010c26b6030821e4dcd2e9024b))
* set max_length for case type description to be 8000 (to prevent SQL Server error, where max length of 10000 is exceeding the maximum of 8000) ([297664d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/297664db017d44e305d3ba924d76086bd57ff748))
* set root_token_time_to_live to 0 during development (disabling the root_token_time_to_live) ([894e7ee](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/894e7ee66ec2195f458ccefe49c2af8aae21b3fc))
* time dimension should always derive from the highest resolution value first ([#276](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/276)) ([d9225e5](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d9225e5beffd9e3a7a3093ff0ad984b158ca2aba))
* update base route handling and change default id_present behavior ([#460](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/460)) ([c1f34cd](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c1f34cd99370a74bec961b96765a424c5de5ce1e))
* xdb auto-creation versus sign-up of new users ([#430](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/430)) ([69ea7bf](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/69ea7bf82f8649a1d5f63ffe8306cf96fa0d599b))
* xdb upload on_exists=ERROR log is now assigned to each existing instance ([#331](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/331)) ([91a013c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/91a013ce7030ea2e33151e118df56f4d63f12a00))

## [7.1.2](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v7.1.1...v7.1.2) (2025-11-28)


### Bug Fixes

* make file_content in request body of type string instead of bytes ([0af71e4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0af71e438eea3e507b99f81ff9503a0e29007e7f))

## [7.1.1](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v7.1.0...v7.1.1) (2025-11-28)


### Bug Fixes

* commondb /update_user added ([#239](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/239)) ([c469517](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c469517351cd6e25f82a27ee49cbf7fec4ebd0a1))

## [7.1.0](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v7.0.5...v7.1.0) (2025-11-28)


### Features

* add file crud endpoints to seqdb ([5b6d9a3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/5b6d9a3c1654ffc24fed6bc14cd7824015d1e935))

## [7.0.5](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v7.0.4...v7.0.5) (2025-11-27)


### Bug Fixes

* fix dependencies ([9c23e3f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/9c23e3fc2c4f811b5f38c7be0581f992844b83a4))
* remove alg check from token validation ([49faed7](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/49faed74eb0d3ab302a9023f3d11425e283e3516))

## [7.0.4](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v7.0.3...v7.0.4) (2025-11-21)


### Bug Fixes

* make release work again (9) ([4ec58af](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/4ec58af9b9dc2eab7dd899d7ec41bc69afdb1a10))

## [7.0.3](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v7.0.2...v7.0.3) (2025-11-21)


### Bug Fixes

* make release work again (8) ([03831e3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/03831e3d1c0a2b32c4302679008f218d59235f0f))

## [7.0.2](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v7.0.1...v7.0.2) (2025-11-21)


### Bug Fixes

* make release work again (3) ([c289fb5](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c289fb5fa3f4337aec0c82d2b40abaf54e46e808))
* make release work again (4) ([433a2b8](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/433a2b8144e5bdc4b9925191ca811614e1dc9716))
* make release work again (5) ([14568dc](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/14568dc3827c93a647b21ee0e566817ee9461b55))
* make release work again (6) ([af1e589](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/af1e589c2e303dbee1308e1fbdc10010682bfe42))
* make release work again (7) ([de61f84](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/de61f84c99df08edd4a180df25788fd77fe8aaf1))

## [7.0.1](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v7.0.0...v7.0.1) (2025-11-21)


### Bug Fixes

* make release work ([bb02699](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/bb0269960877e4e933e9570113b859f3c15c2a25))
* make release work again (1) ([6767075](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/67670751bc213f1a6194d6df1e48408350e284df))

## [7.0.0](https://github.com/RIVM-bioinformatics/gen-epix-api/compare/v6.1.0...v7.0.0) (2025-11-21)


### ⚠ BREAKING CHANGES

* casedb user/me now under ORGANIZATION instead of AUTH service; update_user_own_organization and retrieve_organization_admin_name_emails under ORGANIZATION instead of ABAC

### Features

* Add API-Version header to response of API call ([#111](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/111)) ([279bb75](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/279bb7552f96aa2dfe3f93d641d0cf09c2dc1cc7))
* add cors headers ([d330ac5](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d330ac50e5b05f28fdcd1e5b9e09734ec6c065a4))
* add distribution to repo ([cb59797](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/cb5979705e447715ce533b052c034162348d68f1))
* add distribution to repo ([0703b87](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0703b87c8fb670a32309c3d89e24584c033b1055))
* add GENETIC_READS_FWD and GENETIC_READS_REV ColType ([8da2c76](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8da2c76c4127576ec52775785525628caf8a2a84))
* add http config ([daadb6d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/daadb6d5545e90a7cf4aa4da81db8068be2d795e))
* add renovate automerge for all dev-requirements package updates and minor and patch updates for the packages in requirements.txt ([d5e70da](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d5e70daa469ac2e2fcc4739ef0b4b856b874eb88))
* added permissions endpoint and removed complete user endpoint ([d4a95b6](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d4a95b6c272e4ad2af44ae43e2a70cf882807bd3))
* added RetrieveInviteUserConstraintsCommand and endpoint; fix: root role has all permissions ([#95](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/95)) ([6e1d824](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6e1d8240c733af9387f63f8e6fb71d8db25218b2))
* **auth:** LSP-2360 add IDP token introspection in OidcClient ([#184](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/184)) ([a316d62](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a316d625ed81bab2a9df24c67a8e43847773458a))
* **case:** add model validator and unit tests for case type column order ([#88](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/88)) ([7795a78](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/7795a7878194ce39e5ecbc815661a414b2919687))
* casedb user/me now under ORGANIZATION instead of AUTH service; update_user_own_organization and retrieve_organization_admin_name_emails under ORGANIZATION instead of ABAC ([4f72822](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/4f72822b37bab3f23f1e0d71037dd9119f5b4d3d))
* casedb ValidateCasesCommand first implementation with corresponding endpoint ([#114](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/114)) ([2b5fd6b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2b5fd6b9182011e710b9995986726c6021c8e955))
* **casedb:** Add ABAC-level validation for creating File, ReadSet, and Seq objects ([#200](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/200)) ([202990a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/202990a3eb744010635cdad8fa6b1dfb9eabd2eb))
* **casedb:** Add streaming endpoint for retrieving genetic sequences in FASTA format ([#112](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/112)) ([6f05410](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6f054102483b5335296d1a83dc61ab206826de08))
* create licenses endpoint ([ed26500](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ed265004dd42f6f68be5da5da9a4ec773e1db947))
* **exc:** add ForeignKeyConstraint409HTTPException for handling FK constraint violations ([#78](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/78)) ([4e5014f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/4e5014f54e7434e57715be2f5acd916512548cb2))
* fastapp CrudEndpointGenerator now retrieves default excluded endpoints from Domain ([428e872](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/428e872799cf9d82d6eaf846d2d618b1483844ff))
* fastapp.repository read_fields method added ([493d439](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/493d439021ad64b144173962a0e334dc547835f7))
* Lsp 1605 implement 409 http code ([#80](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/80)) ([aba5179](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/aba51791a38be7fae5cac463f2ecaab6b5d126ef))
* permissions endpoint; major refactoring into common package; some fixes ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/46)) ([20a3fc2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))
* seqdb/omopdb config structure adjusted; casedb config now has seqdb app user ([428e872](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/428e872799cf9d82d6eaf846d2d618b1483844ff))
* **seqdb:** Introduced File content validation for FileCrudCommand ([#221](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/221)) ([ee17c2c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ee17c2ca24a63251e3eba4c0693e60482a9c800d))
* Streaming FASTA sequence retrieval directly from seqdb repository ([#136](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/136)) ([c816aa2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c816aa25a1256593bf063a09c2c646fffbe98829))
* use filter.filter_rows instead of filter.match_rows in dict respository read_fields ([a60fb51](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a60fb51de17ecd42f9f1b6e6089e48215f6897a2))
* user me updates user name when called ([#100](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/100)) ([df9b21d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df9b21d865c2a576f19ac3bc1825cf73c3d96faa))


### Bug Fixes

* .github.workflows.release.yaml - fixed another syntax error ([a6c7371](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a6c7371227308aa94fb95ab6451989419a6d4d26))
* .github.workflows.release.yaml - fixed syntax error ([d379c01](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d379c01d0913b4ea83da250e5817396a61a24ae6))
* .github.workflows.release.yaml - only upload to pypi in case of … ([f226665](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f226665cd0340168722fba966e3723a899d25aae))
* .github.workflows.release.yaml - only upload to pypi in case of a new release ([126781a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/126781a5b8548036399bb24c12bf1cd4e6e87234))
* .github.workflows.release.yaml - pull the newly commited version into build before publishing ([7fdf0a7](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/7fdf0a7b178b4ae5b81fb65b436fabf5c8be17db))
* .github.workflows.release.yaml - pull the newly commited version… ([27e76e2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/27e76e23d49eaa7c66816841fcacf2176e5b08f1))
* .github.workflows.release.yaml - restore old build method ([ade868c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ade868cb103866cf50f4549634a03a10ea157009))
* .github.workflows.release.yaml - restore old build method ([ac1a5b7](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ac1a5b711cdcb0679ad0e3b592c55b425f6075e0))
* .github.workflows.release.yaml - update checkout version number and add fetch-depth: 0 ([317bff1](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/317bff199dd44ad391ab44b49f499b7cf6a61723))
* add all lsp-api commits to this repo ([0ddf4a1](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0ddf4a1c53c1ef14711291fcef3fc50a88b95093))
* add all lsp-api commits to this repo ([07ee0b0](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/07ee0b02682ec68ee6ef6469d8f65c0927f0506f))
* add correct renovate config ([676412e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/676412ef1e36bf372d2c901f7e46b6ef27e5b662))
* add cors origins to settings.toml ([7fd45ca](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/7fd45cabead3d5f13b14ca588ed987a526ba78bf))
* add debugging ([9b4cda5](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/9b4cda5001f5f5ebcf399a68c8e1d79d67be3e1a))
* add encoding to open method ([3d4b3e8](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3d4b3e8d2147e8ef5b63ad584d5f572517e91892))
* add requirements ([479befc](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/479befcf92d6906e6a7ddc925613a1e2ccc52442))
* add requirements ([6848b78](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6848b788df3922a963fa34db08bf77512341df2c))
* add requirements ([f094735](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f0947355082d1d42fc3d30903b216cd8ced8eb87))
* added logging to release workflow ([67e3f92](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/67e3f928a3bc96ffb4b6a868ba42d9fcc4d15fc8))
* allow censors in range filters to be None ([471c7c1](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/471c7c167306f03bebb8d42914098c1d2cd42d79))
* allow command.CaseTypeColSetMemberCrudCommand READ for all users ([c3d5694](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c3d569405ee3cd1d42a3d324cb6289629a063068))
* **auth:** Removed introspection-related configurations and methods ([9e74963](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/9e7496364c684c5f2746104f2ef66058ed38263e))
* case date should can be None when updating cases ([ec5e06d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ec5e06dd4c4a488929c3a31b63b6bb43f98ae331))
* **casedb case_access:** Add full access check in CaseAbac model ([13833da](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/13833da800c3625b5a75cbba57210006e0b1b0f4))
* casedb seqdb remote app propagates HTTP 500 error when failing ([#194](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/194)) ([0c68508](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0c685082f6434c8b913fb157886f623209fa786d))
* casedb.api.case create case/set request bodies fixed ([1983e54](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/1983e544dcaac4044069b284c4c92c2a3f56c324))
* casedb.services.case retrieve_case_or_set_rights fixed ([c383ab0](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c383ab06c8efac451e2027f949a89540af0a96c6))
* changed comment to test release workflow ([81fc52f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/81fc52f65e29bbbab79c9aedea3712bbb61dcd5b))
* changed comment to test release workflow ([972299f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/972299fa92c18256388357c7b5e0ed3d0cbc06e0))
* **deps:** remove comments ([bccd2e8](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/bccd2e88f6faede8a9d801567a0518d6283c9b19))
* **deps:** remove comments ([2441bc2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2441bc257c51c4b53ecf847f118d53803b4b3ed2))
* **deps:** update dependency biopython to v1.85 ([#55](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/55)) ([65f9c40](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/65f9c40165d111dd5568ce96525824e70bbc49be))
* **deps:** update dependency fastapi to v0.116.1 ([#57](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/57)) ([a5a45ee](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a5a45ee27fc4e1ac44cecd728d82b49f672da339))
* **deps:** update dependency httpx to v0.28.1 ([#58](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/58)) ([7197e93](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/7197e93787ac5c9204b34d691beae7737ff9eb62))
* **deps:** update dependency sqlalchemy to v2.0.43 ([#31](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/31)) ([6f87ffb](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6f87ffb957603c7329df4fe43b253cb7ffbcde98))
* **deps:** update dependency sqlmodel to v0.0.24 ([#32](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/32)) ([c270dc3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c270dc3f9f5840c84b7e060b1965ebf9e30387fb))
* downgrade pypi version ([89480b2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/89480b273c0544da8d9a8102c15646b2d65e9000))
* downgrade pypi version ([7a1dd31](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/7a1dd317ee79738df31b893f73cdc03dad1bab15))
* enable verify_at_hash when decoding jwt ([2ee1866](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2ee1866ebed4d7170f2d4fd475d78b3315ff9f60))
* etl_load_demo_data all ([f36efb6](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f36efb67443593e04cf8ce3a24d563e302cb844d))
* fix get_project_version ([f22e5e8](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f22e5e8c9bb601caa44c43150699673c80bb8916))
* fix import off BadRequest400HTTPException ([b9e6dae](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b9e6daec84b8498eaaa2d975b1f1c97233b0a234))
* fix imports common/api/exc ([a6eef3c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a6eef3c0dfaec1bb81b147424475be98f718e7d8))
* fix merge problem AGAIN, fix metadata_admin references ([dd91d80](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/dd91d80669ad18e78fbd3ad29e34afc1671b4d76))
* fix typo in crud.py ([8881f3b](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8881f3b6b376dee7fdcaa027f8c28004afcadce9))
* fix ValidateCasesRequestBody and CreateCasesRequestBody to not extend from Command ([b9e6dae](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b9e6daec84b8498eaaa2d975b1f1c97233b0a234))
* fix wrong indentation and type in oauth_header_cache ([e6c9e8a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e6c9e8a9e269e59df1f14127afe4b7f7a859b64b))
* fix wrong merge in env.py and util.py ([2a388c0](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2a388c0ab6c658c54933379cf88ef18fa7d98b10))
* gen_epix.casedb.app.py - added comment to test semantic versioning ([6a12740](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6a12740fa1aeed18a340d27e224efbec30b63a6c))
* Lsp 2218 a user should have abac access to all users within his organization ([#120](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/120)) ([76e25a9](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/76e25a9b37d9c56e2137d8dd7e82254e39b71a52))
* LSP-2065-Fix-downloading-sequences ([#69](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/69)) ([86282af](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/86282af565a86d614fa469acf97accd304d6f4c4))
* make casedb/omopdb/seqdb OPENAPI gen epix version dynamic ([355cdab](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/355cdab077f8ff7f39b189aa5b18a6af23a6571b))
* make casedb/omopdb/seqdb OPENAPI gen epix version dynamic ([78cc66a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/78cc66a72efd980014f23b1df073fda6783d9564))
* make comparison between keys in lower case ([004282c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/004282c5ceddafade553bf0200b39bc9c0199bc4))
* make comparison between keys in lower case (again) ([b788c34](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b788c343b799f9b724d28ce68da9cae97cddc775))
* ORG_USER should have read permissions for command.CaseTypeColCrudCommand and command.ColCrudCommand ([a44075d](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a44075d15ec85c56482f8c09b780a8c7c1b0a7f5))
* populate command.CreateCasesCommand from request_body ([3f9b2d2](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3f9b2d2763d57067ca9f7bcfaca034c7c5e7be9e))
* pyodbc.programming error; several minor refactorings ([#74](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/74)) ([9dde6bc](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/9dde6bc69e9180ea09c62c706fc135139d768bc5))
* pyproject.toml - add v back to versioning ([15ae1a4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/15ae1a4d03c85ae471d9027b822d80c5f5c7f621))
* ran formatters ([3bba8da](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3bba8da4681a9335b37ef8cbebc551634ef12eb9))
* reconfigured release workflow using different examples ([8d2f05f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8d2f05f17412fb8c8fc63eac7f282ccc635bef2d))
* redefine models attributes in casedb that inherit from seqdb to prefent naming issues ([d5476d8](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d5476d844b017f38e81620284a042142e7589cec))
* remove annotation of typed filters ([b9e6dae](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b9e6daec84b8498eaaa2d975b1f1c97233b0a234))
* remove erdantic dependency to fix the build (implementation needs to be updated still) ([903f8d1](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/903f8d1d7cb598a23c10cf5eb56cdbd02c2bf5ea))
* remove erdantic from import in erm.py ([c1fd337](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c1fd3374198e6c8f17e4c621a2dfde8c9ac0f247))
* remove http enforce protocol ([71dcbcc](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/71dcbcc6c611e880842bde2d9bb6023412390ca2))
* remove running main workflow on push to avoid running the workflow twice ([a7ef328](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a7ef32870e678547c38596d219353352f66c3643))
* remove running main workflow on push to avoid running the workflow twice ([b8ba4cb](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b8ba4cb138f8c694e3dc34b7b6fac67988cb678d))
* retrieval of organization admin names and emails ([493d439](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/493d439021ad64b144173962a0e334dc547835f7))
* retrieve auth service from app_impl instead of app ([491a890](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/491a890735b8dc49ef577f14aa369b95eaddad07))
* rm docs ([2d3c8a7](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2d3c8a7d697975367297d6ab037d5579c77e3630))
* root can add organization object but never delete ([#91](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/91)) ([25b543f](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/25b543f804b1ab4d31bf60cfe95b453fdc64af62))
* root user creation updated to use key claim instead of id to identify if exists or not ([#220](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/220)) ([c685e5c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c685e5c9a9df1ad0c1547a4f6afc2d4ab55896e6))
* run as appuser ([8cbdb9a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8cbdb9a773699f2aa88527e85851aeb6c3267c39))
* run as appuser ([5537740](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/5537740e8d138bcaec4e51d04430ee623bd6de7f))
* **seqdb:** change default HTTP protocol to HTTPS ([b3ed326](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b3ed326e3ffaac3162dd4e80ef46c16078d10a8c))
* **seqdb:** Ensure SSL verification in HTTP client for secure requests ([6ce9167](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6ce916768af60cd9f068b22be41d283adc3bb00f))
* **seqdb:** Fix Pydantic 2.11.7 FieldInfo.annotation retrieval ([#106](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/106)) ([c14f72c](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c14f72ccc39be2eb849a8db06865619f08ebeeb2))
* **seqdb:** Required change for Kubernetes deployment ([52bb11e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/52bb11e1f29277ffb8256a92d66775a4c08ae489))
* **seqdb:** Required change for Kubernetes deployment ([568ba74](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/568ba7468f2539e6c2141a87eaffb9ae7ce2f0f2))
* set distances as empty dict in retrieve_genetic_sequences ([5e26151](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/5e261515b82bf00d0d4b298c778a2b0d53d00293))
* set fastapi to [standard], fix UpdateResponseHeaderMiddleware to not call call_next twice ([427c2ba](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/427c2ba5425e2a639aa65c68ed67b5c1bb4e8c59))
* several logging levels and logging fixes ([#211](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/211)) ([e99c9b0](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e99c9b07a1ac8367795b09b8cd7f210b146a0c07))
* SQL error when param size is to big in region relations ([086a0e4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/086a0e40bb9e6f55c34e9f03dfb0a3d2691982b8))
* temporary fix moving pandas dependency to requirements.txt from dev-requirements.txt ([029a07e](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/029a07e8c8da797498e73c55c480d52c8d6ae844))
* TypedCompositeFilter key should be of type 'str', not 'None' ([e97bfc4](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e97bfc4b2abc6a7db8052707a012f20a85a0db1d))
* update baseBranche renovate ([374c2d3](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/374c2d33343689be4b94f2855a5f923b3476350e))
* update healthcheck ([a76d0ff](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a76d0ff5beeafdac2bd57beda1996c6982888ad2))
* update remote app ([a59ca72](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a59ca72361c751b4e71e04598d2c89323387c327))
* update ssl internal aks issues ([9068b3a](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/9068b3a639b9eab22c316a0e0921df928759ab9a))
* various fixes related to commondb derived classes in casedb/omopdb/seqdb ([#138](https://github.com/RIVM-bioinformatics/gen-epix-api/issues/138)) ([b6ef558](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b6ef5588eb3a4144d9e0f260bc2092e7cc901dfa))

## v6.0.0 (2025-09-08)

### Bug Fixes

- Add encoding to open method
  ([`3d4b3e8`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3d4b3e8d2147e8ef5b63ad584d5f572517e91892))

- Fix merge problem AGAIN, fix metadata_admin references
  ([`dd91d80`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/dd91d80669ad18e78fbd3ad29e34afc1671b4d76))

- **deps**: Remove comments
  ([`2441bc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/2441bc257c51c4b53ecf847f118d53803b4b3ed2))

## v5.0.0 (2025-08-17)

### Bug Fixes

- Add correct renovate config ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Add requirements ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Allow command.CaseTypeColSetMemberCrudCommand READ for all users
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Etl_load_demo_data all ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Fix get_project_version ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Fix imports common/api/exc ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Update baseBranche renovate ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **casedb case_access**: Add full access check in CaseAbac model
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency biopython to v1.85
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency cachetools to v5.5.2
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency dynaconf to v3.2.11
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency fastapi to v0.116.1
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency httpx to v0.28.1
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency sqlalchemy to v2.0.43
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency sqlmodel to v0.0.24
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

### Chores

- Add version uitil ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Fix in openpyxl requirements ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Merge main into dev to have dev be only ahead of main again
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Remove cicd folder ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Renovate fixes ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Temporarily add pytest to requirements.txt
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **.gitignore**: Update ignored paths for test data and logs
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **config**: Migrate config renovate.json
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency black to ==24.10.*
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency mypy to ==1.17.*
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency pandas-stubs to ==2.3.*
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency pyinstrument to ==5.1.*
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency pylint to ==3.3.*
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency pytest to ==8.4.*
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency pytest-cov to ==6.2.*
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency python-dateutil to ==2.9.*
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update dependency types-python-jose to ==3.5.*
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update marocchino/sticky-pull-request-comment action to v2.9.4
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **deps**: Update python-semantic-release/python-semantic-release action to v10.3.1
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **requirements**: Add types-setuptools to dependencies
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **util**: Minor change from copilot review
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

### Code Style

- **test**: Remove unnecessary blank line in test_simple_filter_pydantic_and_plain_python_class
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

### Documentation

- Add version.py doc string ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

### Features

- Added permissions endpoint and removed complete user endpoint
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Casedb user/me now under ORGANIZATION instead of AUTH service; update_user_own_organization and
  retrieve_organization_admin_name_emails under ORGANIZATION instead of ABAC
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Seqdb/omopdb config structure adjusted; casedb config now has seqdb app user
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

### Refactoring

- /util modules moved to /gen_epix/common and /test
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- All classes are registered with each Domain directly after creation of the latter
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Lsp 2193 register all classes with domain directly after creation
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Reduced common imports by defining sets of classes
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Remove constructor reimplementations for concrete SA repositories
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Removed constructor overrides concrete sa repositories
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Rename metadata admin to refdata admin
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Renamed METADATA_ADMIN to REFDATA_ADMIN throughout
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Replaced os.path with PathLib for file operations in repository.py and run.py,
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Sorted models by service type and commands by service type have base classes substituted by
  implementing classes during registration with domain
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- Updated configuring of repository metadata
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **Filter**: Base.py - composite.py - Use getattr() for more efficient and generic filtering
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **test**: Replaced os.path with PathLib in the the test module,
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **test**: Update test utilities and improve type hints
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **util**: Replaced os.path with PathLib in the the util module,
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

### Testing

- Casedb.integration.case_access test fixed; to be expanded with additional tests (WIP)
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **casedb case_access**: Major refactoring of the test, putting scenarios entirely in data
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

- **Filter): test(Filter**: Test_match.py - introduced two unit tests that test the getattr()
  refactoring of composite.py and base.py on both Pydantic and plain Python classes
  ([#68](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/68),
  [`a41b9cc`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a41b9ccc4a54ad29edeb32d8a7b94dc3206e7ad0))

## v4.0.0 (2025-08-17)

### Bug Fixes

- Add correct renovate config ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Add requirements ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Allow command.CaseTypeColSetMemberCrudCommand READ for all users
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Etl_load_demo_data all ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Fix get_project_version ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Fix imports common/api/exc ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Update baseBranche renovate ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **casedb case_access**: Add full access check in CaseAbac model
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency biopython to v1.85
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency cachetools to v5.5.2
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency dynaconf to v3.2.11
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency fastapi to v0.116.1
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency httpx to v0.28.1
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency sqlalchemy to v2.0.43
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency sqlmodel to v0.0.24
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

### Chores

- Add version uitil ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Fix in openpyxl requirements ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Merge main into dev to have dev be only ahead of main again
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Remove cicd folder ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Renovate fixes ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Temporarily add pytest to requirements.txt
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **.gitignore**: Update ignored paths for test data and logs
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **config**: Migrate config renovate.json
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency black to ==24.10.*
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency mypy to ==1.17.*
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency pandas-stubs to ==2.3.*
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency pyinstrument to ==5.1.*
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency pylint to ==3.3.*
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency pytest to ==8.4.*
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency pytest-cov to ==6.2.*
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency python-dateutil to ==2.9.*
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update dependency types-python-jose to ==3.5.*
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update marocchino/sticky-pull-request-comment action to v2.9.4
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **deps**: Update python-semantic-release/python-semantic-release action to v10.3.1
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **requirements**: Add types-setuptools to dependencies
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **util**: Minor change from copilot review
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

### Code Style

- **test**: Remove unnecessary blank line in test_simple_filter_pydantic_and_plain_python_class
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

### Documentation

- Add version.py doc string ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

### Features

- Added permissions endpoint and removed complete user endpoint
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Casedb user/me now under ORGANIZATION instead of AUTH service; update_user_own_organization and
  retrieve_organization_admin_name_emails under ORGANIZATION instead of ABAC
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Seqdb/omopdb config structure adjusted; casedb config now has seqdb app user
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

### Refactoring

- /util modules moved to /gen_epix/common and /test
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- All classes are registered with each Domain directly after creation of the latter
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Lsp 2193 register all classes with domain directly after creation
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Reduced common imports by defining sets of classes
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Replaced os.path with PathLib for file operations in repository.py and run.py,
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- Sorted models by service type and commands by service type have base classes substituted by
  implementing classes during registration with domain
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **Filter**: Base.py - composite.py - Use getattr() for more efficient and generic filtering
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **test**: Replaced os.path with PathLib in the the test module,
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **test**: Update test utilities and improve type hints
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **util**: Replaced os.path with PathLib in the the util module,
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

### Testing

- Casedb.integration.case_access test fixed; to be expanded with additional tests (WIP)
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **casedb case_access**: Major refactoring of the test, putting scenarios entirely in data
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

- **Filter): test(Filter**: Test_match.py - introduced two unit tests that test the getattr()
  refactoring of composite.py and base.py on both Pydantic and plain Python classes
  ([#64](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/64),
  [`df465bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/df465bf402be29500943083bd5603fa29f72bd67))

## v3.0.0 (2025-08-16)

### Bug Fixes

- Add correct renovate config ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Add requirements ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Allow command.CaseTypeColSetMemberCrudCommand READ for all users
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Etl_load_demo_data all ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Fix get_project_version ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Fix imports common/api/exc ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Update baseBranche renovate ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **casedb case_access**: Add full access check in CaseAbac model
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency biopython to v1.85
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency cachetools to v5.5.2
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency dynaconf to v3.2.11
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency fastapi to v0.116.1
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency httpx to v0.28.1
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency sqlalchemy to v2.0.43
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency sqlmodel to v0.0.24
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

### Chores

- Add version uitil ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Fix in openpyxl requirements ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Merge main into dev to have dev be only ahead of main again
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Remove cicd folder ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Renovate fixes ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Temporarily add pytest to requirements.txt
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **.gitignore**: Update ignored paths for test data and logs
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **config**: Migrate config renovate.json
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency black to ==24.10.*
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency mypy to ==1.17.*
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency pandas-stubs to ==2.3.*
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency pyinstrument to ==5.1.*
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency pylint to ==3.3.*
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency pytest to ==8.4.*
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency pytest-cov to ==6.2.*
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency python-dateutil to ==2.9.*
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update dependency types-python-jose to ==3.5.*
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update marocchino/sticky-pull-request-comment action to v2.9.4
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **deps**: Update python-semantic-release/python-semantic-release action to v10.3.1
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **requirements**: Add types-setuptools to dependencies
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **util**: Minor change from copilot review
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

### Code Style

- **test**: Remove unnecessary blank line in test_simple_filter_pydantic_and_plain_python_class
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

### Documentation

- Add version.py doc string ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

### Features

- Added permissions endpoint and removed complete user endpoint
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Casedb user/me now under ORGANIZATION instead of AUTH service; update_user_own_organization and
  retrieve_organization_admin_name_emails under ORGANIZATION instead of ABAC
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Seqdb/omopdb config structure adjusted; casedb config now has seqdb app user
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

### Refactoring

- /util modules moved to /gen_epix/common and /test
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Reduced common imports by defining sets of classes
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- Replaced os.path with PathLib for file operations in repository.py and run.py,
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **Filter**: Base.py - composite.py - Use getattr() for more efficient and generic filtering
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **test**: Replaced os.path with PathLib in the the test module,
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **test**: Update test utilities and improve type hints
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **util**: Replaced os.path with PathLib in the the util module,
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

### Testing

- Casedb.integration.case_access test fixed; to be expanded with additional tests (WIP)
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **casedb case_access**: Major refactoring of the test, putting scenarios entirely in data
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

- **Filter): test(Filter**: Test_match.py - introduced two unit tests that test the getattr()
  refactoring of composite.py and base.py on both Pydantic and plain Python classes
  ([#61](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/61),
  [`f37ff8d`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f37ff8d4c6aa7bc210aa7f387c73f363d269eb69))

## v2.0.0 (2025-08-16)

### Bug Fixes

- Add correct renovate config ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Add requirements ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Allow command.CaseTypeColSetMemberCrudCommand READ for all users
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Etl_load_demo_data all ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Fix get_project_version ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Fix imports common/api/exc ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Update baseBranche renovate ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **casedb case_access**: Add full access check in CaseAbac model
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency cachetools to v5.5.2
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency dynaconf to v3.2.11
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency sqlalchemy to v2.0.43
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency sqlmodel to v0.0.24
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

### Chores

- Add version uitil ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Fix in openpyxl requirements ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Merge main into dev to have dev be only ahead of main again
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Remove cicd folder ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Renovate fixes ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Temporarily add pytest to requirements.txt
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **.gitignore**: Update ignored paths for test data and logs
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **config**: Migrate config renovate.json
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency black to ==24.10.*
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency mypy to ==1.17.*
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency pandas-stubs to ==2.3.*
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency pyinstrument to ==5.1.*
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency pylint to ==3.3.*
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency pytest to ==8.4.*
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency pytest-cov to ==6.2.*
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency python-dateutil to ==2.9.*
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **deps**: Update dependency types-python-jose to ==3.5.*
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **requirements**: Add types-setuptools to dependencies
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **util**: Minor change from copilot review
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

### Code Style

- **test**: Remove unnecessary blank line in test_simple_filter_pydantic_and_plain_python_class
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

### Documentation

- Add version.py doc string ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

### Features

- Added permissions endpoint and removed complete user endpoint
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Casedb user/me now under ORGANIZATION instead of AUTH service; update_user_own_organization and
  retrieve_organization_admin_name_emails under ORGANIZATION instead of ABAC
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Seqdb/omopdb config structure adjusted; casedb config now has seqdb app user
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

### Refactoring

- /util modules moved to /gen_epix/common and /test
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- Replaced os.path with PathLib for file operations in repository.py and run.py,
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **Filter**: Base.py - composite.py - Use getattr() for more efficient and generic filtering
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **test**: Replaced os.path with PathLib in the the test module,
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **test**: Update test utilities and improve type hints
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **util**: Replaced os.path with PathLib in the the util module,
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

### Testing

- Casedb.integration.case_access test fixed; to be expanded with additional tests (WIP)
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **casedb case_access**: Major refactoring of the test, putting scenarios entirely in data
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

- **Filter): test(Filter**: Test_match.py - introduced two unit tests that test the getattr()
  refactoring of composite.py and base.py on both Pydantic and plain Python classes
  ([#54](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/54),
  [`31aed74`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/31aed74c785cfca82a1f92f3d499303234e7f70b))

## v1.0.0 (2025-08-15)

### Bug Fixes

- Add correct renovate config ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Add requirements ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Allow command.CaseTypeColSetMemberCrudCommand READ for all users
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Etl_load_demo_data all ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Fix get_project_version ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Fix imports common/api/exc ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Update baseBranche renovate ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **casedb case_access**: Add full access check in CaseAbac model
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **deps**: Update dependency cachetools to v5.5.2
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **deps**: Update dependency dynaconf to v3.2.11
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **deps**: Update dependency sqlalchemy to v2.0.43
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **deps**: Update dependency sqlmodel to v0.0.24
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

### Chores

- Add version uitil ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Fix in openpyxl requirements ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Merge main into dev to have dev be only ahead of main again
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Remove cicd folder ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Renovate fixes ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Temporarily add pytest to requirements.txt
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **.gitignore**: Update ignored paths for test data and logs
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **config**: Migrate config renovate.json
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **deps**: Update dependency black to ==24.10.*
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **deps**: Update dependency mypy to ==1.17.*
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **deps**: Update dependency pandas-stubs to ==2.3.*
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **deps**: Update dependency pyinstrument to ==5.1.*
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **deps**: Update dependency pylint to ==3.3.*
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **deps**: Update dependency pytest to ==8.4.*
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **requirements**: Add types-setuptools to dependencies
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **util**: Minor change from copilot review
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

### Code Style

- **test**: Remove unnecessary blank line in test_simple_filter_pydantic_and_plain_python_class
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

### Documentation

- Add version.py doc string ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

### Features

- Added permissions endpoint and removed complete user endpoint
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Casedb user/me now under ORGANIZATION instead of AUTH service; update_user_own_organization and
  retrieve_organization_admin_name_emails under ORGANIZATION instead of ABAC
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Permissions endpoint; major refactoring into common package; some fixes
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- Seqdb/omopdb config structure adjusted; casedb config now has seqdb app user
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

### Refactoring

- Replaced os.path with PathLib for file operations in repository.py and run.py,
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **Filter**: Base.py - composite.py - Use getattr() for more efficient and generic filtering
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **test**: Replaced os.path with PathLib in the the test module,
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **test**: Update test utilities and improve type hints
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **util**: Replaced os.path with PathLib in the the util module,
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

### Testing

- Casedb.integration.case_access test fixed; to be expanded with additional tests (WIP)
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **casedb case_access**: Major refactoring of the test, putting scenarios entirely in data
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

- **Filter): test(Filter**: Test_match.py - introduced two unit tests that test the getattr()
  refactoring of composite.py and base.py on both Pydantic and plain Python classes
  ([#46](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/46),
  [`20a3fc2`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/20a3fc2835308437ed254ff01d9062b700462d8c))

## v0.1.10 (2025-08-12)

### Bug Fixes

- Update baseBranche renovate
  ([`374c2d3`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/374c2d33343689be4b94f2855a5f923b3476350e))

### Chores

- **config**: Migrate config renovate.json
  ([`0e66873`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0e66873f7d51ff7547309c2a2fbcfc3e5ce372f9))

## v0.1.9 (2025-08-12)

### Bug Fixes

- Add correct renovate config
  ([`676412e`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/676412ef1e36bf372d2c901f7e46b6ef27e5b662))

## v0.1.8 (2025-08-11)

### Bug Fixes

- Allow command.CaseTypeColSetMemberCrudCommand READ for all users
  ([#18](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/18),
  [`938b5bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/938b5bfe1d58b99d6f0f954a348b30b4741080fa))

- Fix imports common/api/exc ([#18](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/18),
  [`938b5bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/938b5bfe1d58b99d6f0f954a348b30b4741080fa))

### Chores

- Add version uitil ([#18](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/18),
  [`938b5bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/938b5bfe1d58b99d6f0f954a348b30b4741080fa))

### Documentation

- Add version.py doc string ([#18](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/18),
  [`938b5bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/938b5bfe1d58b99d6f0f954a348b30b4741080fa))

### Refactoring

- Replaced os.path with PathLib for file operations in repository.py and run.py,
  ([#18](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/18),
  [`938b5bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/938b5bfe1d58b99d6f0f954a348b30b4741080fa))

- **test**: Replaced os.path with PathLib in the the test module,
  ([#18](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/18),
  [`938b5bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/938b5bfe1d58b99d6f0f954a348b30b4741080fa))

- **util**: Replaced os.path with PathLib in the the util module,
  ([#18](https://github.com/RIVM-bioinformatics/gen-epix-api/pull/18),
  [`938b5bf`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/938b5bfe1d58b99d6f0f954a348b30b4741080fa))

## v0.1.7 (2025-06-04)

### Bug Fixes

- Casedb.api.case create case/set request bodies fixed
  ([`1983e54`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/1983e544dcaac4044069b284c4c92c2a3f56c324))

- Casedb.services.case retrieve_case_or_set_rights fixed
  ([`c383ab0`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/c383ab06c8efac451e2027f949a89540af0a96c6))

- Typedcompositefilter key should be of type 'str', not 'None'
  ([`e97bfc4`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/e97bfc4b2abc6a7db8052707a012f20a85a0db1d))

### Chores

- Add data changes
  ([`1b18bda`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/1b18bda12d3114cf7e5a5731f33707cb9c25142b))

- Changed automatic_new_user org
  ([`da4ae59`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/da4ae599e67710240e16132d2f1b35f0ebd49d53))

- Fix container app azure job
  ([`15a72a4`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/15a72a4b84d51625e7fedf9e09d8f894fceff533))

### Documentation

- Readme.md - fixing images and badges
  ([`d1575e6`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d1575e6f19169473dab001be9164801b718043e6))

## v0.1.6 (2025-06-04)

### Bug Fixes

- .github.workflows.release.yaml - pull the newly commited version into build before publishing
  ([`7fdf0a7`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/7fdf0a7b178b4ae5b81fb65b436fabf5c8be17db))

## v0.1.5 (2025-06-04)

### Bug Fixes

- Changed comment to test release workflow
  ([`972299f`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/972299fa92c18256388357c7b5e0ed3d0cbc06e0))

### Chores

- Output `released` variable to next workflow job
  ([`f9300ab`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/f9300abe45ca1853431d2a6f292acab4ed8f9c4e))

## v0.1.4 (2025-06-04)

### Bug Fixes

- .github.workflows.release.yaml - restore old build method
  ([`ac1a5b7`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/ac1a5b711cdcb0679ad0e3b592c55b425f6075e0))

## v0.1.3 (2025-06-04)

### Bug Fixes

- .github.workflows.release.yaml - only upload to pypi in case of a new release
  ([`126781a`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/126781a5b8548036399bb24c12bf1cd4e6e87234))

## v0.1.2 (2025-06-04)

### Bug Fixes

- Make casedb/omopdb/seqdb OPENAPI gen epix version dynamic
  ([`78cc66a`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/78cc66a72efd980014f23b1df073fda6783d9564))

## v0.1.1 (2025-06-04)

### Bug Fixes

- Remove running main workflow on push to avoid running the workflow twice
  ([`b8ba4cb`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/b8ba4cb138f8c694e3dc34b7b6fac67988cb678d))

## v0.1.0 (2025-06-04)

### Features

- Add distribution to repo
  ([`0703b87`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/0703b87c8fb670a32309c3d89e24584c033b1055))

## v0.0.1 (2025-06-03)

### Bug Fixes

- .github.workflows.release.yaml - fixed another syntax error
  ([`a6c7371`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/a6c7371227308aa94fb95ab6451989419a6d4d26))

- .github.workflows.release.yaml - fixed syntax error
  ([`d379c01`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/d379c01d0913b4ea83da250e5817396a61a24ae6))

- .github.workflows.release.yaml - update checkout version number and add fetch-depth: 0
  ([`317bff1`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/317bff199dd44ad391ab44b49f499b7cf6a61723))

- Added logging to release workflow
  ([`67e3f92`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/67e3f928a3bc96ffb4b6a868ba42d9fcc4d15fc8))

- Gen_epix.casedb.app.py - added comment to test semantic versioning
  ([`6a12740`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/6a12740fa1aeed18a340d27e224efbec30b63a6c))

- Pyproject.toml - add v back to versioning
  ([`15ae1a4`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/15ae1a4d03c85ae471d9027b822d80c5f5c7f621))

- Reconfigured release workflow using different examples
  ([`8d2f05f`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/8d2f05f17412fb8c8fc63eac7f282ccc635bef2d))

## v0.0.0 (2025-06-03)

### Bug Fixes

- Ran formatters
  ([`3bba8da`](https://github.com/RIVM-bioinformatics/gen-epix-api/commit/3bba8da4681a9335b37ef8cbebc551634ef12eb9))
