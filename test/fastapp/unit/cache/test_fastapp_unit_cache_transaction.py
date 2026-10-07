"""Tests for transactional cache invalidation."""

import pytest

from gen_epix.fastapp.cache.invalidation import Invalidation
from gen_epix.fastapp.cache.transaction import invalidation_transaction


def test_identical_requests_collapse_inside_a_transaction() -> None:
    """Repeated broad invalidations are dispatched only once."""
    applied: list[Invalidation] = []

    with invalidation_transaction(applied.append) as transaction:
        for _ in range(5):
            transaction.add(Invalidation.for_tags(["case"]))

    assert len(applied) == 1


def test_namespace_bumps_with_different_generations_are_both_kept() -> None:
    """Collapsing generations would make receivers fall behind the origin."""
    applied: list[Invalidation] = []

    with invalidation_transaction(applied.append) as transaction:
        transaction.add(Invalidation.for_namespace("cases", generation=5))
        transaction.add(Invalidation.for_namespace("cases", generation=6))

    assert [invalidation.generation for invalidation in applied] == [5, 6]


def test_a_closed_transaction_refuses_further_requests() -> None:
    """A late request must not be silently dropped."""
    with invalidation_transaction(lambda invalidation: None) as transaction:
        pass

    with pytest.raises(RuntimeError):
        transaction.add(Invalidation.for_all())
