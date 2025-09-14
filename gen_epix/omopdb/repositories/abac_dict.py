from gen_epix.fastapp.repositories import DictRepository
from gen_epix.omopdb.domain.repository import BaseAbacRepository


class AbacDictRepository(DictRepository, BaseAbacRepository):
    pass
