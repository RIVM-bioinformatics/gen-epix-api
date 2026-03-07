"""Shared base test case for CRUD unit tests under ``casedb.services.case``."""

from typing import Any, Iterable
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

from gen_epix.casedb.domain import model as case_model
from gen_epix.commondb.domain.enum import Role
from gen_epix.commondb.domain.model.organization import User
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.enum import CrudOperationSet
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class BaseCrudTestCase(TestCase):
    """Base test case providing common service and UOW fixtures for CRUD tests.

    Provides
    --------
    ``self.uow``
        A ``BaseUnitOfWork`` mock with context-manager support.
    ``self.service``
        A generic service mock with ``repository``, ``repository.crud``
        (returns ``[]``), ``repository.uow`` (returns ``self.uow``), and
        ``crud`` (returns ``[]``) pre-wired.
    ``self.user``
        A standard ``User`` instance for use in tests.
    ``_make_uow()``
        Static factory for creating additional UOW mocks.
    ``create_crud_command()``
        Factory for creating mocked command objects usable across all CRUD tests.
    """

    def setUp(self) -> None:
        self.uow: BaseUnitOfWork = self._make_uow()
        self.service: Mock = Mock()
        self.service.repository = Mock()
        self.service.repository.uow.return_value = self.uow
        self.service.repository.crud = Mock(return_value=[])
        self.service.crud = Mock(return_value=[])

        # Standard test user
        self.user: User = User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={Role.ORG_USER.value},
            organization_id=uuid4(),
            is_active=True,
        )

        # Case-set-specific service attributes
        self.service._retrieve_case_sets_with_content_right = Mock()
        self.service._retrieve_case_set_data_collections_map = Mock()

    @staticmethod
    def _make_uow() -> BaseUnitOfWork:
        """Create a ``BaseUnitOfWork`` mock with context-manager support."""
        uow: BaseUnitOfWork = Mock(spec=BaseUnitOfWork)
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=None)
        return uow

    def create_crud_command(
        self,
        operation: CrudOperation,
        user: User | None = None,
        user_id: UUID | None = None,
        ids: list[UUID] | None = None,
        objs: list[Any] | None = None,
        obj_ids: Iterable[UUID] | UUID | None = None,
        query_filter: object | None = None,
        set_user_none: bool = False,
    ) -> Mock:
        """Create a mocked command with all standard attributes wired.

        If ``user_id`` is provided, ``cmd.user`` is a plain mock with that id.
        If ``user`` is provided (and ``user_id`` is not), that user is used.
        Otherwise ``self.user`` is used.
        """
        cmd: Mock = Mock()
        if set_user_none:
            cmd.user = None
        elif user_id is not None:
            cmd.user = Mock()
            cmd.user.id = user_id
        else:
            cmd.user = user if user is not None else self.user
        cmd.operation = operation
        cmd.query_filter = query_filter
        cmd.get_obj_ids = Mock(return_value=ids or [uuid4()])
        cmd.get_objs = Mock(return_value=list(objs) if objs is not None else None)
        cmd.obj_ids = obj_ids
        cmd.is_create = Mock(return_value=operation in CrudOperationSet.CREATE.value)
        cmd.is_read = Mock(
            return_value=operation in CrudOperationSet.READ_OR_EXISTS.value
        )
        cmd.is_update = Mock(return_value=operation in CrudOperationSet.UPDATE.value)
        cmd.is_delete = Mock(return_value=operation in CrudOperationSet.DELETE.value)
        return cmd

    def create_case_sets(self, n: int = 2) -> list[Mock]:
        """Create mocked CaseSet objects with required attributes."""
        case_sets: list[Mock] = []
        for _ in range(n):
            case_set: Mock = Mock(spec=case_model.CaseSet)
            case_set.id = uuid4()
            case_set.case_type_id = uuid4()
            case_set.created_in_data_collection_id = uuid4()
            case_sets.append(case_set)
        return case_sets

    def create_case_abac(self, allowed: bool = True) -> Mock:
        """Create a mocked ABAC object with configurable allowance."""
        case_abac: Mock = Mock()
        case_abac.is_allowed = Mock(return_value=allowed)
        return case_abac
