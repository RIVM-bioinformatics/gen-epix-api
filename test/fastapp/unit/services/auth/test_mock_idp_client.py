"""
Unit tests for MockIDPClient authentication flow.

Tests cover all public methods and branches, including:
- id property behavior
- abstract methods raising NotImplementedError
- authorization header parsing and scheme handling
- JWT decoding success, empty claims, and error paths
"""

import asyncio
from typing import Any, Dict, Tuple
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.services.auth.mock_idp_client import MockIDPClient
from gen_epix.fastapp.services.auth.model import Claims


class DummyRequest:
    """Simple request-like object exposing headers mapping."""

    def __init__(self, headers: Dict[str, str] | None = None) -> None:
        self.headers: Dict[str, str] = headers or {}


class DummyLogItem:
    """Minimal log item stub compatible with MockIDPClient usage."""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    def dumps(self) -> str:
        return str(self.kwargs)


def create_client(
    *, logger: Mock | None, id_override: UUID | None = None
) -> MockIDPClient:
    """Helper to create a client with optional logger and fixed id."""
    client: MockIDPClient = MockIDPClient(
        logger=logger,
        log_item_class=DummyLogItem,  # type: ignore[arg-type]
        id=id_override if id_override is not None else uuid4(),
    )
    return client


def make_request(auth_header: str | None) -> DummyRequest:
    """Create a request with or without an Authorization header."""
    headers: Dict[str, str] = {}
    if auth_header is not None:
        headers["authorization"] = auth_header
    return DummyRequest(headers=headers)


def assert_logged_with_code(logger: Mock, code: str) -> None:
    """Assert logger.warning was called with a payload containing the code."""
    assert logger.warning.call_count == 1
    arg: str = logger.warning.call_args[0][0]
    assert code in arg


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestPublicInterface:
    """Public properties and abstract methods behavior."""

    def test_id_property_returns_provided_id(self) -> None:
        # 1. Input
        expected_id: UUID = uuid4()
        logger: Mock = Mock()

        # 2. Mocks
        client: MockIDPClient = create_client(logger=logger, id_override=expected_id)

        # 3. Execute
        actual_id: UUID = client.id

        # 4. Verify
        assert actual_id == expected_id

    def test_id_property_generates_uuid(self) -> None:
        # 1. Input
        logger: Mock = Mock()

        # 2. Mocks
        client: MockIDPClient = create_client(logger=logger, id_override=None)

        # 3. Execute
        actual_id: UUID = client.id

        # 4. Verify
        assert isinstance(actual_id, UUID)

    def test_get_identity_provider_not_implemented(self) -> None:
        # 1. Input
        logger: Mock = Mock()
        client: MockIDPClient = create_client(logger=logger)

        # 2. Execute & Verify
        with pytest.raises(NotImplementedError):
            client.get_identity_provider()

    def test_get_claims_from_userinfo_not_implemented(self) -> None:
        # 1. Input
        logger: Mock = Mock()
        client: MockIDPClient = create_client(logger=logger)

        # 2. Execute & Verify
        with pytest.raises(NotImplementedError):
            client.get_claims_from_userinfo("access-token")

    def test_get_claims_from_jwt_not_implemented(self) -> None:
        # 1. Input
        logger: Mock = Mock()
        client: MockIDPClient = create_client(logger=logger)

        # 2. Execute & Verify
        with pytest.raises(NotImplementedError):
            asyncio.run(client.get_claims_from_jwt("jwt-token"))


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestAuthorizationHandling:
    """Authorization header parsing and scheme handling."""

    def test_no_authorization_header_logs_and_returns_none(self) -> None:
        # 1. Input
        logger: Mock = Mock()
        client: MockIDPClient = create_client(logger=logger)
        request: DummyRequest = make_request(None)

        # 2. Execute
        retval = asyncio.run(client(request))  # type: ignore[arg-type]

        # 3. Verify
        assert retval is None
        assert_logged_with_code(logger, "e14344c3")

    def test_no_authorization_header_no_logger_returns_none(self) -> None:
        # 1. Input
        client: MockIDPClient = create_client(logger=None)
        request: DummyRequest = make_request(None)

        # 2. Execute
        retval = asyncio.run(client(request))  # type: ignore[arg-type]

        # 3. Verify
        assert retval is None

    @pytest.mark.parametrize(
        "scheme, token",
        [
            ("Basic", "abc123"),
            ("Digest", "xyz789"),
            ("Token", "tkn000"),
        ],
    )
    def test_non_bearer_scheme_logs_and_returns_none(
        self, scheme: str, token: str
    ) -> None:
        # 1. Input
        logger: Mock = Mock()
        client: MockIDPClient = create_client(logger=logger)
        request: DummyRequest = make_request(f"{scheme} {token}")

        # 2. Mocks
        module_path: str = "gen_epix.fastapp.services.auth.mock_idp_client"
        with patch(
            f"{module_path}.get_authorization_scheme_param", autospec=True
        ) as mock_param:
            mock_param.return_value = (scheme, token)

            # 3. Execute
            retval = asyncio.run(client(request))  # type: ignore[arg-type]

            # 4. Verify
            assert retval is None
            assert_logged_with_code(logger, "dec5fffe")
            mock_param.assert_called_once()
            called_arg: str = mock_param.call_args[0][0]
            assert called_arg == f"{scheme} {token}"

    @pytest.mark.parametrize("scheme", ["Bearer", "bearer"])
    def test_bearer_scheme_decode_returns_claims_success(self, scheme: str) -> None:
        # 1. Input
        logger: Mock = Mock()
        client: MockIDPClient = create_client(logger=logger)
        token: str = "valid.jwt.token"
        request: DummyRequest = make_request(f"{scheme} {token}")
        decoded_claims: Dict[str, Any] = {"sub": "user-123", "role": "admin"}

        # 2. Mocks
        module_path: str = "gen_epix.fastapp.services.auth.mock_idp_client"
        with (
            patch(
                f"{module_path}.get_authorization_scheme_param", autospec=True
            ) as mock_param,
            patch(f"{module_path}.jwt.decode", autospec=True) as mock_decode,
        ):
            mock_param.return_value = (scheme, token)
            mock_decode.return_value = decoded_claims

            # 3. Execute
            retval = asyncio.run(client(request))  # type: ignore[arg-type]

            # 4. Verify
            assert isinstance(retval, Claims)
            assert retval is not None
            assert retval.claims == decoded_claims
            assert retval.scheme == scheme
            assert retval.token == token
            assert retval.idp_client_id == client.id
            mock_param.assert_called_once()
            mock_decode.assert_called_once()
            decode_args: Tuple[Any, ...] = mock_decode.call_args[0]
            decode_kwargs: Dict[str, Any] = mock_decode.call_args.kwargs
            assert decode_args == (token,)
            assert decode_kwargs == {"options": {"verify_signature": False}}
            assert logger.warning.call_count == 0

    def test_bearer_scheme_decode_returns_empty_claims_returns_none(self) -> None:
        # 1. Input
        logger: Mock = Mock()
        client: MockIDPClient = create_client(logger=logger)
        scheme: str = "Bearer"
        token: str = "empty.jwt.token"
        request: DummyRequest = make_request(f"{scheme} {token}")

        # 2. Mocks
        module_path: str = "gen_epix.fastapp.services.auth.mock_idp_client"
        with (
            patch(
                f"{module_path}.get_authorization_scheme_param", autospec=True
            ) as mock_param,
            patch(f"{module_path}.jwt.decode", autospec=True) as mock_decode,
        ):
            mock_param.return_value = (scheme, token)
            mock_decode.return_value = {}

            # 3. Execute
            retval = asyncio.run(client(request))  # type: ignore[arg-type]

            # 4. Verify
            assert retval is None
            mock_param.assert_called_once()
            mock_decode.assert_called_once()
            assert logger.warning.call_count == 0

    def test_bearer_scheme_decode_raises_auth_exception_logs_and_returns_none(
        self,
    ) -> None:
        # 1. Input
        logger: Mock = Mock()
        client: MockIDPClient = create_client(logger=logger)
        scheme: str = "Bearer"
        token: str = "bad.jwt.token"
        request: DummyRequest = make_request(f"{scheme} {token}")

        # 2. Mocks
        module_path: str = "gen_epix.fastapp.services.auth.mock_idp_client"
        with (
            patch(
                f"{module_path}.get_authorization_scheme_param", autospec=True
            ) as mock_param,
            patch(f"{module_path}.jwt.decode", autospec=True) as mock_decode,
        ):
            mock_param.return_value = (scheme, token)
            mock_decode.side_effect = exc.AuthException("decode failed")

            # 3. Execute
            retval = asyncio.run(client(request))  # type: ignore[arg-type]

            # 4. Verify
            assert retval is None
            assert_logged_with_code(logger, "e86a3bd6")
            mock_param.assert_called_once()
            mock_decode.assert_called_once()

    def test_bearer_scheme_decode_raises_auth_exception_no_logger_returns_none(
        self,
    ) -> None:
        # 1. Input
        client: MockIDPClient = create_client(logger=None)
        scheme: str = "Bearer"
        token: str = "bad.jwt.token"
        request: DummyRequest = make_request(f"{scheme} {token}")

        # 2. Mocks
        module_path: str = "gen_epix.fastapp.services.auth.mock_idp_client"
        with (
            patch(
                f"{module_path}.get_authorization_scheme_param", autospec=True
            ) as mock_param,
            patch(f"{module_path}.jwt.decode", autospec=True) as mock_decode,
        ):
            mock_param.return_value = (scheme, token)
            mock_decode.side_effect = exc.AuthException("decode failed")

            # 3. Execute
            retval = asyncio.run(client(request))  # type: ignore[arg-type]

            # 4. Verify
            assert retval is None
            mock_param.assert_called_once()
            mock_decode.assert_called_once()
