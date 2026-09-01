# casedb / ONTOLOGY — Detailed ERD

Auto-generated.  Service type **ONTOLOGY** — 6 entities.

```mermaid
erDiagram
    %% casedb / ONTOLOGY (detailed)

    %% Relationships
    Concept }o--|| ConceptSet : "concept_set_id"
    Etiology }o--|| Disease : "disease_id"
    Etiology }o--|| EtiologicalAgent : "etiological_agent_id"
    ConceptRelation }o--|| Concept : "from_concept_id"
    ConceptRelation }o--|| Concept : "to_concept_id"

    %% Entity definitions
    ConceptSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        enum type
        enum unit
        string description
    }

    Disease {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string icd_code
    }

    EtiologicalAgent {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string type
    }

    Concept {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID concept_set_id FK
        string code
        string name
        string description
        int rank
        dict[string, Any] props
    }

    Etiology {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID disease_id FK
        UUID etiological_agent_id FK
    }

    ConceptRelation {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID from_concept_id FK
        UUID to_concept_id FK
        enum relation
    }

```
