"""Verify that SeqDB ABAC policy sets reference the correct command classes."""

import pytest

from gen_epix.commondb.domain import command as commondb_command
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.service.abac import BaseAbacService


@pytest.mark.parametrize(
    ("command_set", "expected_commands"),
    [
        (
            "ORGANIZATION_ADMIN_WRITE_COMMANDS",
            {command.ContactCrudCommand, command.SiteCrudCommand},
        ),
        (
            "READ_ORGANIZATION_RESULTS_ONLY_COMMANDS",
            {
                command.OrganizationAdminPolicyCrudCommand,
                commondb_command.OrganizationIdentifierIssuerLinkCrudCommand,
                command.UserInvitationCrudCommand,
                command.RetrieveInviteUserConstraintsCommand,
            },
        ),
        ("READ_SELF_RESULTS_ONLY_COMMANDS", set()),
        ("READ_USER_COMMANDS", {command.UserCrudCommand}),
        (
            "UPDATE_USER_COMMANDS",
            {command.InviteUserCommand, command.UpdateUserCommand},
        ),
    ],
    ids=[
        "organization-admin-write",
        "read-organization-results-only",
        "read-self-results-only",
        "read-user",
        "update-user",
    ],
)
def test_command_sets_use_seqdb_command_types(command_set, expected_commands):
    """Keep each ABAC policy command set aligned with its domain contract."""
    assert getattr(BaseAbacService, command_set) == expected_commands
