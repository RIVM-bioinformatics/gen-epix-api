# omopdb / ORGANIZATION — Detailed ERD

Auto-generated.  Service type **ORGANIZATION** — 14 entities.

```mermaid
erDiagram
    %% omopdb / ORGANIZATION (detailed)

    %% Relationships
    Site }o--|| Organization : "organization_id"
    User }o--|| Organization : "organization_id"
    UserInvitation }o--|| Organization : "organization_id"
    UserInvitation }o--|| User : "invited_by_user_id"
    DataCollectionSetMember }o--|| DataCollectionSet : "data_collection_set_id"
    DataCollectionSetMember }o--|| DataCollection : "data_collection_id"
    OrganizationIdentifierIssuerLink }o--|| Organization : "organization_id"
    OrganizationIdentifierIssuerLink }o--|| IdentifierIssuer : "identifier_issuer_id"
    Contact }o--|| Site : "site_id"
    OrganizationSetMember }o--|| OrganizationSet : "organization_set_id"
    OrganizationSetMember }o--|| Organization : "organization_id"

    %% Entity definitions
    Site {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID organization_id FK
        string name
    }

    OrganizationSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
    }

    User {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string key
        string email
        string name
        string description
        bool is_active
        set[string] roles
        UUID organization_id FK
    }

    UserInvitationConstraints {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id
        set[string] roles
        set[UUID] organization_ids
    }

    UserNameEmail {
        UUID id
        string name
        string email
    }

    UserInvitation {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string key
        string email
        string name
        string description
        string token
        timestamp expires_at
        set[string] roles
        UUID invited_by_user_id FK
        UUID organization_id FK
    }

    Organization {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        string description
    }

    DataCollectionSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID data_collection_set_id FK
        UUID data_collection_id FK
    }

    DataCollectionSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
    }

    DataCollection {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
    }

    OrganizationIdentifierIssuerLink {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID organization_id FK
        UUID identifier_issuer_id FK
    }

    IdentifierIssuer {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        string description
    }

    Contact {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID site_id FK
        string name
        string email
        string phone
    }

    OrganizationSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID organization_set_id FK
        UUID organization_id FK
    }

```
