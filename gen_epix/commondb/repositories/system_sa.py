"""Provide the SQLAlchemy-backed repository for commondb system records.

`SystemSARepository` combines SQLAlchemy persistence with the shared system
repository contract.
"""

from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp.repositories import SARepository


class SystemSARepository(SARepository, BaseSystemRepository):
    """Encapsulates commondb system storage with SQLAlchemy.

    Inherits persistence behavior from `SARepository` and fulfills the
    `BaseSystemRepository` contract.
    """
