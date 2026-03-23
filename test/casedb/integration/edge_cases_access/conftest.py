# These fixtures are used across multiple test modules in the integration test suite, so they are defined in conftest.py
# to avoid duplication and ensure consistent setup of test users, organizations, and reference data for all tests.

from test.casedb.integration.edge_cases_access.setup.setup_case_data import (  # noqa: F401
    setup_case_data,
)
from test.casedb.integration.edge_cases_access.setup.setup_case_type_data import (  # noqa: F401
    setup_case_type_data,
)
from test.casedb.integration.edge_cases_access.setup.setup_test_users_and_organizations import (  # noqa: F401
    setup_test_users_and_organizations,
)
from test.casedb.integration.edge_cases_access.setup.setup_test_users_and_organizations_op import (  # noqa: F401
    setup_test_users_and_organizations_op,
)

# Note: prevents formatters and linters from removing the imports as unused since they are used implicitly as fixtures in the test modules. The actual test modules should import the specific fixtures they use directly from this conftest.py for clarity,
# but this dummy variable ensures that the imports are retained here.
dummy = (
    setup_test_users_and_organizations,
    setup_test_users_and_organizations_op,
    setup_case_type_data,
    setup_case_data,
)  # noqa: F841


print("\n--- Importing conftest.py ---")
