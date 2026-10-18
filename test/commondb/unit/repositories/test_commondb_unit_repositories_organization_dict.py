from uuid import uuid4

import pytest

from gen_epix.commondb.domain import model
from gen_epix.commondb.repositories.organization_dict import OrganizationDictRepository
from gen_epix.fastapp import exc


@pytest.fixture
def repository() -> OrganizationDictRepository:
    user = model.User(
        key="alice@example.org",
        roles={"user"},
        organization_id=uuid4(),
    )
    return OrganizationDictRepository(
        entities=[],
        db={model.User: {"alice": user}},
    )


@pytest.mark.parametrize(
    ("user_key", "expected"),
    [
        pytest.param("ALICE@EXAMPLE.ORG", True, id="case-insensitive-match"),
        pytest.param("missing@example.org", False, id="missing-key"),
        pytest.param(None, False, id="no-key"),
    ],
)
def test_is_existing_user_by_key(
    repository: OrganizationDictRepository,
    user_key: str | None,
    expected: bool,
) -> None:
    assert repository.is_existing_user_by_key(repository.uow(), user_key) is expected


def test_retrieve_user_by_key_is_case_insensitive(
    repository: OrganizationDictRepository,
) -> None:
    user = repository.db[model.User]["alice"]

    assert (
        repository.retrieve_user_by_key(repository.uow(), "ALICE@EXAMPLE.ORG") is user
    )


def test_retrieve_user_by_key_raises_when_key_is_missing(
    repository: OrganizationDictRepository,
) -> None:
    with pytest.raises(exc.NoResultsError):
        repository.retrieve_user_by_key(repository.uow(), "missing@example.org")
