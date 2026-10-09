import pytest

from gen_epix.commondb.domain.command import rbac
from gen_epix.commondb.domain.command.base import Command


@pytest.mark.parametrize(
    "command_class",
    [rbac.RetrieveOwnPermissionsCommand, rbac.RetrieveSubRolesCommand],
    ids=["retrieve-own-permissions", "retrieve-sub-roles"],
)
def test_rbac_command_uses_shared_command_base(
    command_class: type[Command],
) -> None:
    command = command_class()

    assert isinstance(command, Command)
    assert command.user is None
