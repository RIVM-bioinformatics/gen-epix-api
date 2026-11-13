from test.util.mock_compat import Mock

from gen_epix.casedb.domain import command
from gen_epix.casedb.services.case.crud_tree_algorithm_class import (
    case_service_crud_tree_algorithm_class,
)


def test_case_service_crud_tree_algorithm_class_delegates_to_crud() -> None:
    service = Mock()
    cmd = Mock(spec=command.TreeAlgorithmClassCrudCommand)
    expected = object()
    service.crud.return_value = expected

    result = case_service_crud_tree_algorithm_class(service, cmd)

    service.crud.assert_called_once_with(cmd)
    assert result is expected
