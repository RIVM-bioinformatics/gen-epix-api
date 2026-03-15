# seqdb / SYSTEM — Detailed ERD

Auto-generated.  Service type **SYSTEM** — 2 entities.

```mermaid
erDiagram
    %% seqdb / SYSTEM (detailed)

    %% Entity definitions
    Outage {
        UUID id PK
        string description
        timestamp active_from
        timestamp active_to
        timestamp visible_from
        timestamp visible_to
        bool is_active
        bool is_visible
    }

    PackageMetadata {
        UUID id
        string name
        string version
        string license
        string homepage
    }

```
