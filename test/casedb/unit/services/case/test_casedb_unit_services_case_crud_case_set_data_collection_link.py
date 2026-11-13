from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import exc, model
from gen_epix.casedb.services.case import crud_case_set_data_collection_link
from gen_epix.fastapp import CrudOperation
from gen_epix.filter import CompositeFilter, LogicalOperator, UuidSetFilter


class TestCaseSetDataCollectionLinkCrud(BaseCrudTestCase):
    def _configure_read(self, count: int = 1) -> tuple[Mock, Mock, list[Mock]]:
        cmd = self.create_crud_command(operation=CrudOperation.READ_SOME)
        cmd.return_id = False
        cmd.is_read = Mock(return_value=True)
        cmd.is_read_all = Mock(return_value=False)
        cmd.is_delete_all = Mock(return_value=False)
        cmd.is_exists = Mock(return_value=False)
        cmd.is_update = Mock(return_value=False)
        case_sets: list[Mock] = []
        links: list[Mock] = []
        access_by_case_type: dict = {}
        for _ in range(count):
            case_set = Mock(spec=model.CaseSet)
            case_set.id = uuid4()
            case_set.case_type_id = uuid4()
            case_set.created_in_data_collection_id = uuid4()
            link = Mock(spec=model.CaseSetDataCollectionLink)
            link.case_set_id = case_set.id
            link.data_collection_id = uuid4()
            case_sets.append(case_set)
            links.append(link)
            access = Mock(spec=model.CaseTypeAccessAbac)
            access.read_case_set = True
            access_by_case_type[case_set.case_type_id] = {
                link.data_collection_id: access
            }
        self.service.repository.read_fields.return_value = [
            (case_set.id, case_set.case_type_id) for case_set in case_sets
        ]
        self.service.app.pdp.is_exempted.return_value = False
        case_abac = Mock()
        case_abac.case_type_access_abacs = access_by_case_type
        return cmd, case_abac, links

    @staticmethod
    def _patch_abac(monkeypatch, case_abac: Mock | None) -> None:
        monkeypatch.setattr(
            crud_case_set_data_collection_link, "_crud_cascade_delete", Mock()
        )
        monkeypatch.setattr(
            crud_case_set_data_collection_link,
            "get_case_abac_from_command",
            Mock(return_value=case_abac),
        )

    def test_read_checks_case_set_access_in_linked_collection(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        result = crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
            self.service, cmd
        )

        assert result == links
        self.service.repository.read_fields.assert_called_once()
        access = case_abac.case_type_access_abacs[
            self.service.repository.read_fields.return_value[0][1]
        ][links[0].data_collection_id]
        assert access.read_case_set

    def test_mixed_read_raises_when_any_link_is_inaccessible(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read(count=2)
        second_access = case_abac.case_type_access_abacs[
            self.service.repository.read_fields.return_value[1][1]
        ][links[1].data_collection_id]
        second_access.read_case_set = False
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
                self.service, cmd
            )

        assert self.service.repository.read_fields.called

    def test_read_raises_when_collection_has_no_case_set_access(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        case_abac.case_type_access_abacs = {}
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
                self.service, cmd
            )

    def test_read_some_returning_ids_checks_link_rows(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        cmd.return_id = True
        reread_cmd = Mock()
        cmd.model_copy = Mock(return_value=reread_cmd)
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        result = crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
            self.service, cmd
        )

        assert result == [(links[0].case_set_id, links[0].data_collection_id)]
        assert self.service.crud.call_count == 1
        assert cmd.model_copy.call_args.kwargs["update"] == {"return_id": False}

    def test_command_without_case_abac_raises_assertion(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, _, links = self._configure_read()
        self._patch_abac(monkeypatch, None)
        self.service.crud.return_value = links

        with pytest.raises(AssertionError, match="Case ABAC metadata is required"):
            crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
                self.service, cmd
            )

    def test_empty_read_does_not_read_case_set_metadata(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, _ = self._configure_read()
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = []

        result = crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
            self.service, cmd
        )

        assert result == []
        self.service.repository.read_fields.assert_not_called()

    def test_exists_one_authorizes_existing_link_and_returns_true(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        link_id = (links[0].case_set_id, links[0].data_collection_id)
        cmd.operation = CrudOperation.EXISTS_ONE
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(return_value=[link_id])
        cmd.model_copy = Mock(return_value=Mock())
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        result = crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
            self.service, cmd
        )

        assert result is True
        assert cmd.model_copy.call_args.kwargs["update"] == {
            "operation": CrudOperation.READ_SOME,
            "obj_ids": [link_id],
            "return_id": False,
        }

    def test_exists_some_returns_flags_in_requested_id_order(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, links = self._configure_read()
        existing_id = (links[0].case_set_id, links[0].data_collection_id)
        missing_id = (uuid4(), uuid4())
        cmd.operation = CrudOperation.EXISTS_SOME
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(return_value=[existing_id, missing_id])
        cmd.model_copy = Mock(return_value=Mock())
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        result = crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
            self.service, cmd
        )

        assert result == [True, False]

    def test_exists_one_returns_false_without_metadata_lookup_when_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, _ = self._configure_read()
        cmd.operation = CrudOperation.EXISTS_ONE
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(return_value=[(uuid4(), uuid4())])
        cmd.model_copy = Mock(return_value=Mock())
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = []

        result = crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
            self.service, cmd
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
        ].read_case_set = False
        cmd.operation = CrudOperation.EXISTS_ONE
        cmd.is_exists.return_value = True
        cmd.get_obj_ids = Mock(
            return_value=[(links[0].case_set_id, links[0].data_collection_id)]
        )
        cmd.model_copy = Mock(return_value=Mock())
        self._patch_abac(monkeypatch, case_abac)
        self.service.crud.return_value = links

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
                self.service, cmd
            )

    @pytest.mark.parametrize(
        "query_filter",
        [
            None,
            object(),
            CompositeFilter(
                filters=[
                    UuidSetFilter(key="case_set_id", members={uuid4()}),
                    UuidSetFilter(key="data_collection_id", members={uuid4()}),
                ],
                operator=LogicalOperator.OR,
            ),
        ],
    )
    def test_read_all_is_rejected(
        self, monkeypatch: pytest.MonkeyPatch, query_filter: object | None
    ) -> None:
        cmd, case_abac, _ = self._configure_read()
        cmd.operation = CrudOperation.READ_ALL
        cmd.is_read_all.return_value = True
        cmd.query_filter = query_filter
        self._patch_abac(monkeypatch, case_abac)

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
                self.service, cmd
            )

        self.service.crud.assert_not_called()

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
        if operation == CrudOperation.DELETE_ALL:
            cmd.query_filter = object()
        self.service.app.pdp.is_exempted.return_value = False
        monkeypatch.setattr(
            crud_case_set_data_collection_link, "_crud_cascade_delete", Mock()
        )

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
                self.service, cmd
            )

        self.service.crud.assert_not_called()

    @pytest.mark.parametrize("read_access", [False, True])
    @pytest.mark.parametrize("composite", [False, True])
    def test_bounded_query_checks_link_access(
        self, monkeypatch, read_access, composite
    ):
        cmd, abac, links = self._configure_read()
        cmd.operation = CrudOperation.READ_ALL
        cmd.is_read_all.return_value = True
        cmd.query_filter = UuidSetFilter(
            key="case_set_id", members={links[0].case_set_id}
        )
        if composite:
            cmd.query_filter = CompositeFilter(
                filters=[cmd.query_filter, UuidSetFilter(key="id", members={uuid4()})],
                operator=LogicalOperator.AND,
            )
        access = next(iter(next(iter(abac.case_type_access_abacs.values())).values()))
        access.read_case_set = read_access
        self._patch_abac(monkeypatch, abac)
        self.service.crud.return_value = links
        if read_access:
            assert (
                crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
                    self.service, cmd
                )
                == links
            )
        else:
            with pytest.raises(exc.UnauthorizedAuthError):
                crud_case_set_data_collection_link.case_service_crud_case_set_data_collection_link(
                    self.service, cmd
                )
