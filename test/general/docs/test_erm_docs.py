import json
from pathlib import Path
from test.test_client import enum
from test.test_client.util import get_test_name, get_test_output_dir

import docs.erm_hash
from docs import erm


class TestERM:

    TEST_DIR = get_test_output_dir(get_test_name(enum.TestType.DOCS_ERM))
    HASH_FILE = Path.cwd() / "docs" / "assets" / "erm" / "erm.json"

    def test_erm_images_updated(self) -> None:
        expected_hash = docs.erm_hash.generate_hash_for_domain_models(erm.DOMAINS)
        with open(self.HASH_FILE, "r") as handle:
            actual_hash = json.load(handle)["models_hash"]
        assert (
            expected_hash == actual_hash
        ), "ERM diagrams are outdated. Please regenerate them."
