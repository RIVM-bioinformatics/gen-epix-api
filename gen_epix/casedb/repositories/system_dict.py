from gen_epix.casedb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp.repositories import DictRepository


class SystemDictRepository(DictRepository, BaseSystemRepository):
    pass
