import json
from pathlib import Path
from test.test_client import enum
from test.test_client.util import get_test_name, get_test_output_dir

import pytest

import docs.erm.erm_hash


@pytest.mark.scenario_ids("TC-SEC-28-08")
class TestERM:

    HASH_FILE = Path.cwd() / "docs" / "erm" / "erm.json"

    def test_erm_images_updated(self) -> None:
        expected_hash = docs.erm.erm_hash.generate_hash_for_domain_models(
            docs.erm.erm_hash.DOMAINS
        )
        with open(self.HASH_FILE, "r") as handle:
            actual_hash = json.load(handle)["models_hash"]
        assert (
            expected_hash == actual_hash
        ), "ERM diagrams are outdated. Please regenerate them."
