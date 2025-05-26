from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class DictUnitOfWork(BaseUnitOfWork):
    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass
