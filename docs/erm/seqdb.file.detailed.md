# seqdb / FILE — Detailed ERD

Auto-generated.  Service type **FILE** — 1 entities.

```mermaid
erDiagram
    %% seqdb / FILE (detailed)

    %% Entity definitions
    File {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        bytes content
    }

```
