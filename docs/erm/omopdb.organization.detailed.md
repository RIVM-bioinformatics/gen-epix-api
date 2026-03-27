# omopdb / ORGANIZATION — Detailed ERD

Auto-generated.  Service type **ORGANIZATION** — 14 entities.

```mermaid
erDiagram
    %% omopdb / ORGANIZATION (detailed)

    %% Relationships
    OrganizationIdentifierIssuerLink }o--|| Organization : "organization_id"
    OrganizationIdentifierIssuerLink }o--|| IdentifierIssuer : "identifier_issuer_id"
<<<<<<< HEAD
=======
    UserInvitation }o--|| Organization : "organization_id"
    UserInvitation }o--|| User : "invited_by_user_id"
    Contact }o--|| Site : "site_id"
    Site }o--|| Organization : "organization_id"
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    OrganizationSetMember }o--|| OrganizationSet : "organization_set_id"
    OrganizationSetMember }o--|| Organization : "organization_id"
    Contact }o--|| Site : "site_id"
    Site }o--|| Organization : "organization_id"
    DataCollectionSetMember }o--|| DataCollectionSet : "data_collection_set_id"
    DataCollectionSetMember }o--|| DataCollection : "data_collection_id"
    User }o--|| Organization : "organization_id"
<<<<<<< HEAD
    UserInvitation }o--|| Organization : "organization_id"
    UserInvitation }o--|| User : "invited_by_user_id"

    %% Entity definitions
    OrganizationIdentifierIssuerLink {
        UUID id PK
        UUID organization_id FK
        UUID identifier_issuer_id FK
    }

    OrganizationSetMember {
=======

    %% Entity definitions
    IdentifierIssuer {
        UUID id PK
        string code
        string name
        string description
    }

    OrganizationIdentifierIssuerLink {
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
        UUID id PK
        UUID organization_set_id FK
        UUID organization_id FK
<<<<<<< HEAD
=======
        UUID identifier_issuer_id FK
    }

    UserInvitation {
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
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

    Contact {
        UUID id PK
        UUID site_id FK
        string name
        string email
        string phone
    }

<<<<<<< HEAD
    Site {
        UUID id PK
=======
    DataCollectionSet {
        UUID id PK
        string name
        string description
    }

    Site {
        UUID id PK
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
        UUID organization_id FK
        string name
    }

<<<<<<< HEAD
    DataCollection {
        UUID id PK
        string name
        string description
    }

    IdentifierIssuer {
        UUID id PK
        string code
        string name
        string description
=======
    OrganizationSetMember {
        UUID id PK
        UUID organization_set_id FK
        UUID organization_id FK
    }

    OrganizationSet {
        UUID id PK
        string name
        string description
    }

    UserInvitationConstraints {
        UUID id
        set[string] roles
        set[UUID] organization_ids
    }

    DataCollectionSetMember {
        UUID id PK
        UUID data_collection_set_id FK
        UUID data_collection_id FK
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

    DataCollectionSetMember {
        UUID id PK
        UUID data_collection_set_id FK
        UUID data_collection_id FK
    }

<<<<<<< HEAD
    OrganizationSet {
=======
    DataCollection {
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
        UUID id PK
        string name
        string description
    }

<<<<<<< HEAD
    UserNameEmail {
        UUID id
        string name
        string email
    }

=======
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    Organization {
        UUID id PK
        string code
        string name
        string description
    }

<<<<<<< HEAD
    User {
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
        UUID id
        set[string] roles
        set[UUID] organization_ids
    }

    DataCollectionSet {
        UUID id PK
=======
    UserNameEmail {
        UUID id
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
        string name
        string description
    }

    UserInvitation {
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

```
