"""
Abstract base class for ERM diagram generators.

Subclasses implement ``generate_erm_diagrams`` to produce diagrams in a
specific format (Graphviz PNG, Mermaid Markdown, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from docs.erm.erm_hash import DOMAINS
from gen_epix.commondb.domain import DOMAIN as COMMONDB_DOMAIN
from gen_epix.fastapp import Domain

ALL_DOMAINS: list[Domain] = [*DOMAINS, COMMONDB_DOMAIN]


class ErmGenerator(ABC):
    """
    Base class for Entity-Relationship Model diagram generators.

    Parameters
    ----------
    domains
        The domains to generate diagrams for.  Defaults to *all* domains
        (casedb, omopdb, seqdb, commondb).
    """

    def __init__(self, domains: list[Domain] | None = None) -> None:
        self._domains = domains if domains is not None else list(ALL_DOMAINS)

    @property
    def domains(self) -> list[Domain]:
        return self._domains

    @abstractmethod
    def generate_erm_diagrams(self, dir: Path) -> None:
        """Generate ERM diagrams and write them into *dir*."""
        raise NotImplementedError()
