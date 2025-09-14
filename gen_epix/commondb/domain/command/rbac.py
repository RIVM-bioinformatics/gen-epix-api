from gen_epix.commondb.domain.command.base import Command

# Non-CRUD commands


class RetrieveOwnPermissionsCommand(Command):
    pass


class RetrieveSubRolesCommand(Command):
    """
    Retrieves all sub-roles of a user. If the current user roles themselves have some
    sub-roles of each other, those will be included as well.
    """

    pass


# CRUD commands
