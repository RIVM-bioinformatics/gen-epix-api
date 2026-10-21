"""Tests for cache tag rendering and indexing."""

from gen_epix.fastapp.cache.tag import MemoryTagIndex, TagTemplate, render_tags


def test_tag_templates_render_from_call_arguments() -> None:
    """Tags are reproducible by a writer that never made the call."""
    assert TagTemplate("case:{case_id}").render({"case_id": 3}) == "case:3"
    assert render_tags(("case", "case:{case_id}"), {"case_id": 3}) == frozenset(
        {"case", "case:3"}
    )


def test_the_tag_index_keeps_both_directions_consistent() -> None:
    """Removing a key must not leave it reachable through a tag."""
    index = MemoryTagIndex()
    index.add("k", ["a", "b"])

    index.discard_key("k")

    assert index.keys_for("a") == set()
    assert index.tags() == set()


def test_retagging_a_key_drops_its_previous_tags() -> None:
    """A rewritten entry is not invalidated by a tag it no longer has."""
    index = MemoryTagIndex()
    index.add("k", ["old"])

    index.add("k", ["new"])

    assert index.keys_for("old") == set()
    assert index.keys_for("new") == {"k"}
