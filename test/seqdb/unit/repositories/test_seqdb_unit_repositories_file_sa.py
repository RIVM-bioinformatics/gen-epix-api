"""Verify the SQLAlchemy-backed seqdb file repository adapter."""

from typing import Any

from gen_epix.seqdb.domain.model.file import File
from gen_epix.seqdb.domain.repository.file import BaseFileRepository
from gen_epix.seqdb.repositories.file_sa import FileSARepository


def test_repository_implements_file_repository_contract() -> None:
    """Combine SQLAlchemy persistence with the seqdb file contract."""
    assert issubclass(FileSARepository, BaseFileRepository)


def test_create_repository_delegates_configuration(monkeypatch: Any) -> None:
    """Forward entities and connection details to the SQLAlchemy factory."""
    captured: dict[str, Any] = {}

    def fake_create_sa_repository(cls: type, **kwargs: Any) -> str:
        captured["cls"] = cls
        captured.update(kwargs)
        return "repository"

    monkeypatch.setattr(
        FileSARepository,
        "create_sa_repository",
        classmethod(fake_create_sa_repository),
    )

    result = FileSARepository.create_repository(
        entities=[File.ENTITY],
        connection_string="sqlite:///:memory:",
    )

    assert result == "repository"
    assert captured == {
        "cls": FileSARepository,
        "entities": [File.ENTITY],
        "connection_string": "sqlite:///:memory:",
    }
