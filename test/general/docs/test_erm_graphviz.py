"""Test ERM diagrams when erdantic is available.

CI may skip these tests because erdantic depends on pygraphviz, which is
intentionally excluded from dev requirements due to installation difficulties.
See ``docs/erm/erm_graphviz.py`` for details.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

# isort: off
pytest.importorskip("erdantic")

from docs.erm.erm_graphviz import GraphvizErmGenerator
from gen_epix.casedb.domain import DOMAIN

# isort: on


class IncludedTarget(BaseModel):
    value: str


class ExcludedTarget(BaseModel):
    value: str


class Source(BaseModel):
    included: IncludedTarget
    excluded: ExcludedTarget


def test_scoped_graph_excludes_unselected_models_and_links(tmp_path: Path) -> None:
    with patch("pygraphviz.AGraph.draw", autospec=True) as draw:
        GraphvizErmGenerator._draw_scoped([Source, IncludedTarget], tmp_path / "x.png")

    graph = draw.call_args.args[0]
    names = {str(node).rsplit(".", 1)[-1] for node in graph.nodes()}
    edges = {
        (str(a).rsplit(".", 1)[-1], str(b).rsplit(".", 1)[-1]) for a, b in graph.edges()
    }
    assert names == {"Source", "IncludedTarget"}
    assert edges == {("Source", "IncludedTarget")}


def test_service_diagrams_select_persisted_models(tmp_path: Path) -> None:
    with patch.object(GraphvizErmGenerator, "_draw_scoped") as draw:
        GraphvizErmGenerator._generate_for_service(DOMAIN, tmp_path)

    calls = {call.args[1].name: set(call.args[0]) for call in draw.call_args_list}
    for service in DOMAIN.get_service_types():
        tag = f"{DOMAIN.name.lower()}.{service.value.lower()}"
        models = set(DOMAIN.get_models_for_service_type(service))
        persisted = set(
            DOMAIN.get_dag_sorted_models(service_type=service, persistable=True)
        )
        assert calls[f"{tag}.png"] == models
        if persisted and persisted != models:
            assert calls[f"{tag}.persisted.png"] == persisted
        else:
            assert f"{tag}.persisted.png" not in calls


@pytest.mark.parametrize(
    ("persisted", "should_draw"),
    [([], False), ([IncludedTarget, Source], False), ([Source], True)],
    ids=["empty", "all-in-different-order", "subset"],
)
def test_service_persisted_image_selection(
    tmp_path: Path, persisted: list[type[BaseModel]], should_draw: bool
) -> None:
    service = MagicMock(value="example")
    domain = MagicMock(name="domain")
    domain.name = "example"
    domain.get_service_types.return_value = [service]
    domain.get_models_for_service_type.return_value = {Source, IncludedTarget}
    domain.get_dag_sorted_models.return_value = persisted
    persisted_path = tmp_path / "example.example.persisted.png"
    persisted_path.touch()

    with patch.object(GraphvizErmGenerator, "_draw_scoped") as draw:
        GraphvizErmGenerator._generate_for_service(domain, tmp_path)

    assert (
        any(call.args[1] == persisted_path for call in draw.call_args_list)
        is should_draw
    )
    assert persisted_path.exists() is should_draw
