from gen_epix.fastapp.repositories.dict.unit_of_work import DictUnitOfWork


def test_commit_returns_none() -> None:
    assert DictUnitOfWork().commit() is None


def test_rollback_returns_none() -> None:
    assert DictUnitOfWork().rollback() is None
