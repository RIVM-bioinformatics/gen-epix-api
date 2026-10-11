"""Check the SeqDB file repository domain contract."""

from gen_epix.fastapp.repository import BaseRepository
from gen_epix.seqdb.domain.repository.file import BaseFileRepository


def test_base_file_repository_implements_repository_contract():
    """Expose the shared repository contract for SeqDB file persistence."""
    assert issubclass(BaseFileRepository, BaseRepository)
