from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock

import pytest

import gen_epix.casedb.services.case.crud_case_type_set_member as crud_case_type_set_member
from gen_epix.fastapp import CrudOperation


class TestCaseTypeSetMemberCrud(BaseCrudTestCase):
    """Verify reference-data access to case-type-set membership rows."""

    def test_non_exempt_dispatch_uses_abac_handler(self, monkeypatch) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_SOME)
        expected_result = object()
        abac_handler = Mock(return_value=expected_result)
        without_abac_handler = Mock()
        monkeypatch.setattr(
            crud_case_type_set_member,
            "_crud_case_type_set_member_with_abac",
            abac_handler,
        )
        monkeypatch.setattr(
            crud_case_type_set_member,
            "_crud_case_type_set_member_without_abac",
            without_abac_handler,
        )

        result = crud_case_type_set_member.case_service_crud_case_type_set_member(
            self.service, cmd
        )

        assert result is expected_result
        abac_handler.assert_called_once_with(self.service, self.uow, cmd)
        without_abac_handler.assert_not_called()

    def test_exempt_dispatch_uses_unrestricted_handler(self, monkeypatch) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_SOME)
        self.service.app.pdp.is_exempted.return_value = True
        expected_result = object()
        without_abac_handler = Mock(return_value=expected_result)
        abac_handler = Mock()
        monkeypatch.setattr(
            crud_case_type_set_member,
            "_crud_case_type_set_member_without_abac",
            without_abac_handler,
        )
        monkeypatch.setattr(
            crud_case_type_set_member,
            "_crud_case_type_set_member_with_abac",
            abac_handler,
        )

        result = crud_case_type_set_member.case_service_crud_case_type_set_member(
            self.service, cmd
        )

        assert result is expected_result
        without_abac_handler.assert_called_once_with(self.service, self.uow, cmd)
        abac_handler.assert_not_called()

    def test_restricted_read_filters_by_parent_case_type_set_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_SOME)
        ref_data_access = Mock(is_full_access=False)
        access_filter = object()
        ref_data_access.get_case_type_set_filter.return_value = access_filter
        expected_result = object()
        crud_with_filter = Mock(return_value=expected_result)
        monkeypatch.setattr(
            crud_case_type_set_member,
            "get_ref_data_access_from_command",
            Mock(return_value=ref_data_access),
        )
        monkeypatch.setattr(
            crud_case_type_set_member, "crud_with_access_filter", crud_with_filter
        )

        result = crud_case_type_set_member._crud_case_type_set_member_with_abac(
            self.service, self.uow, cmd
        )

        assert result is expected_result
        ref_data_access.get_case_type_set_filter.assert_called_once_with(
            "case_type_set_id"
        )
        crud_with_filter.assert_called_once_with(
            self.service, self.uow, cmd, access_filter
        )
        self.service.crud.assert_not_called()

    @pytest.mark.parametrize("is_full_access", [None, True])
    def test_unrestricted_or_missing_access_metadata_delegates_crud(
        self, monkeypatch: pytest.MonkeyPatch, is_full_access: bool | None
    ) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_SOME)
        ref_data_access = (
            None if is_full_access is None else Mock(is_full_access=is_full_access)
        )
        expected_result = object()
        self.service.crud.return_value = expected_result
        monkeypatch.setattr(
            crud_case_type_set_member,
            "get_ref_data_access_from_command",
            Mock(return_value=ref_data_access),
        )

        result = crud_case_type_set_member._crud_case_type_set_member_with_abac(
            self.service, self.uow, cmd
        )

        assert result is expected_result
        self.service.crud.assert_called_once_with(cmd)
