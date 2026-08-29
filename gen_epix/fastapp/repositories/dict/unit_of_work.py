"""Dictionary repository unit-of-work implementation."""

from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class DictUnitOfWork(BaseUnitOfWork):
    """Provide the dict unit of work framework abstraction."""

    def commit(self) -> None:
        """Perform the commit operation."""
        pass

    def rollback(self) -> None:
        """Perform the rollback operation."""
        pass
