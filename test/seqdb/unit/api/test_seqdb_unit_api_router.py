from test.util.mock_compat import Mock

from gen_epix.seqdb.api import router as seqdb_router
from gen_epix.seqdb.domain import command


def test_create_routers_wires_delete_commands(monkeypatch) -> None:
    """Wire the seqdb-specific reset commands into its system router."""
    system_kwargs = {}

    def endpoint_factory(*_args, **kwargs):
        if "delete_all_operational_data_command_class" in kwargs:
            system_kwargs.update(kwargs)

    for name in vars(seqdb_router):
        if name.startswith("create_") and name != "create_routers":
            monkeypatch.setattr(seqdb_router, name, endpoint_factory)

    routers = seqdb_router.create_routers(Mock())

    assert len(routers) == 7
    assert (
        system_kwargs["delete_all_operational_data_command_class"]
        is command.DeleteAllOperationalDataCommand
    )
    assert (
        system_kwargs["delete_all_ref_data_command_class"]
        is command.DeleteAllRefDataCommand
    )
