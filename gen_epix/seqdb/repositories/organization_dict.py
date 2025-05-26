from gen_epix.fastapp import exc
from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.repository.organization import BaseOrganizationRepository


class OrganizationDictRepository(DictRepository, BaseOrganizationRepository):
    def is_existing_user_by_key(
        self, uow: BaseUnitOfWork, user_key: str | None
    ) -> bool:
        if user_key is None:
            return False
        for user in self._db[model.User].values():
            assert isinstance(user, model.User)
            if user.email == user_key:
                return True
        return False

    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        for user in self._db[model.User].values():
            assert isinstance(user, model.User)
            if user.email == user_key.lower():
                return user
        raise exc.NoResultsError()
