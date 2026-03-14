# commondb — Detailed Entity-Relationship Diagram

Auto-generated from domain model definitions.  Contains **14** persistable entities with their field definitions.

```mermaid
erDiagram
    %% commondb — all persistable entities (detailed)

    %% Relationships
    OrganizationSetMember }o--|| OrganizationSet : "organization_set_id"
    OrganizationSetMember }o--|| Organization : "organization_id"
    DataCollectionSetMember }o--|| DataCollectionSet : "data_collection_set_id"
    DataCollectionSetMember }o--|| DataCollection : "data_collection_id"
    OrganizationIdentifierIssuerLink }o--|| Organization : "organization_id"
    OrganizationIdentifierIssuerLink }o--|| IdentifierIssuer : "identifier_issuer_id"
    Site }o--|| Organization : "organization_id"
    Contact }o--|| Site : "site_id"
    User }o--|| Organization : "organization_id"
    UserInvitation }o--|| Organization : "organization_id"
    UserInvitation }o--|| User : "invited_by_user_id"
    OrganizationAdminPolicy }o--|| Organization : "organization_id"
    OrganizationAdminPolicy }o--|| User : "user_id"

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

    Organization {
        UUID id PK
        string code
        string name
        string description
    }

    OrganizationSet {
        UUID id PK
        string name
        string description
    }

    OrganizationSetMember {
        UUID id PK
        UUID organization_set_id FK
        UUID organization_id FK
    }

    DataCollection {
        UUID id PK
        string name
        string description
    }

    DataCollectionSet {
        UUID id PK
        string name
        string description
    }

    DataCollectionSetMember {
        UUID id PK
        UUID data_collection_set_id FK
        UUID data_collection_id FK
    }

    IdentifierIssuer {
        UUID id PK
        string code
        string name
        string description
    }

    OrganizationIdentifierIssuerLink {
        UUID id PK
        UUID organization_id FK
        UUID identifier_issuer_id FK
    }

    Site {
        UUID id PK
        UUID organization_id FK
        string name
    }

    Contact {
        UUID id PK
        UUID site_id FK
        string name
        string email
        string phone
    }

    User {
        UUID id PK
        string key
        string email
        string name
        bool is_active
        set[string] roles
        UUID organization_id FK
    }

    UserInvitation {
        UUID id PK
        string key
        string email
        string name
        string token
        timestamp expires_at
        set[string] roles
        UUID invited_by_user_id FK
        UUID organization_id FK
    }

    OrganizationAdminPolicy {
        UUID id PK
        UUID organization_id FK
        UUID user_id FK
        bool is_active
    }

```
