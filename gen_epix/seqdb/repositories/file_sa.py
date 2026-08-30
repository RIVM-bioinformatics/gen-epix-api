"""Provide SeqDB persistence behavior for repositories.file_sa."""

from gen_epix.fastapp.repositories.sa.repository import SARepository
from gen_epix.seqdb.domain.repository.file import BaseFileRepository


class FileSARepository(SARepository, BaseFileRepository):
    pass
