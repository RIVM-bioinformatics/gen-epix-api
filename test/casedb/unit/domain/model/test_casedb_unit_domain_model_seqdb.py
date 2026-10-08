"""Check the casedb phylogenetic tree projection model."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model import seqdb
from gen_epix.casedb.domain.model.seqdb import PhylogeneticTree

NEWICK = "(A:1,B:2);"


@pytest.fixture(name="tree_kwargs")
def fixture_tree_kwargs() -> dict:
    """Return fresh minimal valid constructor arguments."""
    return {"tree_algorithm_code": enum.TreeAlgorithmType.UPGMA, "newick_repr": NEWICK}


def test_entity_is_not_persistable() -> None:
    """Check the entity metadata marks the tree as non-persisted."""
    entity = PhylogeneticTree.ENTITY

    assert entity.snake_case_plural_name == "phylogenetic_trees"
    assert entity.persistable is False
    assert seqdb.PhylogeneticTree is PhylogeneticTree


def test_optional_fields_default_to_none(tree_kwargs: dict) -> None:
    """Check omitted optional fields default to None."""
    tree = PhylogeneticTree(**tree_kwargs)

    assert tree.id is None
    assert tree.tree_algorithm_id is None
    assert tree.tree_algorithm is None
    assert tree.protocol_id is None
    assert tree.protocol is None
    assert tree.leaf_ids is None
    assert tree.profile_ids is None
    assert tree.newick_repr == NEWICK


@pytest.mark.parametrize("missing", ["tree_algorithm_code", "newick_repr"])
def test_required_fields_are_enforced(tree_kwargs: dict, missing: str) -> None:
    """Check omitting a required field fails validation."""
    del tree_kwargs[missing]

    with pytest.raises(ValidationError):
        PhylogeneticTree(**tree_kwargs)


def test_tree_algorithm_code_accepts_string_value(tree_kwargs: dict) -> None:
    """Check a valid algorithm string is normalized to the enum member."""
    tree_kwargs["tree_algorithm_code"] = "SLINK"

    tree = PhylogeneticTree(**tree_kwargs)

    assert tree.tree_algorithm_code is enum.TreeAlgorithmType.SLINK


def test_tree_algorithm_code_rejects_unknown_value(tree_kwargs: dict) -> None:
    """Check an unknown algorithm string fails validation."""
    tree_kwargs["tree_algorithm_code"] = "NOT_AN_ALGORITHM"

    with pytest.raises(ValidationError):
        PhylogeneticTree(**tree_kwargs)


@pytest.mark.parametrize("field", ["leaf_ids", "profile_ids"])
@pytest.mark.parametrize("count", [0, 1, 3], ids=["empty", "single", "multiple"])
def test_id_lists_preserve_order_and_duplicates(
    tree_kwargs: dict, field: str, count: int
) -> None:
    """Check ID lists keep size, order, and duplicates."""
    ids = [uuid4() for _ in range(count)]
    ids = ids + ids[:1]
    tree_kwargs[field] = ids

    tree = PhylogeneticTree(**tree_kwargs)

    assert getattr(tree, field) == ids


def test_id_lists_reject_invalid_uuid(tree_kwargs: dict) -> None:
    """Check a malformed UUID in an ID list fails validation."""
    tree_kwargs["leaf_ids"] = ["not-a-uuid"]

    with pytest.raises(ValidationError):
        PhylogeneticTree(**tree_kwargs)


def test_id_fields_coerce_uuid_strings(tree_kwargs: dict) -> None:
    """Check UUID strings are coerced to UUID values."""
    value = uuid4()
    tree_kwargs["protocol_id"] = str(value)
    tree_kwargs["tree_algorithm_id"] = str(value)

    tree = PhylogeneticTree(**tree_kwargs)

    assert tree.protocol_id == value
    assert tree.tree_algorithm_id == value


def test_newick_repr_rejects_non_string(tree_kwargs: dict) -> None:
    """Check a None Newick representation fails validation."""
    tree_kwargs["newick_repr"] = None

    with pytest.raises(ValidationError):
        PhylogeneticTree(**tree_kwargs)
