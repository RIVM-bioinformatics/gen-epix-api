from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.edge_cases_access.setup.define_edge_cases_operational import (
    EDGE_CASES_OP,
)

import pytest

from gen_epix.casedb.domain import model

VERBOSE = False


@pytest.fixture(scope="module")
def setup_test_users_and_organizations_operational(env: Env) -> None:
    """
    Set up test users and organizations for operational data edge case tests.
    Driven by EDGE_CASES_OP — analogous to setup_test_users_and_organizations
    for the reference data tests.
    """
    if VERBOSE:
        print(
            "\n--- Setting up users and organizations for operational edge case tests ---"
        )

    root_user = env.get_root_user()
    env._set_obj(root_user)  # noqa: SLF001

    org1 = env.read_one_by_property(root_user, model.Organization, "name", "org1")
    env._set_obj(org1)  # noqa: SLF001

    created_orgs: set[str] = {"org1"}
    for spec in EDGE_CASES_OP:
        if spec.org_name not in created_orgs:
            env.create_organization(root_user, spec.org_name)
            created_orgs.add(spec.org_name)

    for spec in EDGE_CASES_OP:
        env.invite_and_register_user(root_user, spec.user_name)
