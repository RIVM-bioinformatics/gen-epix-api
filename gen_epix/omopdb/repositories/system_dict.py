from gen_epix.fastapp.repositories import DictRepository
from gen_epix.omopdb.domain.repository.system import BaseSystemRepository


class SystemDictRepository(DictRepository, BaseSystemRepository):
    pass
