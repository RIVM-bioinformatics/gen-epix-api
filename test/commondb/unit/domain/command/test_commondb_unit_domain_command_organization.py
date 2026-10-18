from uuid import UUID

import pytest
from pydantic import ValidationError

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command import organization
from gen_epix.commondb.domain.command.base import (
    Command,
    CrudCommand,
    UpdateAssociationCommand,
)


@pytest.mark.parametrize(
    ("command_class", "model_class"),
    [
        (organization.OrganizationCrudCommand, model.Organization),
        (organization.UserCrudCommand, model.User),
        (organization.UserInvitationCrudCommand, model.UserInvitation),
        (organization.OrganizationSetCrudCommand, model.OrganizationSet),
        (organization.OrganizationSetMemberCrudCommand, model.OrganizationSetMember),
        (organization.SiteCrudCommand, model.Site),
        (organization.ContactCrudCommand, model.Contact),
        (organization.IdentifierIssuerCrudCommand, model.IdentifierIssuer),
        (organization.DataCollectionCrudCommand, model.DataCollection),
        (organization.DataCollectionSetCrudCommand, model.DataCollectionSet),
        (
            organization.DataCollectionSetMemberCrudCommand,
            model.DataCollectionSetMember,
        ),
        (
            organization.OrganizationIdentifierIssuerLinkCrudCommand,
            model.OrganizationIdentifierIssuerLink,
        ),
    ],
    ids=[
        "organization",
        "user",
        "user-invitation",
        "organization-set",
        "organization-set-member",
        "site",
        "contact",
        "identifier-issuer",
        "data-collection",
        "data-collection-set",
        "data-collection-set-member",
        "organization-identifier-issuer-link",
    ],
)
def test_crud_commands_bind_their_domain_model(
    command_class: type[CrudCommand], model_class: type
) -> None:
    assert command_class.MODEL_CLASS is model_class


@pytest.mark.parametrize(
    ("command_class", "association_class", "field_name1", "field_name2"),
    [
        (
            organization.OrganizationSetOrganizationUpdateAssociationCommand,
            model.OrganizationSetMember,
            "organization_set_id",
            "organization_id",
        ),
        (
            organization.DataCollectionSetDataCollectionUpdateAssociationCommand,
            model.DataCollectionSetMember,
            "data_collection_set_id",
            "data_collection_id",
        ),
        (
            organization.OrganizationIdentifierIssuerLinkUpdateAssociationCommand,
            model.OrganizationIdentifierIssuerLink,
            "organization_id",
            "identifier_issuer_id",
        ),
    ],
    ids=["organization-set", "data-collection-set", "identifier-issuer"],
)
def test_association_commands_bind_association_and_link_fields(
    command_class: type[UpdateAssociationCommand],
    association_class: type,
    field_name1: str,
    field_name2: str,
) -> None:
    assert command_class.ASSOCIATION_CLASS is association_class
    assert command_class.LINK_FIELD_NAME1 == field_name1
    assert command_class.LINK_FIELD_NAME2 == field_name2


@pytest.mark.parametrize(
    "command_class",
    [
        organization.OrganizationSetOrganizationUpdateAssociationCommand,
        organization.DataCollectionSetDataCollectionUpdateAssociationCommand,
        organization.InviteUserCommand,
        organization.RegisterInvitedUserCommand,
        organization.RetrieveOrganizationContactsCommand,
        organization.UpdateUserCommand,
        organization.UpdateUserOwnOrganizationCommand,
        organization.RetrieveInviteUserConstraintsCommand,
        organization.RetrieveOrganizationAdminNameEmailsCommand,
        organization.AnonymizeUserCommand,
        organization.OrganizationCrudCommand,
        organization.UserCrudCommand,
        organization.UserInvitationCrudCommand,
        organization.OrganizationSetCrudCommand,
        organization.OrganizationSetMemberCrudCommand,
        organization.SiteCrudCommand,
        organization.ContactCrudCommand,
        organization.IdentifierIssuerCrudCommand,
        organization.DataCollectionCrudCommand,
        organization.DataCollectionSetCrudCommand,
        organization.DataCollectionSetMemberCrudCommand,
        organization.OrganizationIdentifierIssuerLinkCrudCommand,
        organization.OrganizationIdentifierIssuerLinkUpdateAssociationCommand,
    ],
)
def test_organization_commands_extend_shared_command_base(
    command_class: type[Command],
) -> None:
    assert issubclass(command_class, Command)


def test_retrieve_organization_contacts_requires_one_organization_id() -> None:
    organization_id = UUID("c9db1807-b48d-4f38-b7c5-cd2460fb2802")

    with pytest.raises(ValidationError):
        organization.RetrieveOrganizationContactsCommand()

    command = organization.RetrieveOrganizationContactsCommand(
        organization_id=organization_id
    )

    assert command.organization_id == organization_id


def test_update_user_command_defaults_omitted_updates_to_none() -> None:
    command = organization.UpdateUserCommand(
        tgt_user_id=UUID("37ac0a9b-9b8c-4dcf-9ea6-d8e0285af7bf")
    )

    assert command.is_active is None
    assert command.roles is None
    assert command.organization_id is None


def test_update_user_own_organization_defaults_to_regular_update() -> None:
    command = organization.UpdateUserOwnOrganizationCommand(
        organization_id=UUID("492e1138-1fa7-4708-a0f8-02bf78e9f902")
    )

    assert command.is_new_user is False
