# commondb / SYSTEM — Detailed ERD

Auto-generated.  Service type **SYSTEM** — 2 entities.

```mermaid
erDiagram
    %% commondb / SYSTEM (detailed)

    %% Entity definitions
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

    UploadJob {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID user_id
        string job_type
        enum status
        timestamp submitted_at
        timestamp started_at
        timestamp finished_at
        timestamp heartbeat_at
        string worker_id
        string result_json
        int error_status_code
        string error_detail
    }

```
