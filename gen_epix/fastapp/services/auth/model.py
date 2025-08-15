from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import AuthProtocol, OauthFlowType
from gen_epix.fastapp.model import Model


class IDPUser(Model):
    ENTITY: ClassVar = Entity()

    issuer: str = Field(description="The issuer of the user")
    sub: str = Field(description="The sub of the user")


class IdentityProvider(Model):
    ENTITY: ClassVar = Entity()

    name: str = Field(description="Name of the identity provider")
    label: str = Field(description="Label of the identity provider")
    issuer: str = Field(description="The issuer URL of the identity provider")
    auth_protocol: AuthProtocol = Field(description="The authentication protocol")
    oauth_flow: OauthFlowType | None = Field(
        default=None, description="The OAuth flow type of the identity provider"
    )
    discovery_url: str | None = Field(
        default=None, description="The discovery URL of the identity provider"
    )
    client_id: str | None = Field(
        default=None, description="The client ID of the identity provider"
    )
    client_secret: str | None = Field(
        default=None, description="The client secret of the identity provider"
    )
    scope: str | None = Field(
        default=None, description="The scope of the identity provider"
    )


class Claims(Model):
    ENTITY: ClassVar = Entity()

    scheme: str = Field(description="The authorization scheme of the token")
    token: str = Field(description="The original token containing the claims")
    idp_client_id: UUID = Field(
        description="The ID of the IDP client that processed the claims"
    )
    claims: dict[str, str | int | bool | list[str]] = Field(
        description="The claims as verified and processed by the IDP client"
    )


class OIDCConfiguration(Model):
    ENTITY: ClassVar = Entity()

    name: str = Field(description="Service name")
    label: str = Field(description="Service label")
    discovery_url: str = Field(
        description="The URL of the OpenID Connect discovery document"
    )
    client_id: str = Field(description="The client ID of the application")
    client_secret: str | None = Field(
        default=None, description="The client secret of the application"
    )
    scope: str = Field(description="The scope of the application")
