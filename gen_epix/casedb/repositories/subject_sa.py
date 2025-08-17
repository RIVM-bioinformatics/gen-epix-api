from gen_epix.casedb.domain.repository import BaseSubjectRepository
from gen_epix.fastapp.repositories import SARepository


class SubjectSARepository(SARepository, BaseSubjectRepository):
    pass
