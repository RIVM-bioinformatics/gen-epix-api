from gen_epix.fastapp.repositories import SARepository
from gen_epix.omopdb.domain.repository import BaseAbacRepository


class AbacSARepository(SARepository, BaseAbacRepository):
    pass
