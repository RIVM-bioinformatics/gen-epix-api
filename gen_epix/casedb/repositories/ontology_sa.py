"""Provide the SQLAlchemy persistence adapter for casedb ontology data.

`OntologySARepository` combines generic SQLAlchemy storage with the casedb
ontology repository contract; ontology-specific behavior remains in the domain
repository contract and collaborating services.
"""

from gen_epix.casedb.domain.repository import BaseOntologyRepository
from gen_epix.fastapp.repositories import SARepository


class OntologySARepository(SARepository, BaseOntologyRepository):
    """Provide SQLAlchemy-backed persistence for casedb ontology data."""

    pass
