"""Verify phylogenetic tree leaf metadata validation."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.tree import PhylogeneticTree


def _create_tree(**overrides: object) -> PhylogeneticTree:
    """Build a tree with valid required fields and optional overrides."""
    values: dict[str, object] = {
        "tree_algorithm": enum.TreeAlgorithm.SLINK,
        "protocol_id": uuid4(),
        "newick_repr": ";",
    }
    values.update(overrides)
    return PhylogeneticTree(**values)


@pytest.mark.parametrize(
    ("leaf_names", "profile_ids"),
    [
        pytest.param(["leaf"], [], id="empty-profile-list"),
        pytest.param([], [uuid4()], id="empty-leaf-list"),
    ],
)
def test_tree_rejects_mismatched_supplied_leaf_lists(
    leaf_names: list[str], profile_ids: list[object]
) -> None:
    """Reject unequal lengths when both lists are explicitly provided."""
    with pytest.raises(ValidationError, match="same length"):
        _create_tree(leaf_names=leaf_names, profile_ids=profile_ids)


def test_tree_accepts_equal_empty_leaf_lists() -> None:
    """Accept matching empty lists as an explicit empty leaf set."""
    tree = _create_tree(leaf_names=[], profile_ids=[])

    assert tree.leaf_names == []
    assert tree.profile_ids == []


def test_tree_allows_omitted_profile_ids() -> None:
    """Do not compare lengths when profile identifiers are omitted."""
    tree = _create_tree(leaf_names=["leaf"])

    assert tree.leaf_names == ["leaf"]
    assert tree.profile_ids is None
