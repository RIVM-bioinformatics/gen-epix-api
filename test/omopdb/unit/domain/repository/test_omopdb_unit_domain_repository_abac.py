"""Test the OmopDB ABAC repository specialization."""

from gen_epix.commondb.domain.repository import (
    BaseAbacRepository as CommonBaseAbacRepository,
)
from gen_epix.omopdb.domain.repository.abac import (
    BaseAbacRepository as OmopBaseAbacRepository,
)


def test_base_abac_repository_extends_commondb_contract():
    """Verify OmopDB retains the shared ABAC repository contract."""
    assert issubclass(OmopBaseAbacRepository, CommonBaseAbacRepository)
