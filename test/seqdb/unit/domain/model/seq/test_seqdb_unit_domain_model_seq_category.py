"""Validate sequence category domain models."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain.model.seq.category import SeqCategory, SeqCategorySet

SEQ_CATEGORY_SET_ID = UUID(int=1)


@pytest.mark.parametrize(
    ("model", "plural_name", "table_name"),
    [
        pytest.param(SeqCategorySet, "seq_category_sets", "seq_category_set", id="set"),
        pytest.param(SeqCategory, "seq_categories", "seq_category", id="category"),
    ],
)
def test_models_declare_persistable_entity_metadata(model, plural_name, table_name):
    """Expose the expected persistent entity names."""
    assert model.ENTITY.persistable is True
    assert model.ENTITY.snake_case_plural_name == plural_name
    assert model.ENTITY.table_name == table_name


def test_category_declares_category_set_link():
    """Link categories to their sequence category set model."""
    link = SeqCategory.ENTITY.links[1]

    assert link.link_field_name == "seq_category_set_id"
    assert link.link_model_class is SeqCategorySet
    assert link.relationship_field_name == "seq_category_set"


@pytest.mark.parametrize(
    "model", [SeqCategorySet, SeqCategory], ids=["set", "category"]
)
@pytest.mark.parametrize("field_name", ["code", "name"])
def test_code_and_name_enforce_max_length(model, field_name):
    """Accept field values at the limit and reject values beyond it."""
    fields = {"code": "value", "name": "value"}
    if model is SeqCategory:
        fields["seq_category_set_id"] = SEQ_CATEGORY_SET_ID

    fields[field_name] = "x" * 255
    assert getattr(model(**fields), field_name) == "x" * 255

    fields[field_name] = "x" * 256
    with pytest.raises(ValidationError):
        model(**fields)


def test_category_requires_sequence_category_set_id():
    """Require a category-set UUID and preserve its value."""
    with pytest.raises(ValidationError):
        SeqCategory(code="variant", name="Variant")

    category = SeqCategory(
        code="variant",
        name="Variant",
        seq_category_set_id=SEQ_CATEGORY_SET_ID,
    )
    assert category.seq_category_set_id == SEQ_CATEGORY_SET_ID


def test_category_relationship_is_optional_and_accepts_a_model():
    """Default the relationship to None and accept a category-set model."""
    category = SeqCategory(
        code="variant",
        name="Variant",
        seq_category_set_id=SEQ_CATEGORY_SET_ID,
    )
    assert category.seq_category_set is None

    category_set = SeqCategorySet(code="lineage", name="Lineage")
    category = SeqCategory(
        code="variant",
        name="Variant",
        seq_category_set_id=SEQ_CATEGORY_SET_ID,
        seq_category_set=category_set,
    )
    assert category.seq_category_set is category_set
