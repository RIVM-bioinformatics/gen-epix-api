"""Unit tests for the casedb exception re-export module."""

import pytest

from gen_epix.casedb.domain import exc as casedb_exc
from gen_epix.fastapp import exc as fastapp_exc
from gen_epix.fastapp.api import exc as api_exc

FASTAPP_EXCEPTION_NAMES = [
    "DomainException",
    "DataException",
    "InvalidArgumentsError",
    "IdsError",
    "InvalidIdsError",
    "DuplicateIdsError",
    "InvalidModelIdsError",
    "AlreadyExistingIdsError",
    "InvalidLinkIdsError",
    "LinkConstraintViolationError",
    "UniqueConstraintViolationError",
    "NotNullConstraintViolationError",
    "NoResultsError",
    "ServiceException",
    "InitializationServiceError",
    "RepositoryInitializationServiceError",
    "RepositoryServiceError",
    "AuthException",
    "FeatureDisabledServiceError",
    "CredentialsAuthError",
    "UnauthorizedAuthError",
    "UserNotFoundAuthError",
    "UserAlreadyExistsAuthError",
    "ConcurrentModificationError",
    "ServiceUnavailableError",
    "RequestLimitExceededAuthError",
]

API_EXCEPTION_NAMES = [
    "BadRequest400HTTPException",
    "UnauthorizedUser401HTTPException",
    "Forbidden403HTTPException",
    "ResourceNotFound404HTTPException",
    "MethodNotAllowed405HTTPException",
    "ResourceConflict409HTTPException",
    "ForeignKeyConstraint409HTTPException",
    "UnprocessableEntity422HTTPException",
    "InternalServerError500HTTPException",
    "NotImplemented501HTTPException",
    "ServiceUnavailableError503HTTPException",
]


def _public_names(module: object) -> set[str]:
    return {name for name in vars(module) if not name.startswith("_")}


@pytest.mark.parametrize("name", FASTAPP_EXCEPTION_NAMES)
def test_fastapp_exceptions_are_reexported(name: str) -> None:
    """FastApp domain exceptions are the same objects in the casedb module."""
    assert getattr(casedb_exc, name) is getattr(fastapp_exc, name)


@pytest.mark.parametrize("name", API_EXCEPTION_NAMES)
def test_api_exceptions_are_reexported(name: str) -> None:
    """FastApp HTTP exceptions are the same objects in the casedb module."""
    assert getattr(casedb_exc, name) is getattr(api_exc, name)


def test_all_public_names_of_both_sources_are_reexported() -> None:
    """Every public source name, including future additions, is re-exported."""
    expected = _public_names(fastapp_exc) | _public_names(api_exc)
    assert expected <= _public_names(casedb_exc)


def test_source_modules_do_not_define_conflicting_names() -> None:
    """Import order cannot change a re-exported name's identity."""
    for name in _public_names(fastapp_exc) & _public_names(api_exc):
        assert getattr(fastapp_exc, name) is getattr(api_exc, name)


def test_private_names_are_not_reexported() -> None:
    """Underscore-prefixed source names are not leaked by the wildcard imports."""
    private = {
        name
        for name in vars(fastapp_exc).keys() | vars(api_exc).keys()
        if name.startswith("_") and not name.startswith("__")
    }
    assert all(not hasattr(casedb_exc, name) for name in private)


def test_reexported_exceptions_are_raisable() -> None:
    """A re-exported subclass is catchable via the re-exported base class."""
    with pytest.raises(casedb_exc.DomainException):
        raise casedb_exc.NoResultsError("c1a2b3d4", "msg")
