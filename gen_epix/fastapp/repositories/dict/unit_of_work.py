"""Dictionary repository unit-of-work implementation."""

from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class DictUnitOfWork(BaseUnitOfWork):
    """Encapsulates a unit of work for the in-memory dictionary repository."""

    def commit(self) -> None:
        """Keep changes already applied to the dictionary repository."""
        pass

    def rollback(self) -> None:
        """Leave immediately applied dictionary changes unchanged."""
        pass
