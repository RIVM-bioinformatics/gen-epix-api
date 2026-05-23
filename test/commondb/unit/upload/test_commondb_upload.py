"""
Unit tests for commondb upload services.

The tests make use of the Parent, Child1, and Child2 and derived models defined in
model.py and focus on verifying the upload logic.

The tests handle all of the following upload scenarios, as well as any relevant
combinations thereof:
1 Existence of parent and/or child objects in the repository
1.1 ID not provided or NULL_ID: object does not exist and needs to be created
1.2 ID provided by batch creator (new_id): object does not (yet) exist in the repository — create with that ID
2 Provision of child objects (all need to be created/updated)
2.1 Parent without any Child1 or Child2 objects
2.2 Parent with Child1 objects only
2.3 Parent with Child2 objects only
2.4 Parent with both Child1 and Child2 objects
3 Links to reference data in child objects
3.1 Child object with reference data model ID (any except NULL_ID) and no code
3.1.1 Reference model ID not found: error
3.1.2 Reference model ID found: no issue
3.2 Child object with reference data model code and no ID (or NULL_ID)
3.2.1 Reference model code not found: error
3.2.2 Reference model code found: set reference model ID in Child object
3.3 Child object with both reference model ID (any except NULL_ID) and reference model code
3.3.1 Reference model ID and code do not match: error
3.3.2 Reference model ID and code match: no issue
3.4 Child2 object with no ID (or NULL_ID) and no code (reference is optional for Child2)
3.4.1 NULL_ID provided: error since eventual reference ID cannot be NULL_ID
3.4.2 NULL_ID not provided: no issue
4 Parent link in child objects
4.1 NULL_ID: not provided, parent object's ID (after creation, if applicable) to be set during upload
4.2 Actual parent ID
4.2.1 Parent does not exist yet or has different ID: error
4.2.2 Parent exists with that ID: no issue
5 Field mutability for parent and child objects that are already stored and will therefore be updated
5.1: Field that is always mutable
5.1.1: Single value field: field is set to new value
5.1.2: List field: field is set to new list of values
5.1.3: Dict field: individual keys in dict are updated/added/removed:
5.1.3.1 New key, new value not None: add key/value
5.1.3.2 New key, new value is None: do not add key
5.1.3.3 Existing key, new value not None: update key to new value
5.1.3.4 Existing key, new value is None: remove key
5.2: Field that is mutable if empty
5.2.1: Stored value is empty (None, empty list, empty dict): field is set to new value
5.2.2: Stored value is not empty, new value is empty: no issue
5.2.3: Stored value is not empty, new value is not empty: error
5.2.4: Stored UUID value is not empty, new value is NULL_ID: no error (NULL_ID = "not specified")
6 Provision of Identifiers for parent objects (use IdentifierType=PERSON for testing purposes)
6.1 No Identifiers provided: no issue
6.2 One Identifier provided
6.2.1 Existing Identifier i.e. (identifier_issuer, external_id) combination exists already
6.2.1.1 Parent ID None or NULL_ID: set parent ID in upload result
6.2.1.2 Parent ID provided
6.2.1.2.1 Same as existing Identifiers' parent ID: no issue
6.2.1.2.2 Different from existing Identifiers' parent ID: error
6.2.2 New Identifier i.e. (identifier_issuer, external_id) combination does not exist yet for this parent: create new Identifier once parent ID is known
6.2.3 Multiple Identifiers provided
6.2.3.1 Some existing Identifiers: must all point to the same parent ID AND same restrictions as 6.2 per Identifier
6.2.3.2 All new Identifiers: create new Identifiers once parent ID is known
6.3 Identifier issuer invalid
6.3.1 Identifier issuer ID (any except NULL_ID) provided and not found: error
6.3.2 Identifier issuer code provided and not found: error
6.3.3 Both identifier issuer ID (any except NULL_ID) and code provided and do not match: error
7 Upload command on_exists and on_new values
7.1 on_exists=ERROR: error if any existing object
7.2 on_exists=SKIP: skip any existing object, do not update
7.3 on_exists=UPDATE: update any existing object
7.4 on_new=CREATE: create any new object with provided ID (default)
7.5 on_new=SKIP: skip any new object, do not create
7.6 on_new=ERROR: error if any new object
8 Parametrized batch sizes
8.1 Batch of n new parent objects
8.2 Parent with n child objects
9 Identifiers for Child2 objects
9.1 No Identifiers provided: no issue
9.2 One Identifier provided
9.2.1 Existing Identifier i.e. (identifier_issuer, external_id) combination exists already
9.2.1.1 Child2 ID None or NULL_ID: set child2 ID in upload result
9.2.1.2 Child2 ID provided
9.2.1.2.1 Same as existing Identifiers' child2 ID: no issue
9.2.1.2.2 Different from existing Identifiers' child2 ID: error
9.2.2 New Identifier i.e. (identifier_issuer, external_id) combination does not exist yet for this child2: create new Identifier once child2 ID is known
9.2.3 Multiple Identifiers provided
9.2.3.1 Some existing Identifiers: must all point to the same child2 ID AND same restrictions as 9.2 per Identifier
9.2.3.2 All new Identifiers: create new Identifiers once child2 ID is known
9.3 Identifier issuer invalid
9.3.1 Identifier issuer ID (any except NULL_ID) provided and not found: error
9.3.2 Identifier issuer code provided and not found: error
9.3.3 Both identifier issuer ID (any except NULL_ID) and code provided and do not match: error
"""

from test.commondb.unit.upload.model import (
    Child1ForUpload,
    Child2,
    Child2ForUpload,
    Child2Identifier,
    Parent,
    ParentBatchForUpload,
    ParentBatchUploader,
    ParentBatchUploadResult,
    ParentForUpload,
    ParentIdentifier,
    Ref1,
    Ref2,
    UploadParentsCommand,
)
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import EtlStatus, Role, UploadAction, UploadStatusSet
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import (
    IdentifierForUpload,
    IdentifierIssuer,
    User,
)
from gen_epix.commondb.domain.model.upload import ParentUploadResult, UploadResult
from gen_epix.fastapp.app import App
from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class BaseUploadTestCase(TestCase):
    """Base test case with common fixtures and utilities."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Test user
        self.user = User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={Role.APP_ADMIN.value},
            organization_id=uuid4(),
            is_active=True,
        )

        # Test IDs
        self.parent_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.child1_id = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.child2_id = UUID("550e8400-e29b-41d4-a716-446655440003")
        self.ref1_id = UUID("550e8400-e29b-41d4-a716-446655440004")
        self.ref2_id = UUID("550e8400-e29b-41d4-a716-446655440005")
        self.identifier_issuer_id = UUID("550e8400-e29b-41d4-a716-446655440006")
        self.identifier_issuer_id2 = UUID("550e8400-e29b-41d4-a716-446655440007")
        self.identifier_issuer_code = "test_issuer"
        self.identifier_issuer_code2 = "test_issuer2"
        self.identifier_issuer = IdentifierIssuer(
            id=self.identifier_issuer_id,
            code=self.identifier_issuer_code,
            name="Test Issuer",
        )
        self.identifier_issuer2 = IdentifierIssuer(
            id=self.identifier_issuer_id2,
            code=self.identifier_issuer_code2,
            name="Test Issuer 2",
        )
        self.random_ids = [
            UUID("550e8400-e29b-41d4-a716-446655440010"),
            UUID("550e8400-e29b-41d4-a716-446655440011"),
            UUID("550e8400-e29b-41d4-a716-446655440012"),
            UUID("550e8400-e29b-41d4-a716-446655440013"),
            UUID("550e8400-e29b-41d4-a716-446655440014"),
            UUID("550e8400-e29b-41d4-a716-446655440015"),
            UUID("550e8400-e29b-41d4-a716-446655440016"),
            UUID("550e8400-e29b-41d4-a716-446655440017"),
            UUID("550e8400-e29b-41d4-a716-446655440018"),
            UUID("550e8400-e29b-41d4-a716-446655440019"),
        ]
        self.identifier_issuer_code_id_map = {
            self.identifier_issuer_code: self.identifier_issuer_id,
            self.identifier_issuer_code2: self.identifier_issuer_id2,
        }

        # Mock service
        self.service = Mock(spec=BaseService)
        self.service.generate_id = Mock(side_effect=uuid4)
        self.service.repository = Mock()

        # Mock UOW context manager
        self.uow = Mock(spec=BaseUnitOfWork)
        self.uow.__enter__ = Mock(return_value=self.uow)
        self.uow.__exit__ = Mock(return_value=None)
        self.service.repository.uow.return_value = self.uow

        # Mock repository methods
        self.service.repository.crud.return_value = []
        self.service.repository.read_fields.return_value = []

        # Mock app for cross-service calls
        self.service.app = Mock(spec=App)
        self.service.app.handle.return_value = []

        self.batch_uploader = ParentBatchUploader(self.service)

    def create_parent_for_upload(
        self,
        parent_id: UUID | None = None,
        a: str = "a",
        b: list[str] | None = None,
        c: dict[str, str | None] | None = None,
        x: str | None = None,
        y: list[str] | None = None,
        z: dict[str, str | None] | None = None,
        fk_id: UUID | None = None,
        identifiers: list[IdentifierForUpload] | None = None,
        children1: list[Child1ForUpload] | None = None,
        children2: list[Child2ForUpload] | None = None,
    ) -> ParentForUpload:
        """Create a test parent for upload."""
        return ParentForUpload(
            id=parent_id or NULL_ID,
            identifiers=identifiers,
            children1=children1,
            children2=children2,
            parent=Parent(
                a=a,
                b=b or [],
                c=c or {},
                x=x,
                y=y,
                z=z,
                fk_id=fk_id,
            ),
        )

    def get_parent_from_for_upload(
        self,
        parent_for_upload: ParentForUpload,
        id: UUID | None = None,
        a: str | None = None,
        b: list[str] | None = None,
        c: dict[str, str | None] | None = None,
        x: str | None = None,
        y: list[str] | None = None,
        z: dict[str, str | None] | None = None,
        fk_id: UUID | None = None,
    ) -> Parent:
        """Get the Parent model contained in a ParentForUpload model, with optional overrides."""
        parent = parent_for_upload.parent
        return Parent(
            id=id or parent.parent_id if parent else None,
            a=a or parent.a if parent else None,  # type: ignore[arg-type]
            b=b or parent.b if parent else None,  # type: ignore[arg-type]
            c=c
            or (
                {}
                if parent is None or parent.c is None
                else {x: y for x, y in parent.c.items() if y is not None}
            ),
            x=x or parent.x if parent else None,
            y=y or parent.y if parent else None,
            z=z
            or (
                {}
                if parent is None or parent.z is None
                else {x: y for x, y in parent.z.items() if y is not None}
            ),
            fk_id=fk_id if fk_id is not None else (parent.fk_id if parent else None),
        )

    def create_child1_for_upload(
        self,
        child_id: UUID | None = None,
        parent_id: UUID = NULL_ID,
        ref1_id: UUID = NULL_ID,
        ref1_code: str | None = None,
        a: str = "test_a",
        b: list[str] | None = None,
        c: dict[str, str | None] | None = None,
        x: str | None = None,
        y: list[str] | None = None,
        z: dict[str, str | None] | None = None,
    ) -> Child1ForUpload:
        """Create a test child1 for upload."""
        return Child1ForUpload(
            child1_id=child_id or NULL_ID,
            parent_id=parent_id,
            ref1_id=ref1_id,
            ref1_code=ref1_code,
            a=a,
            b=b or [],
            c=c or {},
            x=x,
            y=y,
            z=z,
        )

    def create_child2_for_upload(
        self,
        child_id: UUID | None = None,
        parent_id: UUID = NULL_ID,
        ref2_id: UUID | None = NULL_ID,
        ref2_code: str | None = None,
        a: str = "test_a",
        b: list[str] | None = None,
        c: dict[str, str | None] | None = None,
        x: str | None = None,
        y: list[str] | None = None,
        z: dict[str, str | None] | None = None,
        identifiers: list[IdentifierForUpload] | None = None,
    ) -> Child2ForUpload:
        """Create a test child2 for upload."""
        return Child2ForUpload(
            child2_id=child_id or NULL_ID,
            parent_id=parent_id,
            ref2_id=ref2_id,
            ref2_code=ref2_code,
            a=a,
            b=b or [],
            c=c or {},
            x=x,
            y=y,
            z=z,
            identifiers=identifiers,  # type: ignore[call-arg]
        )

    def create_command_for_parents(
        self,
        parents: list[ParentForUpload] | ParentForUpload,
        on_exists: UploadAction = UploadAction.UPDATE,
        on_new: UploadAction = UploadAction.CREATE,
        validate_command: bool = True,
    ) -> UploadParentsCommand:
        """Create a test upload command."""
        if not isinstance(parents, list):
            parents = [parents]
        if validate_command:
            parent_batch = ParentBatchForUpload(batch_id=uuid4(), parents=parents)  # type: ignore[call-arg]
        else:
            parent_batch = ParentBatchForUpload.model_construct(
                batch_id=uuid4(), parents=parents
            )
        cmd = UploadParentsCommand(
            user=self.user,
            parent_batch=parent_batch,
            on_exists=on_exists,  # type: ignore[call-arg]
            on_new=on_new,  # type: ignore[call-arg]
        )
        return cmd

    def create_ref1(self, ref_id: UUID, code: str = "test_code") -> Ref1:
        """Create a test Ref1 object."""
        return Ref1(id=ref_id, code=code, a="test_ref_a")

    def create_ref2(self, ref_id: UUID, code: str = "test_code") -> Ref2:
        """Create a test Ref2 object."""
        return Ref2(id=ref_id, code=code, a="test_ref_a")

    def create_identifier_for_upload(
        self,
        identifier_issuer_id: UUID | None = None,
        identifier_issuer_code: str = "test_issuer",
        external_id: str = "test_external_id",
    ) -> IdentifierForUpload:
        """Create a test IdentifierForUpload object."""
        return IdentifierForUpload(
            identifier_issuer_id=identifier_issuer_id or NULL_ID,
            identifier_issuer_code=identifier_issuer_code,
            external_id=external_id,
        )

    def get_parent_identifier_from_for_upload(
        self,
        identifier_for_upload: IdentifierForUpload,
        internal_id: UUID,
        identifier_issuer_id: UUID | None = None,
        external_id: str | None = None,
    ) -> ParentIdentifier:
        """Get the ParentIdentifier model corresponding to an IdentifierForUpload model, with optional overrides."""
        return ParentIdentifier(
            identifier_issuer_id=identifier_issuer_id
            or identifier_for_upload.identifier_issuer_id,  # type: ignore[arg-type]
            external_id=external_id or identifier_for_upload.external_id,
            internal_id=internal_id,
        )

    def get_child2_identifier_from_for_upload(
        self,
        identifier_for_upload: IdentifierForUpload,
        internal_id: UUID,
        identifier_issuer_id: UUID | None = None,
        external_id: str | None = None,
    ) -> Child2Identifier:
        """Get the Child2Identifier model corresponding to an IdentifierForUpload model, with optional overrides."""
        return Child2Identifier(
            identifier_issuer_id=identifier_issuer_id
            or identifier_for_upload.identifier_issuer_id,  # type: ignore[arg-type]
            external_id=external_id or identifier_for_upload.external_id,
            internal_id=internal_id,
        )

    def upload_batch(
        self,
        cmd: UploadParentsCommand | list[ParentForUpload] | ParentForUpload,
        on_exists: UploadAction = UploadAction.UPDATE,
        on_new: UploadAction = UploadAction.CREATE,
        validate_command: bool = True,
    ) -> ParentBatchUploadResult:
        """Upload a batch of parents and return the upload result."""
        if isinstance(cmd, UploadParentsCommand):
            pass
        else:
            cmd = self.create_command_for_parents(
                cmd,
                on_exists=on_exists,
                on_new=on_new,
                validate_command=validate_command,
            )
        batch_result = self.batch_uploader.upload_batch(
            cmd,
        )
        return batch_result  # type: ignore[return-value]

    def assertBatchProcessed(self, upload_result: UploadResult) -> None:
        if upload_result.status not in UploadStatusSet.PROCESSED.value:
            self.fail(
                f"Upload was not processed, status: {upload_result.status.value}",
            )

    def assertBatchFailed(self, upload_result: UploadResult) -> None:
        if upload_result.status not in UploadStatusSet.FAILED.value:
            self.fail(
                f"Upload did not fail, status: {upload_result.status.value}",
            )

    def assertHasLogCode(
        self, upload_result: UploadResult, code: list[str] | str
    ) -> None:
        if isinstance(code, str):
            code = [code]
        missing_codes = [x for x in code if not upload_result.has_log_code(x)]
        if missing_codes:
            missing_codes_str = ", ".join(missing_codes)
            if len(missing_codes) == 1:
                self.fail(f"Log missing for code {missing_codes_str}")
            self.fail(f"Logs missing for codes {missing_codes_str}")

    def assertStatusCount(
        self,
        upload_result: ParentUploadResult,
        n_skipped: int = 0,
        n_created: int = 0,
        n_updated: int = 0,
        n_failed: int = 0,
        n_pending: int = 0,
        n_processed: int = 0,
        n_initialized: int = 0,
        n_error: int = 0,
        n_mixed: int = 0,
        n_success: int = 0,
        include_self: bool = False,
    ) -> None:
        expected_status_count = {
            EtlStatus.SKIPPED: n_skipped,
            EtlStatus.CREATED: n_created,
            EtlStatus.UPDATED: n_updated,
            EtlStatus.FAILED: n_failed,
            EtlStatus.PENDING: n_pending,
            EtlStatus.PROCESSED: n_processed,
            EtlStatus.INITIALIZED: n_initialized,
            EtlStatus.ERROR: n_error,
            EtlStatus.MIXED: n_mixed,
            EtlStatus.SUCCESS: n_success,
        }
        actual_status_count = upload_result.get_status_count(include_self=include_self)
        different_status_count = {
            (x, expected_status_count[x], actual_status_count[x])
            for x in EtlStatus
            if actual_status_count[x] != expected_status_count[x]
        }
        if different_status_count:
            different_status_count_str = ""
            different_status_count_str = ", ".join(
                f"{x[0].value} ({x[1]}/{x[2]})" for x in different_status_count
            )
            self.fail(
                f"Status count mismatch (expected/actual): {different_status_count_str}"
            )


# Test Scenario 1: Existence of parent and/or child objects in the repository
@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test1ObjectExistence(BaseUploadTestCase):
    """Test scenarios related to object existence in repository."""

    def test_1_1_parent_id_not_provided_creates_new_object(self) -> None:
        """Test 1.1: ID not provided or NULL_ID - object does not exist and needs to be created."""
        # Create upload batch
        parent = self.create_parent_for_upload()
        # Set up mocks
        created_parent_id = self.random_ids[0]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1)
        self.assertEqual(batch_result.parents[0].id, created_parent_id)

    def test_1_2_parent_id_provided_as_new_id_succeeds(self) -> None:
        """Test 1.2: ID provided by batch creator (new_id); object does not exist yet - should be created with that ID."""
        # Create upload batch
        parent_for_upload = self.create_parent_for_upload(parent_id=self.parent_id)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [False],  # Parents exist
            [parent_for_upload.id],  # Create parents returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1)
        self.assertEqual(batch_result.parents[0].id, parent_for_upload.id)


# Test Scenario 2: Provision of child objects
@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test2ChildObjectProvision(BaseUploadTestCase):
    """Test scenarios related to providing different combinations of child objects."""

    def test_2_1_parent_without_children(self) -> None:
        """Test 2.1: Parent without any Child1 or Child2 objects."""
        # Create upload batch
        parent_for_upload = self.create_parent_for_upload()
        # Set up mocks
        created_parent_id = self.random_ids[0]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1)
        self.assertEqual(batch_result.parents[0].id, created_parent_id)

    def test_2_2_parent_with_child1_only(self) -> None:
        """Test 2.2: Parent with Child1 objects only."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "test_ref1_code")
        child1_for_upload = self.create_child1_for_upload(ref1_code=existing_ref1.code)
        parent_for_upload = self.create_parent_for_upload(children1=[child1_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_child1_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_child1_id,  # ID of the newly created child1
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
            [created_child1_id],  # Create children1 returned IDs
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(batch_result.parents[0].id, created_parent_id)
        self.assertEqual(batch_result.parents[0].children1[0].id, created_child1_id)  # type: ignore[index]

    def test_2_3_parent_with_child2_only(self) -> None:
        """Test 2.3: Parent with Child2 objects only."""
        # Create upload batch
        existing_ref2 = self.create_ref2(self.ref2_id, "test_ref2_code")
        child2_for_upload = self.create_child2_for_upload(ref2_code=existing_ref2.code)
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_child2_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_child2_id,  # ID of the newly created child2
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
            [created_child2_id],  # Create children2 returned IDs
        ]
        self.service.app.handle.side_effect = [
            [existing_ref2],  # Existing Ref2 objects
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(batch_result.parents[0].id, created_parent_id)
        self.assertEqual(batch_result.parents[0].children2[0].id, created_child2_id)  # type: ignore[index]

    def test_2_4_parent_with_both_children(self) -> None:
        """Test 2.4: Parent with both Child1 and Child2 objects."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "test_ref1_code")
        existing_ref2 = self.create_ref2(self.ref2_id, "test_ref2_code")
        child1_for_upload = self.create_child1_for_upload(ref1_code=existing_ref1.code)
        child2_for_upload = self.create_child2_for_upload(ref2_code=existing_ref2.code)
        parent_for_upload = self.create_parent_for_upload(
            children1=[child1_for_upload], children2=[child2_for_upload]
        )
        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_child1_id = self.random_ids[1]
        created_child2_id = self.random_ids[2]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_child1_id,  # ID of the newly created child1
            created_child2_id,  # ID of the newly created child2
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
            [created_child1_id],  # Create children1 returned IDs
            [created_child2_id],  # Create children2 returned IDs
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],  # Existing Ref1 (ID, code) pairs
        ]
        self.service.app.handle.side_effect = [
            [existing_ref2],  # Existing Ref2 objects
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=3)
        self.assertEqual(batch_result.parents[0].id, created_parent_id)
        self.assertEqual(batch_result.parents[0].children1[0].id, created_child1_id)  # type: ignore[index]
        self.assertEqual(batch_result.parents[0].children2[0].id, created_child2_id)  # type: ignore[index]


# Test Scenario 3: Links to reference data in child objects
@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test3ReferenceDataLinks(BaseUploadTestCase):
    """Test scenarios related to reference data linking in child objects."""

    def test_3_1_1_ref_id_provided_not_found_fails(self) -> None:
        """Test 3.1.1: Reference model ID not found - should fail."""
        # Create upload batch
        child1_for_upload = self.create_child1_for_upload(
            ref1_id=self.random_ids[0], ref1_code=None
        )
        parent_for_upload = self.create_parent_for_upload(children1=[child1_for_upload])
        # Set up mocks
        self.service.repository.read_fields.side_effect = [
            [],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=1)

    def test_3_1_2_ref_id_provided_and_found_succeeds(self) -> None:
        """Test 3.1.2: Reference model ID found - should succeed."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1_for_upload = self.create_child1_for_upload(ref1_id=existing_ref1.id, ref1_code=None)  # type: ignore[arg-type]
        parent_for_upload = self.create_parent_for_upload(children1=[child1_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_child1_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_child1_id,  # ID of the newly created child1
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
            [created_child1_id],  # Create children1 returned IDs
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(batch_result.parents[0].id, created_parent_id)
        self.assertEqual(batch_result.parents[0].children1[0].id, created_child1_id)  # type: ignore[index]

    def test_3_2_1_ref_code_provided_not_found_fails(self) -> None:
        """Test 3.2.1: Reference model code not found - should fail."""
        # Create upload batch
        child1_for_upload = self.create_child1_for_upload(
            ref1_id=NULL_ID, ref1_code="non_existent_code"
        )
        parent_for_upload = self.create_parent_for_upload(children1=[child1_for_upload])
        # Set up mocks
        self.service.repository.read_fields.side_effect = [
            [],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=1)

    def test_3_2_2_ref_code_provided_and_found_sets_id(self) -> None:
        """Test 3.2.2: Reference model code found - should succeed (and set reference model ID)."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1_for_upload = self.create_child1_for_upload(
            ref1_id=NULL_ID, ref1_code=existing_ref1.code
        )
        parent_for_upload = self.create_parent_for_upload(children1=[child1_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_child1_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_child1_id,  # ID of the newly created child1
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
            [created_child1_id],  # Create children1 returned IDs
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(batch_result.parents[0].id, created_parent_id)
        self.assertEqual(batch_result.parents[0].children1[0].id, created_child1_id)  # type: ignore[index]
        self.assertEqual(child1_for_upload.ref1_id, self.ref1_id)

    def test_3_3_1_ref_id_and_code_mismatch_fails(self) -> None:
        """Test 3.3.1: Reference model ID and code do not match but both exist - should fail."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        other_existing_ref1 = self.create_ref1(
            self.random_ids[0], "other_existing_code"
        )
        child1_for_upload = self.create_child1_for_upload(ref1_id=existing_ref1.id, ref1_code=other_existing_ref1.code)  # type: ignore[arg-type]
        parent_for_upload = self.create_parent_for_upload(children1=[child1_for_upload])
        # Set up mocks
        self.service.repository.read_fields.side_effect = [
            [
                (existing_ref1.id, existing_ref1.code),
                (other_existing_ref1.id, other_existing_ref1.code),
            ],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=1)

    def test_3_3_2_ref_id_and_code_match_succeeds(self) -> None:
        """Test 3.3.2: Reference model ID and code match - should succeed."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1_for_upload = self.create_child1_for_upload(ref1_id=existing_ref1.id, ref1_code=existing_ref1.code)  # type: ignore[arg-type]
        parent_for_upload = self.create_parent_for_upload(children1=[child1_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_child1_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_child1_id,  # ID of the newly created child1
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
            [created_child1_id],  # Create children1 returned IDs
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)

    def test_3_4_1_child2_null_id_no_code_provided_fails(self) -> None:
        """Test 3.4.1: Child2 with ref ID NULL_ID and no code provided - should fail since eventual reference ID cannot be NULL_ID."""
        # Create upload batch
        child2_for_upload = self.create_child2_for_upload(
            ref2_id=NULL_ID, ref2_code=None
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=1)

    def test_3_4_2_child2_no_id_or_code_succeeds(self) -> None:
        """Test 3.4.2: Child2 with no ID or code - should succeed (reference is optional)."""
        # Create upload batch
        child2_for_upload = self.create_child2_for_upload(ref2_id=None, ref2_code=None)
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_child2_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_child2_id,  # ID of the newly created child2
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
            [created_child2_id],  # Create children2 returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(parent_for_upload.children2[0].ref2_id, None)  # type: ignore[index]


# Test Scenario 4: Parent link in child objects
@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test4ParentLinks(BaseUploadTestCase):
    """Test scenarios related to parent links in child objects."""

    def test_4_1_child_null_parent_id_set_during_upload(self) -> None:
        """Test 4.1: NULL_ID parent - should be set during upload."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1_for_upload = self.create_child1_for_upload(
            parent_id=NULL_ID, ref1_id=existing_ref1.id  # type: ignore[arg-type]
        )
        parent_for_upload = self.create_parent_for_upload(children1=[child1_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_child1_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_child1_id,  # ID of the newly created child1
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
            [created_child1_id],  # Create children1 returned IDs
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(parent_for_upload.children1[0].parent_id, created_parent_id)  # type: ignore[index]

    def test_4_2_1_child_parent_id_parent_not_exists_fails(self) -> None:
        """Test 4.2.1: Parent does not exist or has different ID - should fail."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1_for_upload = self.create_child1_for_upload(
            parent_id=self.parent_id, ref1_id=existing_ref1.id  # type: ignore[arg-type]
        )
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id, children1=[child1_for_upload]
        )
        parent_for_upload.id = self.random_ids[1]  # Different ID than child's parent_id
        # Set up mocks
        created_child1_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_child1_id,  # ID of the newly created child1
        ]
        self.service.repository.crud.side_effect = [
            [False],  # Parents exist
            [created_child1_id],  # Create children1 returned IDs
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(
            parent_for_upload, validate_command=False
        )  # Skip command validation to allow inconsistent IDs
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_pending=1, n_failed=1)

    def test_4_2_2_child_parent_id_matches_succeeds(self) -> None:
        """Test 4.2.2: Parent exists with matching ID - should succeed."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1_for_upload = self.create_child1_for_upload(
            parent_id=self.parent_id, ref1_id=existing_ref1.id  # type: ignore[arg-type]
        )
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id, children1=[child1_for_upload]
        )
        existing_parent = self.get_parent_from_for_upload(parent_for_upload)
        # Set up mocks
        created_parent_id = parent_for_upload.id
        created_child1_id = self.random_ids[0]
        self.service.generate_id.side_effect = [
            created_child1_id,  # ID of the newly created child1
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [created_child1_id],  # Create children1 returned IDs
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=1, n_created=1)
        self.assertEqual(parent_for_upload.id, created_parent_id)
        self.assertEqual(batch_result.parents[0].children1[0].id, created_child1_id)  # type: ignore[index]


# Test Scenario 5: Field mutability for stored objects
@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test5FieldMutability(BaseUploadTestCase):
    """Test scenarios related to field mutability for existing objects."""

    def test_5_1_1_always_mutable_single_value_field(self) -> None:
        """Test 5.1.1: Always mutable single value field - should be updated."""
        # Create upload batch
        existing_value = "value"
        new_value = "new_value"
        resulting_value = new_value
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id, a=new_value
        )
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, a=existing_value
        )
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.parent_id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_updated=1)
        self.assertEqual(existing_parent.a, resulting_value)

    def test_5_1_2_always_mutable_list_field(self) -> None:
        """Test 5.1.2: Always mutable list field - should be updated."""
        # Create upload batch
        existing_value = ["value1", "value2"]
        new_value = ["new_value1", "new_value2", "new_value3"]
        resulting_value = new_value
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id, b=new_value
        )
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, b=existing_value
        )
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.parent_id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_updated=1)
        self.assertEqual(existing_parent.b, resulting_value)

    def test_5_1_3_1_always_mutable_dict_add_new_key(self) -> None:
        """Test 5.1.3.1: Dict field - add new key with non-None value."""
        # Create upload batch
        existing_value = {"key1": "value1", "key2": "value2"}
        new_value = {"key3": "value3"}
        resulting_value = existing_value.copy()
        resulting_value.update(new_value)
        parent_for_upload = self.create_parent_for_upload(parent_id=self.parent_id, c=new_value)  # type: ignore[arg-type]
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, c=existing_value
        )
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.parent_id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_updated=1)
        self.assertEqual(existing_parent.c, resulting_value)

    def test_5_1_3_2_always_mutable_dict_new_key_none_value(self) -> None:
        """Test 5.1.3.2: Dict field - new key with None value should not be added."""
        # Create upload batch
        existing_value = {"key1": "value1", "key2": "value2"}
        new_value = {"key3": None}
        resulting_value = existing_value
        parent_for_upload = self.create_parent_for_upload(parent_id=self.parent_id, c=new_value)  # type: ignore[arg-type]
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, c=existing_value
        )
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.parent_id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=1)
        self.assertEqual(existing_parent.c, resulting_value)

    def test_5_1_3_3_always_mutable_dict_update_existing_key(self) -> None:
        """Test 5.1.3.3: Dict field - update existing key with new value."""
        # Create upload batch
        existing_value = {"key1": "value1", "key2": "value2"}
        new_value = {"key1": "new_value1"}
        resulting_value = existing_value.copy()
        resulting_value.update(new_value)
        parent_for_upload = self.create_parent_for_upload(parent_id=self.parent_id, c=new_value)  # type: ignore[arg-type]
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, c=existing_value
        )
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.parent_id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_updated=1)
        self.assertEqual(existing_parent.c, resulting_value)

    def test_5_1_3_4_always_mutable_dict_remove_existing_key(self) -> None:
        """Test 5.1.3.4: Dict field - remove existing key when new value is None."""
        # Create upload batch
        existing_value = {"key1": "value1", "key2": "value2"}
        new_value = {"key1": None}
        resulting_value = existing_value.copy()
        resulting_value.pop("key1")
        parent_for_upload = self.create_parent_for_upload(parent_id=self.parent_id, c=new_value)  # type: ignore[arg-type]
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, c=existing_value
        )
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.parent_id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_updated=1)
        self.assertEqual(existing_parent.c, resulting_value)

    def test_5_2_1_mutable_if_empty_stored_empty_updated(self) -> None:
        """Test 5.2.1: Mutable if empty - stored None, new value set."""
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id, x="new"
        )
        # Build existing parent with x=None independently (helper can't set x to None)
        existing_parent = Parent(parent_id=self.parent_id, a="a", b=[], c={}, x=None)
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.parent_id],  # Updated parents returned IDs
        ]
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_updated=1)
        self.assertEqual(existing_parent.x, "new")

    def test_5_2_2_mutable_if_empty_stored_not_empty_new_empty(self) -> None:
        """Test 5.2.2: Mutable if empty - stored not empty, new None, no change."""
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id, x=None
        )
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, x="existing"
        )
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
        ]
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=1)
        self.assertEqual(existing_parent.x, "existing")

    def test_5_2_3_mutable_if_empty_stored_not_empty_new_not_empty_fails(self) -> None:
        """Test 5.2.3: Mutable if empty - stored not empty, new different value, error."""
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id, x="new"
        )
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, x="existing"
        )
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
        ]
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1)

    def test_5_2_4_immutable_uuid_null_id_treated_as_not_specified(self) -> None:
        """Test 5.2.4: Immutable UUID field - NULL_ID is treated as "not specified", no error."""
        stored_fk_id = self.random_ids[0]
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id, fk_id=NULL_ID
        )
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, fk_id=stored_fk_id
        )
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
        ]
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=1)
        self.assertEqual(existing_parent.fk_id, stored_fk_id)


# Test Scenario 6: Identifiers for parent objects
@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test6Identifiers(BaseUploadTestCase):
    """Test scenarios related to Identifiers for parent objects."""

    def test_6_1_no_identifiers_provided(self) -> None:
        """Test 6.1: No Identifiers provided - should succeed."""
        # Create upload batch
        parent_for_upload = self.create_parent_for_upload(identifiers=None)
        # Set up mocks
        created_parent_id = self.parent_id
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create children1 returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1)

    def test_6_2_1_1_existing_identifier_null_parent_sets_id(self) -> None:
        """Test 6.2.1.1: Existing Identifier with NULL parent ID - should set parent ID."""
        # Create upload batch
        identifier = self.create_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        existing_parent_id = self.random_ids[0]
        existing_identifier = self.get_parent_identifier_from_for_upload(
            identifier, internal_id=existing_parent_id
        )
        parent_for_upload = self.create_parent_for_upload(identifiers=[identifier])
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, id=existing_parent_id
        )
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the Identifiers
            [existing_identifier],  # The existing Identifiers
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=2)
        self.assertEqual(batch_result.parents[0].id, existing_parent_id)  # type

    def test_6_2_1_2_1_existing_identifier_same_parent_succeeds(self) -> None:
        """Test 6.2.1.2.1: Existing Identifier with same parent ID - should succeed."""
        # Create upload batch
        identifier = self.create_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        existing_parent_id = self.random_ids[0]
        existing_identifier = self.get_parent_identifier_from_for_upload(
            identifier, internal_id=existing_parent_id
        )
        parent_for_upload = self.create_parent_for_upload(
            parent_id=existing_parent_id, identifiers=[identifier]
        )
        existing_parent = self.get_parent_from_for_upload(parent_for_upload)
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the Identifiers
            [existing_identifier],  # The existing Identifiers
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=2)

    def test_6_2_1_2_2_existing_identifier_different_parent_fails(self) -> None:
        """Test 6.2.1.2.2: Existing Identifier with different parent ID - should fail."""
        # Create upload batch
        identifier = self.create_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        other_parent_id = self.random_ids[0]
        existing_parent_id = self.random_ids[1]
        existing_identifier = self.get_parent_identifier_from_for_upload(
            identifier, internal_id=other_parent_id
        )
        parent_for_upload = self.create_parent_for_upload(
            parent_id=existing_parent_id, identifiers=[identifier]
        )
        existing_parent = self.get_parent_from_for_upload(parent_for_upload)
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the Identifiers
            [existing_identifier],  # The existing Identifiers
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=1)

    def test_6_2_2_new_identifier_new_parent(self) -> None:
        """Test 6.2.2: New Identifier for new parent - should succeed."""
        # Create upload batch
        identifier_for_upload = self.create_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        created_parent_id = self.random_ids[1]
        parent_for_upload = self.create_parent_for_upload(
            identifiers=[identifier_for_upload]
        )
        identifier = self.get_parent_identifier_from_for_upload(
            identifier_for_upload,
            internal_id=created_parent_id,
        )
        created_identifier_id = identifier.id
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the Identifiers
            [],  # No existing Identifiers
            [created_identifier_id],  # Created Identifier ID
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(batch_result.parents[0].id, created_parent_id)
        self.assertEqual(
            batch_result.parents[0].identifiers[0].id,  # type: ignore[index]
            created_identifier_id,
        )

    def test_6_2_3_1_multiple_identifiers_some_existing_same_parent(self) -> None:
        """Test 6.2.3.1: Multiple Identifiers, some existing for same parent - should succeed."""
        # Create upload batch
        identifier_for_upload1 = self.create_identifier_for_upload(
            external_id="ext_id_1", identifier_issuer_id=self.identifier_issuer_id
        )
        identifier_for_upload2 = self.create_identifier_for_upload(
            external_id="ext_id_2",
            identifier_issuer_id=self.identifier_issuer_id2,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id,
            identifiers=[
                identifier_for_upload1,
                identifier_for_upload2,
            ],
        )
        existing_identifier1 = self.get_parent_identifier_from_for_upload(
            identifier_for_upload1,
            parent_for_upload.id,  # type: ignore[arg-type]
        )
        created_identifier2 = self.get_parent_identifier_from_for_upload(
            identifier_for_upload2,
            parent_for_upload.id,  # type: ignore[arg-type]
        )
        # Set up mocks
        self.service.app.handle.side_effect = [
            [
                self.identifier_issuer,
                self.identifier_issuer2,
            ],  # The identifier issuers in the Identifiers
            [existing_identifier1],  # The existing Identifiers before creation
            [created_identifier2],
        ]
        existing_parent = self.get_parent_from_for_upload(parent_for_upload)
        self.service.repository.crud.side_effect = [
            [True],  # Parent exists
            [existing_parent],  # Return the existing parent object
        ]

        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1, n_skipped=2)

    def test_6_2_3_1_multiple_identifiers_some_existing_different_parent(self) -> None:
        """Test 6.2.3.1: Multiple Identifiers, some existing for different parent - should fail."""
        # Create upload batch
        identifier1 = self.create_identifier_for_upload(
            external_id="ext_id_1", identifier_issuer_id=self.random_ids[1]
        )
        identifier2 = self.create_identifier_for_upload(
            external_id="ext_id_2",
            identifier_issuer_id=self.identifier_issuer_id2,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        parent_for_upload = self.create_parent_for_upload(
            identifiers=[identifier1, identifier2]
        )
        different_id = self.random_ids[0]
        existing_identifier1 = self.get_parent_identifier_from_for_upload(
            identifier1,
            different_id,  # Different parent ID
        )
        # Set up mocks
        self.service.app.handle.side_effect = [
            [
                self.identifier_issuer,
                self.identifier_issuer2,
            ],  # The identifier issuers in the Identifiers
            [existing_identifier1],  # The existing Identifiers
        ]

        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=2)

    def test_6_2_3_2_multiple_identifiers_all_new_same_issuer(self) -> None:
        """Test 6.2.3.2: Multiple Identifiers, all new but same issuer - should fail."""
        # Create upload batch
        identifier1 = self.create_identifier_for_upload(
            external_id="new_ext_id_1", identifier_issuer_id=self.identifier_issuer_id
        )
        identifier2 = self.create_identifier_for_upload(
            external_id="new_ext_id_2", identifier_issuer_id=self.identifier_issuer_id
        )
        with pytest.raises(ValueError):
            parent_for_upload = self.create_parent_for_upload(
                identifiers=[identifier1, identifier2]
            )

    def test_6_2_3_2_multiple_identifiers_all_new_different_issuer(self) -> None:
        """Test 6.2.3.2: Multiple Identifiers, all new and different issuer - should succeed."""
        # Create upload batch
        identifier_for_upload1 = self.create_identifier_for_upload(
            external_id="new_ext_id_1", identifier_issuer_id=self.identifier_issuer_id
        )
        identifier_for_upload2 = self.create_identifier_for_upload(
            external_id="new_ext_id_2",
            identifier_issuer_id=self.identifier_issuer_id2,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        parent_for_upload = self.create_parent_for_upload(
            identifiers=[
                identifier_for_upload1,
                identifier_for_upload2,
            ]
        )
        created_parent_id = self.random_ids[0]
        created_identifier1_id = self.random_ids[1]
        created_identifier2_id = self.random_ids[2]
        self.service.generate_id.side_effect = [
            created_parent_id,
            created_identifier1_id,
            created_identifier2_id,
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
        ]

        # Set up mocks
        self.service.app.handle.side_effect = [
            [
                self.identifier_issuer,
                self.identifier_issuer2,
            ],  # The identifier issuers in the Identifiers
            [],  # No existing Identifiers
            [
                created_identifier1_id,
                created_identifier2_id,
            ],  # Created Identifier IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=3)

    # TODO: create tests for scenarios 6.3 on invalid identifier issuer


# Test Scenario 7: Upload command on_exists and on_new values
@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test7OnExistsAndOnNewActions(BaseUploadTestCase):
    """Test scenarios related to the on_exists and on_new command parameters."""

    def test_7_1_on_exists_error_with_existing_object_fails(self) -> None:
        """Test 7.1: on_exists=ERROR with existing object - should fail."""
        # Create upload batch
        parent_for_upload = self.create_parent_for_upload(parent_id=self.parent_id)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # EXISTS_SOME: parent exists
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(
            parent_for_upload, on_exists=UploadAction.ERROR
        )
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1)

    def test_7_2_on_exists_skip_with_existing_object_skips(self) -> None:
        """Test 7.2: on_exists=SKIP with existing object - should skip."""
        # Create upload batch
        parent_for_upload = self.create_parent_for_upload(parent_id=self.parent_id)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # EXISTS_SOME: parent exists
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload, on_exists=UploadAction.SKIP)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=1)

    def test_7_3_on_exists_update_with_existing_object_updates(self) -> None:
        """Test 7.3: on_exists=UPDATE with existing object - should update."""
        # Create upload batch
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id, a="new_value"
        )
        # Set up mocks
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, a="old_value"
        )
        self.service.repository.crud.side_effect = [
            [True],  # EXISTS_SOME: parent exists
            [existing_parent],  # READ_SOME: retrieve existing parent for comparison
            [self.parent_id],  # UPDATE_SOME: update returns ID
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(
            parent_for_upload, on_exists=UploadAction.UPDATE
        )
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_updated=1)

    def test_7_4_on_new_create_with_new_id_creates(self) -> None:
        """Test 7.4: on_new=CREATE with new object having provided ID - should create."""
        # Create upload batch with explicit ID that does not yet exist
        parent_for_upload = self.create_parent_for_upload(parent_id=self.parent_id)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [False],  # EXISTS_SOME: parent does not exist
            [self.parent_id],  # CREATE_SOME: create returns provided ID
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload, on_new=UploadAction.CREATE)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1)

    def test_7_5_on_new_skip_with_new_id_skips(self) -> None:
        """Test 7.5: on_new=SKIP with new object having provided ID - should skip."""
        # Create upload batch with explicit ID that does not yet exist
        parent_for_upload = self.create_parent_for_upload(parent_id=self.parent_id)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [False],  # EXISTS_SOME: parent does not exist
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload, on_new=UploadAction.SKIP)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=1)

    def test_7_6_on_new_error_with_new_id_fails(self) -> None:
        """Test 7.6: on_new=ERROR with new object having provided ID - should fail."""
        # Create upload batch with explicit ID that does not yet exist
        parent_for_upload = self.create_parent_for_upload(parent_id=self.parent_id)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [False],  # EXISTS_SOME: parent does not exist
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload, on_new=UploadAction.ERROR)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1)


# Test Scenario 8: Parameterized batch sizes
@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test8ParameterizedBatchSizes(BaseUploadTestCase):
    """Test upload with varying batch sizes."""

    def test_8_batch_of_n_new_parents(self) -> None:
        """Test 8.1: Upload batch of n new parent objects."""
        for n_parents in [1, 3, 5]:
            with self.subTest(n_parents=n_parents):
                self.setUp()  # Reset mocks for each subtest
                parents_for_upload = [
                    self.create_parent_for_upload() for _ in range(n_parents)
                ]
                created_ids = self.random_ids[:n_parents]
                self.service.repository.crud.side_effect = [
                    created_ids,  # CREATE_SOME: create parents returns IDs
                ]
                batch_result = self.upload_batch(parents_for_upload)
                self.assertBatchProcessed(batch_result)
                self.assertStatusCount(batch_result, n_created=n_parents)
                for i, created_id in enumerate(created_ids):
                    self.assertEqual(batch_result.parents[i].id, created_id)

    def test_8_parent_with_n_children(self) -> None:
        """Test 8.2: Upload parent with varying number of Child1 objects."""
        ref1_code = "test_ref1_code"
        for n_children in [0, 1, 3]:
            with self.subTest(n_children=n_children):
                self.setUp()  # Reset mocks for each subtest
                children1 = [
                    self.create_child1_for_upload(ref1_code=ref1_code)
                    for _ in range(n_children)
                ]
                parent_for_upload = self.create_parent_for_upload(
                    children1=children1 if children1 else None,
                )
                created_parent_id = self.random_ids[0]
                created_child_ids = self.random_ids[1 : 1 + n_children]
                crud_side_effects: list[list] = [
                    [created_parent_id],  # CREATE_SOME: create parent returns ID
                ]
                if n_children > 0:
                    crud_side_effects.append(
                        created_child_ids
                    )  # CREATE_SOME: create children returns IDs
                self.service.repository.crud.side_effect = crud_side_effects
                if n_children > 0:
                    self.service.repository.read_fields.side_effect = [
                        [(self.ref1_id, ref1_code)],  # Resolve Ref1 by code
                    ]
                batch_result = self.upload_batch(parent_for_upload)
                self.assertBatchProcessed(batch_result)
                self.assertStatusCount(batch_result, n_created=1 + n_children)


# Test Scenario 9: Identifiers for Child2 objects
@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test9Child2Identifiers(BaseUploadTestCase):
    """Test scenarios related to Identifiers for Child2 objects."""

    def test_9_1_no_identifiers_provided(self) -> None:
        """Test 9.1: No Identifiers provided for Child2 - should succeed."""
        # Create upload batch with Child2 that has no Identifiers
        child2_for_upload = self.create_child2_for_upload(
            ref2_id=None, ref2_code=None, identifiers=None
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_child2_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_child2_id,  # ID of the newly created child2
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
            [created_child2_id],  # Create children2 returned IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)

    def test_9_2_1_1_existing_identifier_null_child2_sets_id(self) -> None:
        """Test 9.2.1.1: Existing Identifier with NULL child2 ID - should set child2 ID."""
        # Create upload batch
        identifier = self.create_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        existing_child2_id = self.random_ids[0]
        existing_identifier = self.get_child2_identifier_from_for_upload(
            identifier, internal_id=existing_child2_id
        )
        child2_for_upload = self.create_child2_for_upload(
            ref2_id=None, ref2_code=None, identifiers=[identifier]
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[1]
        existing_child = Child2(
            id=existing_child2_id,
            parent_id=created_parent_id,
            ref2_id=None,
            a="test_a",
            b=[],
            c={},
            x=None,
            y=None,
            z=None,
        )
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the Identifiers
            [existing_identifier],  # The existing Identifiers
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Child exists
            [created_parent_id],  # Create parent
            [existing_child],  # Existing child for update check
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_child2_id, created_parent_id)],
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1, n_skipped=2)
        self.assertEqual(batch_result.parents[0].children2[0].id, existing_child2_id)  # type: ignore[index]

    def test_9_2_1_2_1_existing_identifier_same_child2_succeeds(self) -> None:
        """Test 9.2.1.2.1: Existing Identifier with same child2 ID - should succeed."""
        # Create upload batch
        identifier = self.create_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        existing_child2_id = self.random_ids[0]
        existing_identifier = self.get_child2_identifier_from_for_upload(
            identifier, internal_id=existing_child2_id
        )
        child2_for_upload = self.create_child2_for_upload(
            child_id=existing_child2_id,
            ref2_id=None,
            ref2_code=None,
            identifiers=[identifier],
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[1]
        existing_child = Child2(
            child2_id=existing_child2_id,
            parent_id=created_parent_id,
            ref2_id=None,
            a="test_a",
            b=[],
            c={},
            x=None,
            y=None,
            z=None,
        )
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the Identifiers
            [existing_identifier],  # The existing Identifiers
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Child exists
            [created_parent_id],  # Create parent
            [existing_child],  # Existing child for update check
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_child2_id, created_parent_id)],
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1, n_skipped=2)

    def test_9_2_1_2_2_existing_identifier_different_child2_fails(self) -> None:
        """Test 9.2.1.2.2: Existing Identifier with different child2 ID - should fail."""
        # Create upload batch
        identifier = self.create_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        other_child2_id = self.random_ids[0]
        existing_child2_id = self.random_ids[1]
        existing_identifier = self.get_child2_identifier_from_for_upload(
            identifier, internal_id=other_child2_id
        )
        child2_for_upload = self.create_child2_for_upload(
            child_id=existing_child2_id,
            ref2_id=None,
            ref2_code=None,
            identifiers=[identifier],
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[2]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the Identifiers
            [existing_identifier],  # The existing Identifiers
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Child exists
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_child2_id, created_parent_id)],
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=2)

    def test_9_2_2_new_identifier_new_child2(self) -> None:
        """Test 9.2.2: New Identifier for new child2 - should succeed."""
        # Create upload batch
        identifier_for_upload = self.create_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        created_parent_id = self.random_ids[0]
        created_child2_id = self.random_ids[1]
        created_identifier_id = self.random_ids[2]
        child2_for_upload = self.create_child2_for_upload(
            ref2_id=None,
            ref2_code=None,
            identifiers=[identifier_for_upload],
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the Identifiers
            [],  # No existing Identifiers
            [created_identifier_id],  # Created Identifier ID
        ]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_child2_id,  # ID of the newly created child2
            created_identifier_id,  # ID for child Identifier
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parent
            [created_child2_id],  # Create child2
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=3)
        self.assertEqual(batch_result.parents[0].children2[0].id, created_child2_id)  # type: ignore[index]
        self.assertEqual(
            batch_result.parents[0].children2[0].identifiers[0].id,  # type: ignore[index]
            created_identifier_id,
        )

    def test_9_2_3_1_multiple_identifiers_some_existing_same_child2(self) -> None:
        """Test 9.2.3.1: Multiple Identifiers, some existing for same child2 - should succeed."""
        # Create upload batch
        identifier1 = self.create_identifier_for_upload(external_id="ext_id_1")
        identifier2 = self.create_identifier_for_upload(
            external_id="ext_id_2",
            identifier_issuer_id=self.identifier_issuer_id2,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        child2_for_upload = self.create_child2_for_upload(
            child_id=self.child2_id,
            ref2_id=None,
            ref2_code=None,
            identifiers=[identifier1, identifier2],
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        existing_identifier1 = self.get_child2_identifier_from_for_upload(
            identifier1,
            self.child2_id,  # type: ignore[arg-type]
        )
        created_identifier2 = self.get_child2_identifier_from_for_upload(
            identifier2,
            self.child2_id,  # type: ignore[arg-type]
        )
        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_identifier2_id = self.random_ids[1]
        existing_child = Child2(
            child2_id=self.child2_id,
            parent_id=created_parent_id,
            ref2_id=None,
            a="test_a",
            b=[],
            c={},
            x=None,
            y=None,
            z=None,
        )
        self.service.app.handle.side_effect = [
            [
                self.identifier_issuer,
                self.identifier_issuer2,
            ],  # The identifier issuers in the Identifiers
            [existing_identifier1],  # Existing Identifiers
            [created_identifier2_id],  # Created Identifier ID
        ]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
            created_identifier2_id,  # ID for child Identifier
            self.random_ids[2],  # Spare ID in case another Identifier is created
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Child exists
            [created_parent_id],  # Create parent
            [existing_child],  # Existing child for update check
        ]
        self.service.repository.read_fields.side_effect = [
            [(self.child2_id, created_parent_id)],
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2, n_skipped=1, n_pending=1)

    def test_9_2_3_1_multiple_identifiers_some_existing_different_child2(self) -> None:
        """Test 9.2.3.1: Multiple Identifiers, some existing for different child2 - should fail."""
        # Create upload batch
        identifier1 = self.create_identifier_for_upload(
            external_id="ext_id_1", identifier_issuer_id=self.random_ids[2]
        )
        identifier2 = self.create_identifier_for_upload(
            external_id="ext_id_2",
            identifier_issuer_id=self.identifier_issuer_id2,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        child2_for_upload = self.create_child2_for_upload(
            ref2_id=None,
            ref2_code=None,
            identifiers=[identifier1, identifier2],
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        different_id = self.random_ids[0]
        existing_identifier1 = self.get_child2_identifier_from_for_upload(
            identifier1,
            different_id,  # Different child2 ID
        )
        # Set up mocks
        self.service.app.handle.side_effect = [
            [
                self.identifier_issuer,
                self.identifier_issuer2,
            ],  # The identifier issuers in the Identifiers
            [existing_identifier1],  # The existing Identifiers
        ]
        self.service.repository.crud.side_effect = [
            [False],  # Child does not exist
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=3)

    def test_9_2_3_2_multiple_identifiers_all_new_same_issuer(self) -> None:
        """Test 9.2.3.2: Multiple Identifiers all new but same issuer - should fail."""
        # Create upload batch
        identifier1 = self.create_identifier_for_upload(
            external_id="new_ext_id_1", identifier_issuer_id=self.identifier_issuer_id
        )
        identifier2 = self.create_identifier_for_upload(
            external_id="new_ext_id_2", identifier_issuer_id=self.identifier_issuer_id
        )
        with pytest.raises(ValueError):
            self.create_child2_for_upload(
                ref2_id=None,
                ref2_code=None,
                identifiers=[identifier1, identifier2],
            )

    def test_9_2_3_2_multiple_identifiers_all_new_different_issuer(self) -> None:
        """Test 9.2.3.2: Multiple Identifiers all new and different issuer - should succeed."""
        # Create upload batch
        identifier1 = self.create_identifier_for_upload(
            external_id="new_ext_id_1", identifier_issuer_id=self.identifier_issuer_id
        )
        identifier2 = self.create_identifier_for_upload(
            external_id="new_ext_id_2",
            identifier_issuer_id=self.identifier_issuer_id2,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        child2_for_upload = self.create_child2_for_upload(
            ref2_id=None,
            ref2_code=None,
            identifiers=[identifier1, identifier2],
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        created_parent_id = self.random_ids[0]
        created_child2_id = self.random_ids[1]
        created_identifier1_id = self.random_ids[2]
        created_identifier2_id = self.random_ids[3]
        self.service.generate_id.side_effect = [
            created_parent_id,
            created_child2_id,
            created_identifier1_id,
            created_identifier2_id,
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parent
            [created_child2_id],  # Create child2
        ]
        # Set up mocks
        self.service.app.handle.side_effect = [
            [
                self.identifier_issuer,
                self.identifier_issuer2,
            ],  # The identifier issuers in the Identifiers
            [],  # No existing Identifiers
            [
                created_identifier1_id,
                created_identifier2_id,
            ],  # Created Identifier IDs
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=4)

    def test_9_3_1_identifier_issuer_id_not_found(self) -> None:
        """Test 9.3.1: Identifier issuer ID (any except NULL_ID) provided and not found - should fail."""
        # Create upload batch
        identifier = self.create_identifier_for_upload(
            identifier_issuer_id=self.random_ids[0]
        )
        child2_for_upload = self.create_child2_for_upload(
            ref2_id=None, ref2_code=None, identifiers=[identifier]
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.app.handle.side_effect = [
            [],  # No identifier issuer found
            [],  # No existing Identifiers
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=2)

    def test_9_3_2_identifier_issuer_code_not_found(self) -> None:
        """Test 9.3.2: Identifier issuer code provided and not found - should fail."""
        # Create upload batch
        identifier = self.create_identifier_for_upload(
            identifier_issuer_id=NULL_ID, identifier_issuer_code="nonexistent_code"
        )
        child2_for_upload = self.create_child2_for_upload(
            ref2_id=None, ref2_code=None, identifiers=[identifier]
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[0]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.app.handle.side_effect = [
            [],  # No identifier issuer found for code
            [],  # No existing Identifiers
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=2)

    def test_9_3_3_identifier_issuer_id_and_code_mismatch(self) -> None:
        """Test 9.3.3: Both identifier issuer ID and code provided but do not match - should fail."""
        # Create upload batch
        identifier = self.create_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        child2_for_upload = self.create_child2_for_upload(
            ref2_id=None, ref2_code=None, identifiers=[identifier]
        )
        parent_for_upload = self.create_parent_for_upload(children2=[child2_for_upload])
        # Set up mocks
        created_parent_id = self.random_ids[0]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.app.handle.side_effect = [
            [self.identifier_issuer, self.identifier_issuer2],  # Mismatched ID/code
            [],  # No existing Identifiers
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=2)


# Combined scenario tests
@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCombinedScenarios(BaseUploadTestCase):
    """Test combinations of different scenarios."""

    def test_parent_with_children_and_identifiers(self) -> None:
        """Test parent with both children and Identifiers."""
        # Create upload batch
        identifier = self.create_identifier_for_upload()
        identifier_id = self.random_ids[0]
        child1_for_upload = self.create_child1_for_upload(ref1_id=self.ref1_id)
        # Optional reference for Child2: use None (not NULL_ID) to avoid resolution error
        child2_for_upload = self.create_child2_for_upload(ref2_id=None, ref2_code=None)
        parent_for_upload = self.create_parent_for_upload(
            identifiers=[identifier],
            children1=[child1_for_upload],
            children2=[child2_for_upload],
        )
        # Set up mocks
        # Resolve Ref1 for Child1
        existing_ref1 = self.create_ref1(self.ref1_id, "test_ref1_code")
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],
        ]
        # ID generation for parent and children
        created_parent_id = self.random_ids[0]
        created_child1_id = self.random_ids[1]
        created_child2_id = self.random_ids[2]
        self.service.generate_id.side_effect = [
            created_parent_id,
            created_child1_id,
            created_child2_id,
            identifier_id,  # ID for parent Identifier
        ]
        # Create operations return IDs
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parent
            [created_child1_id],  # Create child1
            [created_child2_id],  # Create child2
        ]
        # Identifier: resolve issuer, no existing externals, then create
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # Resolve IdentifierIssuer by code
            [],  # No existing Identifiers
            [identifier_id],  # Created Identifier ID
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=4)

    def test_update_existing_parent_with_new_children(self) -> None:
        """Test updating an existing parent with new child objects."""
        # Create upload batch
        child1_for_upload = self.create_child1_for_upload(ref1_id=self.ref1_id)
        parent_for_upload = self.create_parent_for_upload(
            parent_id=self.parent_id, children1=[child1_for_upload]
        )
        # Set up mocks
        existing_parent = self.get_parent_from_for_upload(
            parent_for_upload, a="existing"
        )
        existing_ref1 = self.create_ref1(self.ref1_id, "test_ref1_code")
        created_child1_id = self.random_ids[0]
        self.service.repository.crud.side_effect = [
            [True],  # EXISTS_SOME: parent exists
            [existing_parent],  # READ_SOME: retrieve existing parent for comparison
            [self.parent_id],  # UPDATE_SOME: update returns ID
            [created_child1_id],  # CREATE_SOME: create child1
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(
            parent_for_upload, on_exists=UploadAction.UPDATE
        )
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_updated=1, n_created=1)

    def test_complex_reference_resolution(self) -> None:
        """Test complex reference data resolution across multiple children."""
        # Create upload batch
        # Create children with various reference patterns
        child1_for_upload_with_id = self.create_child1_for_upload(
            ref1_id=self.ref1_id, ref1_code=None
        )
        child1_for_upload_with_code = self.create_child1_for_upload(
            ref1_id=NULL_ID, ref1_code="ref_code"
        )
        child1_for_upload_with_both = self.create_child1_for_upload(
            ref1_id=self.ref1_id, ref1_code="ref_code"
        )
        child2_for_upload_optional = self.create_child2_for_upload(
            ref2_id=None, ref2_code=None
        )
        parent_for_upload = self.create_parent_for_upload(
            children1=[
                child1_for_upload_with_id,
                child1_for_upload_with_code,
                child1_for_upload_with_both,
            ],
            children2=[child2_for_upload_optional],
        )
        # Set up mocks
        # Resolve Ref1 by id and code for Child1 references
        existing_ref1 = self.create_ref1(self.ref1_id, "ref_code")
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],
        ]
        # Create IDs for parent and children
        created_parent_id = self.random_ids[0]
        created_child1_ids = self.random_ids[1:4]
        created_child2_id = self.random_ids[4]
        self.service.generate_id.side_effect = [
            created_parent_id,
            *created_child1_ids,
            created_child2_id,
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parent
            created_child1_ids,  # Create 3 Child1
            [created_child2_id],  # Create 1 Child2
        ]
        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=5)

    def test_child2_with_identifiers_and_parent_relationship(self) -> None:
        """Test Child2 with Identifiers in combination with parent relationships and other children."""
        # Create upload batch
        # Identifier for Child2
        child2_ext_id = self.create_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        # Child2 with Identifier
        child2_for_upload = self.create_child2_for_upload(
            ref2_id=None, ref2_code=None, identifiers=[child2_ext_id]
        )
        # Child1 with reference data
        existing_ref1 = self.create_ref1(self.ref1_id, "test_ref1_code")
        child1_for_upload = self.create_child1_for_upload(ref1_code=existing_ref1.code)
        # Parent with both children
        parent_for_upload = self.create_parent_for_upload(
            children1=[child1_for_upload], children2=[child2_for_upload]
        )

        # Set up mocks
        created_parent_id = self.random_ids[0]
        created_child1_id = self.random_ids[1]
        created_child2_id = self.random_ids[2]
        created_child2_ext_id = self.random_ids[3]

        self.service.generate_id.side_effect = [
            created_parent_id,  # Parent
            created_child1_id,  # Child1
            created_child2_id,  # Child2
            created_child2_ext_id,  # Child2 Identifier
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parent
            [created_child1_id],  # Create child1
            [created_child2_id],  # Create child2
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],  # Existing Ref1
        ]
        # Resolve identifier issuer and check for existing Identifiers
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # Resolve IdentifierIssuer by code
            [],  # No existing Identifiers for Child2
            [created_child2_ext_id],  # Created child2 Identifier ID
        ]

        # Perform upload and verify result
        batch_result = self.upload_batch(parent_for_upload)
        self.assertBatchProcessed(batch_result)
        # Result: 1 parent + 1 child1 + 1 child2 + 1 child2 Identifier
        self.assertStatusCount(batch_result, n_created=4)


@pytest.mark.scenario_ids("TC-11-13-01")
class TestDuplicateIds(BaseUploadTestCase):
    """Duplicate-ID detection converts per-item hard failures into soft FAILED results."""

    def _make_child1(self, child_id: UUID) -> Child1ForUpload:
        """Construct a Child1ForUpload bypassing Pydantic validators (for dup-ID tests)."""
        return Child1ForUpload.model_construct(
            child1_id=child_id,
            parent_id=NULL_ID,
            ref1_id=self.ref1_id,
            ref1_code=None,
            a="a",
            b=[],
            c={},
        )

    def _make_parent(
        self,
        parent_id: UUID,
        children1: list[Child1ForUpload] | None = None,
    ) -> ParentForUpload:
        """Construct a ParentForUpload bypassing Pydantic validators."""
        from test.commondb.unit.upload.model import Parent

        return ParentForUpload.model_construct(
            id=parent_id,
            identifiers=None,
            children1=children1,
            children2=None,
            parent=Parent(a="a", b=[], c={}),
        )

    def _verify_only_cmd(self, parents: list[ParentForUpload]) -> UploadParentsCommand:
        """Build an UploadParentsCommand bypassing all Pydantic batch validators."""
        batch = ParentBatchForUpload.model_construct(
            id=uuid4(), batch_id=uuid4(), parents=parents
        )
        return UploadParentsCommand.model_construct(
            id=uuid4(),
            user=self.user,
            parent_batch=batch,
            on_exists=UploadAction.UPDATE,
            on_new=UploadAction.CREATE,
            verify_only=True,
        )

    def test_duplicate_parent_ids_both_failed_other_unaffected(self) -> None:
        """Duplicate parent UUID → both occurrences FAILED, distinct parent unaffected."""
        shared_id = UUID("aaaaaaaa-0000-0000-0000-000000000001")
        distinct_id = UUID("bbbbbbbb-0000-0000-0000-000000000002")
        p0 = self._make_parent(shared_id)
        p1 = self._make_parent(distinct_id)
        p2 = self._make_parent(shared_id)

        # objects_exist is called for the one distinct ID only.
        self.service.repository.crud.return_value = [False]

        batch_result = self.batch_uploader.upload_batch(  # type: ignore[assignment]
            self._verify_only_cmd([p0, p1, p2])
        )

        r0, r1, r2 = batch_result.get_parent_results()
        self.assertEqual(r0.status, EtlStatus.FAILED)
        self.assertTrue(r0.has_log_code("a1b2c3d4"))
        self.assertEqual(r2.status, EtlStatus.FAILED)
        self.assertTrue(r2.has_log_code("a1b2c3d4"))
        # Distinct parent: PENDING → SKIPPED by verify_only.
        self.assertEqual(r1.status, EtlStatus.SKIPPED)

    def test_duplicate_child_within_one_parent_parent_failed(self) -> None:
        """Two children with the same UUID inside one parent → parent FAILED."""
        child_id = UUID("cccccccc-0000-0000-0000-000000000003")
        c0 = self._make_child1(child_id)
        c1 = self._make_child1(child_id)
        parent = self._make_parent(
            UUID("dddddddd-0000-0000-0000-000000000004"), children1=[c0, c1]
        )

        batch_result = self.batch_uploader.upload_batch(  # type: ignore[assignment]
            self._verify_only_cmd([parent])
        )

        (r,) = batch_result.get_parent_results()
        self.assertEqual(r.status, EtlStatus.FAILED)
        self.assertTrue(r.has_log_code("e5f6a7b8"))

    def test_duplicate_child_across_two_parents_both_parents_failed(self) -> None:
        """Same child UUID in two distinct parents → both parents FAILED, message names both."""
        parent_id_a = UUID("eeeeeeee-0000-0000-0000-000000000005")
        parent_id_b = UUID("ffffffff-0000-0000-0000-000000000006")
        child_id = UUID("11111111-1111-0000-0000-000000000007")
        pa = self._make_parent(
            parent_id_a,
            children1=[self._make_child1(child_id)],
        )
        pb = self._make_parent(
            parent_id_b,
            children1=[self._make_child1(child_id)],
        )

        # objects_exist for parents returns [True, True]; child objects_exist is bypassed.
        self.service.repository.crud.return_value = [True, True]

        batch_result = self.batch_uploader.upload_batch(  # type: ignore[assignment]
            self._verify_only_cmd([pa, pb])
        )

        ra, rb = batch_result.get_parent_results()
        self.assertEqual(ra.status, EtlStatus.FAILED)
        self.assertTrue(ra.has_log_code("e5f6a7b8"))
        self.assertEqual(rb.status, EtlStatus.FAILED)
        self.assertTrue(rb.has_log_code("e5f6a7b8"))
        error_msg = next(e.message for e in ra.logs if e.code == "e5f6a7b8")
        self.assertIn(str(parent_id_a), error_msg)
        self.assertIn(str(parent_id_b), error_msg)

    def test_non_duplicate_batch_unaffected(self) -> None:
        """Batch with fully distinct IDs produces no FAILED results and no duplicate codes."""
        id_a = UUID("22222222-0000-0000-0000-000000000001")
        id_b = UUID("33333333-0000-0000-0000-000000000002")
        c1a = UUID("44444444-0000-0000-0000-000000000003")
        c1b = UUID("55555555-0000-0000-0000-000000000004")
        pa = self._make_parent(id_a, children1=[self._make_child1(c1a)])
        pb = self._make_parent(id_b, children1=[self._make_child1(c1b)])

        # Both parents exist; child objects_exist is also called (two IDs each time).
        self.service.repository.crud.return_value = [True, True]

        batch_result = self.batch_uploader.upload_batch(  # type: ignore[assignment]
            self._verify_only_cmd([pa, pb])
        )

        ra, rb = batch_result.get_parent_results()
        for r in (ra, rb):
            self.assertNotEqual(r.status, EtlStatus.FAILED)
            self.assertFalse(r.has_log_code("a1b2c3d4"))
            self.assertFalse(r.has_log_code("e5f6a7b8"))
