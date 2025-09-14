from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp.repositories import DictRepository


class SystemDictRepository(DictRepository, BaseSystemRepository):
    pass
