"""Test omopdb system command model ordering."""

from test.util.domain_order import assert_models_follow_reverse_dag_order

import pytest

from gen_epix.omopdb.domain import DOMAIN, command


@pytest.mark.parametrize(
    "model_classes",
    [
        pytest.param(
            command.DeleteAllOperationalDataCommand.SORTED_OPERATIONAL_DATA_MODEL_CLASSES,
            id="operational-data",
        ),
        pytest.param(
            command.DeleteAllRefDataCommand.SORTED_REF_DATA_MODEL_CLASSES,
            id="reference-data",
        ),
    ],
)
def test_reset_model_lists_follow_reverse_dag_links(model_classes) -> None:
    """Reset lists delete each linked dependent before its referenced model."""
    assert_models_follow_reverse_dag_order(DOMAIN, model_classes)
