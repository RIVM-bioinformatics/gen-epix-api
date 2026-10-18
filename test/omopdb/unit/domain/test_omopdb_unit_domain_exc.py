"""Unit tests for OmopDB exception re-exports."""

from gen_epix.fastapp.api.exc import BadRequest400HTTPException
from gen_epix.fastapp.exc import NoResultsError
from gen_epix.omopdb.domain import exc


def test_reexports_http_exception() -> None:
    """Expose the shared HTTP exception class."""
    assert exc.BadRequest400HTTPException is BadRequest400HTTPException


def test_reexports_domain_exception() -> None:
    """Expose the shared domain exception class."""
    assert exc.NoResultsError is NoResultsError
