"""
Unit tests for casedb CRUD common utilities.

The tests follow the structure, naming, mocking strategy, typing,
and layout conventions of the reference test file in commondb.
"""

from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.services.case import crud_common
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.commondb.domain.enum import RoleSet as CommonRoleSet
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import CompositeFilter, EqualsStringFilter, Filter, LogicalOperator


class DummyCmd:
    """Minimal dummy command object for testing purposes."""

    def __init__(
        self,
        model_class: type,
        operation: CrudOperation,
        user_id: UUID,
        access_filter: Filter | None = None,
        obj_ids: set[UUID] | None = None,
    ) -> None:
        self.MODEL_CLASS = model_class
        self.operation = operation
        self.user = Mock()
        self.user.id = user_id
        self.access_filter = access_filter
        self._obj_ids = obj_ids

    def get_obj_ids(self, as_set: bool = False) -> set[UUID] | None:
        return self._obj_ids if as_set else (self._obj_ids or set())


class DummyEntity:
    def __init__(self, links: dict[str, object]) -> None:
        self.links = links


class DummyLink:
    def __init__(self, link_model_class: type, link_field_name: str) -> None:
        self.link_model_class = link_model_class
        self.link_field_name = link_field_name


def create_service_mock() -> Mock:
    """Create a BaseCaseService mock with repository and helpers."""
    service: Mock = Mock(spec=BaseCaseService)
    service.repository = Mock()
    service.repository.crud = Mock(return_value=[])
    service._compose_id_filter = Mock(
        side_effect=lambda key_and_ids: EqualsStringFilter(
            key=key_and_ids[0][0], value=""
        )
    )
    service.CASCADE_DELETE_MODEL_CLASSES = {}
    service.crud = Mock(return_value=["ok"])  # type: ignore[assignment]
    return service


def create_uow_mock() -> Mock:
    """Create a BaseUnitOfWork mock with context manager support."""
    uow: Mock = Mock(spec=BaseUnitOfWork)
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestGetCaseAbacFromCommand(TestCase):
    """Tests for get_case_abac_from_command."""

    def test_returns_policy_value(self) -> None:
        # 1. Input
        cmd: Mock = Mock()

        # 2. Mocks
        expected: object = object()
        with patch(
            "gen_epix.casedb.services.case.crud_common.BaseCaseAbacPolicy.get_case_abac_from_command",
            return_value=expected,
        ) as fun:
            # 3. Execute
            retval: object | None = crud_common.get_case_abac_from_command(cmd)

            # 4. Verify
            self.assertIs(retval, expected)
            fun.assert_called_once_with(cmd)

    def test_returns_none(self) -> None:
        # 1. Input
        cmd: Mock = Mock()

        # 2. Mocks
        with patch(
            "gen_epix.casedb.services.case.crud_common.BaseCaseAbacPolicy.get_case_abac_from_command",
            return_value=None,
        ) as fun:
            # 3. Execute
            retval: object | None = crud_common.get_case_abac_from_command(cmd)

            # 4. Verify
            self.assertIsNone(retval)
            fun.assert_called_once_with(cmd)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRoleChecks(TestCase):
    """Tests for role-based checks."""

    def setUp(self) -> None:
        self.service = create_service_mock()
        # Provide role_set_map with string values to match user roles for intersection logic
        self.service.role_set_map = {
            CommonRoleSet.GE_REFDATA_ADMIN: {
                "ROOT",
                "COMMONDB_APP_ADMIN",
                "COMMONDB_REFDATA_ADMIN",
            },
            CommonRoleSet.GE_APP_ADMIN: {"ROOT", "COMMONDB_APP_ADMIN"},
        }

    def test_is_metadata_admin_or_above_true(self) -> None:
        # 1. Input
        user: Mock = Mock()
        user.roles = {"COMMONDB_REFDATA_ADMIN"}

        # 2. Mocks: already set in setUp

        # 3. Execute
        retval: bool = crud_common.is_metadata_admin_or_above(self.service, user)

        # 4. Verify
        self.assertTrue(retval)

    def test_is_metadata_admin_or_above_false(self) -> None:
        # 1. Input
        user: Mock = Mock()
        user.roles = {"COMMONDB_ORG_USER"}

        # 2. Mocks: already set in setUp

        # 3. Execute
        retval: bool = crud_common.is_metadata_admin_or_above(self.service, user)

        # 4. Verify
        self.assertFalse(retval)

    def test_is_app_admin_or_above_true(self) -> None:
        # 1. Input
        user: Mock = Mock()
        user.roles = {"COMMONDB_APP_ADMIN"}

        # 2. Mocks: already set in setUp

        # 3. Execute
        retval: bool = crud_common.is_app_admin_or_above(self.service, user)

        # 4. Verify
        self.assertTrue(retval)

    def test_is_app_admin_or_above_false(self) -> None:
        # 1. Input
        user: Mock = Mock()
        user.roles = {"COMMONDB_ORG_USER"}

        # 2. Execute
        retval: bool = crud_common.is_app_admin_or_above(self.service, user)

        # 3. Verify
        self.assertFalse(retval)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestCommandCategoryChecks(TestCase):
    """Tests for command type categorization helpers."""

    class NoAbacCmd:
        pass

    class MetaCmd:
        pass

    class DataCmd:
        pass

    class OtherCmd:
        pass

    def test_is_no_abac_command_true_false(self) -> None:
        # 1. Input
        no_abac_cmd: TestCommandCategoryChecks.NoAbacCmd = (
            TestCommandCategoryChecks.NoAbacCmd()
        )
        other_cmd: TestCommandCategoryChecks.OtherCmd = (
            TestCommandCategoryChecks.OtherCmd()
        )

        # 2. Mocks
        with patch(
            "gen_epix.casedb.services.case.crud_common.DomainBaseCaseService.NO_ABAC_COMMAND_CLASSES",
            new={TestCommandCategoryChecks.NoAbacCmd},
        ):
            # 3. Execute + Verify
            self.assertTrue(crud_common.is_no_abac_command(no_abac_cmd))  # type: ignore[arg-type]
            self.assertFalse(crud_common.is_no_abac_command(other_cmd))  # type: ignore[arg-type]

    def test_is_metadata_command_true_false(self) -> None:
        # 1. Input
        meta_cmd: TestCommandCategoryChecks.MetaCmd = (
            TestCommandCategoryChecks.MetaCmd()
        )
        other_cmd: TestCommandCategoryChecks.OtherCmd = (
            TestCommandCategoryChecks.OtherCmd()
        )

        # 2. Mocks
        with patch(
            "gen_epix.casedb.services.case.crud_common.DomainBaseCaseService.ABAC_METADATA_COMMAND_CLASSES",
            new={TestCommandCategoryChecks.MetaCmd},
        ):
            # 3. Execute + Verify
            self.assertTrue(crud_common.is_metadata_command(meta_cmd))  # type: ignore[arg-type]
            self.assertFalse(crud_common.is_metadata_command(other_cmd))  # type: ignore[arg-type]

    def test_is_data_command_true_false(self) -> None:
        # 1. Input
        data_cmd: TestCommandCategoryChecks.DataCmd = (
            TestCommandCategoryChecks.DataCmd()
        )
        other_cmd: TestCommandCategoryChecks.OtherCmd = (
            TestCommandCategoryChecks.OtherCmd()
        )

        # 2. Mocks
        with patch(
            "gen_epix.casedb.services.case.crud_common.DomainBaseCaseService.ABAC_DATA_COMMAND_CLASSES",
            new={TestCommandCategoryChecks.DataCmd},
        ):
            # 3. Execute + Verify
            self.assertTrue(crud_common.is_data_command(data_cmd))  # type: ignore[arg-type]
            self.assertFalse(crud_common.is_data_command(other_cmd))  # type: ignore[arg-type]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestCrudWithAccessFilter(TestCase):
    """Tests for crud_with_access_filter including cascade delete behavior."""

    def setUp(self) -> None:
        self.service = create_service_mock()
        self.uow = create_uow_mock()
        self.user_id = uuid4()

    def test_sets_composite_filter_and_restores_original(self) -> None:
        # 1. Input
        orig_filter: EqualsStringFilter = EqualsStringFilter(key="k1", value="v1")
        extra_filter: EqualsStringFilter = EqualsStringFilter(key="k2", value="v2")
        cmd: DummyCmd = DummyCmd(
            model_class=str,
            operation=CrudOperation.READ_ONE,
            user_id=self.user_id,
            access_filter=orig_filter,
        )

        # 2. Mocks
        captured: dict[str, Filter] = {}

        def side_effect(inner_cmd: DummyCmd):  # type: ignore[no-untyped-def]
            captured["during"] = inner_cmd.access_filter  # type: ignore[assignment]
            return ["ok"]

        self.service.crud.side_effect = side_effect

        # 3. Execute
        retval = crud_common.crud_with_access_filter(
            self.service,
            self.uow,
            cmd,  # type: ignore[arg-type]
            access_filter=extra_filter,
            cascade_if_delete=False,
        )

        # 4. Verify
        self.assertEqual(retval, ["ok"])
        self.assertIs(cmd.access_filter, orig_filter)
        self.assertIsInstance(captured["during"], CompositeFilter)
        composite: CompositeFilter = captured["during"]  # type: ignore[assignment]
        self.assertEqual(composite.operator, LogicalOperator.AND)
        self.assertEqual(len(composite.filters), 2)
        self.service.crud.assert_called_once()
        self.service.repository.crud.assert_not_called()

    def test_sets_filter_when_original_is_none(self) -> None:
        # 1. Input
        extra_filter: EqualsStringFilter = EqualsStringFilter(key="k2", value="v2")
        cmd: DummyCmd = DummyCmd(
            model_class=str,
            operation=CrudOperation.READ_ONE,
            user_id=self.user_id,
            access_filter=None,
        )

        # 2. Mocks
        captured: dict[str, Filter | None] = {}

        def side_effect(inner_cmd: DummyCmd):  # type: ignore[no-untyped-def]
            captured["during"] = inner_cmd.access_filter
            return ["ok"]

        self.service.crud.side_effect = side_effect

        # 3. Execute
        retval = crud_common.crud_with_access_filter(
            self.service,
            self.uow,
            cmd,  # type: ignore[arg-type]
            access_filter=extra_filter,
            cascade_if_delete=False,
        )

        # 4. Verify
        self.assertEqual(retval, ["ok"])
        self.assertIsNone(cmd.access_filter)
        self.assertIs(captured["during"], extra_filter)
        self.service.repository.crud.assert_not_called()

    def test_no_access_filter_provided_keeps_original(self) -> None:
        # 1. Input
        orig_filter: EqualsStringFilter = EqualsStringFilter(key="k1", value="v1")
        cmd: DummyCmd = DummyCmd(
            model_class=str,
            operation=CrudOperation.READ_ONE,
            user_id=self.user_id,
            access_filter=orig_filter,
        )

        # 2. Mocks
        captured: dict[str, Filter] = {}

        def side_effect(inner_cmd: DummyCmd):  # type: ignore[no-untyped-def]
            captured["during"] = inner_cmd.access_filter  # type: ignore[assignment]
            return ["ok"]

        self.service.crud.side_effect = side_effect

        # 3. Execute
        retval = crud_common.crud_with_access_filter(
            self.service, self.uow, cmd, access_filter=None, cascade_if_delete=False  # type: ignore[arg-type]
        )

        # 4. Verify
        self.assertEqual(retval, ["ok"])  # type: ignore[arg-type]
        self.assertIs(cmd.access_filter, orig_filter)
        self.assertIs(captured["during"], orig_filter)
        self.service.repository.crud.assert_not_called()

    def test_cascade_not_invoked_when_not_delete(self) -> None:
        # 1. Input
        cmd: DummyCmd = DummyCmd(
            model_class=str, operation=CrudOperation.CREATE_ONE, user_id=self.user_id
        )

        # 2. Execute
        _ = crud_common.crud_with_access_filter(
            self.service, self.uow, cmd, access_filter=None, cascade_if_delete=True  # type: ignore[arg-type]
        )

        # 3. Verify
        self.service.repository.crud.assert_not_called()

    def test_cascade_with_unknown_model_sets_empty_mapping(self) -> None:
        # 1. Input
        cmd: DummyCmd = DummyCmd(
            model_class=type("UnknownModel", (), {}),
            operation=CrudOperation.DELETE_ONE,
            user_id=self.user_id,
            obj_ids={uuid4(), uuid4()},
        )

        # 2. Execute
        _ = crud_common.crud_with_access_filter(
            self.service, self.uow, cmd, access_filter=None, cascade_if_delete=True  # type: ignore[arg-type]
        )

        # 3. Verify
        self.assertIn(cmd.MODEL_CLASS, self.service.CASCADE_DELETE_MODEL_CLASSES)
        self.assertEqual(
            self.service.CASCADE_DELETE_MODEL_CLASSES[cmd.MODEL_CLASS], tuple()
        )
        self.service.repository.crud.assert_not_called()

    def test_cascade_with_non_matching_links_does_nothing(self) -> None:
        # 1. Input
        model_class = type("ModelA", (), {})
        other_model_class = type("ModelB", (), {})
        link_model_class = type("LinkModel", (), {})
        entity = DummyEntity(
            links={
                "l1": DummyLink(
                    link_model_class=other_model_class, link_field_name="fk_id"
                )
            }
        )
        setattr(link_model_class, "ENTITY", entity)
        self.service.CASCADE_DELETE_MODEL_CLASSES[model_class] = (link_model_class,)
        cmd: DummyCmd = DummyCmd(
            model_class=model_class,
            operation=CrudOperation.DELETE_ALL,
            user_id=self.user_id,
            obj_ids={uuid4()},
        )

        # 2. Execute
        _ = crud_common.crud_with_access_filter(
            self.service, self.uow, cmd, access_filter=None, cascade_if_delete=True  # type: ignore[arg-type]
        )

        # 3. Verify
        self.service.repository.crud.assert_not_called()

    def test_cascade_with_matching_link_and_none_obj_ids(self) -> None:
        # 1. Input
        model_class = type("ModelA", (), {})
        link_model_class = type("LinkModel", (), {})
        entity = DummyEntity(
            links={
                "l1": DummyLink(link_model_class=model_class, link_field_name="fk_id")
            }
        )
        setattr(link_model_class, "ENTITY", entity)
        self.service.CASCADE_DELETE_MODEL_CLASSES[model_class] = (link_model_class,)
        cmd: DummyCmd = DummyCmd(
            model_class=model_class,
            operation=CrudOperation.DELETE_SOME,
            user_id=self.user_id,
            obj_ids=None,
        )

        # 2. Execute
        _ = crud_common.crud_with_access_filter(
            self.service, self.uow, cmd, access_filter=None, cascade_if_delete=True  # type: ignore[arg-type]
        )

        # 3. Verify
        self.service.repository.crud.assert_called_once()
        args = self.service.repository.crud.call_args[0]
        self.assertEqual(args[0], self.uow)
        self.assertEqual(args[1], cmd.user.id)
        self.assertIs(args[2], link_model_class)
        self.assertIsNone(args[3])
        self.assertIsNone(args[4])
        self.assertEqual(args[5], CrudOperation.DELETE_ALL)
        self.assertIsNone(self.service.repository.crud.call_args.kwargs.get("filter"))

    def test_cascade_with_matching_link_and_obj_ids_uses_compose_filter(self) -> None:
        # 1. Input
        model_class = type("ModelA", (), {})
        link_model_class = type("LinkModel", (), {})
        entity = DummyEntity(
            links={
                "l1": DummyLink(link_model_class=model_class, link_field_name="fk_id")
            }
        )
        setattr(link_model_class, "ENTITY", entity)
        self.service.CASCADE_DELETE_MODEL_CLASSES[model_class] = (link_model_class,)
        obj_ids: set[UUID] = {uuid4(), uuid4()}
        cmd: DummyCmd = DummyCmd(
            model_class=model_class,
            operation=CrudOperation.DELETE_ONE,
            user_id=self.user_id,
            obj_ids=obj_ids,
        )

        # 2. Execute
        _ = crud_common.crud_with_access_filter(
            self.service, self.uow, cmd, access_filter=None, cascade_if_delete=True  # type: ignore[arg-type]
        )

        # 3. Verify
        self.service.repository.crud.assert_called_once()
        kwargs = self.service.repository.crud.call_args.kwargs
        self.assertIn("filter", kwargs)
        self.assertIsInstance(kwargs["filter"], Filter)

    def test_cascade_with_base_class_mapping_populates_subclass(self) -> None:
        # 1. Input
        base_model_class = type("BaseModelA", (), {})
        subclass_model_class = type("SubModelA", (base_model_class,), {})
        link_model_class = type("LinkModel", (), {})
        entity = DummyEntity(
            links={
                "l1": DummyLink(
                    link_model_class=subclass_model_class, link_field_name="fk_id"
                )
            }
        )
        setattr(link_model_class, "ENTITY", entity)
        self.service.CASCADE_DELETE_MODEL_CLASSES[base_model_class] = (
            link_model_class,
        )
        obj_ids: set[UUID] = {uuid4()}
        cmd: DummyCmd = DummyCmd(
            model_class=subclass_model_class,
            operation=CrudOperation.DELETE_ONE,
            user_id=self.user_id,
            obj_ids=obj_ids,
        )

        # 2. Execute
        _ = crud_common.crud_with_access_filter(
            self.service, self.uow, cmd, access_filter=None, cascade_if_delete=True  # type: ignore[arg-type]
        )

        # 3. Verify
        self.assertIn(subclass_model_class, self.service.CASCADE_DELETE_MODEL_CLASSES)
        self.service.repository.crud.assert_called_once()
