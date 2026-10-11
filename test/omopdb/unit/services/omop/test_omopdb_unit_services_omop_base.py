"""Test OMOP service implementation setup."""

from datetime import datetime
from test.util.mock_compat import Mock
from types import SimpleNamespace
from typing import Any

from gen_epix.omopdb.services.omop.base import BaseOmopService


class _ConcreteOmopService(BaseOmopService):
    """Provide implementations required to instantiate the base service."""

    def upload_persons(self, cmd: Any) -> Any:
        """Satisfy the abstract upload contract for construction tests."""
        raise NotImplementedError

    def retrieve_persons_by_id(self, cmd: Any) -> Any:
        """Satisfy the abstract retrieval contract for construction tests."""
        raise NotImplementedError

    def retrieve_persons_by_query(self, cmd: Any) -> Any:
        """Satisfy the abstract query contract for construction tests."""
        raise NotImplementedError


def test_init_exposes_application_role_mappings() -> None:
    """Keep the application's role mappings available on the service."""
    role_map = {"role": "mapped-role"}
    role_set_map = {"role-set": frozenset({"mapped-role"})}
    app = Mock()
    app.impl = SimpleNamespace(role_map=role_map, role_set_map=role_set_map)
    app.generate_id.return_value = "service-id"
    app.generate_timestamp.return_value = datetime.now()

    service = _ConcreteOmopService(app, register_handlers=False)

    assert service.role_map is role_map
    assert service.role_set_map is role_set_map
