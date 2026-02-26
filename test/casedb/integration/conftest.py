# These fixtures are used across multiple test modules in the integration test suite, so they are defined in conftest.py
# to avoid duplication and ensure consistent setup of test users, organizations, and reference data for all tests.

# setup_case_type_data depends on setup_test_users_and_organizations to ensure that users and
# organizations are created before policies reference them. The parameter is intentionally
# unused in the body — its presence enforces fixture ordering.

from setup_test_users_and_organizations import (
    setup_test_users_and_organizations,
)  # noqa: F
from setup_case_data import setup_case_type_data  # noqa: F401
from setup_case_col_data import setup_case_col_data  # noqa: F401


# Note: prevents formatters and linters from removing the imports as unused since they are used implicitly as fixtures in the test modules. The actual test modules should import the specific fixtures they use directly from this conftest.py for clarity,
# but this dummy variable ensures that the imports are retained here.
dummy = (
    setup_test_users_and_organizations,
    setup_case_type_data,
    setup_case_col_data,
)  # noqa: F841


print("\n--- Importing conftest.py ---")
