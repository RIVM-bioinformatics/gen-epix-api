"""Mock exports for tests using pytest-mock's configured backend."""

from __future__ import annotations

from typing import Any

from pytest_mock.plugin import get_mock_module


class _PytestMockConfig:
    """Minimal config shim needed by pytest-mock's backend resolver."""

    def getini(self, name: str) -> Any:
        if name == "mock_use_standalone_module":
            return False
        return False


_mock = get_mock_module(_PytestMockConfig())

Mock = _mock.Mock
MagicMock = _mock.MagicMock
AsyncMock = getattr(_mock, "AsyncMock", _mock.MagicMock)
patch = _mock.patch
call = _mock.call
