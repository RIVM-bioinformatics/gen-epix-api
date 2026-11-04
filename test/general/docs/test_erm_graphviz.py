from pathlib import Path
from unittest.mock import patch

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
        assert calls[f"{tag}.png"] == set(DOMAIN.get_models_for_service_type(service))
        assert calls[f"{tag}.persisted.png"] == set(
            DOMAIN.get_dag_sorted_models(service_type=service, persistable=True)
        )
