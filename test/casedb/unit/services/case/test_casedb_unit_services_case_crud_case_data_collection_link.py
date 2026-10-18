from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import exc, model
from gen_epix.casedb.services.case import crud_case_data_collection_link
from gen_epix.fastapp import CrudOperation


class TestCaseDataCollectionLinkCrud(BaseCrudTestCase):
    def _configure_read(self, count: int = 1) -> tuple[Mock, Mock, list[Mock]]:
        cmd = self.create_crud_command(operation=CrudOperation.READ_SOME)
        cmd.return_id = False
        cmd.is_read = Mock(return_value=True)
        cmd.is_read_all = Mock(return_value=False)
        cmd.is_delete_all = Mock(return_value=False)
        cmd.is_exists = Mock(return_value=False)
        cmd.is_update = Mock(return_value=False)
        links: list[Mock] = []
        cases: list[Mock] = []
        access_by_case_type: dict = {}
        for _ in range(count):
            case = Mock(spec=model.Case)
            case.id = uuid4()
            case.case_type_id = uuid4()
            case.created_in_data_collection_id = uuid4()
            link = Mock(spec=model.CaseDataCollectionLink)
            link.id = uuid4()
            link.case_id = case.id
            link.data_collection_id = uuid4()
            access = Mock(spec=model.CaseTypeAccessAbac)
            access.read_col_ids = {uuid4()}
            links.append(link)
            cases.append(case)
            access_by_case_type[case.case_type_id] = {link.data_collection_id: access}
        self.service.repository.read_fields.return_value = [
            (case.id, case.case_type_id) for case in cases
        ]
        self.service.app.pdp.is_exempted.return_value = False
        case_abac = Mock()
        case_abac.case_type_access_abacs = access_by_case_type
        return cmd, case_abac, links

    @staticmethod
    def _patch_abac(monkeypatch, case_abac: Mock | None) -> None:
        monkeypatch.setattr(
            crud_case_data_collection_link, "_crud_cascade_delete", Mock()
        )
        monkeypatch.setattr(
            crud_case_data_collection_link,
            "get_case_abac_from_command",
            Mock(return_value=case_abac),
        )

    def test_read_checks_case_access_in_linked_collection(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        result = (
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )
        )

        assert result == links
        self.service.repository.read_fields.assert_called_once()
        access = case_abac.case_type_access_abacs[
            self.service.repository.read_fields.return_value[0][1]
        ][links[0].data_collection_id]
        assert access.read_col_ids

    def test_mixed_read_raises_instead_of_returning_inaccessible_link(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read(count=2)
        second_case_type_id = self.service.repository.read_fields.return_value[1][1]
        second_access = case_abac.case_type_access_abacs[second_case_type_id][
            links[1].data_collection_id
        ]
        second_access.read_col_ids = set()
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )

        assert self.service.repository.read_fields.called

    def test_read_raises_when_collection_has_no_case_type_access(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        case_type_id = self.service.repository.read_fields.return_value[0][1]
        case_abac.case_type_access_abacs = {case_type_id: {}}
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )

    def test_read_raises_when_collection_has_no_readable_columns(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        access_abac = Mock(spec=model.CaseTypeAccessAbac)
        access_abac.read_col_ids = set()
        case_type_id = self.service.repository.read_fields.return_value[0][1]
        case_abac.case_type_access_abacs = {
            case_type_id: {links[0].data_collection_id: access_abac}
        }
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )

    def test_read_some_returning_ids_checks_full_link_rows(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        cmd.return_id = True
        reread_cmd = Mock()
        cmd.model_copy = Mock(return_value=reread_cmd)
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        result = (
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )
        )

        assert result == [links[0].id]
        update = cmd.model_copy.call_args.kwargs["update"]
        assert update["return_id"] is False
        assert self.service.crud.call_count == 1
        self.service.repository.read_fields.assert_called_once()

    def test_exists_one_authorizes_existing_link_and_returns_true(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        link_id = (links[0].case_id, links[0].data_collection_id)
        cmd.operation = CrudOperation.EXISTS_ONE
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(return_value=[link_id])
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        result = (
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )
        )

        assert result is True
        update = cmd.model_copy.call_args.kwargs["update"]
        assert update == {
            "operation": CrudOperation.READ_SOME,
            "obj_ids": [link_id],
            "return_id": False,
        }

    def test_exists_some_returns_flags_in_requested_id_order(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        existing_id = (links[0].case_id, links[0].data_collection_id)
        missing_id = (uuid4(), uuid4())
        cmd.operation = CrudOperation.EXISTS_SOME
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(return_value=[existing_id, missing_id])
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        result = (
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )
        )

        assert result == [True, False]

    def test_exists_one_returns_false_without_metadata_lookup_when_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        cmd.operation = CrudOperation.EXISTS_ONE
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(return_value=[(uuid4(), uuid4())])
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = []

        result = (
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )
        )

        assert result is False
        self.service.repository.read_fields.assert_not_called()

    def test_exists_one_raises_for_inaccessible_existing_link(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        case_type_id = self.service.repository.read_fields.return_value[0][1]
        case_abac.case_type_access_abacs[case_type_id][
            links[0].data_collection_id
        ].read_col_ids = set()
        cmd.operation = CrudOperation.EXISTS_ONE
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(
            return_value=[(links[0].case_id, links[0].data_collection_id)]
        )
        cmd.model_copy = Mock(return_value=Mock())
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )

    @pytest.mark.parametrize("query_filter", [None, object()])
    def test_read_all_is_rejected(
        self, monkeypatch: pytest.MonkeyPatch, query_filter: object | None
    ) -> None:
        cmd, case_abac, _ = self._configure_read()
        cmd.operation = CrudOperation.READ_ALL
        cmd.is_read_all.return_value = True
        cmd.query_filter = query_filter
        self._patch_abac(monkeypatch, case_abac)

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )

        self.service.crud.assert_not_called()

    def test_command_without_case_abac_raises_assertion(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, _, links = self._configure_read()
        self._patch_abac(monkeypatch, None)
        self.service.crud.return_value = links

        with pytest.raises(AssertionError, match="Case ABAC metadata is required"):
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )

    def test_exempt_admin_keeps_raw_crud_behavior(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd = self.create_crud_command(operation=CrudOperation.READ_SOME)
        expected = [Mock(spec=model.CaseDataCollectionLink)]
        self.service.app.pdp.is_exempted.return_value = True
        self.service.crud.return_value = expected
        cascade_delete = Mock()
        monkeypatch.setattr(
            crud_case_data_collection_link, "_crud_cascade_delete", cascade_delete
        )
        get_case_abac = Mock()
        monkeypatch.setattr(
            crud_case_data_collection_link, "get_case_abac_from_command", get_case_abac
        )

        result = (
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )
        )

        assert result == expected
        get_case_abac.assert_not_called()
        self.service.repository.crud.assert_not_called()

    @pytest.mark.parametrize(
        "operation",
        [
            CrudOperation.DELETE_ONE,
            CrudOperation.DELETE_SOME,
            CrudOperation.DELETE_ALL,
        ],
    )
    def test_delete_operations_are_rejected(
        self, monkeypatch: pytest.MonkeyPatch, operation: CrudOperation
    ) -> None:
        cmd = self.create_crud_command(operation=operation)
        self.service.app.pdp.is_exempted.return_value = False
        monkeypatch.setattr(
            crud_case_data_collection_link, "_crud_cascade_delete", Mock()
        )

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_data_collection_link.case_service_crud_case_data_collection_link(
                self.service, cmd
            )

        self.service.crud.assert_not_called()
