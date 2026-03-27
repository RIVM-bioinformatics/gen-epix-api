# casedb / ONTOLOGY — Simplified ERD

Auto-generated.  Service type **ONTOLOGY** — 6 entities, relationships only.

```mermaid
erDiagram
    %% casedb / ONTOLOGY (simplified)

    %% Relationships
<<<<<<< HEAD
=======
    Etiology }o--|| Disease : "disease_id"
    Etiology }o--|| EtiologicalAgent : "etiological_agent_id"
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    Concept }o--|| ConceptSet : "concept_set_id"
    ConceptRelation }o--|| Concept : "from_concept_id"
    ConceptRelation }o--|| Concept : "to_concept_id"
    Etiology }o--|| Disease : "disease_id"
    Etiology }o--|| EtiologicalAgent : "etiological_agent_id"

```
