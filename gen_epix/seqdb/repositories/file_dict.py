from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.seqdb.domain.repository.file import BaseFileRepository


class FileDictRepository(DictRepository, BaseFileRepository):
    pass
