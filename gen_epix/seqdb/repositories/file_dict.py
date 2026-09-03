"""Provide seqdb persistence behavior for repositories.file_dict."""

from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.seqdb.domain.repository.file import BaseFileRepository


class FileDictRepository(DictRepository, BaseFileRepository):
    """Encapsulates dictionary-backed persistence for seqdb uploaded files."""

    pass
