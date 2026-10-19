from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock, patch
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import exc, model
from gen_epix.casedb.domain.enum import CaseRight
from gen_epix.casedb.services.case import crud_case
from gen_epix.fastapp import CrudOperation


class TestCaseCrud(BaseCrudTestCase):
    def _configure_abac_delete(self, allowed: bool) -> tuple[Mock, Mock, Mock]:
        cmd = self.create_crud_command(operation=CrudOperation.DELETE_SOME)
        cmd.is_delete_all = Mock(return_value=False)
        case = Mock(spec=model.Case)
        case.id = uuid4()
        case.case_type_id = uuid4()
        case.created_in_data_collection_id = uuid4()
        case_abac = Mock()
        case_abac.is_allowed = Mock(return_value=allowed)
        self.service.repository.crud.return_value = [case]
        self.service._retrieve_case_data_collections_map = Mock(
            return_value={case.id: set()}
        )
        self.service.app.pdp.is_exempted.return_value = False
        return cmd, case_abac, case

    def test_exempt_admin_keeps_cascade_path(self) -> None:
        events: list[str] = []
        cmd = self.create_crud_command(operation=CrudOperation.READ_SOME)
        self.service.app.pdp.is_exempted.return_value = True
        self.service.crud.side_effect = lambda _: events.append("crud") or True
        with patch(
            f"{crud_case.__name__}._crud_cascade_delete",
            new=Mock(side_effect=lambda *args: events.append("cascade")),
        ) as cascade_delete:
            assert crud_case.case_service_crud_case(self.service, cmd) is True

        assert events == ["cascade", "crud"]
        cascade_delete.assert_called_once_with(self.service, self.uow, cmd)

    def test_abac_delete_checks_rights_before_cascade(self) -> None:
        events: list[str] = []
        cmd, case_abac, case = self._configure_abac_delete(allowed=True)
        case_abac.is_allowed.side_effect = (
            lambda *args, **kwargs: events.append("authorize") or True
        )
        self.service.crud.side_effect = lambda _: events.append("crud") or True
        with (
            patch(
                f"{crud_case.__name__}._crud_cascade_delete",
                new=Mock(side_effect=lambda *args: events.append("cascade")),
            ) as cascade_delete,
            patch(
                f"{crud_case.__name__}.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            assert crud_case.case_service_crud_case(self.service, cmd) is True

        assert events == ["authorize", "cascade", "crud"]
        cascade_delete.assert_called_once_with(self.service, self.uow, cmd)
        case_abac.is_allowed.assert_called_once_with(
            case.case_type_id,
            case.created_in_data_collection_id,
            CaseRight.REMOVE_CASE,
            True,
            current_data_collection_ids=set(),
        )

    def test_abac_delete_denial_does_not_cascade_or_delete(self) -> None:
        cmd, case_abac, _ = self._configure_abac_delete(allowed=False)
        with (
            patch(
                f"{crud_case.__name__}._crud_cascade_delete", new=Mock()
            ) as cascade_delete,
            patch(
                f"{crud_case.__name__}.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            with pytest.raises(exc.UnauthorizedAuthError):
                crud_case.case_service_crud_case(self.service, cmd)

        cascade_delete.assert_not_called()
        self.service.crud.assert_not_called()

    def test_no_policy_delete_still_cascades_before_crud(self) -> None:
        events: list[str] = []
        cmd = self.create_crud_command(operation=CrudOperation.DELETE_SOME)
        self.service.app.pdp.is_exempted.return_value = False
        self.service.crud.side_effect = lambda _: events.append("crud") or True
        with (
            patch(
                f"{crud_case.__name__}._crud_cascade_delete",
                new=Mock(side_effect=lambda *args: events.append("cascade")),
            ) as cascade_delete,
            patch(
                f"{crud_case.__name__}.get_case_abac_from_command",
                new=Mock(return_value=None),
            ),
        ):
            assert crud_case.case_service_crud_case(self.service, cmd) is True

        assert events == ["cascade", "crud"]
        cascade_delete.assert_called_once_with(self.service, self.uow, cmd)

    def test_abac_non_delete_operation_remains_unsupported(self) -> None:
        cmd = self.create_crud_command(operation=CrudOperation.READ_SOME)
        case_abac = Mock()
        self.service.app.pdp.is_exempted.return_value = False
        with (
            patch(
                f"{crud_case.__name__}._crud_cascade_delete", new=Mock()
            ) as cascade_delete,
            patch(
                f"{crud_case.__name__}.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            with pytest.raises(AssertionError, match="Unexpected operation"):
                crud_case.case_service_crud_case(self.service, cmd)

        cascade_delete.assert_not_called()
        case_abac.is_allowed.assert_not_called()
