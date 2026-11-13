"""Test dictionary-backed casedb ontology repository composition."""

from gen_epix.casedb.domain.repository import BaseOntologyRepository
from gen_epix.casedb.repositories import OntologyDictRepository as ExportedRepository
from gen_epix.casedb.repositories.ontology_dict import OntologyDictRepository
from gen_epix.fastapp.repositories import DictRepository


def test_repository_combines_dict_storage_and_ontology_contract() -> None:
    """The repository is dictionary-backed and implements the ontology contract."""
    assert issubclass(OntologyDictRepository, DictRepository)
    assert issubclass(OntologyDictRepository, BaseOntologyRepository)
    assert OntologyDictRepository.__mro__.index(
        DictRepository
    ) < OntologyDictRepository.__mro__.index(BaseOntologyRepository)


def test_repository_is_exported_from_package() -> None:
    """The package export resolves to the module's repository class."""
    assert ExportedRepository is OntologyDictRepository
