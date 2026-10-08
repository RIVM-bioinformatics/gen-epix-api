"""Unit tests for the environment-driven client factory."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import jwt
import pytest

from gen_epix import AppType, create_client, fastapp
from gen_epix.casedb.services.client import CasedbClient
from gen_epix.commondb import client_factory
from gen_epix.commondb.services.client import CommondbClient
from gen_epix.omopdb.services.client import OmopdbClient
from gen_epix.seqdb.services.client import SeqdbClient

_SECRET = "client-factory-test-secret-key-32bytes"
_ENV_SUFFIXES = (
    "HOST",
    "PORT",
    "PROTOCOL",
    "SSL_CERT_FILE",
    "DISABLE_SSL_VERIFICATION",
    "AUTH_PROTOCOL",
    "OAUTH_DISCOVER_FROM_REMOTE",
    "OAUTH_DISCOVERY_URL",
    "OAUTH_TOKEN_ENDPOINT",
    "OAUTH_CLIENT_ID",
    "OAUTH_CLIENT_SECRET",
    "OAUTH_SCOPE",
    "DEFAULT_REQUEST_TIMEOUT",
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Remove client env vars and run in an empty dir so no .env file is read."""
    for app in ("CASEDB", "OMOPDB", "SEQDB", "COMMONDB"):
        for suffix in _ENV_SUFFIXES:
            monkeypatch.delenv(f"{app}_{suffix}", raising=False)
    monkeypatch.chdir(tmp_path)


def _set_env(monkeypatch: pytest.MonkeyPatch, app: str, **values: str) -> None:
    base = {
        "HOST": "svc.example.org",
        "PORT": "8443",
        "OAUTH_TOKEN_ENDPOINT": "https://idp.example.org/token",
        "OAUTH_DISCOVER_FROM_REMOTE": "false",
        "OAUTH_CLIENT_ID": "cid",
        "OAUTH_CLIENT_SECRET": "csecret",
        "OAUTH_SCOPE": "api://x/.default",
    }
    base.update(values)
    for key, value in base.items():
        monkeypatch.setenv(f"{app}_{key}", value)


class TestSettings:
    @pytest.mark.parametrize(
        "app,settings_class",
        [
            ("CASEDB", client_factory.CasedbClientSettings),
            ("OMOPDB", client_factory.OmopdbClientSettings),
            ("SEQDB", client_factory.SeqdbClientSettings),
            ("COMMONDB", client_factory.CommondbClientSettings),
        ],
    )
    def test_env_prefix_per_app(
        self,
        monkeypatch: pytest.MonkeyPatch,
        app: str,
        settings_class: type[client_factory.ClientSettings],
    ) -> None:
        _set_env(monkeypatch, app)
        settings = settings_class.load()
        assert settings.host == "svc.example.org"
        assert settings.port == 8443
        assert settings.oauth_client_secret is not None
        assert settings.oauth_client_secret.get_secret_value() == "csecret"
        assert "csecret" not in repr(settings)

    def test_missing_variable_message(self) -> None:
        with pytest.raises(ValueError, match="SEQDB_PORT"):
            client_factory.SeqdbClientSettings.load()

    def test_invalid_variable_message(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SEQDB_PORT", "not-an-integer")
        with pytest.raises(ValueError, match="validation error"):
            client_factory.SeqdbClientSettings.load()

    def test_env_file_loading(self, tmp_path: Path) -> None:
        (tmp_path / ".env").write_text("SEQDB_PORT=1234\nSEQDB_HOST=from.dotenv\n")
        settings = client_factory.SeqdbClientSettings.load()
        assert (settings.host, settings.port) == ("from.dotenv", 1234)


class TestCreateClient:
    @pytest.mark.parametrize(
        "app,client_class",
        [
            ("casedb", CasedbClient),
            ("omopdb", OmopdbClient),
            (AppType.SEQDB, SeqdbClient),
            ("COMMONDB", CommondbClient),
        ],
    )
    def test_client_class(
        self, monkeypatch: pytest.MonkeyPatch, app: Any, client_class: type
    ) -> None:
        _set_env(monkeypatch, AppType(str(getattr(app, "value", app)).upper()).value)
        client = create_client(app)
        assert type(client) is client_class
        assert client.host == "svc.example.org"
        assert client.port == 8443

    @pytest.mark.parametrize("app", ["nope", "all", AppType.ALL])
    def test_unsupported_app(self, app: Any) -> None:
        with pytest.raises(ValueError, match="Unsupported app"):
            create_client(app)

    def test_retry_policy_and_timeout_passed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _set_env(monkeypatch, "SEQDB", DEFAULT_REQUEST_TIMEOUT="12.5")
        policy = fastapp.RetryPolicy(frozenset({503}), (1,))
        client = create_client("seqdb", retry_policy=policy)
        assert client.retry_policy is policy
        assert client._default_request_timeout == 12.5

    def test_default_has_no_retry_policy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_env(monkeypatch, "SEQDB")
        assert create_client("seqdb").retry_policy is None

    def test_token_bypasses_client_credentials(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _set_env(monkeypatch, "SEQDB")
        client = create_client("seqdb", token="static-token")
        assert client.get_headers(None)["Authorization"] == "Bearer static-token"  # type: ignore[arg-type]
        assert client._oauth_idp_client is None

    def test_token_and_token_provider_exclusive(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _set_env(monkeypatch, "SEQDB")
        with pytest.raises(ValueError, match="not both"):
            create_client("seqdb", token="t", token_provider=lambda: "t")

    def test_explicit_settings(self) -> None:
        settings = client_factory.SeqdbClientSettings(
            port=9, auth_protocol="NONE"  # type: ignore[arg-type]
        )
        assert create_client("seqdb", settings=settings).port == 9


class TestClientCredentialsEndToEnd:
    """Client credentials flow against a mocked token endpoint."""

    @staticmethod
    def _patch_httpx(
        monkeypatch: pytest.MonkeyPatch, token: str
    ) -> list[dict[str, Any]]:
        """Replace httpx.Client in the IDP client, recording constructor kwargs."""
        records: list[dict[str, Any]] = []
        real_client = httpx.Client

        def handler(request: httpx.Request) -> httpx.Response:
            records.append(
                {
                    "url": str(request.url),
                    "authorization": request.headers.get("authorization"),
                    "body": request.content.decode(),
                }
            )
            return httpx.Response(200, json={"access_token": token, "expires_in": 3600})

        def factory(**kwargs: Any) -> httpx.Client:
            records.append({"client_kwargs": kwargs})
            return real_client(transport=httpx.MockTransport(handler))

        monkeypatch.setattr(
            "gen_epix.fastapp.services.auth.oauth_idp_client.httpx.Client", factory
        )
        return records

    def test_obtains_token_with_basic_auth(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _set_env(monkeypatch, "CASEDB")
        token = jwt.encode(
            {"exp": int(datetime.now(timezone.utc).timestamp()) + 3600},
            _SECRET,
            algorithm="HS256",
        )
        records = self._patch_httpx(monkeypatch, token)
        client = create_client("casedb")
        assert client.get_access_token() == token
        client.get_access_token()  # cached
        requests = [r for r in records if "url" in r]
        assert len(requests) == 1
        assert requests[0]["url"] == "https://idp.example.org/token"
        assert requests[0]["authorization"].startswith("Basic ")
        assert "grant_type=client_credentials" in requests[0]["body"]

    def test_disable_ssl_verification_reaches_token_request(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _set_env(monkeypatch, "CASEDB", DISABLE_SSL_VERIFICATION="true")
        records = self._patch_httpx(monkeypatch, "opaque")
        client = create_client("casedb")
        client.get_access_token()
        verify = [r["client_kwargs"]["verify"] for r in records if "client_kwargs" in r]
        assert verify
        assert all(v is client.ssl_context for v in verify)
        assert client.ssl_context is not True

    def test_ssl_cert_file_reaches_token_request(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _set_env(monkeypatch, "CASEDB", SSL_CERT_FILE="/some/ca.pem")
        sentinel = object()
        monkeypatch.setattr(
            "gen_epix.fastapp.client.create_ssl_context",
            lambda host, cert, disable: sentinel,
        )
        records = self._patch_httpx(monkeypatch, "opaque")
        client = create_client("casedb")
        client.get_access_token()
        verify = [r["client_kwargs"]["verify"] for r in records if "client_kwargs" in r]
        assert verify
        assert all(v is sentinel for v in verify)


class TestTokenFiles:
    def test_default_token_file(self) -> None:
        assert client_factory.default_token_file("seqdb") == Path(".token.seqdb")
        assert client_factory.default_token_file(AppType.CASEDB) == Path(
            ".token.casedb"
        )

    def test_resolve_order(self, tmp_path: Path) -> None:
        explicit = tmp_path / "explicit"
        explicit.write_text(" from-file \n")
        Path(".token.seqdb").write_text("from-default")
        assert client_factory.resolve_token("t", explicit, "seqdb") == "t"
        assert client_factory.resolve_token(None, explicit, "seqdb") == "from-file"
        assert client_factory.resolve_token(None, None, "seqdb") == "from-default"

    def test_resolve_none_when_nothing_available(self) -> None:
        assert client_factory.resolve_token(None, None, "seqdb") is None

    def test_empty_token_file_rejected(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty"
        empty.write_text("\n")
        with pytest.raises(ValueError, match="empty"):
            client_factory.read_token_file(empty)
