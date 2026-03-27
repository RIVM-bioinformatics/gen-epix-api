# omopdb / ORGANIZATION — Simplified ERD

Auto-generated.  Service type **ORGANIZATION** — 14 entities, relationships only.

```mermaid
erDiagram
    %% omopdb / ORGANIZATION (simplified)

    %% Relationships
    OrganizationIdentifierIssuerLink }o--|| Organization : "organization_id"
    OrganizationIdentifierIssuerLink }o--|| IdentifierIssuer : "identifier_issuer_id"
    UserInvitation }o--|| Organization : "organization_id"
    UserInvitation }o--|| User : "invited_by_user_id"
    Contact }o--|| Site : "site_id"
    Site }o--|| Organization : "organization_id"
    OrganizationSetMember }o--|| OrganizationSet : "organization_set_id"
    OrganizationSetMember }o--|| Organization : "organization_id"
    DataCollectionSetMember }o--|| DataCollectionSet : "data_collection_set_id"
    DataCollectionSetMember }o--|| DataCollection : "data_collection_id"
    User }o--|| Organization : "organization_id"

    UserInvitationConstraints {
    }

    UserNameEmail {
    }

```
