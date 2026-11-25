"""Test concrete casedb geographic service behavior."""

from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.services.geo import GeoService


def test_retrieve_containing_region_is_explicitly_unsupported() -> None:
    service = GeoService(Mock(), service_type=ServiceType.GEO, register_handlers=False)
    cmd = command.RetrieveContainingRegionCommand(
        region_ids=[uuid4()], region_set_id=uuid4(), level=1
    )

    with pytest.raises(NotImplementedError):
        service.retrieve_containing_region(cmd)
