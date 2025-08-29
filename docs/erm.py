from pathlib import Path

from gen_epix.casedb.domain import DOMAIN as CASEDB_DOMAIN
from gen_epix.fastapp import Domain
from gen_epix.omopdb.domain import DOMAIN as OMOPDB_DOMAIN
from gen_epix.seqdb.domain import DOMAIN as SEQDB_DOMAIN


def generate_erm_diagrams(out_dir: Path) -> None:
    domains = {
        "casedb": CASEDB_DOMAIN,
        "omopdb": OMOPDB_DOMAIN,
        "seqdb": SEQDB_DOMAIN,
    }
    for name, domain in domains.items():
        generate_erm_diagrams_for_domain(domain, out_dir / name)


def generate_erm_diagrams_for_domain(domain: Domain, file_root: Path):
    """
    Generate an Entity-Relationship Model (ERM) diagram for the specified app.
    """
    sorted_model_classes = domain.get_dag_sorted_models()
    domain.get_model_links()  # for loop
    pass
