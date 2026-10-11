"""Unit tests for the casedb geography endpoint registration."""

from test.util.mock_compat import Mock, patch

import pytest

from gen_epix.casedb.api import geo as geo_module
from gen_epix.casedb.domain import enum


@pytest.fixture(name="app")
def app_fixture() -> Mock:
    """Provide a mocked application."""
    return Mock()


@pytest.fixture(name="handle_exception")
def handle_exception_fixture() -> Mock:
    """Provide a mocked exception handler."""
    return Mock()


def test_create_geo_endpoints_registers_geo_crud_endpoints(
    app: Mock, handle_exception: Mock
) -> None:
    """Build GEO endpoint sets with the user dependency and generate them."""
    router = Mock()
    endpoint_sets = Mock()
    generator = f"{geo_module.__name__}.CrudEndpointGenerator"

    with patch(generator) as generator_cls:
        generator_cls.create_crud_endpoint_set_for_domain.return_value = endpoint_sets
        geo_module.create_geo_endpoints(router, app, handle_exception)

    generator_cls.create_crud_endpoint_set_for_domain.assert_called_once_with(
        app,
        service_type=enum.ServiceType.GEO,
        user_dependency=app.impl.registered_user_dependency,
    )
    generator_cls.generate_endpoints.assert_called_once_with(
        router, endpoint_sets, handle_exception
    )


def test_create_geo_endpoints_ignores_extra_kwargs(
    app: Mock, handle_exception: Mock
) -> None:
    """Accept and ignore extra keyword arguments from the router factory."""
    with patch(f"{geo_module.__name__}.CrudEndpointGenerator") as generator_cls:
        geo_module.create_geo_endpoints(
            Mock(), app, handle_exception, unused_option=True
        )

    generator_cls.generate_endpoints.assert_called_once()


@pytest.mark.parametrize("handle_exception", [None], ids=["none"])
def test_create_geo_endpoints_requires_exception_handler(app: Mock, handle_exception):
    """Reject a missing exception handler before touching the generator."""
    with patch(f"{geo_module.__name__}.CrudEndpointGenerator") as generator_cls:
        with pytest.raises(AssertionError):
            geo_module.create_geo_endpoints(Mock(), app, handle_exception)

    generator_cls.create_crud_endpoint_set_for_domain.assert_not_called()
    generator_cls.generate_endpoints.assert_not_called()
