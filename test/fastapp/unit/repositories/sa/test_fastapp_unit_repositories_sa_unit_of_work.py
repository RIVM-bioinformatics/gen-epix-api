"""Regression tests for SQL unit-of-work exception propagation."""

from test.util.mock_compat import Mock

import pytest
from sqlalchemy.exc import IntegrityError

from gen_epix.fastapp import exc
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork


@pytest.mark.parametrize("error_class", [KeyError, ValueError, RuntimeError])
@pytest.mark.parametrize("during_commit", [False, True], ids=["body", "commit"])
def test_unexpected_exception_is_preserved_after_rollback(error_class, during_commit):
    session = Mock()
    original = error_class("original failure")
    if during_commit:
        session.commit.side_effect = original

    with pytest.raises(error_class) as caught:
        with SAUnitOfWork(session):
            if not during_commit:
                raise original

    assert caught.value is original
    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()


def test_unique_constraint_error_still_becomes_domain_exception():
    session = Mock()
    original = IntegrityError("statement", {}, Exception("UNIQUE constraint failed"))

    with pytest.raises(exc.UniqueConstraintViolationError):
        with SAUnitOfWork(session):
            raise original

    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()
