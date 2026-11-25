"""Verify AppImplDetails service-type normalization."""

from enum import Enum

import pytest
from pydantic import ValidationError

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.policy import BasePolicyDecisionPoint
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.fastapp import BaseUserManager
from gen_epix.fastapp.services.rbac import BaseRbacService


def _create_app_impl_details(
    sorted_service_types: tuple[Enum, ...] | list[Enum],
) -> AppImplDetails:
    """Construct AppImplDetails with minimal valid required metadata."""
    return AppImplDetails(
        sorted_service_types=sorted_service_types,
        rbac_service_class=BaseRbacService,
        abac_service_class=BaseAbacService,
        user_manager_class=BaseUserManager,
        pdp_class=BasePolicyDecisionPoint,
        role_map=enum.Role,
        role_set_map=enum.RoleSet,
        role_permissions_map={},
    )


@pytest.mark.parametrize(
    "service_types",
    [
        pytest.param([enum.ServiceType.ABAC, enum.ServiceType.ABAC], id="list"),
        pytest.param((enum.ServiceType.ABAC, enum.ServiceType.ABAC), id="tuple"),
    ],
)
def test_sorted_service_types_reject_duplicates(
    service_types: tuple[Enum, ...] | list[Enum],
) -> None:
    """Apply the unique-service invariant to every accepted collection type."""
    with pytest.raises(ValidationError, match="must not contain duplicates"):
        _create_app_impl_details(service_types)


def test_sorted_service_types_normalizes_tuple_to_list() -> None:
    """Normalize a unique tuple to the declared list field type."""
    details = _create_app_impl_details((enum.ServiceType.ABAC,))

    assert details.sorted_service_types == [enum.ServiceType.ABAC]
