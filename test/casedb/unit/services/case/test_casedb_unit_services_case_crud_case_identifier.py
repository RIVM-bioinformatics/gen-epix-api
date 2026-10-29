from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import exc, model
from gen_epix.casedb.domain.enum import CaseRight
from gen_epix.casedb.services.case import crud_case_identifier
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.enum import OnException


class TestCaseIdentifierCrud(BaseCrudTestCase):
    def _configure_read(self, count: int = 2) -> tuple[Mock, list[Mock]]:
        cmd = self.create_crud_command(operation=CrudOperation.READ_SOME)
        cmd.is_read = Mock(return_value=True)
        cmd.is_read_all = Mock(return_value=False)
        cmd.is_delete_all = Mock(return_value=False)
        cmd.is_exists = Mock(return_value=False)
        cmd.is_update = Mock(return_value=False)
        cmd.return_id = False
        identifiers: list[Mock] = []
        cases: list[Mock] = []
        case_data_collections: dict[object, set[object]] = {}
        for _ in range(count):
            case = Mock(spec=model.Case)
            case.id = uuid4()
            case.case_type_id = uuid4()
            case.created_in_data_collection_id = uuid4()
            identifier = Mock(spec=model.CaseIdentifier)
            identifier.id = uuid4()
            identifier.internal_id = case.id
            identifiers.append(identifier)
            cases.append(case)
            case_data_collections[case.id] = {uuid4()}
        self.service.repository.read_fields.return_value = [
            (case.id, case.case_type_id, case.created_in_data_collection_id)
            for case in cases
        ]
        self.service._retrieve_case_data_collections_map = Mock(
            return_value=case_data_collections
        )
        self.service.app.pdp.is_exempted.return_value = False
        self.service.app.pdp.filter_case_ids.return_value = [case.id for case in cases]
        return cmd, identifiers

    @staticmethod
    def _patch_crud(monkeypatch) -> None:
        monkeypatch.setattr(crud_case_identifier, "_crud_cascade_delete", Mock())

    def test_read_some_filters_identifiers_by_case_access(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, identifiers = self._configure_read()
        self._patch_crud(monkeypatch)
        self.service.app.pdp.filter_case_ids.return_value = [identifiers[0].internal_id]
        self.service.crud.return_value = identifiers

        result = crud_case_identifier.case_service_crud_case_identifier(
            self.service, cmd
        )

        assert result == identifiers[:1]
        case_props = self.service.repository.read_fields.return_value
        data_collection_map = (
            self.service._retrieve_case_data_collections_map.return_value
        )
        pdp_call = self.service.app.pdp.filter_case_ids.call_args
        assert pdp_call.args[2] == CaseRight.READ_CASE
        assert pdp_call.kwargs["on_filtered"] == OnException.RAISE
        expected_collections = data_collection_map[case_props[0][0]] | {
            case_props[0][2]
        }
        assert pdp_call.args[1][0][2] == expected_collections

    def test_created_in_collection_is_used_when_case_has_no_link_rows(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, identifiers = self._configure_read(count=1)
        self._patch_crud(monkeypatch)
        self.service._retrieve_case_data_collections_map.return_value = {}
        self.service.crud.return_value = identifiers

        result = crud_case_identifier.case_service_crud_case_identifier(
            self.service, cmd
        )

        assert result == identifiers
        case_id, case_type_id, created_collection_id = (
            self.service.repository.read_fields.return_value[0]
        )
        assert self.service.app.pdp.filter_case_ids.call_args.args[1] == [
            (case_id, case_type_id, frozenset({created_collection_id}))
        ]

    def test_read_one_raises_when_case_is_inaccessible(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, identifiers = self._configure_read(count=1)
        cmd.operation = CrudOperation.READ_ONE
        self._patch_crud(monkeypatch)
        self.service.app.pdp.filter_case_ids.side_effect = exc.UnauthorizedAuthError(
            "dad1bec1", "not authorized"
        )
        self.service.crud.return_value = identifiers[0]

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_identifier.case_service_crud_case_identifier(self.service, cmd)

    def test_read_some_returning_ids_filters_identifier_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, identifiers = self._configure_read()
        cmd.return_id = True
        cmd.model_copy = Mock(return_value=Mock())
        self._patch_crud(monkeypatch)
        self.service.app.pdp.filter_case_ids.return_value = [identifiers[0].internal_id]
        self.service.crud.return_value = identifiers

        result = crud_case_identifier.case_service_crud_case_identifier(
            self.service, cmd
        )

        assert result == [identifiers[0].id]
        assert self.service.crud.call_count == 1
        assert cmd.model_copy.call_args.kwargs["update"] == {"return_id": False}

    def test_read_one_returning_id_preserves_scalar_shape(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, identifiers = self._configure_read(count=1)
        cmd.operation = CrudOperation.READ_ONE
        cmd.return_id = True
        self._patch_crud(monkeypatch)
        self.service.crud.return_value = identifiers[0]

        result = crud_case_identifier.case_service_crud_case_identifier(
            self.service, cmd
        )

        assert result == identifiers[0].id
        assert cmd.model_copy.call_args.kwargs["update"] == {"return_id": False}

    def test_read_some_raises_when_case_is_inaccessible(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, identifiers = self._configure_read()
        self._patch_crud(monkeypatch)
        self.service.app.pdp.filter_case_ids.side_effect = exc.UnauthorizedAuthError(
            "dad1bec1", "not authorized"
        )
        self.service.crud.return_value = identifiers

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_identifier.case_service_crud_case_identifier(self.service, cmd)

        assert (
            self.service.app.pdp.filter_case_ids.call_args.kwargs["on_filtered"]
            == OnException.RAISE
        )

    def test_empty_read_does_not_retrieve_all_case_data_collection_links(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, _ = self._configure_read(count=0)
        self._patch_crud(monkeypatch)
        self.service.crud.return_value = []

        result = crud_case_identifier.case_service_crud_case_identifier(
            self.service, cmd
        )

        assert result == []
        self.service._retrieve_case_data_collections_map.assert_not_called()
        self.service.repository.read_fields.assert_not_called()
        self.service.app.pdp.filter_case_ids.assert_not_called()

    def test_exists_one_authorizes_existing_identifier_and_returns_true(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, identifiers = self._configure_read(count=1)
        identifier_id = identifiers[0].id
        cmd.operation = CrudOperation.EXISTS_ONE
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(return_value=[identifier_id])
        cmd.model_copy = Mock(return_value=Mock())
        self._patch_crud(monkeypatch)
        self.service.crud.return_value = identifiers[0]

        result = crud_case_identifier.case_service_crud_case_identifier(
            self.service, cmd
        )

        assert result is True
        assert cmd.model_copy.call_args.kwargs["update"] == {
            "operation": CrudOperation.READ_SOME,
            "obj_ids": [identifier_id],
            "return_id": False,
        }

    def test_exists_some_returns_flags_in_requested_id_order(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, identifiers = self._configure_read(count=1)
        existing_id = identifiers[0].id
        missing_id = uuid4()
        cmd.operation = CrudOperation.EXISTS_SOME
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(return_value=[existing_id, missing_id])
        cmd.model_copy = Mock(return_value=Mock())
        self._patch_crud(monkeypatch)
        self.service.crud.return_value = identifiers

        result = crud_case_identifier.case_service_crud_case_identifier(
            self.service, cmd
        )

        assert result == [True, False]

    def test_exists_one_returns_false_without_case_lookup_when_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, _ = self._configure_read(count=0)
        cmd.operation = CrudOperation.EXISTS_ONE
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(return_value=[uuid4()])
        cmd.model_copy = Mock(return_value=Mock())
        self._patch_crud(monkeypatch)
        self.service.crud.return_value = []

        result = crud_case_identifier.case_service_crud_case_identifier(
            self.service, cmd
        )

        assert result is False
        self.service.repository.read_fields.assert_not_called()
        self.service.app.pdp.filter_case_ids.assert_not_called()

    def test_exists_one_raises_for_inaccessible_identifier(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, identifiers = self._configure_read(count=1)
        cmd.operation = CrudOperation.EXISTS_ONE
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(return_value=[identifiers[0].id])
        cmd.model_copy = Mock(return_value=Mock())
        self._patch_crud(monkeypatch)
        self.service.crud.return_value = identifiers[0]
        self.service.app.pdp.filter_case_ids.side_effect = exc.UnauthorizedAuthError(
            "dad1bec1", "not authorized"
        )

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_identifier.case_service_crud_case_identifier(self.service, cmd)

    @pytest.mark.parametrize("query_filter", [None, object()])
    def test_read_all_is_rejected(
        self, monkeypatch: pytest.MonkeyPatch, query_filter: object | None
    ) -> None:
        cmd, _ = self._configure_read()
        cmd.operation = CrudOperation.READ_ALL
        cmd.is_read_all.return_value = True
        cmd.query_filter = query_filter
        self._patch_crud(monkeypatch)

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_identifier.case_service_crud_case_identifier(self.service, cmd)

        self.service.crud.assert_not_called()
