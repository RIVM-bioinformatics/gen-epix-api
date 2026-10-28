from test.seqdb.integration.upload_samples.ref_data import (
    SeqUploadRefData,
    create_ref_data,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env

import pytest


@pytest.fixture(scope="module", name="ref_data")
def upload_ref_data(env: Env) -> SeqUploadRefData:
    return create_ref_data(env)
