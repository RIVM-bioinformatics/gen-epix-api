"""Define commondb commands for retrieving role-based access-control data."""

from gen_epix.commondb.domain.command.base import Command

# Non-CRUD commands


class RetrieveOwnPermissionsCommand(Command):
    """Represents a request to retrieve the effective permissions of the executing user."""

    pass


class RetrieveSubRolesCommand(Command):
    """Represents a request to retrieve all roles inherited below the executing user's assigned roles.

    The result includes sub-roles that are also inherited through another
    assigned role.
    """

    pass


# CRUD commands
