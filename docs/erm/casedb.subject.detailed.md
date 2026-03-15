# casedb / SUBJECT — Detailed ERD

Auto-generated.  Service type **SUBJECT** — 2 entities.

```mermaid
erDiagram
    %% casedb / SUBJECT (detailed)

    %% Relationships
    SubjectIdentifier }o--|| Subject : "subject_id"

    %% Entity definitions
    SubjectIdentifier {
        UUID id PK
        UUID subject_id FK
        UUID identifier_issuer_id FK
        string identifier
    }

    Subject {
        UUID id PK
        UUID data_collection_id FK
        dict[IdentifierIssuer, string] identifiers
        dict[string, Any] content
    }

```
