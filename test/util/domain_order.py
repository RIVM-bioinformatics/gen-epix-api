"""Assertions for domain model ordering in tests."""

from collections.abc import Sequence
from typing import Any

from gen_epix.fastapp.domain import Domain


def assert_models_follow_reverse_dag_order(
    domain: Domain, model_classes: Sequence[type[Any]]
) -> None:
    """Assert linked models are ordered dependents before their dependencies."""
    reverse_dag_positions = {
        model_class: index
        for index, model_class in enumerate(
            domain.get_dag_sorted_models(persistable=True, reverse=True)
        )
    }
    model_positions = {
        model_class: index for index, model_class in enumerate(model_classes)
    }

    assert len(model_positions) == len(model_classes)
    assert set(model_classes) <= reverse_dag_positions.keys()
    for model_class in model_classes:
        assert model_class.ENTITY is not None
        entity = model_class.ENTITY
        links = [*entity.links.values(), *entity.multi_links]
        for link in links:
            linked_model_class = link.link_model_class
            if linked_model_class not in model_positions:
                continue
            assert (
                reverse_dag_positions[model_class]
                < reverse_dag_positions[linked_model_class]
            )
            assert model_positions[model_class] < model_positions[linked_model_class], (
                f"{model_class.__name__} must be deleted before "
                f"{linked_model_class.__name__}"
            )
