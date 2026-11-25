"""Verify base unit-of-work context behavior."""

import pytest

from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class TrackingUnitOfWork(BaseUnitOfWork):
    """Record transaction completion for context-manager tests."""

    def __init__(self) -> None:
        super().__init__()
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def test_keyboard_interrupt_rolls_back_and_propagates() -> None:
    """Roll back and re-raise BaseException subclasses from a managed block."""
    unit_of_work = TrackingUnitOfWork()

    with pytest.raises(KeyboardInterrupt):
        with unit_of_work:
            raise KeyboardInterrupt

    assert unit_of_work.rolled_back is True
    assert unit_of_work.committed is False
