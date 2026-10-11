from test.util.mock_compat import Mock

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.policy.system import BaseHasSystemOutagePolicy
from gen_epix.fastapp import PermissionType


def test_constructor_stores_service_props_and_outage_update_permission() -> None:
    system_service = Mock()
    outage_update_permission = Mock()
    system_service.app.domain.get_permission.return_value = outage_update_permission

    policy = BaseHasSystemOutagePolicy(system_service, cache_ttl=12)

    assert policy.system_service is system_service
    assert policy.props == {"cache_ttl": 12}
    assert policy.outage_update_permission is outage_update_permission
    system_service.app.domain.get_permission.assert_called_once_with(
        command.OutageCrudCommand, PermissionType.UPDATE
    )
