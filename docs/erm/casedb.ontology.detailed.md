# casedb / ONTOLOGY — Detailed ERD

Auto-generated.  Service type **ONTOLOGY** — 6 entities.

```mermaid
erDiagram
    %% casedb / ONTOLOGY (detailed)

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

    %% Entity definitions
<<<<<<< HEAD
=======
    Etiology {
        UUID id PK
        UUID disease_id FK
        UUID etiological_agent_id FK
    }

    Disease {
        UUID id PK
        string name
        string icd_code
    }

    ConceptSet {
        UUID id PK
        string code
        string name
        enum type
        string description
    }

>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    Concept {
        UUID id PK
        UUID concept_set_id FK
        string code
        string name
        string description
        int rank
        dict[string, Any] props
    }

<<<<<<< HEAD
    ConceptSet {
        UUID id PK
        string code
        string name
        enum type
        string regex
        string schema_definition
        string schema_uri
        string description
    }

=======
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    ConceptRelation {
        UUID id PK
        UUID from_concept_id FK
        UUID to_concept_id FK
        enum relation
    }

<<<<<<< HEAD
    Etiology {
        UUID id PK
        UUID disease_id FK
        UUID etiological_agent_id FK
    }

=======
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    EtiologicalAgent {
        UUID id PK
        string name
        string type
<<<<<<< HEAD
    }

    Disease {
        UUID id PK
        string name
        string icd_code
=======
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

```
