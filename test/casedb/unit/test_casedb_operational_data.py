"""Test CaseDB operational-data deletion against both repository backends."""

from test.util.operational_data import BaseOperationalDataTests


class TestCaseOperationalData(BaseOperationalDataTests):
    """Encapsulates the CaseDB reset contract and retained-data boundary."""

    APP_NAME = "casedb"
    SERVICE_NAME = "case"
    EXPECTED_MODELS = {
        "Case",
        "CaseIdentifier",
        "CaseSet",
        "CaseSetMember",
        "CaseDataCollectionLink",
        "CaseSetDataCollectionLink",
    }
