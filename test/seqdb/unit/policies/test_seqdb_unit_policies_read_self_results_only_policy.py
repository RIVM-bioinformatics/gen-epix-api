"""Test the seqdb self-read policy wrapper."""

from types import SimpleNamespace

from gen_epix.commondb.domain import command
from gen_epix.commondb.policies import (
    ReadSelfResultsOnlyPolicy as CommonReadSelfResultsOnlyPolicy,
)
from gen_epix.seqdb.policies.read_self_results_only_policy import (
    ReadSelfResultsOnlyPolicy,
)


def test_is_subclass_of_common_policy() -> None:
    """Inherit the common self-read policy contract."""
    assert issubclass(ReadSelfResultsOnlyPolicy, CommonReadSelfResultsOnlyPolicy)


def test_init_preserves_common_owner_mappings_and_configuration() -> None:
    """Retain common ownership mappings and forward policy configuration."""
    abac_service = SimpleNamespace(
        app=SimpleNamespace(impl=SimpleNamespace(role_map={}, role_set_map={}))
    )

    policy = ReadSelfResultsOnlyPolicy(abac_service, foo="bar")

    assert policy.abac_service is abac_service
    assert policy.props == {"foo": "bar"}
    assert policy.id_attr_by_command_class == {
        command.UserCrudCommand: "id",
        command.UserInvitationCrudCommand: "invited_by_user_id",
    }


def test_init_does_not_share_owner_mappings_between_instances() -> None:
    """Give each policy instance an independent ownership mapping."""
    abac_service = SimpleNamespace(
        app=SimpleNamespace(impl=SimpleNamespace(role_map={}, role_set_map={}))
    )
    first = ReadSelfResultsOnlyPolicy(abac_service)
    second = ReadSelfResultsOnlyPolicy(abac_service)

    first.id_attr_by_command_class.clear()

    assert second.id_attr_by_command_class == {
        command.UserCrudCommand: "id",
        command.UserInvitationCrudCommand: "invited_by_user_id",
    }
