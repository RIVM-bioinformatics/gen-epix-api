"""
Unit tests for case_service_retrieve_is_own_cases.

Tests follow the style and conventions of test_retrieve_case.py,
using typed variables, explicit mocking, and the 1-2-3-4 section structure.
"""

from typing import Any
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, exc, model
from gen_epix.casedb.domain.model.abac.rights import CaseTypeAccessAbac
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.retrieve_is_own_cases import (
    case_service_retrieve_is_own_cases,
)
from gen_epix.commondb.domain.enum import Role


class _FakeCaseAbacPolicy(BaseCaseAbacPolicy):
    """Lightweight policy to inject a case ABAC object into commands."""

    def __init__(self, abac: Any):
        super().__init__(abac_service=Mock(), abac=abac)
        self._abac = abac

    def get_content(self, cmd: Any) -> Any:  # noqa: ARG002
        return self._abac


class BaseIsOwnCasesTestCase(TestCase):
    """Base test case with common fixtures and utilities."""

    def setUp(self) -> None:
        # Test user
        self.user: model.User = model.User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={Role.APP_ADMIN.value},
            organization_id=uuid4(),
            is_active=True,
        )

        # Common IDs
        self.case_type_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440021")
        self.case_id1: UUID = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.case_id2: UUID = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.data_collection_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440501")
        self.private_data_collection_id: UUID = UUID(
            "550e8400-e29b-41d4-a716-446655440601"
        )
        self.other_data_collection_id: UUID = UUID(
            "550e8400-e29b-41d4-a716-446655440602"
        )

        # Service and repository mocks
        self.service: Any = Mock(spec=BaseCaseService)
        self.repository: Any = Mock()
        self.uow: Any = Mock()
        self.uow.__enter__ = Mock(return_value=self.uow)
        self.uow.__exit__ = Mock(return_value=None)
        self.repository.uow = Mock(return_value=self.uow)
        self.service.repository = self.repository
        self.service._get_user_and_repository = Mock(
            return_value=(self.user, self.repository)
        )
        self.service._retrieve_cases_with_content_right = Mock(return_value=([], False))
        self.service._retrieve_case_data_collections_map = Mock(return_value={})

        # Default ABAC mock: full access, case_type_id in allowed set,
        # no private data collections
        self.case_abac: Any = Mock()
        self.case_abac.is_full_access = True
        self.case_abac.get_combinations_with_access_right = Mock(
            return_value={self.case_type_id}
        )
        self.case_abac.case_type_access_abacs = {}

    # Helpers

    def create_command(
        self,
        case_ids: list[UUID] | None = None,
        case_type_id: UUID | None = None,
    ) -> command.RetrieveIsOwnCasesCommand:
        """Create a RetrieveIsOwnCasesCommand for tests."""
        return command.RetrieveIsOwnCasesCommand(
            user=self.user,
            case_type_id=case_type_id or self.case_type_id,
            case_ids=case_ids if case_ids is not None else [],
        )

    def create_case(
        self,
        case_id: UUID,
        created_in_data_collection_id: UUID | None = None,
    ) -> model.Case:
        """Create a Case for tests, defaulting to the common data collection."""
        return model.Case(
            id=case_id,
            code=None,
            case_type_id=self.case_type_id,
            created_in_data_collection_id=(
                created_in_data_collection_id or self.data_collection_id
            ),
            count=None,
            content={},
        )

    def create_case_type_access_abac(
        self,
        data_collection_id: UUID,
        is_private: bool = False,
    ) -> CaseTypeAccessAbac:
        """Create a CaseTypeAccessAbac with all rights disabled."""
        return CaseTypeAccessAbac(
            case_type_id=self.case_type_id,
            data_collection_id=data_collection_id,
            is_private=is_private,
            add_case=False,
            remove_case=False,
            add_case_set=False,
            remove_case_set=False,
            read_col_ids=set(),
            write_col_ids=set(),
            read_case_set=False,
            write_case_set=False,
        )

    def set_retrieve_cases_result(
        self,
        cases: list[model.Case],
        is_max_results_exceeded: bool = False,
    ) -> None:
        """Set the tuple return value of _retrieve_cases_with_content_right."""
        self.service._retrieve_cases_with_content_right.return_value = (
            cases,
            is_max_results_exceeded,
        )

    def attach_abac_policy(self, cmd: command.Command, abac: Any | None = None) -> None:
        """Attach a fake ABAC policy to the command for retrieval."""
        cmd._policies = [
            _FakeCaseAbacPolicy(abac if abac is not None else self.case_abac)
        ]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRetrieveIsOwnCasesUnauthorized(BaseIsOwnCasesTestCase):
    """Tests verifying UnauthorizedAuthError is raised when access is denied."""

    def test_unauthorized_case_type_raises(self) -> None:
        # 1. Input
        cmd: command.RetrieveIsOwnCasesCommand = self.create_command(
            case_ids=[self.case_id1]
        )

        # 2. Mocks: no READ_CASE access at all, no full access
        case_abac: Any = Mock()
        case_abac.is_full_access = False
        case_abac.get_combinations_with_access_right = Mock(return_value={})
        self.attach_abac_policy(cmd, case_abac)

        # 3. Execute
        with pytest.raises(exc.UnauthorizedAuthError):
            case_service_retrieve_is_own_cases(self.service, cmd)

    def test_case_type_not_in_partial_permissions_raises(self) -> None:
        # 1. Input: request a case_type_id the user has no access to
        other_case_type_id: UUID = uuid4()
        cmd: command.RetrieveIsOwnCasesCommand = command.RetrieveIsOwnCasesCommand(
            user=self.user,
            case_type_id=other_case_type_id,
            case_ids=[self.case_id1],
        )

        # 2. Mocks: user has READ_CASE for self.case_type_id only
        case_abac: Any = Mock()
        case_abac.is_full_access = False
        case_abac.get_combinations_with_access_right = Mock(
            return_value={self.case_type_id}
        )
        self.attach_abac_policy(cmd, case_abac)

        # 3. Execute
        with pytest.raises(exc.UnauthorizedAuthError):
            case_service_retrieve_is_own_cases(self.service, cmd)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRetrieveIsOwnCasesFullAccess(BaseIsOwnCasesTestCase):
    """Tests verifying that full-access users bypass the case type permission check."""

    def test_full_access_bypasses_permission_check(self) -> None:
        # 1. Input: case_type_id absent from READ_CASE permissions
        cmd: command.RetrieveIsOwnCasesCommand = self.create_command(case_ids=[])

        # 2. Mocks: full access set, but no case_type_id in allowed set
        case_abac: Any = Mock()
        case_abac.is_full_access = True
        case_abac.get_combinations_with_access_right = Mock(return_value={})
        case_abac.case_type_access_abacs = {}
        self.attach_abac_policy(cmd, case_abac)

        # 3. Execute: must not raise
        result: dict[UUID, bool] = case_service_retrieve_is_own_cases(self.service, cmd)

        # 4. Verify: no cases → empty mapping
        assert result == {}


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRetrieveIsOwnCasesOwnership(BaseIsOwnCasesTestCase):
    """Tests verifying the ownership determination logic."""

    def test_case_owned_via_created_in_data_collection_id(self) -> None:
        # 1. Input: case created in a private data collection
        cmd: command.RetrieveIsOwnCasesCommand = self.create_command(
            case_ids=[self.case_id1]
        )

        # 2. Mocks: private_data_collection_id is marked private in ABAC
        private_abac: CaseTypeAccessAbac = self.create_case_type_access_abac(
            self.private_data_collection_id, is_private=True
        )
        self.case_abac.case_type_access_abacs = {
            self.case_type_id: {self.private_data_collection_id: private_abac}
        }
        self.attach_abac_policy(cmd)
        case: model.Case = self.create_case(
            self.case_id1,
            created_in_data_collection_id=self.private_data_collection_id,
        )
        self.set_retrieve_cases_result([case])
        self.service._retrieve_case_data_collections_map.return_value = {}

        # 3. Execute
        result: dict[UUID, bool] = case_service_retrieve_is_own_cases(self.service, cmd)

        # 4. Verify: case created in a private collection is own
        assert result == {self.case_id1: True}

    def test_case_owned_via_data_collection_link(self) -> None:
        # 1. Input: case created in a non-private collection but linked to a
        #    private one via case_data_collections_map
        cmd: command.RetrieveIsOwnCasesCommand = self.create_command(
            case_ids=[self.case_id1]
        )

        # 2. Mocks
        private_abac: CaseTypeAccessAbac = self.create_case_type_access_abac(
            self.private_data_collection_id, is_private=True
        )
        self.case_abac.case_type_access_abacs = {
            self.case_type_id: {self.private_data_collection_id: private_abac}
        }
        self.attach_abac_policy(cmd)
        # Case created in a non-private data collection
        case: model.Case = self.create_case(
            self.case_id1,
            created_in_data_collection_id=self.data_collection_id,
        )
        self.set_retrieve_cases_result([case])
        # Case is also linked to the private data collection
        self.service._retrieve_case_data_collections_map.return_value = {
            self.case_id1: {self.private_data_collection_id}
        }

        # 3. Execute
        result: dict[UUID, bool] = case_service_retrieve_is_own_cases(self.service, cmd)

        # 4. Verify: link to private collection makes the case own
        assert result == {self.case_id1: True}

    def test_case_not_owned_when_no_private_data_collection_matches(self) -> None:
        # 1. Input: case with no overlap between its data collections and the
        #    user's private data collections
        cmd: command.RetrieveIsOwnCasesCommand = self.create_command(
            case_ids=[self.case_id1]
        )

        # 2. Mocks: private_data_collection_id is private in ABAC
        private_abac: CaseTypeAccessAbac = self.create_case_type_access_abac(
            self.private_data_collection_id, is_private=True
        )
        self.case_abac.case_type_access_abacs = {
            self.case_type_id: {self.private_data_collection_id: private_abac}
        }
        self.attach_abac_policy(cmd)
        # Case created in and linked to non-private collections only
        case: model.Case = self.create_case(
            self.case_id1,
            created_in_data_collection_id=self.other_data_collection_id,
        )
        self.set_retrieve_cases_result([case])
        self.service._retrieve_case_data_collections_map.return_value = {
            self.case_id1: {self.data_collection_id}
        }

        # 3. Execute
        result: dict[UUID, bool] = case_service_retrieve_is_own_cases(self.service, cmd)

        # 4. Verify: no overlap with private collections → not own
        assert result == {self.case_id1: False}

    def test_mixed_ownership_returns_correct_mapping(self) -> None:
        # 1. Input: two cases — case_id1 is own, case_id2 is not
        cmd: command.RetrieveIsOwnCasesCommand = self.create_command(
            case_ids=[self.case_id1, self.case_id2]
        )

        # 2. Mocks
        private_abac: CaseTypeAccessAbac = self.create_case_type_access_abac(
            self.private_data_collection_id, is_private=True
        )
        self.case_abac.case_type_access_abacs = {
            self.case_type_id: {self.private_data_collection_id: private_abac}
        }
        self.attach_abac_policy(cmd)
        # case_id1 was created in the private collection → own
        # case_id2 was created in a non-private collection → not own
        case1: model.Case = self.create_case(
            self.case_id1,
            created_in_data_collection_id=self.private_data_collection_id,
        )
        case2: model.Case = self.create_case(
            self.case_id2,
            created_in_data_collection_id=self.other_data_collection_id,
        )
        self.set_retrieve_cases_result([case1, case2])
        self.service._retrieve_case_data_collections_map.return_value = {}

        # 3. Execute
        result: dict[UUID, bool] = case_service_retrieve_is_own_cases(self.service, cmd)

        # 4. Verify
        assert result == {self.case_id1: True, self.case_id2: False}

    def test_no_private_data_collections_makes_all_cases_not_own(self) -> None:
        # 1. Input: two cases, ABAC has only non-private data collections
        cmd: command.RetrieveIsOwnCasesCommand = self.create_command(
            case_ids=[self.case_id1, self.case_id2]
        )

        # 2. Mocks: all ABAC entries are non-private
        non_private_abac: CaseTypeAccessAbac = self.create_case_type_access_abac(
            self.data_collection_id, is_private=False
        )
        self.case_abac.case_type_access_abacs = {
            self.case_type_id: {self.data_collection_id: non_private_abac}
        }
        self.attach_abac_policy(cmd)
        case1: model.Case = self.create_case(self.case_id1)
        case2: model.Case = self.create_case(self.case_id2)
        self.set_retrieve_cases_result([case1, case2])
        self.service._retrieve_case_data_collections_map.return_value = {}

        # 3. Execute
        result: dict[UUID, bool] = case_service_retrieve_is_own_cases(self.service, cmd)

        # 4. Verify: no private collections → all cases are not own
        assert result == {self.case_id1: False, self.case_id2: False}


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRetrieveIsOwnCasesEdgeCases(BaseIsOwnCasesTestCase):
    """Tests covering edge cases such as empty inputs and empty results."""

    def test_empty_case_ids_returns_empty_mapping(self) -> None:
        # 1. Input: empty list of case IDs
        cmd: command.RetrieveIsOwnCasesCommand = self.create_command(case_ids=[])

        # 2. Mocks: inner retrieval returns nothing
        self.attach_abac_policy(cmd)
        self.set_retrieve_cases_result([])

        # 3. Execute
        result: dict[UUID, bool] = case_service_retrieve_is_own_cases(self.service, cmd)

        # 4. Verify
        assert result == {}

    def test_no_cases_returned_yields_empty_mapping(self) -> None:
        # 1. Input: valid case IDs supplied but no cases found
        cmd: command.RetrieveIsOwnCasesCommand = self.create_command(
            case_ids=[self.case_id1, self.case_id2]
        )

        # 2. Mocks: repository finds nothing for the requested IDs
        self.attach_abac_policy(cmd)
        self.set_retrieve_cases_result([])

        # 3. Execute
        result: dict[UUID, bool] = case_service_retrieve_is_own_cases(self.service, cmd)

        # 4. Verify
        assert result == {}
