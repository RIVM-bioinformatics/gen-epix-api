"""Verify seqdb user-read policy role configuration."""

from types import SimpleNamespace

from gen_epix.seqdb.domain.policy import RoleGenerator
from gen_epix.seqdb.policies.read_user_policy import ReadUserPolicy


def test_read_user_policy_uses_seqdb_role_map() -> None:
    """Construct the policy with the role map generated for seqdb."""
    app_impl = SimpleNamespace(
        get_mapped_class=lambda command_class: command_class,
        role_map={},
        role_set_map={},
    )
    abac_service = SimpleNamespace(app=SimpleNamespace(impl=app_impl))
    policy = ReadUserPolicy(abac_service)

    assert policy.props["role_map"] == RoleGenerator.get_role_map()
