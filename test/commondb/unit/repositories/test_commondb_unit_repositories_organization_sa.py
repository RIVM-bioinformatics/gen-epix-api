"""Test the SQLAlchemy commondb organization repository."""

from collections.abc import Iterator
from test.util.mock_compat import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine

from gen_epix.commondb.domain import model
from gen_epix.commondb.repositories.organization_sa import OrganizationSARepository
from gen_epix.fastapp import exc
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork


@pytest.fixture(name="repository")
def organization_repository() -> Iterator[OrganizationSARepository]:
    engine = create_engine("sqlite://")
    try:
        yield OrganizationSARepository(engine)
    finally:
        engine.dispose()


@pytest.fixture(name="uow")
def unit_of_work() -> SAUnitOfWork:
    return SAUnitOfWork(session=MagicMock())


def test_is_existing_user_by_key_returns_false_without_a_key(
    repository: OrganizationSARepository,
    uow: SAUnitOfWork,
) -> None:
    """Return false without querying when no user key is provided."""
    assert repository.is_existing_user_by_key(uow, None) is False
    uow.session.execute.assert_not_called()


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        pytest.param([], False, id="missing-user"),
        pytest.param([("user-id",)], True, id="existing-user"),
    ],
)
def test_is_existing_user_by_key_normalizes_the_key(
    repository: OrganizationSARepository,
    uow: SAUnitOfWork,
    rows: list[tuple[str]],
    expected: bool,
) -> None:
    """Normalize keys and report whether SQL returned a matching user."""
    uow.session.execute.return_value.all.return_value = rows

    assert repository.is_existing_user_by_key(uow, "ALICE@EXAMPLE.ORG") is expected

    statement = uow.session.execute.call_args.args[0]
    assert list(statement.compile().params.values()) == ["alice@example.org"]


def test_retrieve_user_by_key_matches_case_insensitively(
    repository: OrganizationSARepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return the stored user when the requested key differs only by case."""
    user = model.User(
        key="alice@example.org",
        roles={"user"},
        organization_id=uuid4(),
    )
    monkeypatch.setattr(repository, "crud", lambda *_args: [user])

    assert repository.retrieve_user_by_key(None, "ALICE@EXAMPLE.ORG") is user


def test_retrieve_user_by_key_raises_when_key_is_missing(
    repository: OrganizationSARepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise the repository's not-found error when no user matches."""
    monkeypatch.setattr(repository, "crud", lambda *_args: [])

    with pytest.raises(exc.NoResultsError):
        repository.retrieve_user_by_key(None, "missing@example.org")
