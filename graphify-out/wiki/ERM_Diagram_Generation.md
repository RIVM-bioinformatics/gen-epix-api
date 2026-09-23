# ERM Diagram Generation

> 54 nodes · cohesion 0.06

## Key Concepts

- **erm_mermaid.py** (15 connections) — `docs/erm/erm_mermaid.py`
- **ErmGenerator** (10 connections) — `docs/erm/erm.py`
- **_build_diagram()** (8 connections) — `docs/erm/erm_mermaid.py`
- **_render_entity_block()** (8 connections) — `docs/erm/erm_mermaid.py`
- **erm.py** (7 connections) — `docs/erm/erm.py`
- **erm_graphviz.py** (7 connections) — `docs/erm/erm_graphviz.py`
- **GraphvizErmGenerator** (7 connections) — `docs/erm/erm_graphviz.py`
- **.generate_erm_diagrams()** (6 connections) — `docs/erm/erm_graphviz.py`
- **generate_hash_for_domain_models()** (6 connections) — `docs/erm/erm_hash.py`
- **MermaidErmGenerator** (6 connections) — `docs/erm/erm_mermaid.py`
- **._generate_for_domain()** (6 connections) — `docs/erm/erm_mermaid.py`
- **._generate_for_service()** (6 connections) — `docs/erm/erm_mermaid.py`
- **erm_hash.py** (5 connections) — `docs/erm/erm_hash.py`
- **.generate_erm_diagrams()** (5 connections) — `docs/erm/erm_mermaid.py`
- **_render_relationships()** (5 connections) — `docs/erm/erm_mermaid.py`
- **_write_md()** (5 connections) — `docs/erm/erm_mermaid.py`
- **._generate_for_domain()** (4 connections) — `docs/erm/erm_graphviz.py`
- **._generate_for_service()** (4 connections) — `docs/erm/erm_graphviz.py`
- **_field_marker()** (4 connections) — `docs/erm/erm_mermaid.py`
- **Path** (4 connections)
- **.generate_erm_diagrams()** (3 connections) — `docs/erm/erm.py`
- **Domain** (3 connections)
- **Path** (3 connections)
- **_annotation_to_mermaid_type()** (3 connections) — `docs/erm/erm_mermaid.py`
- **BaseModel** (3 connections)
- *... and 29 more nodes in this community*

## Relationships

- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (5 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (4 shared connections)
- [Field Type Metadata](Field_Type_Metadata.md) (3 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (1 shared connections)

## Source Files

- `docs/erm/erm.py`
- `docs/erm/erm_graphviz.py`
- `docs/erm/erm_hash.py`
- `docs/erm/erm_mermaid.py`
- `test/general/docs/test_docs_erm.py`

## Audit Trail

- EXTRACTED: 92 (95%)
- INFERRED: 5 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*