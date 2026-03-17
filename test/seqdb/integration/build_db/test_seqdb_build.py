import copy
import logging
from test.seqdb.integration.build_db.base import TEST_TYPE, VERBOSE  # REPOSITORY_TYPE,

# Import test classes in order of dependency of execution
from test.seqdb.integration.build_db.create import TestCreate as ModuleTestCreate
from test.seqdb.integration.build_db.delete import TestDelete as ModuleTestDelete
from test.seqdb.integration.build_db.read import TestRead as ModuleTestRead
from test.seqdb.integration.build_db.update import TestUpdate as ModuleTestUpdate
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from test.test_client.pytest_params import BuildDbParams

import pytest

from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.seqdb.domain import enum as seqdb_enum

APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
)


# Three parameter combinations drive the full Create→Read→Update→Delete chain
# independently. Each results in a separate isolated database environment (Env):
#   1. skip_endpoints__SA_SQLITE_EMPTY  — SQLAlchemy/SQLite, bypassing HTTP endpoints
#   2. skip_endpoints__DICT_EMPTY       — In-memory dict repo, bypassing HTTP endpoints
#   3. with_endpoints__DICT_EMPTY       — In-memory dict repo, exercising HTTP endpoints
#
# Note: with_endpoints + SA_SQLITE is intentionally excluded. SA_SQLITE runs in the
# same process via a module-scoped fixture; adding HTTP endpoints introduces threads
# that share the same SQLite connection, causing multi-threading errors.
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
    ids=[p.id for p in _PARAMS],
)
def get_test_client(request) -> Env:
    params: BuildDbParams = request.param
    app_cfg = copy.copy(
        APP_CFGS[f"{TEST_TYPE.value}__{params.dev_repository_config.value}"]
    )
    app_cfg._name = f"{TEST_TYPE.value}__{params.id}"
    return Env.get_test_client(  # type: ignore[return-value]
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


# The conftest.py `pytest_collection_modifyitems` hook rewrites this static depends
# string at collection time to include the current parameter ID, so each combination
# depends only on its own Create run. See conftest.py for full explanation.
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
