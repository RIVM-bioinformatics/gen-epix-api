"""Exercise outbound OAuth behavior using mocked HTTP clients and retry delays."""

import base64
import json
import logging
from test.util.mock_compat import MagicMock, Mock, patch
from typing import Any

import httpx
import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.services.auth import (
    OauthIdpClient,
    OauthTokenClient,
)
from gen_epix.fastapp.services.auth import (
    oauth_token_client as oauth_token_client_module,
)
from gen_epix.fastapp.services.auth.model import OidcServerCfg

HTTPX_CLIENT = f"{oauth_token_client_module.__name__}.httpx.Client"
SLEEP = f"{oauth_token_client_module.__name__}.time.sleep"


@pytest.fixture(name="discovery_doc")
def fixture_discovery_doc() -> dict[str, Any]:
    """Return fresh, complete discovery metadata for each case."""
    return {
        "issuer": "https://issuer.example.com",
        "authorization_endpoint": "https://issuer.example.com/auth",
        "token_endpoint": "https://issuer.example.com/token",
        "jwks_uri": "https://issuer.example.com/jwks",
        "response_types_supported": ["code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
    }


def _create_server_cfg(**kwargs: Any) -> OidcServerCfg:
    props: dict[str, Any] = {
        "name": "TEST",
        "label": "Test IDP",
        "discovery_url": "https://issuer.example.com/.well-known/openid-configuration",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "scope": "openid",
    }
    return OidcServerCfg(**(props | kwargs))


def _create_http_client_mock(json_data: dict[str, Any]) -> tuple[MagicMock, Mock]:
    """Create the context manager returned by httpx.Client and its client."""
    response: Mock = Mock()
    response.json.return_value = json_data
    client: Mock = Mock()
    client.get.return_value = response
    client.post.return_value = response
    context_manager: MagicMock = MagicMock()
    context_manager.__enter__.return_value = client
    context_manager.__exit__.return_value = None
    return context_manager, client


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestOauthTokenClient:
    """Tests for using OauthTokenClient on its own, as a remote client does."""

    @pytest.mark.parametrize("client_class", [OauthTokenClient, OauthIdpClient])
    @pytest.mark.parametrize("ssl_context", [True, False])
    def test_init_updates_server_cfg_from_discovery_url(
        self,
        client_class: type[OauthTokenClient],
        ssl_context: bool,
        discovery_doc: dict[str, Any],
    ) -> None:
        """Initialize standalone and inherited clients with bounded discovery requests."""
        server_cfg = _create_server_cfg()
        context_manager, http_client = _create_http_client_mock(discovery_doc)

        with patch(HTTPX_CLIENT, return_value=context_manager) as client_factory:
            token_client = client_class(server_cfg=server_cfg, ssl_context=ssl_context)

        client_factory.assert_called_once_with(verify=ssl_context, timeout=10.0)
        http_client.get.assert_called_once_with(server_cfg.discovery_url)
        http_client.get.return_value.raise_for_status.assert_called_once()
        assert token_client.server_cfg.token_endpoint == (
            "https://issuer.example.com/token"
        )
        assert token_client.scheme_name == "https://issuer.example.com"
        # The provided configuration is copied, not updated in place
        assert server_cfg.token_endpoint is None

    @pytest.mark.parametrize("client_class", [OauthTokenClient, OauthIdpClient])
    @pytest.mark.parametrize(
        "timeout_class",
        [
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
            httpx.PoolTimeout,
        ],
        ids=["connect", "read", "write", "pool"],
    )
    @pytest.mark.parametrize("with_logger", [True, False])
    def test_discovery_timeout_raises_initialization_error(
        self,
        client_class: type[OauthTokenClient],
        timeout_class: type[httpx.TimeoutException],
        with_logger: bool,
    ) -> None:
        """Wrap each HTTP timeout phase while preserving its cause and log context."""
        server_cfg = _create_server_cfg()
        logger = Mock(spec=logging.Logger) if with_logger else None
        context_manager, http_client = _create_http_client_mock({})
        timeout = timeout_class("discovery endpoint did not respond")
        http_client.get.side_effect = timeout

        with (
            patch(HTTPX_CLIENT, return_value=context_manager) as client_factory,
            pytest.raises(exc.InitializationServiceError) as error,
        ):
            client_class(server_cfg=server_cfg, logger=logger)

        client_factory.assert_called_once_with(verify=True, timeout=10.0)
        http_client.get.assert_called_once_with(server_cfg.discovery_url)
        context_manager.__exit__.assert_called_once()
        assert error.value.__cause__ is timeout
        assert error.value.message is not None
        assert "Timed out accessing discovery URL" in error.value.message
        assert "10.0 seconds" in error.value.message
        if logger is not None:
            logger.error.assert_called_once()
            log_message = json.loads(logger.error.call_args.args[0])
            assert log_message["msg"] == error.value.message
            assert log_message["scheme_name"] == server_cfg.name

    @pytest.mark.parametrize("client_class", [OauthTokenClient, OauthIdpClient])
    def test_discovery_doc_without_url_does_not_make_request(
        self, client_class: type[OauthTokenClient]
    ) -> None:
        """Initialize directly from metadata without contacting a provider."""
        with patch(HTTPX_CLIENT) as client_factory:
            token_client = client_class(
                server_cfg=_create_server_cfg(discovery_url=None),
                discovery_doc={"issuer": "https://issuer.example.com"},
            )

        client_factory.assert_not_called()
        assert token_client.server_cfg.issuer == "https://issuer.example.com"

    def test_init_without_discovery_url_or_doc_raises(self) -> None:
        """Reject initialization when neither discovery source is supplied."""
        server_cfg = _create_server_cfg(discovery_url=None)

        with pytest.raises(exc.InitializationServiceError):
            OauthTokenClient(server_cfg=server_cfg)

    @pytest.mark.parametrize("failure_stage", ["get", "status", "json", "validation"])
    def test_discovery_failure_retains_generic_error(
        self, failure_stage: str, discovery_doc: dict[str, Any]
    ) -> None:
        """Keep non-timeout discovery failures distinguishable from timeouts."""
        context_manager, http_client = _create_http_client_mock(discovery_doc)
        failure = ValueError("invalid discovery response")
        if failure_stage == "get":
            http_client.get.side_effect = failure
        elif failure_stage == "status":
            http_client.get.return_value.raise_for_status.side_effect = failure
        elif failure_stage == "json":
            http_client.get.return_value.json.side_effect = failure
        else:
            http_client.get.return_value.json.return_value = {}

        with (
            patch(HTTPX_CLIENT, return_value=context_manager),
            pytest.raises(exc.InitializationServiceError) as error,
        ):
            OauthTokenClient(server_cfg=_create_server_cfg())

        assert error.value.message == "Error accessing discovery URL"
        if failure_stage == "validation":
            assert isinstance(error.value.__cause__, exc.InitializationServiceError)
        else:
            assert error.value.__cause__ is failure

    def test_discovery_refresh_preserves_credentials_and_uses_override(
        self, discovery_doc: dict[str, Any], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Apply remote metadata without replacing local credentials."""
        token_client = OauthTokenClient(
            server_cfg=_create_server_cfg(discovery_url=None), discovery_doc={}
        )
        monkeypatch.setattr(token_client, "DEFAULT_DISCOVERY_TIMEOUT", 2.5)
        discovery_doc.update(client_id="untrusted", client_secret="untrusted", extra=1)
        context_manager, _ = _create_http_client_mock(discovery_doc)

        with patch(HTTPX_CLIENT, return_value=context_manager) as client_factory:
            token_client.update_server_config_from_discovery(
                url="https://issuer.example.com/discovery",
                doc={"issuer": "https://local.example.com"},
            )

        client_factory.assert_called_once_with(verify=True, timeout=2.5)
        assert token_client.server_cfg.issuer == discovery_doc["issuer"]
        assert token_client.server_cfg.client_id == "client-id"
        assert token_client.server_cfg.client_secret == "client-secret"
        assert not hasattr(token_client.server_cfg, "extra")

    @pytest.mark.parametrize(
        ("expiry", "expected"),
        [
            (3600, 3600.0),
            (0, 0.0),
            (-1, -1.0),
            (0.5, 0.5),
            (None, None),
            (True, None),
            ("3600", None),
            ([], None),
            (float("inf"), None),
            (float("-inf"), None),
            (float("nan"), None),
            (10**400, None),
        ],
        ids=[
            "integer",
            "zero",
            "negative",
            "fraction",
            "null",
            "boolean",
            "string",
            "list",
            "infinity",
            "negative-infinity",
            "nan",
            "overflow",
        ],
    )
    def test_token_expiry_normalization(
        self, expiry: Any, expected: float | None
    ) -> None:
        """Accept finite expiry numbers and discard unusable provider values."""
        token_client = OauthTokenClient(
            server_cfg=_create_server_cfg(
                discovery_url=None, token_endpoint="https://issuer.example.com/token"
            ),
            discovery_doc={},
        )
        context_manager, _ = _create_http_client_mock(
            {"access_token": "the-token", "expires_in": expiry}
        )
        with patch(HTTPX_CLIENT, return_value=context_manager):
            result = token_client.retrieve_jwt_with_client_credentials_flow_and_expiry(
                ""
            )

        assert result == ("the-token", expected)

    def test_retrieve_jwt_with_client_credentials_flow(self) -> None:
        """Encode the scope and authenticate token requests with client credentials."""
        server_cfg = _create_server_cfg(
            discovery_url=None, token_endpoint="https://issuer.example.com/token"
        )
        token_client = OauthTokenClient(
            server_cfg=server_cfg,
            discovery_doc={"issuer": "https://issuer.example.com"},
        )
        context_manager, http_client = _create_http_client_mock(
            {"access_token": "the-token"}
        )

        with patch(HTTPX_CLIENT, return_value=context_manager):
            token = token_client.retrieve_jwt_with_client_credentials_flow("a b")

        assert token == "the-token"
        http_client.post.assert_called_once()
        args, kwargs = http_client.post.call_args
        assert args == ("https://issuer.example.com/token",)
        assert kwargs["data"] == "grant_type=client_credentials&scope=a%20b"
        assert kwargs["headers"]["Authorization"] == (
            "Basic " + base64.b64encode(b"client-id:client-secret").decode()
        )

    def test_retrieve_jwt_retries_and_then_raises(self) -> None:
        """Exhaust configured retries before reporting provider unavailability."""
        logger: Mock = Mock(spec=logging.Logger)
        logger.level = logging.INFO
        token_client = OauthTokenClient(
            server_cfg=_create_server_cfg(
                discovery_url=None, token_endpoint="https://issuer.example.com/token"
            ),
            logger=logger,
            discovery_doc={"issuer": "https://issuer.example.com"},
            client_credential_flow_max_retries=2,
        )
        context_manager, http_client = _create_http_client_mock({})
        http_client.post.side_effect = RuntimeError("no connection")

        with (
            patch(HTTPX_CLIENT, return_value=context_manager),
            patch(SLEEP) as sleep,
            pytest.raises(exc.ServiceUnavailableError),
        ):
            token_client.retrieve_jwt_with_client_credentials_flow("openid")

        assert http_client.post.call_count == 3
        assert sleep.call_count == 2
        logger.error.assert_called_once()

    @pytest.mark.parametrize("with_logger", [True, False])
    @pytest.mark.parametrize("failure_kind", ["connection", "missing-token", "status"])
    def test_zero_retries_makes_one_attempt(
        self, with_logger: bool, failure_kind: str
    ) -> None:
        """Zero retries still permits one request and never sleeps."""
        logger = Mock(spec=logging.Logger) if with_logger else None
        token_client = OauthTokenClient(
            server_cfg=_create_server_cfg(
                discovery_url=None, token_endpoint="https://issuer.example.com/token"
            ),
            discovery_doc={},
            logger=logger,
        )
        context_manager, http_client = _create_http_client_mock({})
        if failure_kind == "connection":
            http_client.post.side_effect = httpx.ConnectError("offline")
        elif failure_kind == "status":
            http_client.post.return_value.raise_for_status.side_effect = ValueError(
                "bad status"
            )

        with (
            patch(HTTPX_CLIENT, return_value=context_manager),
            patch(SLEEP) as sleep,
            pytest.raises(exc.ServiceUnavailableError),
        ):
            token_client.retrieve_jwt_with_client_credentials_flow(
                "openid", max_retries=0, base_delay=0
            )

        http_client.post.assert_called_once()
        sleep.assert_not_called()
        if logger is not None:
            logger.warning.assert_called_once()
            logger.error.assert_called_once()

    def test_retry_recovers_and_preserves_custom_headers(self) -> None:
        """Retry a transient failure with configured delay and copied headers."""
        headers = {"Custom-Header": "value"}
        token_client = OauthTokenClient(
            server_cfg=_create_server_cfg(
                discovery_url=None, token_endpoint="https://issuer.example.com/token"
            ),
            discovery_doc={},
            client_credential_flow_request_headers=headers,
            client_credential_flow_max_retries=1,
            client_credential_flow_base_delay=0.25,
        )
        context_manager, http_client = _create_http_client_mock({"access_token": "ok"})
        http_client.post.side_effect = [
            httpx.ReadTimeout("slow response"),
            http_client.post.return_value,
        ]
        with patch(HTTPX_CLIENT, return_value=context_manager), patch(SLEEP) as sleep:
            assert token_client.retrieve_jwt_with_client_credentials_flow("x&y") == "ok"

        assert http_client.post.call_count == 2
        sleep.assert_called_once_with(0.25)
        assert headers == {"Custom-Header": "value"}
        assert http_client.post.call_args.kwargs["headers"]["Custom-Header"] == "value"
        assert http_client.post.call_args.kwargs["data"].endswith("scope=x%26y")

    @pytest.mark.parametrize("refresh_finds_endpoint", [True, False])
    def test_missing_token_endpoint_refreshes_discovery(
        self, refresh_finds_endpoint: bool, discovery_doc: dict[str, Any]
    ) -> None:
        """Refresh absent token metadata and fail if discovery still omits it."""
        logger = Mock(spec=logging.Logger)
        logger.level = logging.DEBUG
        token_client = OauthTokenClient(
            server_cfg=_create_server_cfg(discovery_url=None),
            discovery_doc={},
            logger=logger,
        )
        token_client.server_cfg.discovery_url = "https://issuer.example.com/discovery"
        if not refresh_finds_endpoint:
            discovery_doc.pop("token_endpoint")
        context_manager, http_client = _create_http_client_mock(discovery_doc)
        http_client.post.return_value = Mock()
        http_client.post.return_value.json.return_value = {"access_token": "ok"}
        with patch(HTTPX_CLIENT, return_value=context_manager):
            if refresh_finds_endpoint:
                assert (
                    token_client.retrieve_jwt_with_client_credentials_flow("") == "ok"
                )
            else:
                with pytest.raises(exc.ServiceUnavailableError, match="Token endpoint"):
                    token_client.retrieve_jwt_with_client_credentials_flow("")
                http_client.post.assert_not_called()

        logger.debug.assert_called_once()

    def test_oauth_idp_client_extends_token_client(self) -> None:
        """Keep outbound token retrieval shared with the inbound IDP client."""
        assert issubclass(OauthIdpClient, OauthTokenClient)
        assert (
            OauthIdpClient.retrieve_jwt_with_client_credentials_flow
            is OauthTokenClient.retrieve_jwt_with_client_credentials_flow
        )
