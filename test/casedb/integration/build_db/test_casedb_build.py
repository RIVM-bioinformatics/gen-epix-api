import copy
import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.build_db.base import TEST_TYPE, VERBOSE  # REPOSITORY_TYPE,

# Import test classes in order of dependency of execution
from test.casedb.integration.build_db.create import TestCreate as ModuleTestCreate
from test.casedb.integration.build_db.delete import TestDelete as ModuleTestDelete
from test.casedb.integration.build_db.read import TestRead as ModuleTestRead
from test.casedb.integration.build_db.update import TestUpdate as ModuleTestUpdate
from test.test_client.pytest_params import BuildDbParams

import pytest

from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain import enum as commondb_enum
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.seqdb.domain import enum as seqdb_enum

# SEQDB_APP_CFGS must be built first; CASEDB_APP_CFGS references it so that
# the casedb app can locate the embedded seqdb local app configuration.
SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
    log_any=VERBOSE,
)
CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
    log_any=VERBOSE,
)


# Two parameter combinations drive the full Create→Read→Update→Delete chain
# independently. Each results in a separate isolated database environment (Env):
#   1. skip_endpoints__SA_SQLITE_EMPTY  — SQLAlchemy/SQLite, bypassing HTTP endpoints
#   2. skip_endpoints__DICT_EMPTY       — In-memory dict repo, bypassing HTTP endpoints
#   3. with_endpoints__DICT_EMPTY       — In-memory dict repo, exercising HTTP endpoints
#
# Note: SA_SQLITE_EMPTY is excluded because casedb requires a running seqdb (embedded
# via LOCAL mode). SA_SQLITE + endpoints introduces a multi-threading issue on that
# shared SQLite connection.
#
# Note: with_endpoints + DICT_EMPTY would share the same underlying cfg dict as
# skip_endpoints + DICT_EMPTY (copy.copy is shallow). CommondbRemoteApp._create_local_app
# calls local_app_props.pop("app_cfg"), which removes seqdb's AppCfg from the shared
# dict. The second fixture call would then fall back to constructing a new seqdb AppCfg
# from the current env vars, which may point to SA_SQL → MSSQL connection error.
# This is fixed by restoring seqdb_local_app["app_cfg"] from SEQDB_APP_CFGS before
# each fixture call (see fixture body below).
_PARAMS = [
    BuildDbParams(
        skip_endpoints=True,
        dev_repository_config=commondb_enum.DevRepositoryConfig.SA_SQLITE_EMPTY,
    ),
    BuildDbParams(
        skip_endpoints=True,
        dev_repository_config=commondb_enum.DevRepositoryConfig.DICT_EMPTY,
    ),
]


# module-scoped: one Env instance is created per parameter combination and shared
# across all test classes in this file for that combination. The `ids` list makes
# the pytest node IDs human-readable, e.g.:
#   TestCreate[skip_endpoints__DICT_EMPTY]::test_create_user_first_root
@pytest.fixture(
    scope="module",
    name="env",
    params=_PARAMS,
    ids=[p.id for p in _PARAMS],
)
def get_test_client(request) -> Env:
    params: BuildDbParams = request.param
    cfg_key = f"{TEST_TYPE.value}__{params.dev_repository_config.value}"
    app_cfg = copy.copy(CASEDB_APP_CFGS[cfg_key])
    app_cfg._name = f"{TEST_TYPE.value}__{params.id}"
    # CommondbRemoteApp._create_local_app pops "app_cfg" from the seqdb_local_app dict.
    # Because copy.copy is shallow, that pop mutates the shared underlying cfg dict and
    # removes the key for any subsequent fixture call using the same dev_repository_config.
    # Without this restore, the next call would create a new seqdb AppCfg from env vars,
    # which may point to SA_SQL (MSSQL) → DBAPIError on machines without ODBC installed.
    app_cfg.cfg["service"]["seqdb"]["props"]["seqdb_local_app"]["app_cfg"] = (
        SEQDB_APP_CFGS[cfg_key]
    )
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
