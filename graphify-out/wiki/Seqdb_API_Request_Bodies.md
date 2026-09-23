# Seqdb API Request Bodies

> 27 nodes · cohesion 0.13

## Key Concepts

- **api/seq.py** (28 connections) — `gen_epix/seqdb/api/seq.py`
- **seqdb/api/__init__.py** (20 connections) — `gen_epix/seqdb/api/__init__.py`
- **PydanticBaseModel** (10 connections)
- **CalculatePhylogeneticTreeRequestBody** (6 connections) — `gen_epix/seqdb/api/seq.py`
- **CreateFileRequestBody** (4 connections) — `gen_epix/seqdb/api/file.py`
- **ConvertSeqFormatRequestBody** (4 connections) — `gen_epix/seqdb/api/seq.py`
- **RetrieveBestSeqClassificationPerSampleRequestBody** (4 connections) — `gen_epix/seqdb/api/seq.py`
- **RetrieveBestSeqPerSampleRequestBody** (4 connections) — `gen_epix/seqdb/api/seq.py`
- **RetrieveBestSeqProfilePerSampleRequestBody** (4 connections) — `gen_epix/seqdb/api/seq.py`
- **RetrieveSampleIdentifiersByIdsRequestBody** (4 connections) — `gen_epix/seqdb/api/seq.py`
- **RetrieveSamplesByIdsRequestBody** (4 connections) — `gen_epix/seqdb/api/seq.py`
- **RetrieveSeqFastaRequestBody** (4 connections) — `gen_epix/seqdb/api/seq.py`
- **RetrieveSimilarProfilesRequestBody** (4 connections) — `gen_epix/seqdb/api/seq.py`
- **UpdateSeqDistancesRequestBody** (4 connections) — `gen_epix/seqdb/api/seq.py`
- **.validate_limit()** (4 connections) — `gen_epix/seqdb/api/seq.py`
- **UploadSamplesRequestBody** (3 connections) — `gen_epix/seqdb/api/seq.py`
- **# TODO: is a temporary option, to be removed once the memory handling is…** (2 connections) — `gen_epix/seqdb/api/seq.py`
- **# TODO: is a temporary option, to be removed once the numpy-vectorised ALLELE…** (2 connections) — `gen_epix/seqdb/api/seq.py`
- **PydanticBaseModel** (1 connections)
- **Represents a base64-encoded file creation request.** (1 connections) — `gen_epix/seqdb/api/file.py`
- **Expose seqdb API request representations for router composition.** (1 connections) — `gen_epix/seqdb/api/__init__.py`
- **model_validator** (1 connections)
- **Self** (1 connections)
- **Expose seqdb api.seq API adapters and request representations.** (1 connections) — `gen_epix/seqdb/api/seq.py`
- **Normalize the deprecated maximum-profile field into ``limit``.** (1 connections) — `gen_epix/seqdb/api/seq.py`
- *... and 2 more nodes in this community*

## Relationships

- [Casedb Case API Models](Casedb_Case_API_Models.md) (11 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (5 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (3 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (2 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (2 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (2 shared connections)
- [Case API Endpoints](Case_API_Endpoints.md) (2 shared connections)
- [Phylogenetics & Format Conversion](Phylogenetics_&_Format_Conversion.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (1 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (1 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/api/__init__.py`
- `gen_epix/seqdb/api/file.py`
- `gen_epix/seqdb/api/seq.py`

## Audit Trail

- EXTRACTED: 77 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*