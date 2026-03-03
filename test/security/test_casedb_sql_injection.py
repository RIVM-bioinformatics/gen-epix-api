import logging

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.commondb.repositories.sa_model.organization import User
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.seqdb.domain import enum as seqdb_enum
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.case_upload.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
)

CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
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
