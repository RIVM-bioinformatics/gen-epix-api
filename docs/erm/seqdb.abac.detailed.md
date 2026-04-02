# seqdb / ABAC — Detailed ERD

Auto-generated.  Service type **ABAC** — 1 entities.

```mermaid
erDiagram
    %% seqdb / ABAC (detailed)

    %% Entity definitions
    OrganizationAdminPolicy {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID organization_id FK
        UUID user_id FK
        bool is_active
    }

```
