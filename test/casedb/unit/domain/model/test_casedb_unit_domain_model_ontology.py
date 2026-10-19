"""Tests for casedb ontology model validation."""

import pytest

from gen_epix.casedb.domain.model.ontology import Concept


def test_concept_props_normalization_does_not_mutate_input_mapping() -> None:
    """Normalize a copied props mapping and preserve the caller's input."""
    original = {
        "lb": 1,
        "ub": 2.5,
        "lb_in": 1,
        "ub_in": 0,
        "custom": ["value"],
    }
    source = original.copy()

    concept = Concept(
        concept_set_id="00000000-0000-0000-0000-000000000001",
        code="example",
        props=source,
    )

    assert concept.props == {
        "lb": 1.0,
        "ub": 2.5,
        "lb_in": True,
        "ub_in": False,
        "custom": ["value"],
    }
    assert source == original


@pytest.mark.parametrize(
    ("props_value", "expected"),
    [
        pytest.param(
            '{"lb": 3, "lb_in": 1}', {"lb": 3.0, "lb_in": True}, id="json-object"
        ),
        pytest.param(None, None, id="none"),
    ],
)
def test_concept_props_accepts_json_and_none(
    props_value: str | None, expected: dict[str, object] | None
) -> None:
    """Parse JSON props and preserve None without requiring a source mapping."""
    concept = Concept(
        concept_set_id="00000000-0000-0000-0000-000000000001",
        code="example",
        props=props_value,
    )
    assert concept.props == expected
