from gen_epix.casedb.domain.repository import BaseAbacRepository
from gen_epix.fastapp.repositories import SARepository


class AbacSARepository(SARepository, BaseAbacRepository):
    pass
