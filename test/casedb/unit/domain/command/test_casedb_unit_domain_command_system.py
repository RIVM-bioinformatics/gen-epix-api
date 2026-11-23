"""Test casedb system command model ordering."""

from test.util.domain_order import assert_models_follow_reverse_dag_order

import pytest

from gen_epix.casedb.domain import DOMAIN, command, model


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


KEPT_MODEL_CLASSES = [
    model.UserAccessCasePolicy,
    model.UserShareCasePolicy,
    model.CaseTypeSet,
    model.CaseTypeSetCategory,
    model.ColSet,
]


def test_ref_data_reset_keeps_user_policies_and_their_targets() -> None:
    """A reset keeps admin-created user policies and the sets they point at."""
    deleted = set(command.DeleteAllRefDataCommand.SORTED_REF_DATA_MODEL_CLASSES)
    deleted_operational = set(
        command.DeleteAllOperationalDataCommand.SORTED_OPERATIONAL_DATA_MODEL_CLASSES
    )
    for model_class in KEPT_MODEL_CLASSES:
        assert model_class not in deleted
        assert model_class not in deleted_operational
    # The remaining reference data, including organization policies, is still deleted
    assert model.OrganizationAccessCasePolicy in deleted
    assert model.OrganizationShareCasePolicy in deleted
    assert model.CaseTypeSetMember in deleted
    assert model.ColSetMember in deleted
    assert model.CaseType in deleted
    assert model.Col in deleted


@pytest.mark.parametrize(
    "kept_class", [model.UserAccessCasePolicy, model.UserShareCasePolicy]
)
def test_ref_data_reset_does_not_delete_models_kept_policies_link_to(
    kept_class,
) -> None:
    """No model a kept policy links to is deleted, so no foreign key is violated."""
    deleted = set(command.DeleteAllRefDataCommand.SORTED_REF_DATA_MODEL_CLASSES)
    for link in kept_class.ENTITY.links.values():
        assert link.link_model_class not in deleted, link.link_model_class.__name__
