from types import SimpleNamespace
from typing import cast

import pytest

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.service.rbac import BaseRbacService


@pytest.mark.parametrize(
    "method_name",
    ["retrieve_own_permissions", "retrieve_sub_roles"],
)
def test_abstract_handlers_raise_not_implemented_error(method_name: str) -> None:
    method = getattr(BaseRbacService, method_name)

    with pytest.raises(NotImplementedError):
        method(None, None)


def test_register_handlers_registers_expected_handlers() -> None:
    class CrudCommand:
        """Test CRUD command registered by the default handler hook."""

    handlers: dict[type, object] = {}
    crud_handler = object()
    permissions_handler = object()
    sub_roles_handler = object()

    def register_handler(command_class: type, handler: object) -> None:
        handlers[command_class] = handler

    service = cast(
        BaseRbacService,
        SimpleNamespace(
            app=SimpleNamespace(register_handler=register_handler),
            register_default_crud_handlers=lambda: register_handler(
                CrudCommand, crud_handler
            ),
            retrieve_own_permissions=permissions_handler,
            retrieve_sub_roles=sub_roles_handler,
        ),
    )

    BaseRbacService.register_handlers(service)

    assert handlers == {
        CrudCommand: crud_handler,
        command.RetrieveOwnPermissionsCommand: permissions_handler,
        command.RetrieveSubRolesCommand: sub_roles_handler,
    }
