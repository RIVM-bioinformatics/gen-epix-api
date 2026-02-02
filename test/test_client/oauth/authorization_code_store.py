"""
Authorization Code Store

In-memory storage for OAuth 2.0 Authorization Codes used in the
Authorization Code grant flow. Codes are single-use and expire
after a short period.
"""

import base64
import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass
class AuthorizationCode:
    """Representation of an OAuth 2.0 authorization code."""

    code: str
    client_id: str
    user_id: str
    scopes: list[str]
    redirect_uri: str
    nonce: str | None = None
    code_challenge: str | None = None
    code_challenge_method: str | None = None  # "S256" or "plain"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_in: int = 300  # 5 minutes default
    used: bool = False

    @property
    def expires_at(self) -> datetime:
        return self.created_at + timedelta(seconds=self.expires_in)

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at


class AuthorizationCodeStore:
    """In-memory store managing authorization codes."""

    def __init__(self) -> None:
        self._codes: dict[str, AuthorizationCode] = {}

    def issue_code(
        self,
        client_id: str,
        user_id: str,
        scopes: list[str],
        redirect_uri: str,
        nonce: str | None = None,
        code_challenge: str | None = None,
        code_challenge_method: str | None = None,
        expires_in: int = 300,
    ) -> AuthorizationCode:
        code = secrets.token_urlsafe(32)
        auth_code = AuthorizationCode(
            code=code,
            client_id=client_id,
            user_id=user_id,
            scopes=scopes,
            redirect_uri=redirect_uri,
            nonce=nonce,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            expires_in=expires_in,
        )
        self._codes[code] = auth_code
        return auth_code

    def get(self, code: str) -> AuthorizationCode | None:
        return self._codes.get(code)

    def validate(
        self, code: str, client_id: str, redirect_uri: str
    ) -> AuthorizationCode | None:
        auth_code = self._codes.get(code)
        if not auth_code:
            return None
        if auth_code.used or auth_code.is_expired:
            return None
        if auth_code.client_id != client_id:
            return None
        if auth_code.redirect_uri != redirect_uri:
            return None
        return auth_code

    def consume(self, code: str) -> AuthorizationCode | None:
        auth_code = self._codes.get(code)
        if not auth_code:
            return None
        auth_code.used = True
        return auth_code

    @staticmethod
    def verify_pkce(
        code_verifier: str, code_challenge: str, method: str | None
    ) -> bool:
        if not code_challenge:
            # No PKCE required
            return True
        if not code_verifier:
            return False
        if method is None or method.lower() == "plain":
            return secrets.compare_digest(code_verifier, code_challenge)
        # S256 method
        digest = hashlib.sha256(code_verifier.encode()).digest()
        calculated = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        return secrets.compare_digest(calculated, code_challenge)

    def clear(self) -> None:
        self._codes.clear()
