import pytest

from test.casedb.casedb_test_client import CasedbTestClient as Env
from gen_epix.casedb.domain import model

# These fixtures are used across multiple test modules in the integration test suite, so they are defined in conftest.py
# to avoid duplication and ensure consistent setup of test users, organizations, and reference data for all tests.


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


# The test_data fixture needs to declare a dependency on setup_test_users_and_organizations
# to ensure it runs after the user is properly set up.
# => properly setting up the root user and organization before the case test data creation begins.
@pytest.fixture(scope="module")
def setup_case_type_data(env: Env, setup_test_users_and_organizations: None) -> None:
    """
    Create reference data (diseases, etiological agents, case types and share policies) for tests.
    Objects are automatically stored in env.db by create methods.
    """
    root_user = env.get_root_user()

    env.create_disease(root_user, "disease_1")
    env.create_disease(root_user, "disease_2")

    env.create_etiological_agent(root_user, "etiological_agent_1")
    env.create_etiological_agent(root_user, "etiological_agent_2")

    # Create case type using pre-created reference data from env.db
    # This case type should only be accessible to users with proper ABAC policies
    case_type_1 = env.create_case_type(
        root_user, "case_type_1", "disease_1", "etiological_agent_1"
    )
    assert case_type_1 is not None

    # case type 2 is created to test that users with access to case type 1 do not automatically
    # get access to case type 2 (i.e. no over-permissioning)
    # It will also be used for user policy access tests
    # (user policy should be commpletely ignored for reference data access,
    # but we want to verify that in the tests)
    case_type_2 = env.create_case_type(
        root_user, "case_type_2", "disease_1", "etiological_agent_1"
    )

    # Create case type set category
    env.create_case_type_set_category(root_user, "category_1", 0)

    # Create case type sets
    env.create_case_type_set(
        root_user, "case_type_set1", [case_type_1.id], "category_1"
    )
    env.create_case_type_set(
        root_user, "case_type_set2", [case_type_2.id], "category_1"
    )
    # Create data collection
    env.create_data_collection(root_user, "data_collection1")

    # Create organization access policy for the case type 1 through case type set 1 for org1
    # This policy should grant access to org users for the case type
    env.create_organization_access_case_policy(
        root_user, "org_case_policy1_1", "case_type_set1"
    )

    # org2 should not have any org policies to test that users in org2 do not have access to case types since there are no org policies granting access to their org

    # for org_user1_2 we will create both org and user policies to test that user policy does not grant additional access beyond org policy for reference data access
    # there is already an org policy that grants access to case_type_1, so we will create a user policy that grants access to case_type_2
    # and verify that it does not grant access to case_type_2 since case types are shared at org level for reference data access
    env.create_user_access_case_policy(
        root_user, "org_user1_2", "data_collection1", "case_type_set2"
    )

    # for org_user1_3 we will create both org and user policies that grant access to the same case type set
    # to verify that it does not cause any issues and user still has access to the case type via the org policy
    env.create_user_access_case_policy(
        root_user, "org_user1_3", "data_collection1", "case_type_set1"
    )

    # for org_user2_2 we will create a user policy that grants access to case_type_1 but no org policy to verify that user policies do not grant access to case types for reference data access since case types are shared at org level
    env.create_user_access_case_policy(
        root_user, "org_user2_2", "data_collection1", "case_type_set1"
    )
