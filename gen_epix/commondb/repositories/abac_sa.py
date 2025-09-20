from gen_epix.commondb.domain.repository import BaseAbacRepository
from gen_epix.fastapp.repositories import SARepository


class AbacSARepository(SARepository, BaseAbacRepository):
    pass
