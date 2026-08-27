# Entity Key Generation

> 70 nodes · cohesion 0.05

## Key Concepts

- **entity.py** (71 connections) — `gen_epix/fastapp/domain/entity.py`
- **seq/seq.py** (40 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **protocol.py** (35 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **create_links()** (32 connections) — `gen_epix/fastapp/domain/util.py`
- **create_keys()** (26 connections) — `gen_epix/fastapp/domain/util.py`
- **locus.py** (21 connections) — `gen_epix/seqdb/domain/model/seq/locus.py`
- **fastapp/domain/util.py** (19 connections) — `gen_epix/fastapp/domain/util.py`
- **BaseSeq** (18 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **taxon.py** (13 connections) — `gen_epix/seqdb/domain/model/seq/taxon.py`
- **ref_seq.py** (12 connections) — `gen_epix/seqdb/domain/model/seq/ref_seq.py`
- **LocusSet** (11 connections) — `gen_epix/seqdb/domain/model/seq/locus.py`
- **tree.py** (11 connections) — `gen_epix/seqdb/domain/model/seq/tree.py`
- **Key** (10 connections) — `gen_epix/fastapp/domain/key.py`
- **Locus** (10 connections) — `gen_epix/seqdb/domain/model/seq/locus.py`
- **RefSeq** (10 connections) — `gen_epix/seqdb/domain/model/seq/ref_seq.py`
- **Allele** (9 connections) — `gen_epix/seqdb/domain/model/seq/locus.py`
- **LocusCodeMap** (8 connections) — `gen_epix/seqdb/domain/model/seq/locus.py`
- **.create_entity()** (7 connections) — `gen_epix/commondb/domain/model/organization.py`
- **create_multi_links()** (7 connections) — `gen_epix/fastapp/domain/util.py`
- **PhylogeneticTree** (7 connections) — `gen_epix/seqdb/domain/model/seq/tree.py`
- **TreeAlgorithm** (6 connections) — `gen_epix/seqdb/domain/model/seq/tree.py`
- **key.py** (5 connections) — `gen_epix/fastapp/domain/key.py`
- **UUID** (5 connections)
- **RefAllele** (5 connections) — `gen_epix/seqdb/domain/model/seq/locus.py`
- **TreeAlgorithmClass** (5 connections) — `gen_epix/seqdb/domain/model/seq/tree.py`
- *... and 45 more nodes in this community*

## Relationships

- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (69 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (41 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (24 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (17 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (13 shared connections)
- [Domain Entity Registration](Domain_Entity_Registration.md) (12 shared connections)
- [Seq Format Validation](Seq_Format_Validation.md) (12 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (11 shared connections)
- [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md) (6 shared connections)
- [Seq File Format Validation](Seq_File_Format_Validation.md) (6 shared connections)
- [Taxon Model](Taxon_Model.md) (4 shared connections)
- [SA Repository Mapper & ERM Diagram Gen](SA_Repository_Mapper_&_ERM_Diagram_Gen.md) (3 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/organization.py`
- `gen_epix/fastapp/domain/entity.py`
- `gen_epix/fastapp/domain/key.py`
- `gen_epix/fastapp/domain/util.py`
- `gen_epix/seqdb/domain/model/seq/base.py`
- `gen_epix/seqdb/domain/model/seq/locus.py`
- `gen_epix/seqdb/domain/model/seq/protocol.py`
- `gen_epix/seqdb/domain/model/seq/ref_seq.py`
- `gen_epix/seqdb/domain/model/seq/seq.py`
- `gen_epix/seqdb/domain/model/seq/taxon.py`
- `gen_epix/seqdb/domain/model/seq/tree.py`

## Audit Trail

- EXTRACTED: 346 (95%)
- INFERRED: 17 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*