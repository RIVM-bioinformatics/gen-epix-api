# casedb / ORGANIZATION — Simplified ERD

Auto-generated.  Service type **ORGANIZATION** — 14 entities, relationships only.

```mermaid
erDiagram
    %% casedb / ORGANIZATION (simplified)

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
=======
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0

    UserNameEmail {
    }

    UserInvitationConstraints {
    }

```
