from test.casedb.integration.define_edge_cases import (
    EDGE_CASES,
)


from test.casedb.casedb_test_client import CasedbTestClient as Env
import pytest


from gen_epix.casedb.domain import model

VERBOSE = True  # Set to True to enable detailed print statements during setup for debugging purposes;


@pytest.fixture(scope="module")
def setup_test_users_and_organizations(env: Env) -> None:
    """
    Set up common test users and organizations driven by EDGE_CASES.

    Creates:
    - root user (bootstrapped into env.db)
    - org1 (bootstrapped into env.db, pre-configured as the root organization)
    - any additional orgs referenced in EDGE_CASES (e.g. org2), in order of first appearance
    - one user per EdgeCaseSpec; role and org membership are derived from
      the user_name naming convention by invite_and_register_user
    """

    if VERBOSE:
        print("\n--- Setting up test users and organizations for edge case tests ---")

    root_user = env.get_root_user()
    env._set_obj(root_user)  # noqa: SLF001

    org1 = env.read_one_by_property(root_user, model.Organization, "name", "org1")
    env._set_obj(org1)  # noqa: SLF001

    # Create orgs not already bootstrapped (org1 is pre-configured as the root org)
    created_orgs: set[str] = {"org1"}
    for spec in EDGE_CASES:
        if spec.org_name not in created_orgs:
            env.create_organization(root_user, spec.org_name)
            created_orgs.add(spec.org_name)

    # Create users; role and org membership are derived from user_name by invite_and_register_user
    for spec in EDGE_CASES:
        env.invite_and_register_user(root_user, spec.user_name)
