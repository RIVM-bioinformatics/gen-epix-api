from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import exc, model
from gen_epix.casedb.domain.enum import CaseRight
from gen_epix.casedb.services.case import crud_case_set_member
from gen_epix.fastapp import CrudOperation
from gen_epix.filter import CompositeFilter, LogicalOperator
from gen_epix.filter.uuid_set import UuidSetFilter


class TestCaseSetMemberCrud(BaseCrudTestCase):
    def _configure_read(
        self, count: int = 1, return_id: bool = False
    ) -> tuple[Mock, Mock, list[Mock], list[Mock], list[Mock]]:
        cmd = self.create_crud_command(
            operation=CrudOperation.READ_SOME,
            query_filter=object(),
        )
        cmd.return_id = return_id
        cmd.is_read = Mock(return_value=True)
        cmd.is_read_all = Mock(return_value=False)
        cmd.is_delete_all = Mock(return_value=False)
        cmd.is_update = Mock(return_value=False)
        case_abac = Mock()
        members: list[Mock] = []
        cases: list[Mock] = []
        case_sets: list[Mock] = []
        for _ in range(count):
            case = Mock(spec=model.Case)
            case.id = uuid4()
            case.case_type_id = uuid4()
            case.created_in_data_collection_id = uuid4()
            case_set = Mock(spec=model.CaseSet)
            case_set.id = uuid4()
            case_set.case_type_id = uuid4()
            case_set.created_in_data_collection_id = uuid4()
            member = Mock(spec=model.CaseSetMember)
            member.id = uuid4()
            member.case_id = case.id
            member.case_set_id = case_set.id
            members.append(member)
            cases.append(case)
            case_sets.append(case_set)
        self.service.repository.crud.side_effect = [cases, case_sets]
        self.service._retrieve_case_data_collections_map.return_value = {}
        self.service._retrieve_case_set_data_collections_map.return_value = {}
        self.service.app.pdp.is_exempted.return_value = False
        return cmd, case_abac, members, cases, case_sets

    @staticmethod
    def _patch_case_abac(monkeypatch, case_abac: Mock | None) -> None:
        monkeypatch.setattr(
            crud_case_set_member,
            "get_case_abac_from_command",
            Mock(return_value=case_abac),
        )

    def test_read_filters_member_unless_both_parents_are_readable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, members, cases, case_sets = self._configure_read(count=3)
        case_abac.is_allowed.side_effect = [True, True, True, False, False]
        self._patch_case_abac(monkeypatch, case_abac)
        self.service.crud.return_value = members
        case_collection_ids = {uuid4()}
        case_set_collection_ids = {uuid4()}
        self.service._retrieve_case_data_collections_map.return_value = {
            cases[0].id: case_collection_ids
        }
        self.service._retrieve_case_set_data_collections_map.return_value = {
            case_sets[0].id: case_set_collection_ids
        }

        result = crud_case_set_member.case_service_crud_case_set_member(
            self.service, cmd
        )

        assert result == [members[0]]
        assert case_abac.is_allowed.call_count == 5
        assert case_abac.is_allowed.call_args_list[0].args == (
            cases[0].case_type_id,
            cases[0].created_in_data_collection_id,
            CaseRight.READ_CASE,
        )
        assert case_abac.is_allowed.call_args_list[0].kwargs[
            "current_data_collection_ids"
        ] == case_collection_ids | {cases[0].created_in_data_collection_id}
        assert case_abac.is_allowed.call_args_list[1].args == (
            case_sets[0].case_type_id,
            case_sets[0].created_in_data_collection_id,
            CaseRight.READ_CASE_SET,
        )
        assert case_abac.is_allowed.call_args_list[1].kwargs[
            "current_data_collection_ids"
        ] == case_set_collection_ids | {case_sets[0].created_in_data_collection_id}

    def test_filtered_id_read_reloads_uuid_ids_and_filters_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, members, cases, case_sets = self._configure_read(
            count=2, return_id=True
        )
        member_ids = [member.id for member in members]
        reload_cmd = Mock()
        cmd.model_copy = Mock(return_value=reload_cmd)
        case_abac.is_allowed.side_effect = [False, True, True]
        self._patch_case_abac(monkeypatch, case_abac)
        self.service.crud.side_effect = [member_ids, members]
        self.service.repository.crud.side_effect = [cases, case_sets]

        result = crud_case_set_member._crud_case_set_member_with_abac(
            self.service, self.uow, cmd
        )

        assert result == [member_ids[1]]
        assert cmd.model_copy.call_args.kwargs["update"]["obj_ids"] == member_ids
        assert self.service.crud.call_count == 2

    def test_unfiltered_bulk_read_is_rejected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, _, _, _ = self._configure_read()
        cmd.query_filter = None
        cmd.operation = CrudOperation.READ_ALL
        cmd.is_read_all.return_value = True
        self._patch_case_abac(monkeypatch, case_abac)

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_member._crud_case_set_member_with_abac(
                self.service, self.uow, cmd
            )

        self.service.crud.assert_not_called()

    def test_filtered_bulk_read_by_case_ids_is_allowed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, members, _, _ = self._configure_read()
        cmd.operation = CrudOperation.READ_ALL
        cmd.query_filter = UuidSetFilter(
            key="case_id",
            members=frozenset({str(uuid4()), str(uuid4())}),
        )
        cmd.is_read_all.return_value = True
        self._patch_case_abac(monkeypatch, case_abac)
        self.service.crud.return_value = members

        result = crud_case_set_member._crud_case_set_member_with_abac(
            self.service, self.uow, cmd
        )

        assert result == members
        self.service.crud.assert_called_once_with(cmd)

    def test_filtered_bulk_read_by_case_set_and_case_ids_is_allowed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, members, _, _ = self._configure_read()
        cmd.operation = CrudOperation.READ_ALL
        cmd.query_filter = CompositeFilter(
            filters=[
                UuidSetFilter(key="case_id", members=frozenset({str(uuid4())})),
                UuidSetFilter(
                    key="case_set_id",
                    members=frozenset({str(uuid4())}),
                ),
            ],
            operator=LogicalOperator.AND,
        )
        cmd.is_read_all.return_value = True
        self._patch_case_abac(monkeypatch, case_abac)
        self.service.crud.return_value = members

        result = crud_case_set_member._crud_case_set_member_with_abac(
            self.service, self.uow, cmd
        )

        assert result == members
        self.service.crud.assert_called_once_with(cmd)

    def test_inverted_case_id_filter_is_not_an_allowed_bulk_read(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, case_abac, _, _, _ = self._configure_read()
        cmd.operation = CrudOperation.READ_ALL
        cmd.query_filter = UuidSetFilter(
            key="case_id",
            members=frozenset({str(uuid4())}),
            invert=True,
        )
        cmd.is_read_all.return_value = True
        self._patch_case_abac(monkeypatch, case_abac)

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_member._crud_case_set_member_with_abac(
                self.service, self.uow, cmd
            )

        self.service.crud.assert_not_called()

    def test_command_without_case_abac_keeps_crud_behavior(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, _, members, _, _ = self._configure_read()
        self._patch_case_abac(monkeypatch, None)
        self.service.crud.return_value = members

        result = crud_case_set_member._crud_case_set_member_with_abac(
            self.service, self.uow, cmd
        )

        assert result == members
        self.service.repository.crud.assert_not_called()

    @pytest.mark.parametrize(
        ("access_decisions", "is_accessible"),
        [
            pytest.param([True, True], True, id="both-parents-readable"),
            pytest.param([False], False, id="case-unreadable"),
            pytest.param([True, False], False, id="case-set-unreadable"),
        ],
    )
    def test_scalar_read_returns_member_only_when_both_parents_are_readable(
        self,
        monkeypatch: pytest.MonkeyPatch,
        access_decisions: list[bool],
        is_accessible: bool,
    ) -> None:
        cmd, case_abac, members, _, _ = self._configure_read()
        cmd.operation = CrudOperation.READ_ONE
        cmd.query_filter = None
        cmd.is_read_all.return_value = False
        case_abac.is_allowed.side_effect = access_decisions
        self._patch_case_abac(monkeypatch, case_abac)
        self.service.crud.return_value = members[0]

        result = crud_case_set_member._crud_case_set_member_with_abac(
            self.service, self.uow, cmd
        )

        assert result is (members[0] if is_accessible else None)

    def test_exempt_dispatch_preserves_admin_crud_behavior(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, _, members, _, _ = self._configure_read()
        self.service.app.pdp.is_exempted.return_value = True
        self.service.crud.return_value = members
        get_case_abac = Mock()
        monkeypatch.setattr(
            crud_case_set_member, "get_case_abac_from_command", get_case_abac
        )

        result = crud_case_set_member.case_service_crud_case_set_member(
            self.service, cmd
        )

        assert result == members
        get_case_abac.assert_not_called()
