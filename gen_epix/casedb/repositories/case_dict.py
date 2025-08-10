from gen_epix.casedb.domain.repository import BaseCaseRepository
from gen_epix.fastapp.repositories import DictRepository


class CaseDictRepository(DictRepository, BaseCaseRepository):
    pass
