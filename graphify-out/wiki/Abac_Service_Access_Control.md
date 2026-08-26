# Abac Service Access Control

> 34 nodes · cohesion 0.09

## Key Concepts

- **ServiceType** (24 connections) — `gen_epix/casedb/domain/enum.py`
- **casedb/domain/service/__init__.py** (17 connections) — `gen_epix/casedb/domain/service/__init__.py`
- **BaseSeqdbService** (12 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **service/case.py** (11 connections) — `gen_epix/casedb/domain/service/case.py`
- **casedb/domain/service/abac.py** (10 connections) — `gen_epix/casedb/domain/service/abac.py`
- **BaseAbacService** (10 connections) — `gen_epix/casedb/domain/service/abac.py`
- **service/geo.py** (8 connections) — `gen_epix/casedb/domain/service/geo.py`
- **service/seqdb.py** (8 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **BaseGeoService** (7 connections) — `gen_epix/casedb/domain/service/geo.py`
- **service/ontology.py** (7 connections) — `gen_epix/casedb/domain/service/ontology.py`
- **BaseOntologyService** (6 connections) — `gen_epix/casedb/domain/service/ontology.py`
- **services/geo.py** (5 connections) — `gen_epix/casedb/services/geo.py`
- **.get_case_abac()** (4 connections) — `gen_epix/casedb/domain/service/abac.py`
- **.get_ref_data_access()** (4 connections) — `gen_epix/casedb/domain/service/abac.py`
- **.create_file()** (4 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **.retrieve_phylogenetic_tree()** (4 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **.retrieve_similar_profiles()** (4 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **GeoService** (4 connections) — `gen_epix/casedb/services/geo.py`
- **.retrieve_genetic_sequence_fasta_by_id()** (3 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **UUID** (3 connections)
- **services/ontology.py** (3 connections) — `gen_epix/casedb/services/ontology.py`
- **OntologyService** (3 connections) — `gen_epix/casedb/services/ontology.py`
- **Command** (2 connections)
- **CommonAbacService** (1 connections)
- **Get case access control permissions for command.** (1 connections) — `gen_epix/casedb/domain/service/abac.py`
- *... and 9 more nodes in this community*

## Relationships

- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (9 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (8 shared connections)
- [Organization Service](Organization_Service.md) (7 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (5 shared connections)
- [Base Service Class](Base_Service_Class.md) (5 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (5 shared connections)
- [Case Service CRUD](Case_Service_CRUD.md) (4 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (3 shared connections)
- [File Creation Command](File_Creation_Command.md) (2 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (2 shared connections)
- [Geo/Ontology/Abac Repositories](Geo-Ontology-Abac_Repositories.md) (2 shared connections)
- [Region Containment Command](Region_Containment_Command.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/domain/enum.py`
- `gen_epix/casedb/domain/service/__init__.py`
- `gen_epix/casedb/domain/service/abac.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/domain/service/geo.py`
- `gen_epix/casedb/domain/service/ontology.py`
- `gen_epix/casedb/domain/service/seqdb.py`
- `gen_epix/casedb/services/geo.py`
- `gen_epix/casedb/services/ontology.py`

## Audit Trail

- EXTRACTED: 107 (86%)
- INFERRED: 17 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*