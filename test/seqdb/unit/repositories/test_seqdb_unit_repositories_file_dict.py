from gen_epix.seqdb.domain.model.file import File
from gen_epix.seqdb.repositories.file_dict import FileDictRepository


def test_create_repository_initializes_empty_file_store() -> None:
    """Create the dictionary repository with an empty file store."""
    repository = FileDictRepository.create_repository(entities=[File.ENTITY])

    assert isinstance(repository, FileDictRepository)
    assert repository.db == {File: {}}
