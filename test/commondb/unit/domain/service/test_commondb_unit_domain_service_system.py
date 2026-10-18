from types import SimpleNamespace
from typing import cast

import pytest

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.service.system import BaseSystemService


@pytest.mark.parametrize(
    "method_name",
    [
        "register_policies",
        "retrieve_outages",
        "retrieve_licenses",
        "retrieve_feature_flags",
        "delete_all_operational_data",
        "delete_all_ref_data",
    ],
)
def test_abstract_methods_raise_not_implemented_error(method_name: str) -> None:
    method = getattr(BaseSystemService, method_name)

    with pytest.raises(NotImplementedError):
        if method_name == "register_policies":
            method(None)
        else:
            method(None, None)


def test_register_handlers_registers_expected_handlers() -> None:
    class CrudCommand:
        """Test CRUD command registered by the default handler hook."""

    handlers: dict[type, object] = {}
    crud_handler = object()
    operational_data_handler = object()
    ref_data_handler = object()
    outages_handler = object()
    licenses_handler = object()
    feature_flags_handler = object()

    def register_handler(command_class: type, handler: object) -> None:
        handlers[command_class] = handler

    service = cast(
        BaseSystemService,
        SimpleNamespace(
            app=SimpleNamespace(register_handler=register_handler),
            register_default_crud_handlers=lambda: register_handler(
                CrudCommand, crud_handler
            ),
            delete_all_operational_data=operational_data_handler,
            delete_all_ref_data=ref_data_handler,
            retrieve_outages=outages_handler,
            retrieve_licenses=licenses_handler,
            retrieve_feature_flags=feature_flags_handler,
        ),
    )

    BaseSystemService.register_handlers(service)

    assert handlers == {
        CrudCommand: crud_handler,
        command.DeleteAllOperationalDataCommand: operational_data_handler,
        command.DeleteAllRefDataCommand: ref_data_handler,
        command.RetrieveOutagesCommand: outages_handler,
        command.RetrieveLicensesCommand: licenses_handler,
        command.RetrieveFeatureFlagsCommand: feature_flags_handler,
    }
