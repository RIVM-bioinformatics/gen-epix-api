import logging
from test.omopdb.integration.person_upload.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.omopdb.omopdb_test_client import omopdbTestClient as Env

import pytest

from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.omopdb.domain import enum

OMOPDB_APP_CFGS = get_app_cfgs(
    AppType.OMOPDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=OMOPDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


class TestPersonUpload:
    # TODO: add setup to create Organizations, Users, Concepts, Domains, ...
    pass
