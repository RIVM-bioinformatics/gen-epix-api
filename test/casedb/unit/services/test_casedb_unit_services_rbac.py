"""Verify casedb-specific configuration of the shared RBAC service."""

from test.util.mock_compat import patch

from gen_epix.casedb.domain import enum
from gen_epix.casedb.services import rbac


def test_init_forwards_common_configuration_and_casedb_roles() -> None:
    app = object()
    logger = object()

    with patch(
        f"{rbac.__name__}.CommonRbacService.__init__", return_value=None
    ) as common_init:
        service = rbac.RbacService(app, logger=logger, custom_option="custom value")

    common_init.assert_called_once_with(
        app,
        logger=logger,
        role_enum=enum.Role,
        custom_option="custom value",
    )
    assert isinstance(service, rbac.RbacService)
