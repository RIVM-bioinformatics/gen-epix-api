import hashlib
import pickle
from pathlib import Path

from gen_epix.casedb.domain import DOMAIN as CASEDB_DOMAIN
from gen_epix.fastapp import Domain
from gen_epix.omopdb.domain import DOMAIN as OMOPDB_DOMAIN
from gen_epix.seqdb.domain import DOMAIN as SEQDB_DOMAIN

DOMAINS = [CASEDB_DOMAIN, OMOPDB_DOMAIN, SEQDB_DOMAIN]


def generate_hash_for_domain_models(
    domains: list[Domain], dir: Path | None = None
) -> str:
    """
    Generates a SHA-256 hash for a list of sorted classes by pickling them to a
    temporary file and then hashing the file.
    """
    sorted_model_classes = []
    for domain in domains:
        sorted_model_classes.extend(domain.get_dag_sorted_models(persistable=True))
    hash_code = hashlib.sha256(pickle.dumps(sorted_model_classes)).hexdigest()
    return hash_code
