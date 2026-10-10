from uuid import UUID

import pytest

from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.classification import (
    AstPrediction,
    SeqClassification,
    SeqTaxonomy,
)


@pytest.mark.parametrize(
    ("model", "format", "extra_fields"),
    [
        pytest.param(
            SeqClassification,
            enum.SeqClassificationFormat.PRIMARY_CATEGORY_ONLY,
            {"primary_category_id": UUID(int=4)},
            id="classification",
        ),
        pytest.param(
            AstPrediction,
            enum.AstResultFormat.AST_RESULT_FORMAT1,
            {},
            id="ast-prediction",
        ),
        pytest.param(
            SeqTaxonomy,
            enum.SeqTaxonomyFormat.TAXONOMY_FORMAT1,
            {"primary_taxon_id": UUID(int=5)},
            id="taxonomy",
        ),
    ],
)
def test_content_models_accept_content_without_hash_verification(
    model, format, extra_fields
):
    """Keep content unchanged while content-hash verification is unimplemented."""
    content = "content with no matching hash"
    instance = model(
        sample_id=UUID(int=1),
        protocol_id=UUID(int=2),
        format=format,
        content_hash=UUID(int=3),
        content=content,
        **extra_fields,
    )

    assert instance.content == content
    assert instance.content_hash == UUID(int=3)


def test_classification_declares_primary_category_link() -> None:
    """Link the primary category identifier to the sequence category model."""
    link = SeqClassification.ENTITY.links[4]

    assert link.link_field_name == "primary_category_id"
    assert link.relationship_field_name == "primary_category"
