"""Provide casedb's dictionary-backed ontology repository implementation.

`OntologyDictRepository` combines `DictRepository` storage with the
`BaseOntologyRepository` contract used by casedb services.
"""

from gen_epix.casedb.domain.repository import BaseOntologyRepository
from gen_epix.fastapp.repositories import DictRepository


class OntologyDictRepository(DictRepository, BaseOntologyRepository):
    """Provide dictionary-backed persistence for casedb ontology data."""

    pass
