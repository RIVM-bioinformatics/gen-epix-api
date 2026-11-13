"""Configure OmopDB commands for shared attribute-based access control.

`BaseAbacService` maps shared ABAC command groups to OmopDB command types where
the domain provides specialized commands. Shared policy registration consumes
these groups without changing its authorization behavior.
"""

from gen_epix.commondb.services import AbacService as CommonAbacService
from gen_epix.fastapp.model import Command
from gen_epix.omopdb.domain import command


class BaseAbacService(CommonAbacService):
    """Encapsulates OmopDB command groups for shared ABAC policy registration.

    Specialized shared commands are translated to their OmopDB equivalents;
    commands without an OmopDB specialization retain their shared type.
    """

    ORGANIZATION_ADMIN_WRITE_COMMANDS: set[type[Command]] = {  # type: ignore[assignment]
        command.COMMON_COMMAND_MAP.get(x, x)
        for x in CommonAbacService.ORGANIZATION_ADMIN_WRITE_COMMANDS
    } | set()

    READ_ORGANIZATION_RESULTS_ONLY_COMMANDS: set[type[Command]] = {  # type: ignore[assignment]
        command.COMMON_COMMAND_MAP.get(x, x)
        for x in CommonAbacService.READ_ORGANIZATION_RESULTS_ONLY_COMMANDS
    } | set()

    READ_SELF_RESULTS_ONLY_COMMANDS: set[type[Command]] = {  # type: ignore[assignment]
        command.COMMON_COMMAND_MAP.get(x, x)
        for x in CommonAbacService.READ_SELF_RESULTS_ONLY_COMMANDS
    } | set()

    READ_USER_COMMANDS: set[type[Command]] = {  # type: ignore[assignment]
        command.COMMON_COMMAND_MAP.get(x, x)
        for x in CommonAbacService.READ_USER_COMMANDS
    } | set()

    UPDATE_USER_COMMANDS: set[type[Command]] = {  # type: ignore[assignment]
        command.COMMON_COMMAND_MAP.get(x, x)
        for x in CommonAbacService.UPDATE_USER_COMMANDS
    } | set()
