"""Provide SQLAlchemy-backed persistence for casedb ontology data."""

from gen_epix.casedb.domain.repository import BaseOntologyRepository
from gen_epix.fastapp.repositories import SARepository


class OntologySARepository(SARepository, BaseOntologyRepository):
    """Provide SQLAlchemy-backed persistence for casedb ontology data."""

    pass
