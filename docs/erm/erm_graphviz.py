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
from collections.abc import Collection
from pathlib import Path

import erdantic as erd

from docs.erm.erm import ErmGenerator
from docs.erm.erm_hash import DOMAINS, generate_hash_for_domain_models
from gen_epix.fastapp import Domain
from gen_epix.fastapp.model import Model

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
            erd.draw(*sorted_model_classes, out=dir / f"{domain.name.lower()}.png")
            GraphvizErmGenerator._draw_scoped(
                sorted_model_classes, dir / f"{domain.name.lower()}.persisted.png"
            )

    @staticmethod
    def _generate_for_service(domain: Domain, dir: Path) -> None:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", category=RuntimeWarning, module="pygraphviz.*"
            )
            for service_type in domain.get_service_types():
                model_classes = domain.get_models_for_service_type(service_type)
                tag = f"{domain.name.lower()}.{service_type.value.lower()}"
                GraphvizErmGenerator._draw_scoped(model_classes, dir / f"{tag}.png")
                persisted_models = domain.get_dag_sorted_models(
                    service_type=service_type, persistable=True
                )
                GraphvizErmGenerator._draw_scoped(
                    persisted_models, dir / f"{tag}.persisted.png"
                )

    @staticmethod
    def _draw_scoped(model_classes: Collection[type[Model]], out: Path) -> None:
        """Draw only the supplied models and relationships between them."""
        diagram = erd.create(*model_classes)
        graph = diagram.to_graphviz()
        included = set(model_classes)
        for name, model in diagram.models.items():
            if model.raw_model not in included:
                graph.remove_node(name)
        graph.draw(out, prog="dot")
