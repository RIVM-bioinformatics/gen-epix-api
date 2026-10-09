from types import SimpleNamespace
from typing import cast
from uuid import UUID

import pytest

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.enum import ServiceType
from gen_epix.commondb.domain.service.organization import BaseOrganizationService
from gen_epix.fastapp.model import UpdateAssociationCommand


@pytest.mark.parametrize(
    "method_name",
    [
        "retrieve_organization_contacts",
        "retrieve_user_by_key",
        "invite_user",
        "retrieve_invite_user_constraints",
        "register_invited_user",
        "update_user",
        "anonymize_user",
    ],
)
def test_abstract_handlers_raise_not_implemented_error(method_name: str) -> None:
    method = getattr(BaseOrganizationService, method_name)

    with pytest.raises(NotImplementedError):
        method(None, None)


def test_generate_user_invitation_token_returns_uuid4() -> None:
    token = BaseOrganizationService.generate_user_invitation_token(object())

    assert str(UUID(token)) == token
    assert UUID(token).version == 4


def test_register_handlers_registers_expected_handlers() -> None:
    class AssociationCommand:
        """Test association command returned by the domain registry."""

    class CrudCommand:
        """Test CRUD command registered by the default handler hook."""

    handlers: dict[type, object] = {}
    crud_handler = object()
    association_handler = object()
    contacts_handler = object()
    invite_handler = object()
    constraints_handler = object()
    registration_handler = object()
    update_handler = object()
    anonymize_handler = object()

    def register_handler(command_class: type, handler: object) -> None:
        handlers[command_class] = handler

    def get_commands_for_service_type(
        service_type: ServiceType, *, base_class: type
    ) -> list[type]:
        assert service_type is ServiceType.ORGANIZATION
        assert base_class is UpdateAssociationCommand
        return [AssociationCommand]

    service = cast(
        BaseOrganizationService,
        SimpleNamespace(
            app=SimpleNamespace(
                register_handler=register_handler,
                domain=SimpleNamespace(
                    get_commands_for_service_type=get_commands_for_service_type
                ),
            ),
            service_type=ServiceType.ORGANIZATION,
            register_default_crud_handlers=lambda: register_handler(
                CrudCommand, crud_handler
            ),
            update_association=association_handler,
            retrieve_organization_contacts=contacts_handler,
            invite_user=invite_handler,
            retrieve_invite_user_constraints=constraints_handler,
            register_invited_user=registration_handler,
            update_user=update_handler,
            anonymize_user=anonymize_handler,
        ),
    )

    BaseOrganizationService.register_handlers(service)

    assert handlers == {
        CrudCommand: crud_handler,
        AssociationCommand: association_handler,
        command.RetrieveOrganizationContactsCommand: contacts_handler,
        command.InviteUserCommand: invite_handler,
        command.RetrieveInviteUserConstraintsCommand: constraints_handler,
        command.RegisterInvitedUserCommand: registration_handler,
        command.UpdateUserCommand: update_handler,
        command.AnonymizeUserCommand: anonymize_handler,
    }
