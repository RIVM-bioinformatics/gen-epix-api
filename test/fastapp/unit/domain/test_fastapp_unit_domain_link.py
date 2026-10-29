import pytest
from pydantic import BaseModel

from gen_epix.fastapp.domain.link import Link, MultiLink


def test_multi_link_from_tuple_round_trips() -> None:
    link_tuple = ("items", BaseModel)

    link = MultiLink.from_tuple(link_tuple)

    assert link.to_tuple() == link_tuple


@pytest.mark.parametrize(
    "relationship_field_name",
    [None, "relationship"],
    ids=["no-relationship-field", "relationship-field"],
)
def test_link_from_tuple_round_trips(
    relationship_field_name: str | None,
) -> None:
    link_tuple = ("item", BaseModel, relationship_field_name)

    link = Link.from_tuple(link_tuple)

    assert link.to_tuple() == link_tuple
