"""
OpenID Connect Provider

This module implements OpenID Connect (OIDC) functionality on top of OAuth 2.0,
including ID token generation, userinfo endpoint, and discovery metadata.
"""

from datetime import datetime, timedelta, timezone
from test.test_client.oauth.jwks import JWKSManager
from typing import Any


class OIDCProvider:
    """OpenID Connect provider implementation."""

    def __init__(self, jwks_manager: JWKSManager):
        """Initialize OIDC provider with JWKS manager."""
        self.jwks_manager = jwks_manager

    def create_discovery_document(self, issuer: str) -> dict[str, Any]:
        """Create OpenID Connect discovery document."""
        return {
            "issuer": issuer,
            "authorization_endpoint": f"{issuer}/oauth/authorize",
            "token_endpoint": f"{issuer}/oauth/token",
            "userinfo_endpoint": f"{issuer}/oauth/userinfo",
            "jwks_uri": f"{issuer}/.well-known/jwks.json",
            "introspection_endpoint": f"{issuer}/oauth/introspect",
            "revocation_endpoint": f"{issuer}/oauth/revoke",
            "end_session_endpoint": f"{issuer}/oauth/logout",
            # Supported response types
            "response_types_supported": [
                "code",
                "token",
                "id_token",
                "code token",
                "code id_token",
                "token id_token",
                "code token id_token",
            ],
            # Supported grant types
            "grant_types_supported": [
                "authorization_code",
                "client_credentials",
                "refresh_token",
            ],
            # Supported subject types
            "subject_types_supported": ["public"],
            # Supported signing algorithms
            "id_token_signing_alg_values_supported": ["RS256"],
            "token_endpoint_auth_signing_alg_values_supported": ["RS256"],
            "userinfo_signing_alg_values_supported": ["RS256"],
            # Supported scopes
            "scopes_supported": [
                "openid",
                "profile",
                "email",
                "address",
                "phone",
                "offline_access",
                "read",
                "write",
            ],
            # Supported claims
            "claims_supported": [
                "sub",
                "iss",
                "aud",
                "exp",
                "iat",
                "auth_time",
                "nonce",
                "name",
                "given_name",
                "family_name",
                "email",
                "email_verified",
                "picture",
                "locale",
            ],
            # Authentication methods
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
                "client_secret_jwt",
                "private_key_jwt",
            ],
            # Response modes
            "response_modes_supported": ["query", "fragment", "form_post"],
            # Additional OIDC features
            "claim_types_supported": ["normal"],
            "claims_parameter_supported": False,
            "request_parameter_supported": False,
            "request_uri_parameter_supported": False,
            "require_request_uri_registration": False,
        }

    def create_id_token(
        self,
        subject: str,
        audience: str,
        issuer: str,
        nonce: str | None = None,
        auth_time: int | None = None,
        additional_claims: dict[str, Any] | None = None,
        expires_in: int = 3600,
    ) -> str:
        """Create an OpenID Connect ID Token."""
        now = datetime.now(timezone.utc)

        # Standard OIDC claims
        payload = {
            "iss": issuer,
            "sub": subject,
            "aud": audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
        }

        # Optional auth_time (time when authentication occurred)
        if auth_time:
            payload["auth_time"] = auth_time
        else:
            payload["auth_time"] = int(now.timestamp())

        # Optional nonce for replay protection
        if nonce:
            payload["nonce"] = nonce

        # Additional custom claims
        if additional_claims:
            payload.update(additional_claims)

        return str(self.jwks_manager.create_jwt(payload))

    def validate_id_token(self, id_token: str) -> dict[str, Any]:
        """Validate and decode an ID token."""
        result = self.jwks_manager.verify_jwt(id_token)
        return dict(result) if result else {}

    def create_userinfo_response(
        self,
        subject: str,
        scopes: list[str],
        user_claims: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create userinfo endpoint response based on scopes."""

        # Start with subject
        userinfo: dict[str, Any] = {"sub": subject}

        # Default user claims for client credentials (limited info)
        default_claims = {
            "name": f"Client {subject}",
            "given_name": "Client",
            "family_name": subject,
            "email": f"{subject}@example.com",
            "email_verified": False,
            "picture": f"https://www.gravatar.com/avatar/{hash(subject) % 1000}",
            "locale": "en-US",
        }

        # Use provided claims or defaults
        claims = user_claims or default_claims

        # Add claims based on requested scopes
        if "profile" in scopes:
            profile_claims = [
                "name",
                "given_name",
                "family_name",
                "middle_name",
                "nickname",
                "preferred_username",
                "profile",
                "picture",
                "website",
                "gender",
                "birthdate",
                "zoneinfo",
                "locale",
                "updated_at",
            ]
            for claim in profile_claims:
                if claim in claims:
                    userinfo[claim] = str(claims[claim])

        if "email" in scopes:
            email_claims = ["email", "email_verified"]
            for claim in email_claims:
                if claim in claims:
                    if claim == "email_verified":
                        # Keep boolean for email_verified
                        userinfo[claim] = (
                            bool(claims[claim])
                            if claims[claim] in ["True", "true", True]
                            else False
                        )
                    else:
                        userinfo[claim] = str(claims[claim])

        if "address" in scopes:
            if "address" in claims:
                # Keep address as dict/object
                userinfo["address"] = claims["address"]

        if "phone" in scopes:
            phone_claims = ["phone_number", "phone_number_verified"]
            for claim in phone_claims:
                if claim in claims:
                    if claim == "phone_number_verified":
                        # Keep boolean for phone_number_verified
                        userinfo[claim] = (
                            bool(claims[claim])
                            if claims[claim] in ["True", "true", True]
                            else False
                        )
                    else:
                        userinfo[claim] = str(claims[claim])

        return userinfo

    def get_supported_algorithms(self) -> list[str]:
        """Get list of supported signing algorithms."""
        return ["RS256"]

    def create_jwks_response(self) -> dict[str, Any]:
        """Create JWKS response."""
        result = self.jwks_manager.get_public_keys()
        return dict(result) if result else {}

    def validate_nonce(self, nonce: str) -> bool:
        """Validate nonce parameter (basic validation)."""
        if not nonce:
            return False

        # Basic validation: non-empty string, reasonable length
        return len(nonce) <= 255 and nonce.isprintable()

    def extract_claims_from_scope(self, scopes: list[str]) -> list[str]:
        """Extract claims that should be included based on scopes."""
        claims = ["sub"]  # Always include subject

        if "profile" in scopes:
            claims.extend(
                [
                    "name",
                    "given_name",
                    "family_name",
                    "middle_name",
                    "nickname",
                    "preferred_username",
                    "profile",
                    "picture",
                    "website",
                    "gender",
                    "birthdate",
                    "zoneinfo",
                    "locale",
                ]
            )

        if "email" in scopes:
            claims.extend(["email", "email_verified"])

        if "address" in scopes:
            claims.append("address")

        if "phone" in scopes:
            claims.extend(["phone_number", "phone_number_verified"])

        return list(set(claims))  # Remove duplicates

    def create_logout_response(self, redirect_uri: str | None = None) -> dict[str, Any]:
        """Create logout response."""
        response = {
            "status": "logged_out",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if redirect_uri:
            response["redirect_uri"] = redirect_uri

        return response
