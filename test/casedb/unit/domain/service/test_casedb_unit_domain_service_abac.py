from gen_epix.casedb.domain import command, enum
from gen_epix.casedb.domain.service.abac import BaseAbacService


def test_retrieve_seq_distances_is_exempted_for_app_admin() -> None:
    assert (
        BaseAbacService.ABAC_EXEMPTED_ROLE_SET_MAP[
            command.RetrieveSeqDistancesByCasesCommand
        ]
        is enum.RoleSet.GE_APP_ADMIN
    )
