# commondb / ORGANIZATION — Detailed ERD

Auto-generated.  Service type **ORGANIZATION** — 14 entities.

```mermaid
erDiagram
    %% commondb / ORGANIZATION (detailed)

    %% Relationships
    DataCollectionSetMember }o--|| DataCollectionSet : "data_collection_set_id"
    DataCollectionSetMember }o--|| DataCollection : "data_collection_id"
    Contact }o--|| Site : "site_id"
    User }o--|| Organization : "organization_id"
    UserInvitation }o--|| Organization : "organization_id"
    UserInvitation }o--|| User : "invited_by_user_id"
    Site }o--|| Organization : "organization_id"
    OrganizationSetMember }o--|| OrganizationSet : "organization_set_id"
    OrganizationSetMember }o--|| Organization : "organization_id"
    OrganizationIdentifierIssuerLink }o--|| Organization : "organization_id"
    OrganizationIdentifierIssuerLink }o--|| IdentifierIssuer : "identifier_issuer_id"

    %% Entity definitions
    DataCollectionSetMember {
        UUID id PK
        UUID data_collection_set_id FK
        UUID data_collection_id FK
    }

    DataCollectionSet {
        UUID id PK
        string name
        string description
    }

    OrganizationSet {
        UUID id PK
        string name
        string description
    }

    DataCollection {
        UUID id PK
        string name
        string description
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

    IdentifierIssuer {
        UUID id PK
        string code
        string name
        string description
    }

    UserNameEmail {
        UUID id
        string name
        string email
    }

    Site {
        UUID id PK
        UUID organization_id FK
        string name
    }

    OrganizationSetMember {
        UUID id PK
        UUID organization_set_id FK
        UUID organization_id FK
    }

    Organization {
        UUID id PK
        string name
        string legal_entity_code
    }

    OrganizationIdentifierIssuerLink {
        UUID id PK
        UUID organization_id FK
        UUID identifier_issuer_id FK
    }

    UserInvitationConstraints {
        UUID id
        set[string] roles
        set[UUID] organization_ids
    }

```
