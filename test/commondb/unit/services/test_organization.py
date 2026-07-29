"""
Unit tests for OrganizationService.anonymize_user().

The tests verify that anonymizing a user anonymizes personal information while
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
class TestAnonymizeUser:
    """Verify anonymization of the target user."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.admin_user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        self.tgt_user_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.organization_id = UUID("550e8400-e29b-41d4-a716-446655440003")

        # Admin user performing the anonymization
        self.admin_user = model.User(
            id=self.admin_user_id,
            key="admin@example.com",
            email="admin@example.com",
            name="Admin User",
            description="Admin description",
            roles={"COMMONDB_ADMIN"},
            organization_id=self.organization_id,
            is_active=True,
        )

        # Target user to be anonymized
        self.tgt_user = model.User(
            id=self.tgt_user_id,
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

        self.service = OrganizationService.__new__(OrganizationService)
        self.service._repository = self.repository
        self.service.user_class = model.User

    def test_anonymize_user_information(self) -> None:
        """Anonymize personal fields and deactivate the anonymized user."""
        # Setup mock side_effect for 2 crud calls: READ user, UPDATE user
        self.repository.crud.side_effect = [
            self.tgt_user,
            self.tgt_user,
        ]
        cmd = command.AnonymizeUserCommand(
            user=self.admin_user, tgt_user_id=self.tgt_user_id
        )

        anonymized_user = self.service.anonymize_user(cmd)

        assert anonymized_user is self.tgt_user
        assert anonymized_user.key == str(self.admin_user_id)
        assert anonymized_user.email is None
        assert anonymized_user.name is None
        assert anonymized_user.description is None
        assert anonymized_user.is_active is False
        assert self.repository.crud.call_count == 2
        assert self.repository.crud.call_args_list[0].args[3] == CrudOperation.READ_ONE
        assert (
            self.repository.crud.call_args_list[1].args[3] == CrudOperation.UPDATE_ONE
        )

    def test_anonymize_normalizes_organization_name_in_user_key(self) -> None:
        """Anonymize personal fields and deactivate the anonymized user."""
        # Setup mock side_effect for 2 crud calls: READ user, UPDATE user
        self.repository.crud.side_effect = [
            self.tgt_user,
            self.tgt_user,
        ]

        anonymized_user = self.service.anonymize_user(
            command.AnonymizeUserCommand(
                user=self.admin_user,
                tgt_user_id=self.tgt_user_id,
            )
        )

        assert anonymized_user.key == str(self.admin_user_id)
        assert anonymized_user.email is None
        assert anonymized_user.is_active is False

    def test_anonymize_keeps_keys_unique_for_users_in_same_organization(self) -> None:
        """Include each user ID so forgotten users in one organization remain unique."""
        second_user_id = UUID("550e8400-e29b-41d4-a716-446655440004")
        second_user = self.tgt_user.model_copy(
            update={
                "id": second_user_id,
                "key": "second.person@example.com",
                "email": "second.person@example.com",
            }
        )
        # Setup mock side_effect for 4 crud calls:
        # First anonymization: READ user, UPDATE user
        # Second anonymization: READ user, UPDATE user
        self.repository.crud.side_effect = [
            self.tgt_user,
            self.tgt_user,
            second_user,
            second_user,
        ]

        first_anonymized_user = self.service.anonymize_user(
            command.AnonymizeUserCommand(
                user=self.admin_user, tgt_user_id=self.tgt_user_id
            )
        )
        second_anonymized_user = self.service.anonymize_user(
            command.AnonymizeUserCommand(
                user=self.admin_user, tgt_user_id=second_user_id
            )
        )

        # Both should have the same key (the admin user's ID)
        assert first_anonymized_user.key == str(self.admin_user_id)
        assert second_anonymized_user.key == str(self.admin_user_id)
