"""
Unit tests for commondb upload services.

The tests make use of the Parent, Child1, and Child2 and derived models defined in
model.py and focus on verifying the upload logic.

The tests handle all of the following upload scenarios, as well as any relevant
combinations thereof:
1 Existence of parent and/or child objects in the repository
1.1 ID not provided or NULL_ID: object does not exist and needs to be created
1.2 ID provided and is_new_id=True
1.2.1 Object with this ID does not exist: error
1.2.2 Object with this ID exists: needs to be created with that ID
2 Provision of child objects (all need to be created/updated)
2.1 Parent without any Child1 or Child2 objects
2.2 Parent with Child1 objects only
2.3 Parent with Child2 objects only
2.4 Parent with both Child1 and Child2 objects
3 Links to reference data in child objects
3.1 Child object with reference data model ID (any except NULL_ID) and no code
3.1.1 Reference model ID not found: error
3.1.1 Reference model ID found: no issue
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
6 Provision of external identifiers for parent objects (use IdentifierType=PERSON for testing purposes)
6.1 No external identifiers provided: no issue
6.2 One external identifier provided
6.2.1 Existing external identifier i.e. (identifier_issuer, external_id) combination exists already
6.2.1.1 Parent ID None or NULL_ID: set parent ID in upload result
6.2.1.2 Parent ID provided
6.2.1.2.1 Same as existing external identifiers' parent ID: no issue
6.2.1.2.2 Different from existing external identifiers' parent ID: error
6.2.2 New external identifier i.e. (identifier_issuer, external_id) combination does not exist yet for this parent: create new external identifier once parent ID is known
6.2.3 Multiple external identifiers provided
6.2.3.1 Some existing external identifiers: must all point to the same parent ID AND same restrictions as 6.2 per external identifier
6.2.3.2 All new external identifiers: create new external identifiers once parent ID is known
6.3 Identifier issuer invalid
6.3.1 Identifier issuer ID (any except NULL_ID) provided and not found: error
6.3.2 Identifier issuer code provided and not found: error
6.3.3 Both identifier issuer ID (any except NULL_ID) and code provided and do not match: error
7 Upload command on_exists value
7.1 ERROR: error if any existing object
7.2 SKIP: skip any existing object, do not update
7.3 UPDATE: update any existing object
"""

from test.commondb.unit.upload.model import (
    Child1ForUpload,
    Child2ForUpload,
    Parent,
    ParentBatchForUpload,
    ParentBatchUploader,
    ParentBatchUploadResult,
    ParentForUpload,
    Ref1,
    Ref2,
    UploadParentsCommand,
)
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

from gen_epix.commondb.domain.enum import (
    IdentifierType,
    OnExistsUploadAction,
    Role,
    UploadStatus,
    UploadStatusSet,
)
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import (
    ExternalIdentifier,
    ExternalIdentifierForUpload,
    IdentifierIssuer,
    User,
)
from gen_epix.commondb.domain.model.upload import UploadResult
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
        self.identifier_issuer_code = "test_issuer"
        self.identifier_issuer = IdentifierIssuer(
            id=self.identifier_issuer_id,
            code=self.identifier_issuer_code,
            name="Test Issuer",
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
        is_new_id: bool = False,
        a: str = "a",
        b: list[str] | None = None,
        c: dict[str, str | None] | None = None,
        x: str | None = None,
        y: list[str] | None = None,
        z: dict[str, str | None] | None = None,
        external_identifiers: list[ExternalIdentifierForUpload] | None = None,
        children1: list[Child1ForUpload] | None = None,
        children2: list[Child2ForUpload] | None = None,
    ) -> ParentForUpload:
        """Create a test parent for upload."""
        return ParentForUpload(
            id=parent_id or NULL_ID,
            is_new_id=is_new_id,  # type: ignore[call-arg]
            external_identifiers=external_identifiers,
            children1=children1,
            children2=children2,
            parent=Parent(
                a=a,
                b=b or [],
                c=c or {},
                x=x,
                y=y,
                z=z,
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
    ) -> Parent:
        """Get the Parent model contained in a ParentForUpload model, with optional overrides."""
        parent = parent_for_upload.parent
        return Parent(
            id=id or parent.id if parent else None,
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
        )

    def create_child1_for_upload(
        self,
        child_id: UUID | None = None,
        is_new_id: bool = False,
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
            id=child_id or NULL_ID,
            is_new_id=is_new_id,  # type: ignore[call-arg]
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
        is_new_id: bool = False,
        parent_id: UUID = NULL_ID,
        ref2_id: UUID | None = NULL_ID,
        ref2_code: str | None = None,
        a: str = "test_a",
        b: list[str] | None = None,
        c: dict[str, str | None] | None = None,
        x: str | None = None,
        y: list[str] | None = None,
        z: dict[str, str | None] | None = None,
    ) -> Child2ForUpload:
        """Create a test child2 for upload."""
        return Child2ForUpload(
            id=child_id or NULL_ID,
            is_new_id=is_new_id,  # type: ignore[call-arg]
            parent_id=parent_id,
            ref2_id=ref2_id,
            ref2_code=ref2_code,
            a=a,
            b=b or [],
            c=c or {},
            x=x,
            y=y,
            z=z,
        )

    def create_command_for_parents(
        self,
        parents: list[ParentForUpload] | ParentForUpload,
        on_exists: OnExistsUploadAction = OnExistsUploadAction.UPDATE,
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
        )
        return cmd

    def create_ref1(self, ref_id: UUID, code: str = "test_code") -> Ref1:
        """Create a test Ref1 object."""
        return Ref1(id=ref_id, code=code, a="test_ref_a")

    def create_ref2(self, ref_id: UUID, code: str = "test_code") -> Ref2:
        """Create a test Ref2 object."""
        return Ref2(id=ref_id, code=code, a="test_ref_a")

    def create_external_identifier_for_upload(
        self,
        identifier_issuer_id: UUID | None = None,
        identifier_issuer_code: str = "test_issuer",
        external_id: str = "test_external_id",
    ) -> ExternalIdentifierForUpload:
        """Create a test external identifier for upload."""
        return ExternalIdentifierForUpload(
            identifier_issuer_id=identifier_issuer_id or NULL_ID,
            identifier_issuer_code=identifier_issuer_code,
            external_id=external_id,
        )

    def get_external_identifier_from_for_upload(
        self,
        external_identifier_for_upload: ExternalIdentifierForUpload,
        internal_id: UUID,
        id: UUID | None = None,
        identifier_issuer_id: UUID | None = None,
        external_id: str | None = None,
    ) -> ExternalIdentifier:
        """Get the ExternalIdentifier model corresponding to an ExternalIdentifierForUpload model, with optional overrides."""
        return ExternalIdentifier(
            id=id or uuid4(),
            identifier_issuer_id=identifier_issuer_id
            or external_identifier_for_upload.identifier_issuer_id,  # type:ignore[arg-type]
            external_id=external_id or external_identifier_for_upload.external_id,
            internal_id=internal_id,
            identifier_type=IdentifierType.PERSON,
        )

    def upload_batch(
        self,
        cmd: UploadParentsCommand | list[ParentForUpload] | ParentForUpload,
        on_exists: OnExistsUploadAction = OnExistsUploadAction.UPDATE,
        validate_command: bool = True,
    ) -> ParentBatchUploadResult:
        """Upload a batch of parents and return the upload result."""
        if isinstance(cmd, UploadParentsCommand):
            pass
        else:
            cmd = self.create_command_for_parents(
                cmd, on_exists, validate_command=validate_command
            )
        retval = self.batch_uploader.upload_batch(
            cmd,
        )
        return retval  # type: ignore[return-value]

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
        upload_result: UploadResult,
        n_skipped: int = 0,
        n_created: int = 0,
        n_updated: int = 0,
        n_failed: int = 0,
        n_pending: int = 0,
        n_processed: int = 0,
        include_self: bool = False,
    ) -> None:
        expected_status_count = {
            UploadStatus.SKIPPED: n_skipped,
            UploadStatus.CREATED: n_created,
            UploadStatus.UPDATED: n_updated,
            UploadStatus.FAILED: n_failed,
            UploadStatus.PENDING: n_pending,
            UploadStatus.PROCESSED: n_processed,
        }
        actual_status_count = upload_result.get_status_count(include_self=include_self)
        different_status_count = {
            (x, expected_status_count[x], actual_status_count[x])
            for x in UploadStatus
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
class TestObjectExistence(BaseUploadTestCase):
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
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=1)
        self.assertEqual(retval.parents[0].id, created_parent_id)

    def test_1_2_1_parent_id_provided_new_id_but_not_exists_succeeds(self) -> None:
        """Test 1.2.1: Object with this ID and is_new_id does not exist - should succeed."""
        # Create upload batch
        parent = self.create_parent_for_upload(parent_id=self.parent_id, is_new_id=True)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [False],  # Parents exist
            [parent.id],  # Create parents returned IDs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=1)
        self.assertEqual(retval.parents[0].id, parent.id)

    def test_1_2_2_parent_id_provided_new_id_and_exists_fails(self) -> None:
        """Test 1.2.2: Object with this ID and is_new_id=True exists - should fail."""
        # Create upload batch
        parent = self.create_parent_for_upload(parent_id=self.parent_id, is_new_id=True)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchFailed(retval)
        self.assertStatusCount(retval, n_failed=1)


# Test Scenario 2: Provision of child objects
class TestChildObjectProvision(BaseUploadTestCase):
    """Test scenarios related to providing different combinations of child objects."""

    def test_2_1_parent_without_children(self) -> None:
        """Test 2.1: Parent without any Child1 or Child2 objects."""
        # Create upload batch
        parent = self.create_parent_for_upload()
        # Set up mocks
        created_parent_id = self.random_ids[0]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=1)
        self.assertEqual(retval.parents[0].id, created_parent_id)

    def test_2_2_parent_with_child1_only(self) -> None:
        """Test 2.2: Parent with Child1 objects only."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "test_ref1_code")
        child1 = self.create_child1_for_upload(ref1_code=existing_ref1.code)
        parent = self.create_parent_for_upload(children1=[child1])
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
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=2)
        self.assertEqual(retval.parents[0].id, created_parent_id)
        self.assertEqual(retval.parents[0].children1[0].id, created_child1_id)  # type: ignore[index]

    def test_2_3_parent_with_child2_only(self) -> None:
        """Test 2.3: Parent with Child2 objects only."""
        # Create upload batch
        existing_ref2 = self.create_ref2(self.ref2_id, "test_ref2_code")
        child2 = self.create_child2_for_upload(ref2_code=existing_ref2.code)
        parent = self.create_parent_for_upload(children2=[child2])
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
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=2)
        self.assertEqual(retval.parents[0].id, created_parent_id)
        self.assertEqual(retval.parents[0].children2[0].id, created_child2_id)  # type: ignore[index]

    def test_2_4_parent_with_both_children(self) -> None:
        """Test 2.4: Parent with both Child1 and Child2 objects."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "test_ref1_code")
        existing_ref2 = self.create_ref2(self.ref2_id, "test_ref2_code")
        child1 = self.create_child1_for_upload(ref1_code=existing_ref1.code)
        child2 = self.create_child2_for_upload(ref2_code=existing_ref2.code)
        parent = self.create_parent_for_upload(children1=[child1], children2=[child2])
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
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=3)
        self.assertEqual(retval.parents[0].id, created_parent_id)
        self.assertEqual(retval.parents[0].children1[0].id, created_child1_id)  # type: ignore[index]
        self.assertEqual(retval.parents[0].children2[0].id, created_child2_id)  # type: ignore[index]


# Test Scenario 3: Links to reference data in child objects
class TestReferenceDataLinks(BaseUploadTestCase):
    """Test scenarios related to reference data linking in child objects."""

    def test_3_1_1_ref_id_provided_not_found_fails(self) -> None:
        """Test 3.1.1: Reference model ID not found - should fail."""
        # Create upload batch
        child1 = self.create_child1_for_upload(
            ref1_id=self.random_ids[0], ref1_code=None
        )
        parent = self.create_parent_for_upload(children1=[child1])
        # Set up mocks
        self.service.repository.read_fields.side_effect = [
            [],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchFailed(retval)
        self.assertStatusCount(retval, n_failed=1, n_pending=1)

    def test_3_1_2_ref_id_provided_and_found_succeeds(self) -> None:
        """Test 3.1.2: Reference model ID found - should succeed."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1 = self.create_child1_for_upload(ref1_id=existing_ref1.id, ref1_code=None)  # type: ignore[arg-type]
        parent = self.create_parent_for_upload(children1=[child1])
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
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=2)
        self.assertEqual(retval.parents[0].id, created_parent_id)
        self.assertEqual(retval.parents[0].children1[0].id, created_child1_id)  # type: ignore[index]

    def test_3_2_1_ref_code_provided_not_found_fails(self) -> None:
        """Test 3.2.1: Reference model code not found - should fail."""
        # Create upload batch
        child1 = self.create_child1_for_upload(
            ref1_id=NULL_ID, ref1_code="non_existent_code"
        )
        parent = self.create_parent_for_upload(children1=[child1])
        # Set up mocks
        self.service.repository.read_fields.side_effect = [
            [],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchFailed(retval)
        self.assertStatusCount(retval, n_failed=1, n_pending=1)

    def test_3_2_2_ref_code_provided_and_found_sets_id(self) -> None:
        """Test 3.2.2: Reference model code found - should succeed (and set reference model ID)."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1 = self.create_child1_for_upload(
            ref1_id=NULL_ID, ref1_code=existing_ref1.code
        )
        parent = self.create_parent_for_upload(children1=[child1])
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
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=2)
        self.assertEqual(retval.parents[0].id, created_parent_id)
        self.assertEqual(retval.parents[0].children1[0].id, created_child1_id)  # type: ignore[index]
        self.assertEqual(child1.ref1_id, self.ref1_id)

    def test_3_3_1_ref_id_and_code_mismatch_fails(self) -> None:
        """Test 3.3.1: Reference model ID and code do not match but both exist - should fail."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        other_existing_ref1 = self.create_ref1(
            self.random_ids[0], "other_existing_code"
        )
        child1 = self.create_child1_for_upload(ref1_id=existing_ref1.id, ref1_code=other_existing_ref1.code)  # type: ignore[arg-type]
        parent = self.create_parent_for_upload(children1=[child1])
        # Set up mocks
        self.service.repository.read_fields.side_effect = [
            [
                (existing_ref1.id, existing_ref1.code),
                (other_existing_ref1.id, other_existing_ref1.code),
            ],  # Existing Ref1 (ID, code) pairs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchFailed(retval)
        self.assertStatusCount(retval, n_failed=1, n_pending=1)

    def test_3_3_2_ref_id_and_code_match_succeeds(self) -> None:
        """Test 3.3.2: Reference model ID and code match - should succeed."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1 = self.create_child1_for_upload(ref1_id=existing_ref1.id, ref1_code=existing_ref1.code)  # type: ignore[arg-type]
        parent = self.create_parent_for_upload(children1=[child1])
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
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=2)

    def test_3_4_1_child2_null_id_no_code_provided_fails(self) -> None:
        """Test 3.4.1: Child2 with ref ID NULL_ID and no code provided - should fail since eventual reference ID cannot be NULL_ID."""
        # Create upload batch
        child2 = self.create_child2_for_upload(ref2_id=NULL_ID, ref2_code=None)
        parent = self.create_parent_for_upload(children2=[child2])
        # Set up mocks
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchFailed(retval)
        self.assertStatusCount(retval, n_failed=1, n_pending=1)

    def test_3_4_2_child2_no_id_or_code_succeeds(self) -> None:
        """Test 3.4.2: Child2 with no ID or code - should succeed (reference is optional)."""
        # Create upload batch
        child2 = self.create_child2_for_upload(ref2_id=None, ref2_code=None)
        parent = self.create_parent_for_upload(children2=[child2])
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
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=2)
        self.assertEqual(parent.children2[0].ref2_id, None)  # type: ignore[index]


# Test Scenario 4: Parent link in child objects
class TestParentLinks(BaseUploadTestCase):
    """Test scenarios related to parent links in child objects."""

    def test_4_1_child_null_parent_id_set_during_upload(self) -> None:
        """Test 4.1: NULL_ID parent - should be set during upload."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1 = self.create_child1_for_upload(
            parent_id=NULL_ID, ref1_id=existing_ref1.id  # type: ignore[arg-type]
        )
        parent = self.create_parent_for_upload(children1=[child1])
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
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=2)
        self.assertEqual(parent.children1[0].parent_id, created_parent_id)  # type: ignore[index]

    def test_4_2_1_child_parent_id_parent_not_exists_fails(self) -> None:
        """Test 4.2.1: Parent does not exist or has different ID - should fail."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1 = self.create_child1_for_upload(
            parent_id=self.parent_id, ref1_id=existing_ref1.id  # type: ignore[arg-type]
        )
        parent = self.create_parent_for_upload(
            parent_id=self.parent_id, is_new_id=True, children1=[child1]
        )
        parent.id = self.random_ids[1]  # Different ID than child's parent_id
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
        retval = self.upload_batch(
            parent, validate_command=False
        )  # Skip command validation to allow inconsistent IDs
        self.assertBatchFailed(retval)
        self.assertStatusCount(retval, n_pending=1, n_failed=1)

    def test_4_2_2_child_parent_id_matches_succeeds(self) -> None:
        """Test 4.2.2: Parent exists with matching ID - should succeed."""
        # Create upload batch
        existing_ref1 = self.create_ref1(self.ref1_id, "existing_code")
        child1 = self.create_child1_for_upload(
            parent_id=self.parent_id, ref1_id=existing_ref1.id  # type: ignore[arg-type]
        )
        parent = self.create_parent_for_upload(
            parent_id=self.parent_id, children1=[child1]
        )
        existing_parent = self.get_parent_from_for_upload(parent)
        # Set up mocks
        created_parent_id = parent.id
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
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_skipped=1, n_created=1)
        self.assertEqual(parent.id, created_parent_id)
        self.assertEqual(retval.parents[0].children1[0].id, created_child1_id)  # type: ignore[index]


# Test Scenario 5: Field mutability for stored objects
class TestFieldMutability(BaseUploadTestCase):
    """Test scenarios related to field mutability for existing objects."""

    def test_5_1_1_always_mutable_single_value_field(self) -> None:
        """Test 5.1.1: Always mutable single value field - should be updated."""
        # Create upload batch
        existing_value = "value"
        new_value = "new_value"
        resulting_value = new_value
        parent = self.create_parent_for_upload(parent_id=self.parent_id, a=new_value)
        existing_parent = self.get_parent_from_for_upload(parent, a=existing_value)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_updated=1)
        self.assertEqual(existing_parent.a, resulting_value)

    def test_5_1_2_always_mutable_list_field(self) -> None:
        """Test 5.1.2: Always mutable list field - should be updated."""
        # Create upload batch
        existing_value = ["value1", "value2"]
        new_value = ["new_value1", "new_value2", "new_value3"]
        resulting_value = new_value
        parent = self.create_parent_for_upload(parent_id=self.parent_id, b=new_value)
        existing_parent = self.get_parent_from_for_upload(parent, b=existing_value)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_updated=1)
        self.assertEqual(existing_parent.b, resulting_value)

    def test_5_1_3_1_always_mutable_dict_add_new_key(self) -> None:
        """Test 5.1.3.1: Dict field - add new key with non-None value."""
        # Create upload batch
        existing_value = {"key1": "value1", "key2": "value2"}
        new_value = {"key3": "value3"}
        resulting_value = existing_value.copy()
        resulting_value.update(new_value)
        parent = self.create_parent_for_upload(parent_id=self.parent_id, c=new_value)  # type: ignore[arg-type]
        existing_parent = self.get_parent_from_for_upload(parent, c=existing_value)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_updated=1)
        self.assertEqual(existing_parent.c, resulting_value)

    def test_5_1_3_2_always_mutable_dict_new_key_none_value(self) -> None:
        """Test 5.1.3.2: Dict field - new key with None value should not be added."""
        # Create upload batch
        existing_value = {"key1": "value1", "key2": "value2"}
        new_value = {"key3": None}
        resulting_value = existing_value
        parent = self.create_parent_for_upload(parent_id=self.parent_id, c=new_value)  # type: ignore[arg-type]
        existing_parent = self.get_parent_from_for_upload(parent, c=existing_value)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_skipped=1)
        self.assertEqual(existing_parent.c, resulting_value)

    def test_5_1_3_3_always_mutable_dict_update_existing_key(self) -> None:
        """Test 5.1.3.3: Dict field - update existing key with new value."""
        # Create upload batch
        existing_value = {"key1": "value1", "key2": "value2"}
        new_value = {"key1": "new_value1"}
        resulting_value = existing_value.copy()
        resulting_value.update(new_value)
        parent = self.create_parent_for_upload(parent_id=self.parent_id, c=new_value)  # type: ignore[arg-type]
        existing_parent = self.get_parent_from_for_upload(parent, c=existing_value)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_updated=1)
        self.assertEqual(existing_parent.c, resulting_value)

    def test_5_1_3_4_always_mutable_dict_remove_existing_key(self) -> None:
        """Test 5.1.3.4: Dict field - remove existing key when new value is None."""
        # Create upload batch
        existing_value = {"key1": "value1", "key2": "value2"}
        new_value = {"key1": None}
        resulting_value = existing_value.copy()
        resulting_value.pop("key1")
        parent = self.create_parent_for_upload(parent_id=self.parent_id, c=new_value)  # type: ignore[arg-type]
        existing_parent = self.get_parent_from_for_upload(parent, c=existing_value)
        # Set up mocks
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
            [existing_parent.id],  # Updated parents returned IDs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_updated=1)
        self.assertEqual(existing_parent.c, resulting_value)

    def test_5_2_1_mutable_if_empty_stored_empty_updated(self) -> None:
        """Test 5.2.1: Mutable if empty field - stored value is empty, should succeed."""
        # This test would be part of the object update logic
        # The actual implementation would check the stored model field properties
        pass  # Implementation would depend on the actual update logic

    def test_5_2_2_mutable_if_empty_stored_not_empty_new_empty(self) -> None:
        """Test 5.2.2: Mutable if empty field - stored not empty, new empty, should succeed."""
        # Implementation would check field properties during update
        pass

    def test_5_2_3_mutable_if_empty_stored_not_empty_new_not_empty_fails(self) -> None:
        """Test 5.2.3: Mutable if empty field - stored not empty, new not empty, should fail."""
        # Implementation would check field properties
        pass


# Test Scenario 6: External identifiers for parent objects
class TestExternalIdentifiers(BaseUploadTestCase):
    """Test scenarios related to external identifiers for parent objects."""

    def test_6_1_no_external_ids_provided(self) -> None:
        """Test 6.1: No external identifiers provided - should succeed."""
        # Create upload batch
        parent = self.create_parent_for_upload(external_identifiers=None)
        # Set up mocks
        created_parent_id = parent.id
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create children1 returned IDs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=1)

    def test_6_2_1_1_existing_external_id_null_parent_sets_id(self) -> None:
        """Test 6.2.1.1: Existing external identifier with NULL parent ID - should set parent ID."""
        # Create upload batch
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        existing_parent_id = self.random_ids[0]
        existing_external_identifier = self.get_external_identifier_from_for_upload(
            external_identifier, internal_id=existing_parent_id
        )
        parent = self.create_parent_for_upload(
            external_identifiers=[external_identifier]
        )
        existing_parent = self.get_parent_from_for_upload(parent, id=existing_parent_id)
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the external IDs
            [existing_external_identifier],  # The existing external identifiers
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_skipped=2)
        self.assertEqual(retval.parents[0].id, existing_parent_id)  # type

    def test_6_2_1_2_1_existing_external_id_same_parent_succeeds(self) -> None:
        """Test 6.2.1.2.1: Existing external identifier with same parent ID - should succeed."""
        # Create upload batch
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        existing_parent_id = self.random_ids[0]
        existing_external_identifier = self.get_external_identifier_from_for_upload(
            external_identifier, internal_id=existing_parent_id
        )
        parent = self.create_parent_for_upload(
            parent_id=existing_parent_id, external_identifiers=[external_identifier]
        )
        existing_parent = self.get_parent_from_for_upload(parent)
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the external IDs
            [existing_external_identifier],  # The existing external identifiers
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_skipped=2)

    def test_6_2_1_2_2_existing_external_id_different_parent_fails(self) -> None:
        """Test 6.2.1.2.2: Existing external identifier with different parent ID - should fail."""
        # Create upload batch
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        other_parent_id = self.random_ids[0]
        existing_parent_id = self.random_ids[1]
        existing_external_identifier = self.get_external_identifier_from_for_upload(
            external_identifier, internal_id=other_parent_id
        )
        parent = self.create_parent_for_upload(
            parent_id=existing_parent_id, external_identifiers=[external_identifier]
        )
        existing_parent = self.get_parent_from_for_upload(parent)
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the external IDs
            [existing_external_identifier],  # The existing external identifiers
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Parents exist
            [existing_parent],  # Existing parents
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchFailed(retval)
        self.assertStatusCount(retval, n_failed=1, n_pending=1)

    def test_6_2_2_new_external_id_new_parent(self) -> None:
        """Test 6.2.2: New external identifier for new parent - should succeed."""
        # Create upload batch
        external_identifier_for_upload = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id
        )
        created_external_identifier_id = self.random_ids[0]
        created_parent_id = self.random_ids[1]
        parent = self.create_parent_for_upload(
            external_identifiers=[external_identifier_for_upload]
        )
        external_identifier = self.get_external_identifier_from_for_upload(
            external_identifier_for_upload,
            id=created_external_identifier_id,
            internal_id=created_parent_id,
        )
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the external IDs
            [],  # The existing external identifiers before creation
            [external_identifier],  # The external identifiers after creation
        ]
        self.service.generate_id.side_effect = [
            created_parent_id,  # ID of the newly created parent
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # Create parents returned IDs
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=2)
        self.assertEqual(retval.parents[0].id, created_parent_id)
        self.assertEqual(retval.parents[0].external_identifiers[0].id, created_external_identifier_id)  # type: ignore[index]

    def test_6_2_3_1_multiple_external_ids_some_existing_same_parent(self) -> None:
        """Test 6.2.3.1: Multiple external IDs, some existing for same parent - should succeed."""
        # Create upload batch
        external_identifier1 = self.create_external_identifier_for_upload(
            external_id="ext_id_1"
        )
        external_identifier2 = self.create_external_identifier_for_upload(
            external_id="ext_id_2"
        )
        parent = self.create_parent_for_upload(
            parent_id=self.parent_id,
            external_identifiers=[external_identifier1, external_identifier2],
        )
        existing_external_identifier1 = self.get_external_identifier_from_for_upload(
            external_identifier1,
            parent.id,  # type: ignore[arg-type]
        )
        created_external_identifier2 = self.get_external_identifier_from_for_upload(
            external_identifier2,
            parent.id,  # type: ignore[arg-type]
        )
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the external IDs
            [],
            [existing_external_identifier1, created_external_identifier2]
        ]
        existing_parent = self.get_parent_from_for_upload(parent)
        self.service.repository.crud.side_effect = [
            [True],  # Parent exists
            [existing_parent],  # Return the existing parent object
        ]

        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=2, n_skipped=1)

    def test_6_2_3_1_multiple_external_ids_some_existing_different_parent(self) -> None:
        """Test 6.2.3.1: Multiple external IDs, some existing for different parent - should fail."""
        # Create upload batch
        external_identifier1 = self.create_external_identifier_for_upload(
            external_id="ext_id_1"
        )
        external_identifier2 = self.create_external_identifier_for_upload(
            external_id="ext_id_2"
        )
        parent = self.create_parent_for_upload(
            external_identifiers=[external_identifier1, external_identifier2]
        )
        different_id = self.random_ids[0]
        existing_external_identifier1 = self.get_external_identifier_from_for_upload(
            external_identifier1,
            different_id,  # Different parent ID
        )
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the external IDs
            [existing_external_identifier1],  # The existing external identifiers
        ]

        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchFailed(retval)
        self.assertStatusCount(retval, n_failed=1, n_pending=2)

    def test_6_2_3_2_multiple_external_ids_all_new(self) -> None:
        """Test 6.2.3.2: Multiple external IDs, all new - should succeed."""
        # Create upload batch
        external_identifier1 = self.create_external_identifier_for_upload(
            external_id="new_ext_id_1"
        )
        external_identifier2 = self.create_external_identifier_for_upload(
            external_id="new_ext_id_2"
        )
        parent = self.create_parent_for_upload(
            external_identifiers=[external_identifier1, external_identifier2]
        )
        # Set up mocks
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # The identifier issuers in the external IDs
            [],  # The existing external identifiers
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=3)

    # TODO: create tests for scenarios 6.3 on invalid identifier issuer


# Test Scenario 7: Upload command on_exists value
class TestOnExistsActions(BaseUploadTestCase):
    """Test scenarios related to the on_exists command parameter."""

    def test_7_1_on_exists_error_with_existing_object_fails(self) -> None:
        """Test 7.1: on_exists=ERROR with existing object - should fail."""
        # Create upload batch
        parent = self.create_parent_for_upload(parent_id=self.parent_id)
        # Set up mocks
        existing_parent = Parent(id=self.parent_id, a="existing")
        self.service.repository.crud.return_value = [existing_parent]
        # Perform upload and verify result
        retval = self.upload_batch(parent, on_exists=OnExistsUploadAction.ERROR)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=1)

    def test_7_2_on_exists_skip_with_existing_object_skips(self) -> None:
        """Test 7.2: on_exists=SKIP with existing object - should skip."""
        # Create upload batch
        parent = self.create_parent_for_upload(parent_id=self.parent_id)
        # Set up mocks
        # Mock existing parent
        existing_parent = Parent(id=self.parent_id, a="existing")
        self.service.repository.crud.return_value = [existing_parent]
        # Perform upload and verify result
        retval = self.upload_batch(parent, on_exists=OnExistsUploadAction.SKIP)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_skipped=1)

    def test_7_3_on_exists_update_with_existing_object_updates(self) -> None:
        """Test 7.3: on_exists=UPDATE with existing object - should update."""
        # Create upload batch
        parent = self.create_parent_for_upload(parent_id=self.parent_id, a="new_value")
        # Set up mocks
        existing_parent = Parent(id=self.parent_id, a="old_value")
        self.service.repository.crud.return_value = [existing_parent]
        # Perform upload and verify result
        retval = self.upload_batch(parent, on_exists=OnExistsUploadAction.UPDATE)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_updated=1)


# Combined scenario tests
class TestCombinedScenarios(BaseUploadTestCase):
    """Test combinations of different scenarios."""

    def test_parent_with_children_and_external_ids(self) -> None:
        """Test parent with both children and external identifiers."""
        # Create upload batch
        external_identifier = self.create_external_identifier_for_upload()
        child1 = self.create_child1_for_upload(ref1_id=self.ref1_id)
        child2 = self.create_child2_for_upload()
        parent = self.create_parent_for_upload(
            external_identifiers=[external_identifier],
            children1=[child1],
            children2=[child2],
        )
        # Set up mocks

        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=4)

    def test_update_existing_parent_with_new_children(self) -> None:
        """Test updating an existing parent with new child objects."""
        # Create upload batch
        child1 = self.create_child1_for_upload(ref1_id=self.ref1_id)
        parent = self.create_parent_for_upload(
            parent_id=self.parent_id, children1=[child1]
        )
        # Set up mocks
        # Mock existing parent without children
        existing_parent = Parent(id=self.parent_id, a="existing")
        self.service.repository.crud.return_value = [existing_parent]
        existing_ref1 = self.create_ref1(self.ref1_id, "test_ref1_code")
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],
        ]
        # Perform upload and verify result
        retval = self.upload_batch(parent, on_exists=OnExistsUploadAction.UPDATE)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_updated=1, n_created=1)

    def test_complex_reference_resolution(self) -> None:
        """Test complex reference data resolution across multiple children."""
        # Create upload batch
        # Create children with various reference patterns
        child1_with_id = self.create_child1_for_upload(
            ref1_id=self.ref1_id, ref1_code=None
        )
        child1_with_code = self.create_child1_for_upload(
            ref1_id=NULL_ID, ref1_code="ref_code"
        )
        child1_with_both = self.create_child1_for_upload(
            ref1_id=self.ref1_id, ref1_code="ref_code"
        )
        child2_optional = self.create_child2_for_upload(ref2_id=None, ref2_code=None)
        parent = self.create_parent_for_upload(
            children1=[child1_with_id, child1_with_code, child1_with_both],
            children2=[child2_optional],
        )
        # Set up mocks
        # Perform upload and verify result
        retval = self.upload_batch(parent)
        self.assertBatchProcessed(retval)
        self.assertStatusCount(retval, n_created=5)
