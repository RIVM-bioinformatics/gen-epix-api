"""Verify command translation for OmopDB attribute-based access control."""

import pytest

from gen_epix.commondb.domain import command as common_command
from gen_epix.omopdb.domain import command
from gen_epix.omopdb.domain.service.abac import BaseAbacService


@pytest.mark.parametrize(
    ("actual", "expected"),
    [
        pytest.param(
            BaseAbacService.ORGANIZATION_ADMIN_WRITE_COMMANDS,
            {common_command.ContactCrudCommand, common_command.SiteCrudCommand},
            id="unmapped-shared-commands",
        ),
        pytest.param(
            BaseAbacService.READ_ORGANIZATION_RESULTS_ONLY_COMMANDS,
            {
                command.OrganizationAdminPolicyCrudCommand,
                common_command.OrganizationIdentifierIssuerLinkCrudCommand,
                command.UserInvitationCrudCommand,
                common_command.RetrieveInviteUserConstraintsCommand,
            },
            id="mixed-mapped-and-unmapped-commands",
        ),
        pytest.param(
            BaseAbacService.READ_SELF_RESULTS_ONLY_COMMANDS,
            set(),
            id="empty-group",
        ),
        pytest.param(
            BaseAbacService.READ_USER_COMMANDS,
            {command.UserCrudCommand},
            id="mapped-command",
        ),
        pytest.param(
            BaseAbacService.UPDATE_USER_COMMANDS,
            {command.InviteUserCommand, command.UpdateUserCommand},
            id="multiple-mapped-commands",
        ),
    ],
)
def test_command_groups_use_omopdb_command_types(actual, expected):
    """Check that ABAC groups use their OMOP command types where defined."""
    assert actual == expected
