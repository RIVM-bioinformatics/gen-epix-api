"""Verify locus gene-product validation."""

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.locus import Locus


def test_non_gene_locus_rejects_gene_product_code_with_accurate_message() -> None:
    """Explain that gene-product codes are restricted to gene loci."""
    with pytest.raises(ValidationError, match="only allowed for locus_type GENE"):
        Locus(
            code="locus-1",
            locus_type=enum.LocusType.OTHER,
            gene_product_code="product-1",
        )


def test_gene_locus_accepts_gene_product_code() -> None:
    """Allow a gene-product code for a gene locus."""
    locus = Locus(
        code="locus-1",
        locus_type=enum.LocusType.GENE,
        gene_product_code="product-1",
    )

    assert locus.gene_product_code == "product-1"
