from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import command, exc, model
from gen_epix.casedb.domain.enum import CaseRight
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.domain.service.abac import BaseAbacService
from gen_epix.casedb.services.case import crud_case_set_member
from gen_epix.fastapp import CrudOperation
from gen_epix.filter import CompositeFilter, LogicalOperator, UuidSetFilter


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

    @pytest.mark.parametrize(
        "operation", [CrudOperation.EXISTS_ONE, CrudOperation.EXISTS_SOME]
    )
    @pytest.mark.parametrize(
        "access", ["allowed", "case_denied", "set_denied", "missing"]
    )
    def test_exists_respects_parent_access_and_missing_ids(
        self, monkeypatch, operation, access
    ):
        _, abac, members, _, _ = self._configure_read()
        member = members[0]
        missing_id = uuid4()
        requested = (
            [member.id, missing_id, member.id]
            if operation == CrudOperation.EXISTS_SOME
            else [member.id]
        )
        cmd = command.CaseSetMemberCrudCommand(
            user=self.user,
            operation=operation,
            obj_ids=(
                requested if operation == CrudOperation.EXISTS_SOME else requested[0]
            ),
        )
        self._patch_case_abac(monkeypatch, abac)
        abac.is_allowed.side_effect = {
            "allowed": [True, True],
            "case_denied": [False],
            "set_denied": [True, False],
        }.get(access, [])
        self.service.crud.return_value = [] if access == "missing" else members

        result = crud_case_set_member.case_service_crud_case_set_member(
            self.service, cmd
        )

        expected = access == "allowed"
        assert result == (
            expected
            if operation == CrudOperation.EXISTS_ONE
            else [expected, False, expected]
        )
        read_cmd = self.service.crud.call_args.args[0]
        assert read_cmd.operation == CrudOperation.READ_ALL
        assert read_cmd.obj_ids is None
        assert read_cmd.query_filter.key == "id"
        assert read_cmd.query_filter.members == set(requested)

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

    def test_command_without_case_abac_is_rejected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, _, members, _, _ = self._configure_read()
        self._patch_case_abac(monkeypatch, None)
        self.service.crud.return_value = members

        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_member._crud_case_set_member_with_abac(
                self.service, self.uow, cmd
            )
        self.service.crud.assert_not_called()

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

    @pytest.mark.parametrize("key", ["case_id", "case_set_id"])
    @pytest.mark.parametrize(
        "decisions,expected_count",
        [([True, True], 1), ([False], 0), ([True, False], 0)],
    )
    def test_bounded_query_preserves_parent_access_checks(
        self, monkeypatch, key, decisions, expected_count
    ):
        cmd, abac, members, _, _ = self._configure_read()
        cmd.operation = CrudOperation.READ_ALL
        cmd.is_read_all.return_value = True
        cmd.query_filter = UuidSetFilter(key=key, members={uuid4()})
        abac.is_allowed.side_effect = decisions
        self._patch_case_abac(monkeypatch, abac)
        self.service.crud.return_value = members
        result = crud_case_set_member.case_service_crud_case_set_member(
            self.service, cmd
        )
        assert result == members[:expected_count]

    @pytest.mark.parametrize(
        "query_filter",
        [
            pytest.param(
                # Exact filter sent by the UI when removing cases from an event
                CompositeFilter.model_validate(
                    {
                        "filters": [
                            {
                                "invert": False,
                                "key": "case_id",
                                "members": [str(uuid4())],
                                "type": "UUID_SET",
                            },
                            {
                                "invert": False,
                                "key": "case_set_id",
                                "members": [str(uuid4())],
                                "type": "UUID_SET",
                            },
                        ],
                        "operator": "AND",
                        "type": "COMPOSITE",
                    }
                ),
                id="and-case-and-case-set",
            ),
            pytest.param(
                CompositeFilter(
                    filters=[
                        UuidSetFilter(key="case_set_id", members={uuid4()}),
                        UuidSetFilter(key="id", members={uuid4()}),
                    ],
                    operator=LogicalOperator.AND,
                ),
                id="and-one-bounded-child",
            ),
            pytest.param(
                CompositeFilter(
                    filters=[
                        UuidSetFilter(key="case_id", members={uuid4()}),
                        UuidSetFilter(key="case_set_id", members={uuid4()}),
                    ],
                    operator=LogicalOperator.OR,
                ),
                id="or-all-children-bounded",
            ),
        ],
    )
    def test_bounded_composite_query_preserves_parent_access_checks(
        self, monkeypatch, query_filter
    ):
        cmd, abac, members, _, _ = self._configure_read()
        cmd.operation = CrudOperation.READ_ALL
        cmd.is_read_all.return_value = True
        cmd.query_filter = query_filter
        abac.is_allowed.side_effect = [True, True]
        self._patch_case_abac(monkeypatch, abac)
        self.service.crud.return_value = members
        result = crud_case_set_member.case_service_crud_case_set_member(
            self.service, cmd
        )
        assert result == members
        assert abac.is_allowed.call_count == 2

    @pytest.mark.parametrize(
        "query_filter",
        [
            pytest.param(
                CompositeFilter(
                    filters=[
                        UuidSetFilter(key="case_id", members={uuid4()}),
                        UuidSetFilter(key="id", members={uuid4()}),
                    ],
                    operator=LogicalOperator.OR,
                ),
                id="or-with-unbounded-child",
            ),
            pytest.param(
                CompositeFilter(
                    filters=[
                        UuidSetFilter(key="id", members={uuid4()}),
                        UuidSetFilter(key="case_id", invert=True, members={uuid4()}),
                    ],
                    operator=LogicalOperator.AND,
                ),
                id="and-without-bounded-child",
            ),
            pytest.param(
                CompositeFilter(
                    filters=[UuidSetFilter(key="case_id", members={uuid4()})],
                    operator=LogicalOperator.AND,
                    invert=True,
                ),
                id="inverted-and",
            ),
            pytest.param(
                CompositeFilter(
                    filters=[UuidSetFilter(key="case_id", members={uuid4()})],
                    operator=LogicalOperator.NOT,
                ),
                id="not",
            ),
            pytest.param(
                CompositeFilter(
                    filters=[
                        UuidSetFilter(key="case_id", members={uuid4()}),
                        UuidSetFilter(key="case_set_id", members={uuid4()}),
                    ],
                    operator=LogicalOperator.XOR,
                ),
                id="xor",
            ),
        ],
    )
    def test_unbounded_composite_query_still_rejected(self, monkeypatch, query_filter):
        cmd, abac, _, _, _ = self._configure_read()
        cmd.is_read_all.return_value = True
        cmd.query_filter = query_filter
        self._patch_case_abac(monkeypatch, abac)
        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_member.case_service_crud_case_set_member(self.service, cmd)
        self.service.crud.assert_not_called()

    @pytest.mark.parametrize("key,invert", [("id", False), ("case_id", True)])
    def test_unbounded_query_still_rejected(self, monkeypatch, key, invert):
        cmd, abac, _, _, _ = self._configure_read()
        cmd.is_read_all.return_value = True
        cmd.query_filter = UuidSetFilter(key=key, invert=invert, members={uuid4()})
        self._patch_case_abac(monkeypatch, abac)
        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_member.case_service_crud_case_set_member(self.service, cmd)
        self.service.crud.assert_not_called()

    @pytest.mark.parametrize(
        "decisions,allowed",
        [([True, True], True), ([False], False), ([True, False], False)],
    )
    def test_create_requires_readable_case_and_writable_set_before_persisting(
        self, monkeypatch, decisions, allowed
    ):
        cmd, abac, members, _, _ = self._configure_read()
        members[0].id = None
        cmd.operation = CrudOperation.CREATE_SOME
        cmd.is_create.return_value = True
        cmd.is_read.return_value = False
        cmd.get_objs.return_value = members
        abac.is_allowed.side_effect = decisions
        self._patch_case_abac(monkeypatch, abac)
        self.service.crud.return_value = members
        if allowed:
            assert (
                crud_case_set_member.case_service_crud_case_set_member(
                    self.service, cmd
                )
                == members
            )
            self.service.crud.assert_called_once_with(cmd)
            assert abac.is_allowed.call_args_list[1].args[2] == CaseRight.WRITE_CASE_SET
            self.service._verify_case_set_member_case_type.assert_called_once_with(
                cmd.user, members
            )
        else:
            with pytest.raises(exc.UnauthorizedAuthError):
                crud_case_set_member.case_service_crud_case_set_member(
                    self.service, cmd
                )
            self.service.crud.assert_not_called()
            self.service._verify_case_set_member_case_type.assert_not_called()

    def test_authorized_create_validates_case_type_before_persisting(self, monkeypatch):
        cmd, abac, members, _, _ = self._configure_read()
        cmd.operation = CrudOperation.CREATE_SOME
        cmd.is_create.return_value = True
        cmd.is_read.return_value = False
        cmd.get_objs.return_value = members
        abac.is_allowed.return_value = True
        self._patch_case_abac(monkeypatch, abac)
        self.service._verify_case_set_member_case_type.side_effect = (
            exc.InvalidArgumentsError("3e11edd5", "Different case type")
        )

        with pytest.raises(exc.InvalidArgumentsError):
            crud_case_set_member.case_service_crud_case_set_member(self.service, cmd)

        self.service.crud.assert_not_called()

    @pytest.mark.parametrize("shared", [False, True])
    def test_real_query_command_and_abac_resolve_shared_private_origin_data(
        self, shared
    ):
        _, _, members, cases, case_sets = self._configure_read()
        case_type_id = cases[0].case_type_id
        case_sets[0].case_type_id = case_type_id
        national_id = uuid4()
        access = model.CaseTypeAccessAbac(
            case_type_id=case_type_id,
            data_collection_id=national_id,
            is_private=False,
            add_case=False,
            remove_case=False,
            add_case_set=False,
            remove_case_set=False,
            read_col_ids={uuid4()},
            write_col_ids=set(),
            read_case_set=True,
            write_case_set=False,
        )
        abac = model.CaseAbac(
            is_full_access=False,
            case_type_access_abacs={case_type_id: {national_id: access}},
            case_type_share_abacs={},
        )
        cmd = command.CaseSetMemberCrudCommand(
            user=self.user,
            operation=CrudOperation.READ_ALL,
            query_filter=UuidSetFilter(key="case_id", members={cases[0].id}),
        )
        assert type(cmd) in BaseAbacService.CASE_ABAC_COMMANDS
        abac_service = Mock()
        abac_service.get_case_abac.return_value = abac
        cmd._policies.append(BaseCaseAbacPolicy(abac_service))
        self.service.crud.return_value = members
        self.service._retrieve_case_data_collections_map.return_value = {
            cases[0].id: {national_id} if shared else set()
        }
        self.service._retrieve_case_set_data_collections_map.return_value = {
            case_sets[0].id: {national_id}
        }
        assert crud_case_set_member.case_service_crud_case_set_member(
            self.service, cmd
        ) == (members if shared else [])

    def test_mixed_create_batch_is_rejected_before_any_member_is_written(
        self, monkeypatch
    ):
        cmd, abac, members, _, _ = self._configure_read(count=2)
        cmd.operation = CrudOperation.CREATE_SOME
        cmd.is_create.return_value = True
        cmd.is_read.return_value = False
        cmd.get_objs.return_value = members
        abac.is_allowed.side_effect = [True, True, True, False]
        self._patch_case_abac(monkeypatch, abac)
        with pytest.raises(exc.UnauthorizedAuthError):
            crud_case_set_member.case_service_crud_case_set_member(self.service, cmd)
        self.service.crud.assert_not_called()
        self.service._verify_case_set_member_case_type.assert_not_called()
