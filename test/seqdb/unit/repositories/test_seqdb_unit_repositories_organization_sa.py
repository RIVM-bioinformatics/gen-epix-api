"""Test seqdb-specific model bindings in the SQL organization repository."""

from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine

from gen_epix.seqdb.domain import model
from gen_epix.seqdb.repositories import sa_model
from gen_epix.seqdb.repositories.organization_sa import OrganizationSARepository


@pytest.fixture(name="sqlite_engine")
def engine_fixture() -> Iterator[Engine]:
    """Provide an in-memory engine for repository construction."""
    engine = create_engine("sqlite://")
    yield engine
    engine.dispose()


def test_initializes_seqdb_model_types(sqlite_engine: Engine) -> None:
    """Bind seqdb domain and SQL models to the shared organization repository."""
    repository = OrganizationSARepository(sqlite_engine, register_mappers=False)

    assert repository.user_class is model.User
    assert repository.user_invitation_class is model.UserInvitation
    assert repository.sa_user_class is sa_model.User
    assert repository.sa_user_invitation_class is sa_model.UserInvitation
