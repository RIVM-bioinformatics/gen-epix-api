"""Verify optional automatic-user configuration validation."""

from types import SimpleNamespace

import pytest

from gen_epix.commondb.domain.service.user_manager import BaseUserManager
from gen_epix.fastapp.exc import InitializationServiceError


def test_none_disables_auto_created_user_configuration() -> None:
    """Leave automatic user creation disabled when configuration is omitted."""
    manager = SimpleNamespace()

    BaseUserManager.init_auto_created_user_cfg(manager, None)

    assert manager._auto_created_user_cfg is None


def test_empty_auto_created_user_configuration_is_rejected() -> None:
    """Reject a supplied mapping that omits its required values."""
    manager = SimpleNamespace()

    with pytest.raises(
        InitializationServiceError,
        match="missing required keys: organization_id, roles",
    ):
        BaseUserManager.init_auto_created_user_cfg(manager, {})
