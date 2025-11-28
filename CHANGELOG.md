# CHANGELOG

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
