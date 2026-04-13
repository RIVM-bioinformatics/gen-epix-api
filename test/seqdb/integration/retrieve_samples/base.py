from test.test_client.enum import EnumTestType

TEST_TYPE = EnumTestType.SEQDB_INTEGRATION_RETRIEVE_FULL_SAMPLES

SKIP_ENDPOINTS = (
    True  # SA_SQLITE uses attached SQLite schemas; endpoint threads break that setup
)
SKIP_RAISE = True
SKIP_CREATE_DATA = True
VERBOSE = True
