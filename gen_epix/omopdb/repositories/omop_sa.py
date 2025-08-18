from gen_epix.fastapp.repositories import SARepository
from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository


class OmopSARepository(SARepository, BaseOmopRepository):
    pass
