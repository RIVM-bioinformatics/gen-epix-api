from test.casedb.casedb_test_client import CasedbTestClient as Env

import pytest


VERBOSE = True  # Set to True to enable detailed print statements during setup for debugging purposes;


@pytest.fixture(scope="module")
def setup_case_col_data(
    env: Env, setup_test_users_and_organizations: None  # noqa: ARG001
) -> None:  # noqa: ARG001

    if VERBOSE:
        print("\n--- Setting up case type column set data for edge case tests ---")
