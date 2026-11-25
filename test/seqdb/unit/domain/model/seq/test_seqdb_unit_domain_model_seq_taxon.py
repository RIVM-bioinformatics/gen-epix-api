"""Verify NCBI taxon identifier normalization."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.taxon import Taxon


def _taxon(ncbi_taxid: int | float | str | None) -> Taxon:
    return Taxon(
        code="test",
        name="Test taxon",
        rank=enum.TaxonRank.SPECIES,
        ncbi_taxid=ncbi_taxid,
        ancestor_taxon_ids=[uuid4()],
    )


def test_optional_ncbi_taxid_accepts_none() -> None:
    """Keep an explicit None for the optional NCBI identifier."""
    assert _taxon(None).ncbi_taxid is None


@pytest.mark.parametrize("value", [123, 123.0, "NCBI:txid123"])
def test_ncbi_taxid_normalizes_integral_values(value: int | float | str) -> None:
    """Normalize integer, integral float, and prefixed string identifiers."""
    assert _taxon(value).ncbi_taxid == 123


def test_ncbi_taxid_rejects_fractional_values() -> None:
    """Reject fractional identifiers instead of truncating them."""
    with pytest.raises(ValidationError, match="must be an integer"):
        _taxon(1.9)
