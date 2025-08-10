from gen_epix.casedb.domain.repository import BaseAbacRepository
from gen_epix.fastapp.repositories import DictRepository


class AbacDictRepository(DictRepository, BaseAbacRepository):
    pass
