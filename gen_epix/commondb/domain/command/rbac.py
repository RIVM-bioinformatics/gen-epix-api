"""Define commondb commands for retrieving role-based access-control data."""

from gen_epix.commondb.domain.command.base import Command

# Non-CRUD commands


class RetrieveOwnPermissionsCommand(Command):
    """Retrieve the effective permissions of the executing user."""

    pass


class RetrieveSubRolesCommand(Command):
    """Retrieve all roles inherited below the executing user's assigned roles.

    The result includes sub-roles that are also inherited through another
    assigned role.
    """

    pass


# CRUD commands
