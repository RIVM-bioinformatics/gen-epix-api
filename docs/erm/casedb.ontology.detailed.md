# casedb / ONTOLOGY — Detailed ERD

Auto-generated.  Service type **ONTOLOGY** — 6 entities.

```mermaid
erDiagram
    %% casedb / ONTOLOGY (detailed)

    %% Relationships
    Etiology }o--|| Disease : "disease_id"
    Etiology }o--|| EtiologicalAgent : "etiological_agent_id"
    ConceptRelation }o--|| Concept : "from_concept_id"
    ConceptRelation }o--|| Concept : "to_concept_id"
    Concept }o--|| ConceptSet : "concept_set_id"

    %% Entity definitions
    Etiology {
        UUID id PK
        UUID disease_id FK
        UUID etiological_agent_id FK
    }

    EtiologicalAgent {
        UUID id PK
        string name
        string type
    }

    ConceptRelation {
        UUID id PK
        UUID from_concept_id FK
        UUID to_concept_id FK
        enum relation
    }

    ConceptSet {
        UUID id PK
        string code
        string name
        enum type
        string description
    }

    Concept {
        UUID id PK
        UUID concept_set_id FK
        string code
        string name
        string description
        int rank
        dict[string, Any] props
    }

    Disease {
        UUID id PK
        string name
        string icd_code
    }

```
