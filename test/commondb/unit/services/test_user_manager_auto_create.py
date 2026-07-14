"""
Unit tests for UserManager.auto_create_new_user().

Tests verify that the refactored implementation:
- Maintains all existing behavior (regression tests)
- Correctly implements the new root organization auto-creation feature
- Follows proper exception semantics and ordering
"""

from typing import Any
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain import exc, model
from gen_epix.commondb.services.user_manager import UserManager
from gen_epix.fastapp.enum import CrudOperation


@pytest.fixture
def root_org_id() -> UUID:
    """UUID for the configured root organization."""
    return UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def root_org(root_org_id: UUID) -> model.Organization:
    """Root organization model."""
    return model.Organization(
        id=root_org_id,
        name="Root Organization",
        code="ROOT_ORG",
    )


@pytest.fixture
def other_org_id() -> UUID:
    """UUID for a non-root organization."""
    return UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture
def other_org(other_org_id: UUID) -> model.Organization:
    """Non-root organization model."""
    return model.Organization(
        id=other_org_id,
        name="Other Organization",
        code="OTHER_ORG",
    )


@pytest.fixture
def root_user(root_org_id: UUID) -> model.User:
    """Root user model for root_cfg."""
    return model.User(
        id=uuid4(),
        key="root_key",
        email="root@example.org",
        name="Root User",
        is_active=True,
        roles={"COMMONDB_ROOT"},
        organization_id=root_org_id,
    )


@pytest.fixture
def test_user_id() -> UUID:
    """UUID for test user to be auto-created."""
    return UUID("00000000-0000-0000-0000-000000000010")


@pytest.fixture
def claims_basic() -> dict[str, Any]:
    """Basic claims for auto-create user."""
    return {
        "__key__": "testuser@example.org",
        "email": "testuser@example.org",
        "name": "Test User",
    }


@pytest.fixture
def mock_organization_service(root_org: model.Organization) -> Mock:
    """Mock BaseOrganizationService."""
    service = Mock()
    service.repository = Mock()
    service.app = Mock()
    service.app.impl = Mock()
    service.app.impl.get_mapped_class.side_effect = lambda cls: cls
    service.generate_id.side_effect = uuid4
    return service


@pytest.fixture
def mock_rbac_service() -> Mock:
    """Mock BaseRbacService."""
    service = Mock()
    service.root_role = "COMMONDB_ROOT"
    service.guest_role = "COMMONDB_GUEST"
    service.get_roles.return_value = {
        "COMMONDB_ROOT",
        "COMMONDB_GUEST",
        "COMMONDB_ADMIN",
    }
    return service


def make_user_manager(
    organization_service: Mock,
    rbac_service: Mock,
    root_org: model.Organization,
    root_org_id: UUID,
    auto_created_user_cfg: dict[str, Any] | None = None,
) -> UserManager:
    """Factory to create UserManager with mocked dependencies."""
    root_cfg = {
        "organization": {
            "id": str(root_org_id),
            "name": root_org.name,
            "code": root_org.code,
        },
        "user": {
            "key": "root_key",
            "email": root_org.name,
            "name": "Root User",
        },
    }
    return UserManager(
        organization_service=organization_service,
        rbac_service=rbac_service,
        root_cfg=root_cfg,
        auto_created_user_cfg=auto_created_user_cfg,
    )


class TestAutoCreateNewUserRegressions:
    """Verify that existing behavior is preserved after refactoring."""

    def test_returns_none_when_config_not_provided(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        claims_basic: dict[str, Any],
    ) -> None:
        """When auto_created_user_cfg is None, returns None without side effects."""
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=None,
        )
        result = user_manager.auto_create_new_user(claims_basic)
        assert result is None
        # Verify no repository interactions
        mock_organization_service.repository.uow.assert_not_called()

    def test_raises_when_non_root_org_does_not_exist(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        other_org_id: UUID,
        claims_basic: dict[str, Any],
    ) -> None:
        """Raises InitializationServiceError when org doesn't exist and
        org_id != root_org_id."""
        auto_cfg = {
            "organization_id": str(other_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )
        # Mock repository to indicate organization does not exist
        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )
        mock_organization_service.repository.crud.return_value = False

        with pytest.raises(exc.InitializationServiceError) as exc_info:
            user_manager.auto_create_new_user(claims_basic)
        assert "26baf193" in str(exc_info.value)

    def test_raises_when_user_already_exists(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        claims_basic: dict[str, Any],
    ) -> None:
        """Raises ServiceException when user already exists."""
        auto_cfg = {
            "organization_id": str(root_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )
        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )
        # Organization exists
        mock_organization_service.repository.crud.side_effect = [
            True,  # organization exists
        ]
        # User already exists
        mock_organization_service.repository.is_existing_user_by_key.return_value = True

        with pytest.raises(exc.ServiceException) as exc_info:
            user_manager.auto_create_new_user(claims_basic)
        assert "98a3327c" in str(exc_info.value)

    def test_raises_when_construct_user_returns_none(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
    ) -> None:
        """Raises CredentialsAuthError when required key claim is missing."""
        auto_cfg = {
            "organization_id": str(root_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )
        # Claims without __key__ to trigger construct failure
        claims_no_key = {"email": "test@example.org"}

        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )
        # Organization exists
        mock_organization_service.repository.crud.side_effect = [
            True,  # organization exists
        ]
        # User does not exist
        mock_organization_service.repository.is_existing_user_by_key.return_value = (
            False
        )

        with pytest.raises(exc.CredentialsAuthError):
            user_manager.auto_create_new_user(claims_no_key)

    def test_creates_user_successfully_when_all_validations_pass(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        test_user_id: UUID,
        claims_basic: dict[str, Any],
    ) -> None:
        """Creates and returns a new user when all validations pass."""
        auto_cfg = {
            "organization_id": str(root_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )

        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )

        # Organization exists
        mock_organization_service.repository.crud.side_effect = [
            True,  # EXISTS_ONE for org
            model.User(  # CREATE_ONE for user
                id=test_user_id,
                key=claims_basic["__key__"],
                email=claims_basic["email"],
                name=claims_basic["name"],
                is_active=True,
                roles={"COMMONDB_GUEST"},
                organization_id=root_org_id,
            ),
        ]
        mock_organization_service.repository.is_existing_user_by_key.return_value = (
            False
        )
        mock_organization_service.generate_id.return_value = test_user_id

        result = user_manager.auto_create_new_user(claims_basic)

        assert result is not None
        assert result.id == test_user_id
        assert result.key == claims_basic["__key__"]

    def test_generates_and_assigns_user_id_before_persistence(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        test_user_id: UUID,
        claims_basic: dict[str, Any],
    ) -> None:
        """Verifies the generated user ID is assigned before CRUD.CREATE."""
        auto_cfg = {
            "organization_id": str(root_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )

        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )

        # Capture the user object passed to CREATE_ONE
        created_user = None

        def capture_crud(*args: Any, **kwargs: Any) -> Any:
            nonlocal created_user
            if args[3] == CrudOperation.CREATE_ONE:
                created_user = kwargs.get("objs") or args[4]
            elif args[3] == CrudOperation.EXISTS_ONE:
                return True
            return created_user

        mock_organization_service.repository.crud.side_effect = capture_crud
        mock_organization_service.repository.is_existing_user_by_key.return_value = (
            False
        )
        # Ensure generate_id returns the test_user_id consistently
        mock_organization_service.generate_id.side_effect = lambda: test_user_id

        user_manager.auto_create_new_user(claims_basic)

        assert created_user is not None
        assert created_user.id == test_user_id

    def test_verifies_repo_create_call_with_expected_user_object(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        test_user_id: UUID,
        claims_basic: dict[str, Any],
    ) -> None:
        """Verifies the repository CREATE call receives the expected user."""
        auto_cfg = {
            "organization_id": str(root_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )

        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )

        expected_user = model.User(
            id=test_user_id,
            key=claims_basic["__key__"],
            email=claims_basic["email"],
            name=claims_basic["name"],
            is_active=True,
            roles={"COMMONDB_GUEST"},
            organization_id=root_org_id,
        )

        mock_organization_service.repository.crud.side_effect = [
            True,  # EXISTS_ONE for org
            expected_user,  # CREATE_ONE for user
        ]
        mock_organization_service.repository.is_existing_user_by_key.return_value = (
            False
        )
        mock_organization_service.generate_id.side_effect = lambda: test_user_id

        result = user_manager.auto_create_new_user(claims_basic)

        # Verify crud was called with CREATE_ONE and the user object
        create_calls = [
            x
            for x in mock_organization_service.repository.crud.call_args_list
            if x[0][3] == CrudOperation.CREATE_ONE
        ]
        assert len(create_calls) == 1
        assert create_calls[0][1]["objs"].key == expected_user.key
        assert create_calls[0][1]["objs"].email == expected_user.email
        assert create_calls[0][1]["objs"].id == test_user_id

        assert result is not None
        assert result.key == expected_user.key


class TestAutoCreateNewUserRootOrgFeature:
    """Verify the new root organization auto-creation feature."""

    def test_auto_creates_root_org_when_missing_and_org_id_matches_root(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        test_user_id: UUID,
        claims_basic: dict[str, Any],
    ) -> None:
        """When root org doesn't exist and org_id == root_org_id, creates
        the root organization and proceeds with user creation."""
        auto_cfg = {
            "organization_id": str(root_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )

        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )

        def crud_side_effect(*args: Any, **kwargs: Any) -> Any:
            operation = args[3]
            if operation == CrudOperation.EXISTS_ONE:
                return False
            elif operation == CrudOperation.CREATE_ONE:
                # CREATE_ONE for organization
                if "objs" in kwargs and isinstance(kwargs["objs"], model.Organization):
                    return kwargs["objs"]
                # CREATE_ONE for user
                return kwargs.get("objs")
            return None

        mock_organization_service.repository.crud.side_effect = crud_side_effect
        mock_organization_service.repository.is_existing_user_by_key.return_value = (
            False
        )
        mock_organization_service.generate_id.side_effect = lambda: test_user_id

        result = user_manager.auto_create_new_user(claims_basic)

        assert result is not None
        assert result.id == test_user_id

        # Verify that organization CREATE was called
        create_org_calls = [
            x
            for x in mock_organization_service.repository.crud.call_args_list
            if x[0][3] == CrudOperation.CREATE_ONE
            and "objs" in x[1]
            and isinstance(x[1]["objs"], model.Organization)
        ]
        assert len(create_org_calls) == 1
        assert create_org_calls[0][1]["objs"].id == root_org_id

    def test_skips_org_creation_when_org_already_exists(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        test_user_id: UUID,
        claims_basic: dict[str, Any],
    ) -> None:
        """When organization already exists, organization creation is
        skipped."""
        auto_cfg = {
            "organization_id": str(root_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )

        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )

        def crud_side_effect(*args: Any, **kwargs: Any) -> Any:
            operation = args[3]
            if operation == CrudOperation.EXISTS_ONE:
                # Organization exists
                return True
            elif operation == CrudOperation.CREATE_ONE:
                # Only user creation, not org
                return kwargs.get("objs")
            return None

        mock_organization_service.repository.crud.side_effect = crud_side_effect
        mock_organization_service.repository.is_existing_user_by_key.return_value = (
            False
        )
        mock_organization_service.generate_id.return_value = test_user_id

        result = user_manager.auto_create_new_user(claims_basic)

        assert result is not None

        # Verify that organization CREATE was NOT called
        create_org_calls = [
            x
            for x in mock_organization_service.repository.crud.call_args_list
            if x[0][3] == CrudOperation.CREATE_ONE
            and "objs" in x[1]
            and isinstance(x[1]["objs"], model.Organization)
        ]
        assert len(create_org_calls) == 0

    def test_org_validation_happens_before_user_existence_check(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        test_user_id: UUID,
        claims_basic: dict[str, Any],
    ) -> None:
        """Organization validation/creation happens before user existence
        check."""
        auto_cfg = {
            "organization_id": str(root_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )

        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )

        call_order = []

        def crud_side_effect(*args: Any, **kwargs: Any) -> Any:
            operation = args[3]
            if operation == CrudOperation.EXISTS_ONE:
                call_order.append("EXISTS_ONE_ORG")
                return True
            elif operation == CrudOperation.CREATE_ONE:
                call_order.append("CREATE_ONE_USER")
                return kwargs.get("objs")
            return None

        def is_existing_user_side_effect(*args: Any, **kwargs: Any) -> bool:
            call_order.append("IS_EXISTING_USER")
            return False

        mock_organization_service.repository.crud.side_effect = crud_side_effect
        mock_organization_service.repository.is_existing_user_by_key.side_effect = (
            is_existing_user_side_effect
        )
        mock_organization_service.generate_id.return_value = test_user_id

        result = user_manager.auto_create_new_user(claims_basic)

        assert result is not None
        # Verify order: org EXISTS check must happen before user EXISTS check
        assert call_order.index("EXISTS_ONE_ORG") < call_order.index("IS_EXISTING_USER")

    def test_user_creation_not_attempted_if_org_creation_fails(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        other_org_id: UUID,
    ) -> None:
        """When organization creation fails, user creation is not
        attempted."""
        auto_cfg = {
            "organization_id": str(other_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )

        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )

        # Organization doesn't exist
        mock_organization_service.repository.crud.return_value = False
        mock_organization_service.repository.is_existing_user_by_key.return_value = (
            False
        )

        with pytest.raises(exc.InitializationServiceError):
            user_manager.auto_create_new_user({"__key__": "test@example.org"})

        # Verify only EXISTS_ONE was called, not CREATE_ONE
        crud_calls = mock_organization_service.repository.crud.call_args_list
        operations = [call[0][3] for call in crud_calls]
        assert CrudOperation.EXISTS_ONE in operations
        assert CrudOperation.CREATE_ONE not in operations

    def test_root_org_auto_create_with_non_root_org_id_still_raises(
        self,
        mock_organization_service: Mock,
        mock_rbac_service: Mock,
        root_org: model.Organization,
        root_org_id: UUID,
        other_org_id: UUID,
        claims_basic: dict[str, Any],
    ) -> None:
        """Even with auto-create feature, if org_id != root_org_id and
        org doesn't exist, still raises InitializationServiceError."""
        auto_cfg = {
            "organization_id": str(other_org_id),
            "roles": {"COMMONDB_GUEST"},
        }
        user_manager = make_user_manager(
            mock_organization_service,
            mock_rbac_service,
            root_org,
            root_org_id,
            auto_created_user_cfg=auto_cfg,
        )

        mock_uow = Mock()
        mock_organization_service.repository.uow.return_value.__enter__ = Mock(
            return_value=mock_uow
        )
        mock_organization_service.repository.uow.return_value.__exit__ = Mock(
            return_value=False
        )

        # Organization doesn't exist
        mock_organization_service.repository.crud.return_value = False

        with pytest.raises(exc.InitializationServiceError) as exc_info:
            user_manager.auto_create_new_user(claims_basic)
        assert "26baf193" in str(exc_info.value)

        # Verify no CREATE_ONE was called
        create_calls = [
            x
            for x in mock_organization_service.repository.crud.call_args_list
            if x[0][3] == CrudOperation.CREATE_ONE
        ]
        assert len(create_calls) == 0
