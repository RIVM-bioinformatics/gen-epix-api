import json
from pathlib import Path
from test.test_client import enum
from test.test_client.util import get_test_name, get_test_output_dir

from docs import erm
from gen_epix.casedb.domain import DOMAIN as CASEDB_DOMAIN
from gen_epix.omopdb.domain import DOMAIN as OMOPDB_DOMAIN
from gen_epix.seqdb.domain import DOMAIN as SEQDB_DOMAIN


class TestERM:
    DOMAINS = {
        "casedb": CASEDB_DOMAIN,
        "omopdb": OMOPDB_DOMAIN,
        "seqdb": SEQDB_DOMAIN,
    }

    TEST_DIR = get_test_output_dir(get_test_name(enum.TestType.DOCS_ERM))

    def test_erm_images_updated(self):
        print("test")
        combined_sorted_model_classes = erm.get_sorted_model_classes(self.DOMAINS)
        # read the existing json file with hash code
        pickle_file_path = self.TEST_DIR / "temp_domain_pickle_file.pkl"
        erm.create_domain_pickle_file(combined_sorted_model_classes, pickle_file_path)
        domain_pickle_hash = erm.create_sha256_hash(pickle_file_path)
        erm.remove_file(pickle_file_path)
        json_file = Path.cwd() / "docs" / "assets" / "erm" / "erm.json"
        with open(json_file, "r") as handle:
            hash_dict = json.load(handle)
        assert (
            hash_dict["models_hash"] == domain_pickle_hash
        ), "ERM diagrams are outdated. Please run 'make docs-erm' to regenerate them."
