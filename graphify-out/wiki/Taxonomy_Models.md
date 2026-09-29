# Taxonomy Models

> 20 nodes · cohesion 0.12

## Key Concepts

- **Taxon** (12 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **field_validator** (4 connections)
- **._serialize_ancestor_taxon_ids()** (4 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **._validate_ancestor_taxon_ids()** (4 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **._validate_rank()** (4 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **Model** (3 connections)
- **UUID** (3 connections)
- **._validate_ncbi_ancestor_taxids()** (3 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **._validate_ncbi_taxid()** (3 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **TaxonSet** (3 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **TaxonSetMember** (3 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **field_serializer** (1 connections)
- **Represents a set of taxa, for example a set of taxa that are relevant for a…** (1 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **Represents a member of a taxon set, representing the inclusion of a specific…** (1 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **Represents a taxonomic unit in a unified taxonomy. A single unified taxonomy is…** (1 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **Normalize an NCBI taxon identifier, accepting its standard prefix.** (1 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **Normalize JSON or prefixed NCBI ancestor identifiers to integers.** (1 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **Normalize a JSON ancestor identifier list to UUID objects.** (1 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **Normalize a taxon rank, accepting spaced NCBI rank names.** (1 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **Serialize ancestor taxon identifiers as strings.** (1 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`

## Relationships

- [Commondb Base Models](Commondb_Base_Models.md) (7 shared connections)
- [Base Sequence Model](Base_Sequence_Model.md) (1 shared connections)
- [Seqdb File Commands & Enums](Seqdb_File_Commands_&_Enums.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/model/seq/taxon.py`

## Audit Trail

- EXTRACTED: 30 (94%)
- INFERRED: 2 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*