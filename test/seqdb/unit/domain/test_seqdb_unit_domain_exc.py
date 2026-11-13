"""Test the seqdb domain exception re-exports."""

from gen_epix.fastapp import api as fastapp_api
from gen_epix.fastapp import exc as fastapp_exc
from gen_epix.seqdb.domain import exc


def test_reexports_domain_exception_types() -> None:
    """Expose shared domain exception classes without wrapping them."""
    assert exc.InvalidArgumentsError is fastapp_exc.InvalidArgumentsError
    assert exc.NoResultsError is fastapp_exc.NoResultsError


def test_reexports_http_exception_types() -> None:
    """Expose shared HTTP exception classes without wrapping them."""
    assert exc.BadRequest400HTTPException is fastapp_api.exc.BadRequest400HTTPException
