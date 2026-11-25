"""Verify common sequence CRUD error-message construction."""

from gen_epix.commondb.domain.command import CrudCommand
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.services.seq.crud_common import _get_not_implemented_message


def test_not_implemented_message_accepts_userless_command() -> None:
    """Build an unsupported-operation message without requiring a user."""
    cmd = CrudCommand.model_construct(user=None, operation=CrudOperation.UPSERT_ONE)

    assert _get_not_implemented_message(cmd) == (
        "Command CrudCommand operation UPSERT_ONE not implemented"
    )
