"""Test casedb SQLAlchemy ontology repository composition."""

from gen_epix.casedb.domain.repository import BaseOntologyRepository
from gen_epix.casedb.repositories import OntologySARepository as ExportedRepository
from gen_epix.casedb.repositories.ontology_sa import OntologySARepository
from gen_epix.fastapp.repositories import SARepository


def test_repository_combines_sql_storage_and_ontology_contract() -> None:
    """The repository provides SQLAlchemy storage and the ontology contract."""
    assert issubclass(OntologySARepository, SARepository)
    assert issubclass(OntologySARepository, BaseOntologyRepository)
    assert OntologySARepository.__mro__.index(
        SARepository
    ) < OntologySARepository.__mro__.index(BaseOntologyRepository)


def test_repository_is_exported_from_package() -> None:
    """The package export resolves to the module's repository class."""
    assert ExportedRepository is OntologySARepository
