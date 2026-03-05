"""
JSON Web Key Set (JWKS) Manager

This module handles JWT token generation, verification, and key management
for the OAuth 2.0 provider. It generates RSA key pairs and provides
JWKS endpoints for token verification.
"""

import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


class JWKSManager:
    """Manages JSON Web Keys for JWT token operations."""

    def __init__(self, key_size: int = 2048):
        """Initialize JWKS manager with a new RSA key pair."""
        self.key_size = key_size
        self._private_key: RSAPrivateKey
        self._public_key: RSAPublicKey
        self._kid: str
        self._generate_key_pair()

    def _generate_key_pair(self) -> None:
        """Generate a new RSA key pair."""
        # Generate private key
        self._private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=self.key_size, backend=default_backend()
        )

        # Get public key
        self._public_key = self._private_key.public_key()

        # Generate key ID (kid) from public key
        public_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        self._kid = hashlib.sha256(public_pem).hexdigest()[:16]

    def create_jwt(self, payload: dict[str, Any], algorithm: str = "RS256") -> str:
        """Create a JWT token with the given payload."""
        if not payload.get("kid"):
            payload["kid"] = self._kid

        # Convert private key to PEM format for PyJWT
        private_pem = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Create JWT with key ID in header
        headers = {"kid": self._kid}

        return jwt.encode(
            payload=payload, key=private_pem, algorithm=algorithm, headers=headers
        )

    def verify_jwt(
        self, token: str, algorithm: str = "RS256", audience: str | None = None
    ) -> dict[str, Any]:
        """Verify and decode a JWT token."""
        # Convert public key to PEM format for PyJWT
        public_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        decode_kwargs = {"jwt": token, "key": public_pem, "algorithms": [algorithm]}

        if audience is not None:
            # Validate against the provided audience
            decode_kwargs["audience"] = audience
        else:
            # Disable audience validation if no audience provided
            decode_kwargs["options"] = {"verify_aud": False}

        decoded = jwt.decode(**decode_kwargs)
        return cast(dict[str, Any], decoded)

    def get_public_keys(self) -> dict[str, Any]:
        """Get the public keys in JWKS format."""
        # Get public key numbers
        public_numbers = self._public_key.public_numbers()

        # Convert to bytes with proper padding
        def _int_to_base64url_uint(val: int) -> str:
            """Convert integer to base64url-encoded bytes."""
            byte_length = (val.bit_length() + 7) // 8
            val_bytes = val.to_bytes(byte_length, "big")
            return base64.urlsafe_b64encode(val_bytes).decode("ascii").rstrip("=")

        # Create JWK
        jwk = {
            "kty": "RSA",
            "use": "sig",
            "kid": self._kid,
            "alg": "RS256",
            "n": _int_to_base64url_uint(public_numbers.n),
            "e": _int_to_base64url_uint(public_numbers.e),
        }

        return {"keys": [jwk]}

    def get_key_id(self) -> str:
        """Get the current key ID."""
        return self._kid

    def rotate_keys(self) -> str:
        """Generate a new key pair and return the new key ID."""
        old_kid = self._kid
        self._generate_key_pair()
        return self._kid

    def create_id_token(
        self,
        subject: str,
        audience: str,
        issuer: str,
        expires_in: int = 3600,
        nonce: str | None = None,
        additional_claims: dict[str, Any] | None = None,
    ) -> str:
        """Create an OpenID Connect ID Token."""
        now = datetime.now(timezone.utc)

        payload = {
            "iss": issuer,
            "sub": subject,
            "aud": audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
            "auth_time": int(now.timestamp()),
        }

        if nonce:
            payload["nonce"] = nonce

        if additional_claims:
            payload.update(additional_claims)

        return self.create_jwt(payload)

    def validate_token_signature(self, token: str) -> bool:
        """Validate only the signature of a JWT token without checking claims."""
        try:
            self.verify_jwt(token)
            return True
        except jwt.InvalidTokenError:
            return False

    def decode_token_header(self, token: str) -> dict[str, Any]:
        """Decode JWT header without verification."""
        try:
            return jwt.get_unverified_header(token)
        except jwt.InvalidTokenError:
            return {}

    def decode_token_payload(self, token: str) -> dict[str, Any]:
        """Decode JWT payload without verification (use carefully!)."""
        try:
            # This is unsafe and should only be used for debugging
            decoded = jwt.decode(token, options={"verify_signature": False})
            return cast(dict[str, Any], decoded)
        except jwt.InvalidTokenError:
            return {}

    def get_public_key_pem(self) -> str:
        """Get the public key in PEM format."""
        pem_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem_bytes.decode("utf-8")

    def get_private_key_pem(self) -> str:
        """Get the private key in PEM format (use with caution!)."""
        pem_bytes = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return pem_bytes.decode("utf-8")
