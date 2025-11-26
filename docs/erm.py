import json
import os
import warnings
from pathlib import Path

from docs.erm_hash import generate_hash_for_domain_models
from gen_epix.casedb.domain import DOMAIN as CASEDB_DOMAIN
from gen_epix.fastapp import Domain
from gen_epix.omopdb.domain import DOMAIN as OMOPDB_DOMAIN
from gen_epix.seqdb.domain import DOMAIN as SEQDB_DOMAIN

# Disable Graphviz Pango plugin warnings on Windows
# This prevents "Could not load gvplugin_pango.dll" warnings
os.environ.setdefault("GRAPHVIZ_DOT", "-Gfontname=Arial")

DOMAINS = [CASEDB_DOMAIN, OMOPDB_DOMAIN, SEQDB_DOMAIN]


def generate_erm_diagrams(dir: Path) -> None:
    """
    Generates Entity-Relationship Model (ERM) diagrams for all domains and their services,
    """

    # Suppress Graphviz/Pango warnings that are common on Windows
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", category=RuntimeWarning, module="pygraphviz.*"
        )

        # Create directory if it does not exist
        if not Path(dir).is_dir():
            Path.mkdir(dir)

        # Generate ERM diagrams for each domain and its services
        for domain in DOMAINS:
            generate_erm_diagrams_for_domain(domain, dir)
            generate_erm_diagrams_for_service(domain, dir)

        # Generate and save hash for all model classes across domains
        all_classes_hash = generate_hash_for_domain_models(DOMAINS, dir)
        with open(dir / "erm.json", "wt") as handle:
            json.dump({"models_hash": all_classes_hash}, handle)


def generate_erm_diagrams_for_domain(domain: Domain, dir: Path) -> None:
    """
    Generates and saves an Entity-Relationship Model (ERM) diagram for the entire domain.
    """
    # Suppress Graphviz/Pango warnings
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


def generate_erm_diagrams_for_service(domain: Domain, dir: Path) -> None:
    """
    Generates and saves Entity-Relationship Model (ERM) diagrams for each service type within the domain.
    """
    # Suppress Graphviz/Pango warnings
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
