"""Test SeqDB operational-data deletion and retained shared sequence assets."""

from test.util.operational_data import BaseOperationalDataTests


class TestSeqOperationalData(BaseOperationalDataTests):
    """Encapsulates the SeqDB reset contract and retained-data boundary."""

    APP_NAME = "seqdb"
    SERVICE_NAME = "seq"
    EXPECTED_MODELS = {
        "Sample",
        "SampleDataCollectionLink",
        "SampleIdentifier",
        "ReadSet",
        "ReadSetIdentifier",
        "Seq",
        "SeqIdentifier",
        "SeqProfile",
        "SeqProfileIdentifier",
        "SeqDistance",
        "SeqClassification",
        "SeqTaxonomy",
        "PcrMeasurement",
        "AstMeasurement",
        "AstPrediction",
    }
