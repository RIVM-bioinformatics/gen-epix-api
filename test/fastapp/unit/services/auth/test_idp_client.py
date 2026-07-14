"""
Unit tests for IdpClient base class.

Follows the reference test style for structure and clarity.
"""

import asyncio
import ssl
from test.util.mock_compat import Mock
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import Request

from gen_epix.fastapp.services.auth.idp_client import IdpClient


class DummyIdpClient(IdpClient):
    """Concrete minimal client that delegates to base for abstract methods.

    This allows testing the NotImplementedError paths in the base class.
    """

    def get_identity_provider(
        self,
    ) -> Any:  # pragma: no cover - behavior tested via base
        return super().get_identity_provider()  # type: ignore[safe-super]

    async def get_claims_from_jwt(self, jwt_token: str) -> Any:
        return await IdpClient.get_claims_from_jwt(self, jwt_token)  # type: ignore[safe-super]

    def get_claims_from_userinfo(self, access_token: str) -> Any:
        return super().get_claims_from_userinfo(access_token)  # type: ignore[safe-super]

    async def get_claims_from_jwt(self, jwt_token: str) -> dict[str, Any] | None:
        raise NotImplementedError()

    async def __call__(self, request: Request) -> Any:
        return await IdpClient.__call__(self, request)  # type: ignore[safe-super]


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestIdpClientInitialization:
    """Test initialization and public attributes of IdpClient."""

    def test_default_initialization_sets_expected_values(self) -> None:
        # 1. Create input data
        scheme_name: str = "bearer"

        # 2. Set up mocks
        fixed_id: UUID = UUID("00000000-0000-0000-0000-000000000123")

        # 3. Execute
        # Patch uuid4 by monkeypatching via pytest (keeps isolation and type hints)
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("uuid.uuid4", lambda: fixed_id)
            client: DummyIdpClient = DummyIdpClient(scheme_name=scheme_name)

        # 4. Verify
        assert client.scheme_name == scheme_name
        assert client.token_name == IdpClient.DEFAULT_TOKEN
        assert client.id == fixed_id
        assert client.ssl_context is True

    def test_initialization_with_overrides(self) -> None:
        # 1. Create input data
        scheme_name: str = "oauth2"
        token_name: str = "access_token"
        provided_id: UUID = uuid4()
        context: ssl.SSLContext = ssl.create_default_context()

        # 2. Set up mocks - none

        # 3. Execute
        client: DummyIdpClient = DummyIdpClient(
            scheme_name=scheme_name,
            token_name=token_name,
            id=provided_id,
            ssl_context=context,
        )

        # 4. Verify
        assert client.scheme_name == scheme_name
        assert client.token_name == token_name
        assert client.id == provided_id
        assert client.ssl_context is context

    def test_ssl_context_boolean_values(self) -> None:
        # 1. Create input data
        scheme_name: str = "scheme"

        # 2. Set up mocks - none

        # 3. Execute
        client_true: DummyIdpClient = DummyIdpClient(
            scheme_name=scheme_name, ssl_context=True
        )
        client_false: DummyIdpClient = DummyIdpClient(
            scheme_name=scheme_name, ssl_context=False
        )

        # 4. Verify
        assert client_true.ssl_context is True
        assert not (client_false.ssl_context is True)


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestIdpClientAbstractMethods:
    """Test abstract method behavior exposed via base class."""

    def setup_method(self) -> None:
        self.client: DummyIdpClient = DummyIdpClient(scheme_name="bearer")

    def test_get_identity_provider_raises_not_implemented(self) -> None:
        # 1. Create input - none

        # 2. Set up mocks - none

        # 3. Execute & 4. Verify
        with pytest.raises(NotImplementedError):
            _ = self.client.get_identity_provider()

    def test_get_claims_from_jwt_raises_not_implemented(self) -> None:
        # 1. Create input data
        token: str = "jwt-token"

        # 2. Set up mocks - none

        # 3. Execute & 4. Verify
        with pytest.raises(NotImplementedError):
            asyncio.run(self.client.get_claims_from_jwt(token))

    def test_get_claims_from_userinfo_raises_not_implemented(self) -> None:
        # 1. Create input data
        access_token: str = "access"

        # 2. Set up mocks - none

        # 3. Execute & 4. Verify
        with pytest.raises(NotImplementedError):
            _ = self.client.get_claims_from_userinfo(access_token)

    def test___call___raises_not_implemented(self) -> None:
        # 1. Create input data
        request: Request = Mock(spec=Request)

        # 2. Set up mocks - none

        # 3. Execute & 4. Verify
        with pytest.raises(NotImplementedError):
            asyncio.run(self.client(request))
