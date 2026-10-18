"""Unit tests for the casedb ABAC endpoint registration adapter."""

from test.util.mock_compat import Mock, patch

import pytest

from gen_epix.casedb.api import abac as casedb_abac
from gen_epix.casedb.domain import enum


@pytest.fixture(name="common_factory")
def common_factory_fixture():
    """Patch the shared ABAC endpoint factory."""
    with patch(f"{casedb_abac.__name__}.create_common_abac_endpoints") as factory:
        yield factory


def test_delegates_with_casedb_abac_service_type(common_factory) -> None:
    """Delegate to the shared factory using the casedb ABAC service type."""
    router, app, handler = Mock(), Mock(), Mock()

    casedb_abac.create_abac_endpoints(router, app, handler)

    common_factory.assert_called_once_with(
        router=router,
        app=app,
        service_type=enum.ServiceType.ABAC,
        handle_exception=handler,
    )


def test_handle_exception_defaults_to_none(common_factory) -> None:
    """Pass None through when no exception handler is supplied."""
    casedb_abac.create_abac_endpoints(Mock(), Mock())

    assert common_factory.call_args.kwargs["handle_exception"] is None


def test_extra_kwargs_are_ignored(common_factory) -> None:
    """Swallow unknown keyword arguments instead of forwarding them."""
    casedb_abac.create_abac_endpoints(Mock(), Mock(), unexpected=1)

    assert "unexpected" not in common_factory.call_args.kwargs
    assert set(common_factory.call_args.kwargs) == {
        "router",
        "app",
        "service_type",
        "handle_exception",
    }


def test_factory_exception_propagates(common_factory) -> None:
    """Propagate errors raised by the shared factory."""
    common_factory.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        casedb_abac.create_abac_endpoints(Mock(), Mock())
