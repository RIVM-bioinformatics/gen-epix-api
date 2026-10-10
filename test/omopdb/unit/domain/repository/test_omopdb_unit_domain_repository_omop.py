"""Verify the OMOP repository query contract."""

import inspect

import pytest

from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository


@pytest.mark.parametrize(
    "method_name",
    [
        "get_person_ids_modified_in_range",
        "get_full_persons_by_person_ids",
        "get_specimen_ids_by_cohort_ids",
    ],
)
def test_query_methods_are_abstract(method_name):
    """Ensure each OMOP query must be implemented by concrete repositories."""
    assert getattr(BaseOmopRepository, method_name).__isabstractmethod__


@pytest.mark.parametrize(
    ("method_name", "parameter_names", "required_parameter_names"),
    [
        (
            "get_person_ids_modified_in_range",
            ("self", "uow", "modified_since", "modified_until"),
            ("uow",),
        ),
        (
            "get_full_persons_by_person_ids",
            ("self", "person_ids"),
            ("person_ids",),
        ),
        (
            "get_specimen_ids_by_cohort_ids",
            ("self", "cohort_definition_id", "cohort_ids"),
            ("cohort_definition_id", "cohort_ids"),
        ),
    ],
)
def test_query_method_parameter_names_match_contract(
    method_name, parameter_names, required_parameter_names
):
    """Preserve the public parameter names and order for each query method."""
    parameters = inspect.signature(getattr(BaseOmopRepository, method_name)).parameters

    assert tuple(parameters) == parameter_names
    assert all(
        parameters[name].default is inspect.Parameter.empty
        for name in required_parameter_names
    )


def test_person_modified_range_bounds_are_optional():
    """Keep both timestamp range bounds optional in the repository contract."""
    parameters = inspect.signature(
        BaseOmopRepository.get_person_ids_modified_in_range
    ).parameters

    assert parameters["modified_since"].default is None
    assert parameters["modified_until"].default is None
