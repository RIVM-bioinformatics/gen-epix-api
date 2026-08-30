"""Dictionary repository unit-of-work implementation."""

from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class DictUnitOfWork(BaseUnitOfWork):
    """Unit of work for the in-memory dictionary repository."""

    def commit(self) -> None:
        """Commit the requested value."""
        pass

    def rollback(self) -> None:
        """Rollback the requested value."""
        pass
