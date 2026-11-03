import base64
import logging
from test.util.mock_compat import MagicMock, Mock, patch
from typing import Any

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.services.auth import OauthIdpClient, OauthTokenClient
from gen_epix.fastapp.services.auth.model import OidcServerCfg

HTTPX_CLIENT = "gen_epix.fastapp.services.auth.oauth_token_client.httpx.Client"
SLEEP = "gen_epix.fastapp.services.auth.oauth_token_client.time.sleep"


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

    def test_init_updates_server_cfg_from_discovery_url(self) -> None:
        server_cfg = _create_server_cfg()
        context_manager, http_client = _create_http_client_mock(
            {
                "issuer": "https://issuer.example.com",
                "authorization_endpoint": "https://issuer.example.com/auth",
                "token_endpoint": "https://issuer.example.com/token",
                "jwks_uri": "https://issuer.example.com/jwks",
                "response_types_supported": ["code"],
                "subject_types_supported": ["public"],
                "id_token_signing_alg_values_supported": ["RS256"],
            }
        )

        with patch(HTTPX_CLIENT, return_value=context_manager):
            token_client = OauthTokenClient(server_cfg=server_cfg)

        http_client.get.assert_called_once_with(server_cfg.discovery_url)
        assert token_client.server_cfg.token_endpoint == (
            "https://issuer.example.com/token"
        )
        assert token_client.scheme_name == "https://issuer.example.com"
        # The provided configuration is copied, not updated in place
        assert server_cfg.token_endpoint is None

    def test_init_without_discovery_url_or_doc_raises(self) -> None:
        server_cfg = _create_server_cfg(discovery_url=None)

        with pytest.raises(exc.InitializationServiceError):
            OauthTokenClient(server_cfg=server_cfg)

    def test_retrieve_jwt_with_client_credentials_flow(self) -> None:
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

        with patch(HTTPX_CLIENT, return_value=context_manager), patch(SLEEP) as sleep:
            with pytest.raises(exc.ServiceUnavailableError):
                token_client.retrieve_jwt_with_client_credentials_flow("openid")

        assert http_client.post.call_count == 3
        assert sleep.call_count == 2
        logger.error.assert_called_once()

    def test_oauth_idp_client_extends_token_client(self) -> None:
        assert issubclass(OauthIdpClient, OauthTokenClient)
        assert (
            OauthIdpClient.retrieve_jwt_with_client_credentials_flow
            is OauthTokenClient.retrieve_jwt_with_client_credentials_flow
        )
