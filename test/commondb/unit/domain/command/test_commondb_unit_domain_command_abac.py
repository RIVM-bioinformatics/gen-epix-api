from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command import abac
from gen_epix.commondb.domain.command.base import Command, CrudCommand


def test_retrieve_organizations_under_admin_command_uses_shared_command_base() -> None:
    command = abac.RetrieveOrganizationsUnderAdminCommand()

    assert isinstance(command, Command)
    assert command.user is None


def test_organization_admin_policy_crud_command_targets_policy_model() -> None:
    command_class = abac.OrganizationAdminPolicyCrudCommand

    assert issubclass(command_class, CrudCommand)
    assert command_class.MODEL_CLASS is model.OrganizationAdminPolicy
