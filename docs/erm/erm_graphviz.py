"""
Graphviz / erdantic-based ERM diagram generator.

Produces PNG Entity-Relationship diagrams using the ``erdantic`` library
(which depends on ``pygraphviz``).

Note: ``erdantic`` is not listed in ``dev-requirements.txt`` because
``pygraphviz`` is difficult to install on some systems.  Install it
manually when you need to regenerate the Graphviz diagrams.
"""

from __future__ import annotations

import json
import os
import warnings
from pathlib import Path

import erdantic as erd

from docs.erm.erm import ErmGenerator
from docs.erm.erm_hash import DOMAINS, generate_hash_for_domain_models
from gen_epix.fastapp import Domain

# Disable Graphviz Pango plugin warnings on Windows
# This prevents "Could not load gvplugin_pango.dll" warnings
os.environ.setdefault("GRAPHVIZ_DOT", "-Gfontname=Arial")


class GraphvizErmGenerator(ErmGenerator):
    """
    Generates Entity-Relationship Model diagrams as PNG files via
    ``erdantic`` / Graphviz.
    """

    def __init__(self, domains: list[Domain] | None = None) -> None:
        # Default to the three domains originally used by erm.py (no commondb)
        super().__init__(domains if domains is not None else list(DOMAINS))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_erm_diagrams(self, dir: Path) -> None:
        """
        Generate ERM diagrams (PNG) for every domain and its services.
        Also writes an ``erm.json`` hash file.
        """
        dir = Path(dir)
        dir.mkdir(parents=True, exist_ok=True)

        for domain in self.domains:
            self._generate_for_domain(domain, dir)
            self._generate_for_service(domain, dir)

        # Persist a hash so downstream tooling can detect model changes
        all_classes_hash = generate_hash_for_domain_models(self.domains, dir)
        with open(dir / "erm.json", "wt") as handle:
            json.dump({"models_hash": all_classes_hash}, handle)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_for_domain(domain: Domain, dir: Path) -> None:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", category=RuntimeWarning, module="pygraphviz.*"
            )
            sorted_model_classes = domain.get_dag_sorted_models(persistable=True)
            erd.draw(
                *sorted_model_classes,
                out=dir / f"{domain.name.lower()}.png",
                limit_search_models_to=[x.__name__ for x in sorted_model_classes],
            )

    @staticmethod
    def _generate_for_service(domain: Domain, dir: Path) -> None:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", category=RuntimeWarning, module="pygraphviz.*"
            )
            for service_type in domain.get_service_types():
                model_classes = domain.get_models_for_service_type(service_type)
                erd.draw(
                    *model_classes,
                    out=dir / f"{domain.name.lower()}.{service_type.value.lower()}.png",
                    limit_search_models_to=[x.__name__ for x in model_classes],
                )
