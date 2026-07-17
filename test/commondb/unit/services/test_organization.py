"""
Unit tests for OrganizationService.forget_user().

The tests verify that forgetting a user anonymizes personal information while
preserving a deterministic, organization-scoped user key.
"""

from test.util.mock_compat import Mock
from uuid import UUID

import pytest

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.services.organization import OrganizationService
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


@pytest.mark.scenario_ids("TC-COMMONDB-ORGANIZATION-FORGET-USER")
class TestForgetUser:
    """Verify anonymization of the current user."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.user_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.organization_id = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.user = model.User(
            id=self.user_id,
            key="person@example.com",
            email="person@example.com",
            name="Person Example",
            description="Personal description",
            roles={"COMMONDB_USER"},
            organization_id=self.organization_id,
            is_active=True,
        )
        self.organization = model.Organization(
            id=self.organization_id,
            code="ORG",
            name="Example Organization",
        )

        self.repository = Mock()
        self.uow = Mock(spec=BaseUnitOfWork)
        self.uow.__enter__ = Mock(return_value=self.uow)
        self.uow.__exit__ = Mock(return_value=None)
        self.repository.uow.return_value = self.uow
        self.repository.crud.side_effect = [self.organization, self.user]

        self.service = OrganizationService.__new__(OrganizationService)
        self.service._repository = self.repository
        self.service.user_class = model.User

    def test_forget_personal_user_information(self) -> None:
        """Anonymize personal fields and deactivate the forgotten user."""
        cmd = command.ForgetUserCommand(user=self.user)

        forgotten_user = self.service.forget_user(cmd)

        assert forgotten_user is self.user
        assert (
            forgotten_user.key == f"forgotten_user_example_organization_{self.user_id}"
        )
        assert (
            forgotten_user.email
            == f"forgotten_user_example_organization_{self.user_id}"
        )
        assert (
            forgotten_user.name,
            forgotten_user.description,
            forgotten_user.is_active,
        ) == ("Forgotten User", None, False)
        assert self.repository.crud.call_count == 2
        assert self.repository.crud.call_args_list[0].args[3] == CrudOperation.READ_ONE
        assert (
            self.repository.crud.call_args_list[1].args[3] == CrudOperation.UPDATE_ONE
        )

    def test_forget_normalizes_organization_name_in_user_key(self) -> None:
        """Build the anonymized key from a lowercase, space-normalized organization name."""
        self.organization.name = "Example Public Health Organization"

        forgotten_user = self.service.forget_user(
            command.ForgetUserCommand(user=self.user)
        )

        expected_key = (
            f"forgotten_user_example_public_health_organization_{self.user_id}"
        )
        assert forgotten_user.key == expected_key
        assert forgotten_user.email == expected_key

    def test_forget_keeps_keys_unique_for_users_in_same_organization(self) -> None:
        """Include each user ID so forgotten users in one organization remain unique."""
        second_user_id = UUID("550e8400-e29b-41d4-a716-446655440003")
        second_user = self.user.model_copy(
            update={
                "id": second_user_id,
                "key": "second.person@example.com",
                "email": "second.person@example.com",
            }
        )
        self.repository.crud.side_effect = [
            self.organization,
            self.user,
            self.organization,
            second_user,
        ]

        first_forgotten_user = self.service.forget_user(
            command.ForgetUserCommand(user=self.user)
        )
        second_forgotten_user = self.service.forget_user(
            command.ForgetUserCommand(user=second_user)
        )

        assert first_forgotten_user.key != second_forgotten_user.key
        assert str(self.user_id) in first_forgotten_user.key
        assert str(second_user_id) in second_forgotten_user.key
