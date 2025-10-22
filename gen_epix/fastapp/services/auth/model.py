from typing import ClassVar
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import AuthProtocol, OAuthFlow
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
    oauth_flow: OAuthFlow | None = Field(
        default=None, description="The OAuth flow type of the identity provider"
    )
    discovery_url: str | None = Field(
        default=None, description="The discovery URL of the identity provider"
    )
    client_id: str | None = Field(
        default=None, description="The client ID that tokens should be requested for"
    )
    client_secret: str | None = Field(default=None, description="The client secret")
    scope: str | None = Field(
        default=None, description="The OIDC scopes, space separated"
    )
    public: bool = Field(
        default=False, description="Whether the identity provider is public"
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


class OidcServerCfg(Model):
    """OpenID Connect Provider Configuration model.

    This model represents the OpenID Provider Metadata as defined in Section 3 of the
    OpenID Connect Discovery 1.0 specification. It includes all required, recommended,
    and optional metadata fields that an OpenID Provider may publish in its discovery
    document.

    The metadata is typically retrieved from the /.well-known/openid-configuration
    endpoint and describes the OpenID Provider's configuration, including endpoint
    locations, supported algorithms, and capabilities.

    Reference:
        OpenID Connect Discovery 1.0 incorporating errata set 2, Section 3
        https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata

    Note:
        This model extends the basic configuration fields (name, label, client_id, etc.)
        with the complete set of OpenID Provider Metadata fields for full specification
        compliance.
    """

    NON_SPEC_FIELDS: ClassVar[set[str]] = {
        "name",
        "label",
        "discovery_url",
        "client_id",
        "client_secret",
        "scope",
        "public",
    }
    SPEC_REQUIRED_FIELDS: ClassVar[set[str]] = {
        "issuer",
        "authorization_endpoint",
        "jwks_uri",
        "response_types_supported",
        "subject_types_supported",
        "id_token_signing_alg_values_supported",
    }

    ENTITY: ClassVar = Entity()

    # Core configuration fields (not from discovery document)
    name: str = Field(description="Service name")
    label: str = Field(description="Service label")
    discovery_url: str | None = Field(
        default=None, description="The URL of the OpenID Connect discovery document"
    )
    client_id: str = Field(description="The client ID of the application")
    client_secret: str | None = Field(
        default=None, description="The client secret of the application"
    )
    claim_map: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of identity provider claims to standard names",
    )
    audience: str | None = Field(
        default=None,
        description="The audience that the identity provider will include in the aud claim of tokens",
    )
    scope: str = Field(description="The scope of the application")
    public: bool = Field(
        default=False, description="Whether the identity provider is public"
    )

    # OpenID Provider Metadata fields from Section 3 of the specification

    # REQUIRED fields, made optional here as they may be absent until discovery is done
    issuer: str | None = Field(
        default=None,
        description="URL using the https scheme with no query or fragment components that the OP asserts as its Issuer Identifier",
    )
    authorization_endpoint: str | None = Field(
        default=None, description="URL of the OP's OAuth 2.0 Authorization Endpoint"
    )
    jwks_uri: str | None = Field(
        default=None, description="URL of the OP's JWK Set document"
    )
    response_types_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the OAuth 2.0 response_type values that this OP supports",
    )
    subject_types_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the Subject Identifier types that this OP supports",
    )
    id_token_signing_alg_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the JWS signing algorithms supported by the OP for the ID Token",
    )

    # REQUIRED unless only Implicit Flow is used
    token_endpoint: str | None = Field(
        default=None, description="URL of the OP's OAuth 2.0 Token Endpoint"
    )

    # RECOMMENDED fields
    userinfo_endpoint: str | None = Field(
        default=None, description="URL of the OP's UserInfo Endpoint"
    )
    registration_endpoint: str | None = Field(
        default=None, description="URL of the OP's Dynamic Client Registration Endpoint"
    )
    scopes_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the OAuth 2.0 scope values that this server supports",
    )
    claims_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the Claim Names of the Claims that the OpenID Provider MAY be able to supply values for",
    )

    # OPTIONAL fields
    introspection_endpoint: str | None = Field(
        default=None, description="URL of the OP's Token Introspection Endpoint"
    )
    response_modes_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the OAuth 2.0 response_mode values that this OP supports",
    )
    grant_types_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the OAuth 2.0 Grant Type values that this OP supports",
    )
    acr_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the Authentication Context Class References that this OP supports",
    )
    id_token_encryption_alg_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the JWE encryption algorithms supported by the OP for the ID Token",
    )
    id_token_encryption_enc_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the JWE encryption algorithms supported by the OP for the ID Token",
    )
    userinfo_signing_alg_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the JWS signing algorithms supported by the UserInfo Endpoint",
    )
    userinfo_encryption_alg_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the JWE encryption algorithms supported by the UserInfo Endpoint",
    )
    userinfo_encryption_enc_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the JWE encryption algorithms supported by the UserInfo Endpoint",
    )
    request_object_signing_alg_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the JWS signing algorithms supported by the OP for Request Objects",
    )
    request_object_encryption_alg_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the JWE encryption algorithms supported by the OP for Request Objects",
    )
    request_object_encryption_enc_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the JWE encryption algorithms supported by the OP for Request Objects",
    )
    token_endpoint_auth_methods_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of Client Authentication methods supported by this Token Endpoint",
    )
    token_endpoint_auth_signing_alg_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the JWS signing algorithms supported by the Token Endpoint",
    )
    display_values_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the display parameter values that the OpenID Provider supports",
    )
    claim_types_supported: list[str] | None = Field(
        default=None,
        description="JSON array containing a list of the Claim Types that the OpenID Provider supports",
    )
    service_documentation: str | None = Field(
        default=None,
        description="URL of a page containing human-readable information that developers might want or need to know when using the OpenID Provider",
    )
    claims_locales_supported: list[str] | None = Field(
        default=None,
        description="Languages and scripts supported for values in Claims being returned",
    )
    ui_locales_supported: list[str] | None = Field(
        default=None,
        description="Languages and scripts supported for the user interface",
    )
    claims_parameter_supported: bool | None = Field(
        default=None,
        description="Boolean value specifying whether the OP supports use of the claims parameter",
    )
    request_parameter_supported: bool | None = Field(
        default=None,
        description="Boolean value specifying whether the OP supports use of the request parameter",
    )
    request_uri_parameter_supported: bool | None = Field(
        default=None,
        description="Boolean value specifying whether the OP supports use of the request_uri parameter",
    )
    require_request_uri_registration: bool | None = Field(
        default=None,
        description="Boolean value specifying whether the OP requires any request_uri values used to be pre-registered",
    )
    op_policy_uri: str | None = Field(
        default=None,
        description="URL that the OpenID Provider provides to the person registering the Client to read about the OP's requirements",
    )
    op_tos_uri: str | None = Field(
        default=None,
        description="URL that the OpenID Provider provides to the person registering the Client to read about the OpenID Provider's terms of service",
    )

    @model_validator(mode="after")
    def _validate(self) -> "OidcServerCfg":
        """Validate that all required fields are set after model initialization."""
        for new_claim_name, orig_claim_name in self.claim_map.items():
            if new_claim_name == orig_claim_name:
                raise ValueError(
                    f"Claim map cannot map claim '{new_claim_name}' to itself in OIDC server config '{self.name}'"
                )
        return self

    def is_valid(self) -> bool:
        """Check if the configuration has the required fields set."""
        return all(getattr(self, x) is not None for x in self.SPEC_REQUIRED_FIELDS)

    def get_invalid_fields(self) -> list[str]:
        """Get a list of required fields that are not set."""
        return [x for x in self.SPEC_REQUIRED_FIELDS if getattr(self, x) is None]
