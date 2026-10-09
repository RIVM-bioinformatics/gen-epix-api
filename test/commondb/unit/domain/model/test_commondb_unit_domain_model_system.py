"""Verify system model fields and default values."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from gen_epix.commondb.domain.model.system import (
    DeleteAllOperationalDataResult,
    DeleteAllRefDataResult,
    Outage,
    PackageMetadata,
)


def test_outage_defaults_optional_fields_to_none() -> None:
    outage = Outage()

    assert outage.description is None
    assert outage.active_from is None
    assert outage.active_to is None
    assert outage.visible_from is None
    assert outage.visible_to is None
    assert outage.is_active is None
    assert outage.is_visible is None


def test_outage_preserves_explicit_window_and_override_values() -> None:
    active_from = datetime(2026, 1, 1, tzinfo=UTC)
    active_to = datetime(2026, 1, 2, tzinfo=UTC)
    visible_from = datetime(2025, 12, 1, tzinfo=UTC)
    visible_to = datetime(2026, 1, 3, tzinfo=UTC)

    outage = Outage(
        description="Planned maintenance",
        active_from=active_from,
        active_to=active_to,
        visible_from=visible_from,
        visible_to=visible_to,
        is_active=False,
        is_visible=True,
    )

    assert outage.description == "Planned maintenance"
    assert outage.active_from == active_from
    assert outage.active_to == active_to
    assert outage.visible_from == visible_from
    assert outage.visible_to == visible_to
    assert outage.is_active is False
    assert outage.is_visible is True


def test_package_metadata_requires_name_and_version() -> None:
    for payload in ({"version": "1.0"}, {"name": "example"}):
        with pytest.raises(ValidationError):
            PackageMetadata.model_validate(payload)


def test_package_metadata_defaults_optional_fields_to_none() -> None:
    metadata = PackageMetadata(name="example", version="1.0")

    assert metadata.license is None
    assert metadata.homepage is None


@pytest.mark.parametrize(
    "result_class",
    [DeleteAllOperationalDataResult, DeleteAllRefDataResult],
    ids=["operational-data", "reference-data"],
)
def test_delete_result_requires_success_and_has_independent_details(
    result_class: type[DeleteAllOperationalDataResult] | type[DeleteAllRefDataResult],
) -> None:
    with pytest.raises(ValidationError):
        result_class.model_validate({})

    first = result_class(success=True)
    second = result_class(success=False)
    first.details["records"] = "deleted"

    assert first.success is True
    assert first.details == {"records": "deleted"}
    assert second.details == {}
    assert first.created_at is None
    assert first.modified_at is None
    assert first.modified_by is None
