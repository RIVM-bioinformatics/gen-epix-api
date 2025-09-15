from docs import erm
from gen_epix.casedb.domain import DOMAIN as CASEDB_DOMAIN
from gen_epix.omopdb.domain import DOMAIN as OMOPDB_DOMAIN
from gen_epix.seqdb.domain import DOMAIN as SEQDB_DOMAIN


class TestERM:
    def __init__(self):
        self.domains = {
            "casedb": CASEDB_DOMAIN,
            "omopdb": OMOPDB_DOMAIN,
            "seqdb": SEQDB_DOMAIN,
        }

    def test_erm_images_updated(self):
        print("test")
        combined_sorted_model_classes = erm.get_sorted_model_classes(self.domains)
