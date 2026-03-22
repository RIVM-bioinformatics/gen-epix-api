import copy
import logging
from test.commondb.integration.build_db.base import (  # REPOSITORY_TYPE,
    TEST_TYPE,
    VERBOSE,
)

# Import test classes in order of dependency of execution
from test.commondb.integration.build_db.create import TestCreate as ModuleTestCreate
from test.commondb.integration.build_db.delete import TestDelete as ModuleTestDelete
from test.commondb.integration.build_db.read import TestRead as ModuleTestRead
from test.commondb.integration.build_db.update import TestUpdate as ModuleTestUpdate
from test.commondb.test_client.util import get_test_client as commondb_get_test_client
from test.test_client.pytest_params import BuildDbParams

import pytest

from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.commondb.test.test_client import TestClient as Env

APP_CFGS = get_app_cfgs(
    AppType.COMMONDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
)


# Three parameter combinations drive the full Create→Read→Update→Delete chain
# independently. Each results in a separate isolated database environment (Env):
#   1. skip_endpoints__SA_SQLITE_EMPTY  — SQLAlchemy/SQLite, bypassing HTTP endpoints
#   2. skip_endpoints__DICT_EMPTY       — In-memory dict repo, bypassing HTTP endpoints
#   3. with_endpoints__DICT_EMPTY       — In-memory dict repo, exercising HTTP endpoints
_PARAMS = [
    BuildDbParams(
        skip_endpoints=True,
        dev_repository_config=enum.DevRepositoryConfig.SA_SQLITE_EMPTY,
    ),
    BuildDbParams(
        skip_endpoints=True,
        dev_repository_config=enum.DevRepositoryConfig.DICT_EMPTY,
    ),
]


# module-scoped: one Env instance is created per parameter combination and shared
# across all test classes in this file for that combination. The `ids` list makes
# the pytest node IDs human-readable, e.g.:
#   TestCreate[skip_endpoints__SA_SQLITE_EMPTY]::test_create_user_first_root
@pytest.fixture(
    scope="module",
    name="env",
    params=_PARAMS,
    ids=[
        p.id for p in _PARAMS
    ],  # Note id is a calculated property based on the parameter values, e.g. "skip_endpoints__SA_SQLITE_EMPTY"
)
def get_test_client(request) -> Env:
    params: BuildDbParams = request.param
    app_cfg = copy.copy(
        APP_CFGS[f"{TEST_TYPE.value}__{params.dev_repository_config.value}"]
    )
    app_cfg._name = f"{TEST_TYPE.value}__{params.id}"
    return commondb_get_test_client(
        test_type=TEST_TYPE.value,
        app_cfg=app_cfg,
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not params.skip_endpoints,
    )


# @pytest.mark.dependency() with no `depends=` simply registers all methods in this
# class as named dependencies so later classes can refer to them.
@pytest.mark.dependency()
class TestCreate(ModuleTestCreate):
    pass


# @pytest.mark.dependency(depends=["TestCreate::test_create_user_first_root"]) declares
# that every test in TestRead must only run if test_create_user_first_root passed.
#
# Because the `env` fixture is parametrized, pytest generates one node per combination,
# e.g. "TestCreate::test_create_user_first_root[skip_endpoints__SA_SQLITE_EMPTY]".
# A naive static depends string would NOT match those suffixed IDs and the entire
# TestRead class would be skipped for all combinations.
#
# The conftest.py `pytest_collection_modifyitems` hook fixes this at collection time:
# it detects that the class items have a callspec (i.e. are parametrized) and rewrites
# the depends list by appending the current parameter ID, so the resolved dependency
# for the "skip_endpoints__SA_SQLITE_EMPTY" run becomes:
#   "TestCreate::test_create_user_first_root[skip_endpoints__SA_SQLITE_EMPTY]"
#
# Each parameter combination therefore depends only on its own Create run, never on
# a different combination's results.
@pytest.mark.dependency(depends=["TestCreate::test_create_user_first_root"])
class TestRead(ModuleTestRead):
    pass


# Analogous to TestRead above: depends on test_read_user from the *same* combination.
@pytest.mark.dependency(depends=["TestRead::test_read_user"])
class TestUpdate(ModuleTestUpdate):
    pass


# Analogous to the above: depends on test_update_user from the *same* combination.
@pytest.mark.dependency(depends=["TestUpdate::test_update_user"])
class TestDelete(ModuleTestDelete):
    pass
