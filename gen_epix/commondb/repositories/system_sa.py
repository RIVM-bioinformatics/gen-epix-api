from gen_epix.common.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp.repositories import SARepository


class SystemSARepository(SARepository, BaseSystemRepository):
    pass
