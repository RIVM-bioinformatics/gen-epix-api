import logging
from test.commondb.test_client.util import get_test_client as commondb_get_test_client
from test.test_client.enum import TestType

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.commondb.repositories.sa_model.organization import User
from gen_epix.commondb.test.test_client import TestClient as Env
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork

TEST_TYPE = TestType.COMMONDB_INTEGRATION_SQL_INJECTION
SKIP_ENDPOINTS = False
SKIP_RAISE = False
SKIP_CREATE_DATA = False
VERBOSE = False
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.SA_SQLITE_DEMO


APP_CFGS = get_app_cfgs(
    AppType.COMMONDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return commondb_get_test_client(
        test_type=TEST_TYPE.value,
        app_cfg=APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


class TestSQLInjection:

    @pytest.fixture(scope="module")
    def session(self, env: Env) -> Session:
        return env.app.impl.repositories[  # type: ignore[no-any-return]
            enum.ServiceType.ORGANIZATION
        ].get_session()

    def test_sql_injection_orm_where_clause(self, session: Session) -> None:
        # Arrange
        malicious_input = "'; DROP TABLE users; --"

        # Act - ORM parameterizes the value; the string is passed as a bind parameter,
        # not interpolated into the SQL string
        result = session.execute(select(User).where(User.key == malicious_input)).all()

        # Assert - no results returned, and no SQL error raised; the injection string
        # was treated as a literal value
        assert result == []

    def test_sql_injection_tautology_bypass(self, session: Session) -> None:
        # Arrange - tautology attempts to make the WHERE clause always evaluate to true
        tautology_input = "' OR '1'='1"

        # Act - ORM parameterizes the value, preventing the tautology from being
        # interpreted as SQL logic
        result = session.execute(select(User).where(User.key == tautology_input)).all()

        # Assert - no results returned; all rows were not leaked by the bypass attempt
        assert result == []

    def test_sql_injection_is_existing_user_by_key(
        self, env: Env, session: Session
    ) -> None:
        # Arrange
        malicious_input = "'; DROP TABLE users; --"
        repository = env.app.impl.repositories[enum.ServiceType.ORGANIZATION]
        uow = SAUnitOfWork(session)

        # Act - the repository method wraps an ORM select().where() call with the
        # user_key bound as a parameter
        result = repository.is_existing_user_by_key(uow, malicious_input)

        # Assert - returns False (no matching user), no exception raised
        assert result is False
