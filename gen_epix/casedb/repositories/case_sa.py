from gen_epix.casedb.domain.repository import BaseCaseRepository
from gen_epix.fastapp.repositories import SARepository


class CaseSARepository(SARepository, BaseCaseRepository):
    pass
