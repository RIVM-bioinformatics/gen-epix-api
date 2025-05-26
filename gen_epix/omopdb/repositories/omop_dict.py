from gen_epix.fastapp.repositories import DictRepository
from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository


class OmopDictRepository(DictRepository, BaseOmopRepository):
    pass
