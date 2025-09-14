from gen_epix.common.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp.repositories import DictRepository


class SystemDictRepository(DictRepository, BaseSystemRepository):
    pass
