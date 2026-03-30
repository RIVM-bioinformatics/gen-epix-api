# casedb / SYSTEM — Detailed ERD

Auto-generated.  Service type **SYSTEM** — 2 entities.

```mermaid
erDiagram
    %% casedb / SYSTEM (detailed)

    %% Entity definitions
    PackageMetadata {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id
        string name
        string version
        string license
        string homepage
    }

    Outage {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string description
        timestamp active_from
        timestamp active_to
        timestamp visible_from
        timestamp visible_to
        bool is_active
        bool is_visible
    }

```
