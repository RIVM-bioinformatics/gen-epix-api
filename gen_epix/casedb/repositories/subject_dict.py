from gen_epix.casedb.domain.repository.subject import BaseSubjectRepository
from gen_epix.fastapp.repositories import DictRepository


class SubjectDictRepository(DictRepository, BaseSubjectRepository):
    pass
