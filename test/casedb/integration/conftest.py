import pytest

from test.casedb.casedb_test_client import CasedbTestClient as Env
from gen_epix.casedb.domain import model


@pytest.fixture(scope="module")
def setup_test_users_and_organizations(env: Env) -> None:
    """
    Set up common test users and organizations used across integration test modules.

    Creates:
    - root user (bootstrapped into env.db)
    - org1 (bootstrapped into env.db, pre-configured as the root organization)
    - org2 (created fresh)
    - org_user1_1: user in org1 with no user policy (org policy access only)
    - org_user1_2: user in org1 with both org and user policy on different case type sets
    - org_user1_3: user in org1 with both org and user policy on the same case type set
    - org_user2_1: user in org2 with no policies at all
    - org_user2_2: user in org2 with a user policy but no org policy
    """
    root_user = env.get_root_user()
    env._set_obj(root_user)

    org1 = env.read_one_by_property(root_user, model.Organization, "name", "org1")
    env._set_obj(org1)

    env.create_organization(root_user, "org2")

    # User with org policy but no user policy (should have access to case types shared with org)
    env.invite_and_register_user(root_user, "org_user1_1")

    # User with both org and user policies (should only have access to org-shared case types)
    env.invite_and_register_user(root_user, "org_user1_2")

    # User with both org and user policies on the same case type set (should have access to org-shared case types)
    env.invite_and_register_user(root_user, "org_user1_3")

    # User with no policies (should have no access to case types)
    env.invite_and_register_user(root_user, "org_user2_1")

    # User with user policy but no org policy (should have no access to case types, since case types are shared at org level)
    env.invite_and_register_user(root_user, "org_user2_2")
