# casedb / ORGANIZATION — Simplified ERD

Auto-generated.  Service type **ORGANIZATION** — 15 entities, relationships only.

```mermaid
erDiagram
    %% casedb / ORGANIZATION (simplified)

    %% Relationships
    DataCollectionSetMember }o--|| DataCollectionSet : "data_collection_set_id"
    DataCollectionSetMember }o--|| DataCollection : "data_collection_id"
    UserInvitation }o--|| Organization : "organization_id"
    UserInvitation }o--|| User : "invited_by_user_id"
    OrganizationSetMember }o--|| OrganizationSet : "organization_set_id"
    OrganizationSetMember }o--|| Organization : "organization_id"
    Site }o--|| Organization : "organization_id"
    Contact }o--|| Site : "site_id"
    User }o--|| Organization : "organization_id"
    ExternalIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    OrganizationIdentifierIssuerLink }o--|| Organization : "organization_id"
    OrganizationIdentifierIssuerLink }o--|| IdentifierIssuer : "identifier_issuer_id"

    UserNameEmail {
    }

    UserInvitationConstraints {
    }

```
