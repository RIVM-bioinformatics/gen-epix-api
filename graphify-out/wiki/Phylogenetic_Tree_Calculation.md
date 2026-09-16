# Phylogenetic Tree Calculation

> 15 nodes · cohesion 0.13

## Key Concepts

- **calculate_phylogenetic_tree.py** (28 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **repository/seq.py** (12 connections) — `gen_epix/seqdb/domain/repository/seq.py`
- **service/seq.py** (12 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **_correct_nj_tree_negative_branch_lengths_recursion()** (4 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **_get_newick_repr_recursion()** (4 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **ClusterNode** (1 connections)
- **Define seqdb domain interfaces and policies for domain.repository.seq.** (1 connections) — `gen_epix/seqdb/domain/repository/seq.py`
- **Define seqdb domain interfaces and policies for domain.service.seq.** (1 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **Any** (1 connections)
- **# TODO: this should be parameterised, so that such higher** (1 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **# TODO: convert condensed distance matrix directly to lower triangle** (1 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **Recursively update negative branch lengths by adding the negative branch length…** (1 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **# TODO: check if this is correct. Non-terminal branches may have their length** (1 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **Convert sciply.cluster.hierarchy.to_tree()-output to Newick format. :param…** (1 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **# TODO: Fix filtering for sa_sql quality mixin enum conversion** (1 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`

## Relationships

- [Sequence Repository Queries](Sequence_Repository_Queries.md) (4 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (4 shared connections)
- [Seq Service Interface](Seq_Service_Interface.md) (4 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (4 shared connections)
- [Seqdb File Commands & Enums](Seqdb_File_Commands_&_Enums.md) (3 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (3 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (3 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (2 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (2 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (2 shared connections)

## Source Files

- `gen_epix/seqdb/domain/repository/seq.py`
- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`

## Audit Trail

- EXTRACTED: 56 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*