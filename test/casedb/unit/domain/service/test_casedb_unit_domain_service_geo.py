"""Unit tests for the casedb geographic service base class."""

from test.util.mock_compat import Mock, call

import pytest

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.service import geo
from gen_epix.casedb.domain.service.geo import BaseGeoService


class _GeoService(BaseGeoService):
    def retrieve_containing_region(self, cmd):  # type: ignore[no-untyped-def]
        return []


@pytest.fixture
def app() -> Mock:
    app = Mock()
    app.generate_id.return_value = "id-1"
    app.domain.get_crud_commands_for_service_type.return_value = []
    return app


@pytest.fixture
def make_service(app: Mock):
    def _make(**kwargs) -> _GeoService:  # type: ignore[no-untyped-def]
        kwargs.setdefault("service_type", ServiceType.GEO)
        return _GeoService(app, **kwargs)

    return _make


def test_service_type_is_geo() -> None:
    assert BaseGeoService.SERVICE_TYPE == ServiceType.GEO


def test_base_class_is_abstract(app: Mock) -> None:
    with pytest.raises(TypeError, match="retrieve_containing_region"):
        BaseGeoService(app)  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated


def test_retrieve_containing_region_is_abstract() -> None:
    assert "retrieve_containing_region" in BaseGeoService.__abstractmethods__


def test_module_exports_service_class() -> None:
    assert geo.BaseGeoService is BaseGeoService


def test_register_handlers_registers_containing_region_handler(
    app: Mock, make_service
) -> None:
    service = make_service()

    assert (
        call(
            command.RetrieveContainingRegionCommand, service.retrieve_containing_region
        )
        in app.register_handler.call_args_list
    )


def test_register_handlers_registers_crud_commands_for_geo(
    app: Mock, make_service
) -> None:
    crud_cmd_class = Mock()
    app.domain.get_crud_commands_for_service_type.return_value = [crud_cmd_class]

    service = make_service()

    app.domain.get_crud_commands_for_service_type.assert_called_once_with(
        ServiceType.GEO
    )
    assert call(crud_cmd_class, service.crud) in app.register_handler.call_args_list


def test_register_handlers_registers_crud_before_containing_region(
    app: Mock, make_service
) -> None:
    crud_cmd_class = Mock()
    app.domain.get_crud_commands_for_service_type.return_value = [crud_cmd_class]

    make_service()

    registered = [c.args[0] for c in app.register_handler.call_args_list]
    assert registered == [crud_cmd_class, command.RetrieveContainingRegionCommand]


def test_register_handlers_not_called_when_disabled(app: Mock, make_service) -> None:
    make_service(register_handlers=False)

    assert app.register_handler.call_args_list == []


def test_register_handlers_can_be_called_explicitly(app: Mock, make_service) -> None:
    service = make_service(register_handlers=False)

    service.register_handlers()

    assert app.register_handler.call_args_list == [
        call(
            command.RetrieveContainingRegionCommand, service.retrieve_containing_region
        )
    ]


def test_register_handlers_without_crud_commands_registers_only_containment(
    app: Mock, make_service
) -> None:
    make_service()

    assert app.register_handler.call_count == 1
