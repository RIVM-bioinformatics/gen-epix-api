# Base Sequence Model

> 30 nodes · cohesion 0.08

## Key Concepts

- **BaseSeq** (18 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **RefSeq** (8 connections) — `gen_epix/seqdb/domain/model/seq/ref_seq.py`
- **._validate_model()** (7 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Contig** (7 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **Allele** (5 connections) — `gen_epix/seqdb/domain/model/seq/locus.py`
- **.get_seq_hash()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._validate_content()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **decode_ascii_from_gzip_base64()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._serialize_id()** (4 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **._serialize_contigs()** (4 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **.get_nucleotide_seq()** (3 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **RefAllele** (3 connections) — `gen_epix/seqdb/domain/model/seq/locus.py`
- **model_validator** (2 connections)
- **Self** (2 connections)
- **UUID** (2 connections)
- **field_serializer** (2 connections)
- **UUID** (2 connections)
- **Model** (1 connections)
- **Validate that the content hash matches the content.** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Represents a sequence with a validated representation, length, and hash. The…** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Normalize and validate the sequence representation, length, and hash. Derives…** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Return the nucleotide sequence represented by this model. Args: ref_seq_str:…** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Decode a gzip-compressed base64 string.** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Compute a hash for the given string, which is expected to contain a nucleotide…** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Represents a reference allele for a locus. This can be an actual sequence or an…** (1 connections) — `gen_epix/seqdb/domain/model/seq/locus.py`
- *... and 5 more nodes in this community*

## Relationships

- [Commondb Base Models](Commondb_Base_Models.md) (17 shared connections)
- [Contig Length Computed Fields](Contig_Length_Computed_Fields.md) (3 shared connections)
- [Sequence Format Enums](Sequence_Format_Enums.md) (2 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (1 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (1 shared connections)
- [Sequence Format Conversion](Sequence_Format_Conversion.md) (1 shared connections)
- [Seq Profile Content Validation](Seq_Profile_Content_Validation.md) (1 shared connections)
- [Protocol & Profile Type Enums](Protocol_&_Profile_Type_Enums.md) (1 shared connections)
- [Taxonomy Models](Taxonomy_Models.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/model/seq/base.py`
- `gen_epix/seqdb/domain/model/seq/locus.py`
- `gen_epix/seqdb/domain/model/seq/ref_seq.py`
- `gen_epix/seqdb/domain/model/seq/seq.py`

## Audit Trail

- EXTRACTED: 56 (92%)
- INFERRED: 5 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*