from typing import Generator
from uuid import UUID

import gen_epix.fastapp.model
from gen_epix import fastapp
from gen_epix.commondb.domain import command, exc, model
from gen_epix.commondb.domain.enum import OnExistsUploadAction, UploadStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload,
    BaseBatchUploadResult,
    UploadResult,
)
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_number import EqualsNumberFilter
from gen_epix.filter.string_set import StringSetFilter
from gen_epix.filter.uuid_set import UuidSetFilter


class BatchUploader:
    """
    A class encapsulating batch upload functionality, intended as a singleton.
    """

    def __init__(
        self,
        upload_batch_command_class: type[command.UploadBatchCommandMixin],
        stored_model_field_props: dict[
            type[model.Model], dict[str, gen_epix.fastapp.model.ModelFieldProps]
        ],
        service: BaseService,
    ):
        self.upload_batch_command_class = upload_batch_command_class
        self.service = service
        self.stored_model_field_props = stored_model_field_props

        # Derive some constants for convenience
        self.cmd_batch_field_name = (
            self.upload_batch_command_class.BATCH_FOR_UPLOAD_FIELD_NAME
        )
        self.batch_for_upload_class = (
            self.upload_batch_command_class.BATCH_FOR_UPLOAD_CLASS
        )
        self.batch_upload_result_class = (
            self.upload_batch_command_class.BATCH_UPLOAD_RESULT_CLASS
        )
        self.batch_parents_for_upload_field_name = (
            self.batch_for_upload_class.PARENTS_FOR_UPLOAD_FIELD_NAME
        )
        self.parent_for_upload_class = (
            self.batch_for_upload_class.PARENT_FOR_UPLOAD_CLASS
        )
        self.parent_identifier_type = (
            self.parent_for_upload_class.PARENT_IDENTIFIER_TYPE
        )
        self.parent_class = self.parent_for_upload_class.PARENT_CLASS
        self.parent_result_class = self.batch_upload_result_class.PARENT_RESULT_CLASS
        self.external_identifier_for_upload_class = (
            self.parent_for_upload_class.EXTERNAL_IDENTIFIER_FOR_UPLOAD_CLASS
        )
        self.external_identifier_class = (
            self.parent_for_upload_class.EXTERNAL_IDENTIFIER_CLASS
        )
        self.external_identifier_crud_command_class = (
            self.service.app.domain.get_crud_command_for_model(
                self.external_identifier_class
            )
        )
        self.child_for_upload_class_map = (
            self.parent_for_upload_class.CHILD_FOR_UPLOAD_CLASS_MAP
        )
        self.children_field_name_map = (
            self.parent_for_upload_class.CHILDREN_FIELD_NAME_MAP
        )
        self.child_model_parent_id_field_name_map = (
            self.parent_for_upload_class.CHILD_PARENT_ID_FIELD_NAME_MAP
        )
        self.external_identifiers_field_name = (
            self.parent_for_upload_class.EXTERNAL_IDENTIFIERS_FIELD_NAME
        )

    def get_batch_for_upload(
        self, cmd: command.UploadBatchCommandMixin
    ) -> BaseBatchForUpload:
        """Get the batch for upload from the command."""
        return cmd.get_batch_for_upload()

    def get_parents_for_upload(
        self, cmd: command.UploadBatchCommandMixin
    ) -> list[model.ParentForUpload]:
        """Get parent models from the command."""
        return self.get_batch_for_upload(cmd).get_parents_for_upload()

    def get_parent_results(
        self, retval: BaseBatchUploadResult
    ) -> list[model.ParentUploadResult]:
        """Get parent upload results from the batch upload result."""
        return retval.get_parent_results()

    def parent_result_items(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
    ) -> Generator[tuple[model.ParentForUpload, model.ParentUploadResult], None, None]:
        """Get (parent, parent_result) items from the batch upload result."""
        parents = cmd.get_batch_for_upload().get_parents_for_upload()
        parent_results = retval.get_parent_results()
        for parent, parent_result in zip(parents, parent_results):
            yield parent, parent_result

    def upload_batch(
        self,
        cmd: command.UploadBatchCommandMixin,
    ) -> BaseBatchUploadResult:
        """
        See command.UploadSamplesCommand for details.
        """
        # Verify arguments
        assert isinstance(cmd, command.Command)
        if cmd.id is None:
            raise exc.InvalidArgumentsError("cmd.id must be set")

        #  Check user rights
        self.verify_user_rights(cmd)

        # Initialize the upload result
        retval = self.init_batch_upload_result(cmd)
        retval.add_info(
            code="f1e2d3c4",
            message="Upload started",
        )

        with self.service.repository.uow() as uow:
            # Verify batch
            retval.add_info(
                code="8b4c2f91",
                message="Verification started",
            )
            success = self.verify_batch(cmd, retval, uow)
            retval.add_info(
                code="a3f7e9d2",
                message="Verification ended",
            )
            if cmd.verify_only:
                # Stop here if only verification was requested
                retval.add_info(
                    code="b5c6d7e8",
                    message="Verification only requested, upload will not proceed",
                )
                return retval
            if not success:
                # Do not proceed with upsert due to errors
                retval.add_error(
                    code="d6e5c3b4",
                    message="Verification found errors, upload will not proceed",
                )
                return retval

            # Upsert the batch data
            retval.add_info(
                code="c1a2b3d4",
                message="Upsert started",
            )
            success = self.upsert_batch(cmd, retval, uow)
            retval.add_info(
                code="e4f5a6b7",
                message="Upsert ended",
            )
            if not success:
                # Rollback due to errors, but do not raise an exception since those will be reported in retval
                retval.add_error(
                    code="f8e7d6c5",
                    message="Upload had errors",
                )
                uow.rollback()
                retval.add_info(
                    code="7729440d",
                    message="Upload had errors, changes have been rolled back",
                )
        retval.add_info(
            code="7b9e4a2f",
            message="Upload ended",
        )

        # Assign final status
        if retval.status == UploadStatus.PENDING:
            status_count = retval.get_status_count(include_self=False)
            n_results = sum(status_count.values())
            if status_count[UploadStatus.SKIPPED] == n_results:
                retval.status = UploadStatus.SKIPPED
            elif status_count[UploadStatus.CREATED] == n_results:
                retval.status = UploadStatus.CREATED
            elif status_count[UploadStatus.UPDATED] == n_results:
                retval.status = UploadStatus.UPDATED
            else:
                # Mixed results, use status processed
                retval.status = UploadStatus.PROCESSED

        return retval

    def verify_user_rights(self, cmd: command.UploadBatchCommandMixin) -> None:
        """
        Verify that the user has rights to perform the upload.
        This base implementation performs no verification. Override as needed.
        """
        pass

    def init_batch_upload_result(
        self, cmd: command.UploadBatchCommandMixin
    ) -> BaseBatchUploadResult:
        """Initialize the batch upload result. Override as needed."""
        assert isinstance(cmd, command.Command)
        # Initialize parent results
        parent_results: list[model.ParentUploadResult] = []
        for parent_for_upload in self.get_parents_for_upload(cmd):
            # Intialize parent result
            parent_result = self.parent_result_class(status=UploadStatus.PENDING)
            # Initialise external identifier results
            external_identifiers = parent_for_upload.external_identifiers
            external_identifier_results = (
                None
                if external_identifiers is None
                else [
                    UploadResult(status=UploadStatus.PENDING)
                    for _ in external_identifiers
                ]
            )
            parent_result.external_identifiers = external_identifier_results
            # Initialize child results
            for children_field_name in self.children_field_name_map.values():
                children: list[model.Model] | None = getattr(
                    parent_for_upload, children_field_name
                )
                child_results = (
                    None
                    if children is None
                    else [
                        UploadResult(id=x.id, status=UploadStatus.PENDING)
                        for x in children
                    ]
                )
                setattr(parent_result, children_field_name, child_results)
            # Add parent result to parent results
            parent_results.append(parent_result)

        # Initialize batch result
        kwargs = {self.batch_parents_for_upload_field_name: parent_results}
        retval = self.batch_upload_result_class(
            batch_id=cmd.id,
            status=UploadStatus.PENDING,
            **kwargs,  # type: ignore[arg-type]
        )
        return retval

    def verify_batch(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Verify parents, children, external identifiers and reference data.
        """
        success = True
        # Verify external identifiers first to fill in any missing parent IDs
        success &= self.verify_external_identifiers(cmd, retval, uow)
        success &= self.verify_parents(cmd, retval, uow)
        success &= self.verify_children(cmd, retval, uow)
        # Verify reference data last since it may depend on parent and children verification
        success &= self.verify_refdata(cmd, retval, uow)
        return success

    def upsert_batch(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create or update parents, children, external identifiers and reference data.
        """
        success = True
        # Create refdata before parents and children to ensure all references exist
        success &= self.create_refdata(cmd, retval, uow)
        # Create and update parents before children to ensure parents exist
        success &= self.create_parents(cmd, retval, uow)
        success &= self.update_parents(cmd, retval, uow)
        success &= self.create_children(cmd, retval, uow)
        success &= self.update_children(cmd, retval, uow)
        # Create external identifiers last to preserve atomicity without two-phase
        # commit: if there were any errors after this and a rollback is therefore
        # needed, the external identifiers could otherwise have already been changed
        # in the meantime
        success &= self.create_external_identifiers(cmd, retval, uow)
        return success

    def verify_external_identifiers(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """Retrieve and verify identifier issuers in external IDs"""
        assert isinstance(cmd, command.Command)
        success = True

        # Retrieve and verify identifier issuers in external IDs provided by ID
        success &= self.verify_link_id(
            cmd,
            retval,
            uow,
            self.external_identifiers_field_name,
            "identifier_issuer_id",
            "identifier_issuer_code",
            model.IdentifierIssuer,
            is_same_service=False,
            is_frozen=True,
        )

        # Retrieve and verify external IDs
        external_identifier_tuples: list[tuple[UUID, str]] = (
            list(  # type:ignore[assignment]
                {
                    (y.identifier_issuer_id, y.external_id)
                    for x in self.get_parents_for_upload(cmd)
                    for y in x.get_external_identifiers() or []
                }
            )
        )
        if not external_identifier_tuples:
            return success

        # Get all external identifiers matching the provided external
        # identifiers and identifier issuers, but not their combination
        # This leaves the possibility that the same external identifier for a
        # different identifier issuer is retrieved: this is addressed after
        # retrieval, allowing a straightforward filter here
        existing_external_identifiers: list[model.ExternalIdentifier] = (
            self.service.app.handle(
                command.ExternalIdentifierCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.READ_ALL,
                    query_filter=CompositeFilter(
                        operator=LogicalOperator.AND,
                        filters=[  # type:ignore[arg-type]
                            EqualsNumberFilter(
                                key="identifier_type",
                                value=self.parent_identifier_type.value,
                            ),
                            UuidSetFilter(
                                key="identifier_issuer_id",
                                members=frozenset(
                                    {x[0] for x in external_identifier_tuples}
                                ),
                            ),
                            StringSetFilter(
                                key="external_id",
                                members=frozenset(
                                    {x[1] for x in external_identifier_tuples}
                                ),
                            ),
                        ],
                    ),
                )
            )
        )
        existing_external_identifier_map: dict[
            tuple[UUID, str], model.ExternalIdentifier
        ] = {
            (x.identifier_issuer_id, x.external_id): x
            for x in existing_external_identifiers
        }

        # Verify external IDs for each parent
        for parent, parent_result in self.parent_result_items(cmd, retval):
            external_identifiers: list[model.ExternalIdentifier] = (
                getattr(parent, self.external_identifiers_field_name) or []
            )
            external_identifier_results: list[UploadResult] = (
                getattr(parent_result, self.external_identifiers_field_name) or []
            )
            for external_identifier, external_identifier_result in zip(
                external_identifiers, external_identifier_results
            ):
                if external_identifier_result.status != UploadStatus.PENDING:
                    # Not pending (likely skipped or failed), no need to check existence
                    continue
                key: tuple[UUID, str] = (
                    external_identifier.identifier_issuer_id,
                    external_identifier.external_id,
                )
                if key not in existing_external_identifier_map:
                    continue
                # External ID already exists
                existing_external_identifier = existing_external_identifier_map[key]
                external_identifier_result.id = existing_external_identifier.id
                external_identifier_result.status = UploadStatus.SKIPPED
                # Cross-validate with parent ID if given and not new ID, otherwise fill in parent ID
                if (
                    parent.id is not None
                    and parent.id != NULL_ID
                    and not parent.is_new_id
                ):
                    # Parent already exists
                    if existing_external_identifier.internal_id != parent.id:
                        success = False
                        external_identifier_result.add_error(
                            "f8a9b0c1",
                            f"External identifier {external_identifier.external_id} refers to {self.parent_class.NAME}.id={existing_external_identifier.internal_id}, which does not match uploaded {self.parent_class.NAME}.id={parent.id}",
                        )
                else:
                    # Parent does not exist yet, fill in parent ID
                    parent.id = existing_external_identifier.internal_id
                    parent_result.id = parent.id

        return success

    def verify_parents(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """Check parent model existence when ID is given"""
        assert isinstance(cmd, command.Command)
        user_id = cmd.user.id if cmd.user else None
        success = True

        # Get parent IDs and check existence
        parent_id_is_new_id_pairs = list(
            {
                (x.id, x.is_new_id)
                for x in self.get_parents_for_upload(cmd)
                if x.id is not None and x.id != NULL_ID
            }
        )
        parent_ids = [x[0] for x in parent_id_is_new_id_pairs]
        new_parent_ids = {x for x, is_new in parent_id_is_new_id_pairs if is_new}
        if parent_ids:
            # Some parent IDs are given, check existence
            # Check existence of given parent IDs
            parents_exist: list[bool] = (
                self.service.repository.crud(  # type:ignore[assignment]
                    uow,
                    user_id,
                    self.parent_class,
                    None,
                    parent_ids,
                    CrudOperation.EXISTS_SOME,
                )
            )
            existing_parent_ids = {x for x, y in zip(parent_ids, parents_exist) if y}
            already_existing_new_parent_ids = new_parent_ids.intersection(
                existing_parent_ids
            )
            for parent, parent_result in self.parent_result_items(cmd, retval):
                parent_id = parent.id
                if parent_id == NULL_ID:
                    parent_id = None
                if parent_id is None:
                    # Parent ID not given, cannot exist
                    continue
                if parent_id in already_existing_new_parent_ids:
                    # Parent ID given as new ID and already exists
                    success = False
                    parent_result.add_error(
                        "e5f43210",
                        f"New ID already exists",
                    )
                    continue
                # Parent ID given as new ID and does not exist, this is acceptable
                if parent.is_new_id:
                    continue
                # Parent ID given but not as new ID, and exists
                if parent_id in existing_parent_ids:
                    parent_result.id = parent_id
                    if cmd.on_exists == OnExistsUploadAction.ERROR:
                        success = False
                        parent_result.add_error(
                            "d3f5b6a1",
                            f"{self.parent_class.NAME} already exists and on_exists={cmd.on_exists.value}.",
                        )
                    continue
                # Parent ID given but not as new ID, and does not exist
                success = False
                parent_result.add_error(
                    "a9b7c4e2",
                    f"{self.parent_class.NAME}.id={parent.id} does not exist.",
                )
        return success

    def verify_children(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """Check child model existence and consistency"""
        assert isinstance(cmd, command.Command)
        user_id = cmd.user.id if cmd.user else None
        success = True

        # Verify each child model for each parent
        for model_class, children_field_name in self.children_field_name_map.items():
            parent_id_field_name = self.child_model_parent_id_field_name_map[
                model_class
            ]
            # Collect all IDs for this child model and determine existence
            child_id_is_new_id_pairs: list[tuple[UUID, bool]] = list(
                {
                    (y.id, y.is_new_id)
                    for x in self.get_parents_for_upload(cmd)
                    for y in getattr(x, children_field_name) or []
                    if y.id is not None and y.id != NULL_ID
                }
            )

            # Get existing children if there are IDs to check
            child_ids = [x[0] for x in child_id_is_new_id_pairs]
            new_child_ids = {x[0] for x in child_id_is_new_id_pairs if x[1]}
            existing_child_ids = set()
            existing_child_parent_id_map: dict[UUID, UUID] = {}
            if child_ids:
                # Some child IDs are given, check existence
                children_exist: list[bool] = (
                    self.service.repository.crud(  # type:ignore[assignment]
                        uow,
                        user_id,
                        model_class,
                        None,
                        child_ids,
                        CrudOperation.EXISTS_SOME,
                    )
                )
                existing_child_ids = {x for x, y in zip(child_ids, children_exist) if y}
                already_existing_new_child_ids = new_child_ids.intersection(
                    existing_child_ids
                )
                # Get (id, parent_id) for all existing ids
                if existing_child_ids:
                    result_iter = self.service.repository.read_fields(
                        uow,
                        user_id,
                        model_class,
                        ["id", parent_id_field_name],
                        filter=UuidSetFilter(
                            key="id", members=frozenset(existing_child_ids)
                        ),
                    )
                    existing_child_parent_id_map = {x[0]: x[1] for x in result_iter}
            else:
                already_existing_new_child_ids = set()

            # Process all children (both with and without IDs)
            for parent, parent_result in self.parent_result_items(cmd, retval):
                children: list[model.Model] = getattr(parent, children_field_name) or []
                child_results: list[UploadResult] = (
                    getattr(parent_result, children_field_name) or []
                )
                for child, child_result in zip(children, child_results):
                    child_parent_id = getattr(child, parent_id_field_name, None)
                    has_parent_id = parent.id is not None and parent.id != NULL_ID
                    has_child_parent_id = (
                        child_parent_id is not None and child_parent_id != NULL_ID
                    )
                    # Check consistency of parent ID in child and assign in either direction if possible
                    if has_parent_id:
                        # Parent ID given
                        if has_child_parent_id:
                            # Child parent ID given: check if identical
                            if parent.id != child_parent_id:
                                success = False
                                child_result.add_error(
                                    "b4c5d6e7",
                                    f"{parent_id_field_name}={child_parent_id} does not match {self.parent_for_upload_class.NAME}.id={parent.id}",
                                )
                            if child.id in existing_child_ids:
                                # Child exists: check if parent ID matches existing data
                                assert child.id is not None
                                existing_parent_id = existing_child_parent_id_map.get(
                                    child.id
                                )
                                if existing_parent_id != parent.id:
                                    success = False
                                    child_result.add_error(
                                        "e8f9a0b1",
                                        f"{model_class.NAME}.id={child.id} refers to {parent_id_field_name}={existing_parent_id}, which does not match existing {self.parent_for_upload_class.NAME}.id={parent.id}",
                                    )
                        else:
                            # Child parent ID not given: fill in from parent
                            setattr(child, parent_id_field_name, parent.id)
                    else:
                        # Parent ID not given
                        if has_child_parent_id:
                            # Parent ID not given: fill in from child
                            parent.id = child_parent_id
                        else:
                            # Neither parent ID nor child parent ID given
                            pass
                    # Continue with child ID
                    if child.id == NULL_ID:
                        # Set child ID to None if NULL_ID
                        child.id = None
                    # Child does not exist yet
                    if child.id is None:
                        continue
                    # Child ID given as new ID and already exists
                    if child.id in already_existing_new_child_ids:
                        success = False
                        child_result.add_error(
                            "a7b2c4d8",
                            "New ID already exists",
                        )
                        continue
                    # New ID given and does not exist, this is acceptable
                    if getattr(child, "is_new_id"):
                        continue
                    # Child ID given but not as new ID, and does not exist
                    if child.id not in existing_child_ids:
                        success = False
                        child_result.add_error(
                            "d4f5e6a7",
                            f"ID does not exist",
                        )
                        continue  # Skip to next child since this one doesn't exist
                    # Child ID given but not as new ID, and exists
                    if cmd.on_exists == OnExistsUploadAction.ERROR:
                        success = False
                        child_result.add_error(
                            "c6e7f8a0",
                            f"{child.__class__.NAME} already exists and on_exists={cmd.on_exists.value}",
                        )
        return success

    def verify_refdata(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """
        Verify reference data values. Performs no action and returns True by default.

        Override as needed.
        """
        return True

    def verify_link_id(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
        child_field_name_or_class: str | type[model.Model],
        link_id_field_name: str,
        link_code_field_name: str,
        linked_model_class: type[model.Model],
        linked_model_id_field_name: str = "id",
        linked_model_code_field_name: str = "code",
        is_same_service: bool = True,
        is_frozen: bool = False,
    ) -> bool:
        """Set and verify entities provided by ID and/or code, filling in IDs and verifying consistency"""
        assert isinstance(cmd, command.Command)
        user_id = cmd.user.id if cmd.user else None
        success = True

        # Get child field name
        if isinstance(child_field_name_or_class, str):
            child_field_name = child_field_name_or_class
        else:
            child_field_name = self.children_field_name_map[child_field_name_or_class]

        # Initialize some data
        id_code_tuples = list(
            {
                (getattr(y, link_id_field_name), getattr(y, link_code_field_name))
                for x in self.get_parents_for_upload(cmd)
                for y in getattr(x, child_field_name) or []
            }
        )
        ids = {x[0] for x in id_code_tuples if x[0] is not None and x[0] != NULL_ID}
        codes = {x[1] for x in id_code_tuples if x[1] is not None}
        id_code_map: dict[UUID, str] = {}
        code_id_map: dict[str, UUID] = {}

        # Retrieve links from child model provided by ID and/or code
        if not ids and not codes:
            # No IDs or codes provided, nothing to look up (but NULL_ID still has to be verified)
            pass
        elif is_same_service:
            # Same service: use repository directly
            result_iter = self.service.repository.read_fields(
                uow,
                user_id,
                linked_model_class,
                [linked_model_id_field_name, linked_model_code_field_name],
                filter=CompositeFilter(
                    operator=LogicalOperator.OR,
                    filters=[
                        UuidSetFilter(
                            key=linked_model_id_field_name, members=frozenset(ids)
                        ),
                        StringSetFilter(
                            key=linked_model_code_field_name, members=frozenset(codes)
                        ),
                    ],
                ),
            )
            id_code_map = {x[0]: x[1] for x in result_iter}
            code_id_map = {y: x for x, y in id_code_map.items()}
        else:
            # Different service: issue a command
            crud_command_class = self.service.app.domain.get_crud_command_for_model(
                linked_model_class
            )
            link_objs: list[model.Model] = self.service.app.handle(
                crud_command_class(
                    user=cmd.user,
                    operation=CrudOperation.READ_ALL,
                    query_filter=CompositeFilter(
                        operator=LogicalOperator.OR,
                        filters=[
                            UuidSetFilter(
                                key=linked_model_id_field_name, members=frozenset(ids)
                            ),
                            StringSetFilter(
                                key=linked_model_code_field_name,
                                members=frozenset(codes),
                            ),
                        ],
                    ),
                )
            )
            id_code_map = {
                getattr(x, linked_model_id_field_name): getattr(
                    x, linked_model_code_field_name
                )
                for x in link_objs
            }
            code_id_map = {
                getattr(x, linked_model_code_field_name): getattr(
                    x, linked_model_id_field_name
                )
                for x in link_objs
            }

        # Verify links
        for parent, parent_result in self.parent_result_items(cmd, retval):
            children: list[model.Model] = getattr(parent, child_field_name) or []
            child_results: list[UploadResult] = (
                getattr(parent_result, child_field_name) or []
            )
            for i, (child, child_result) in enumerate(zip(children, child_results)):
                # Get link ID and code
                link_id = getattr(child, link_id_field_name)
                is_null_id = link_id == NULL_ID
                if is_null_id:
                    link_id = None
                link_code = getattr(child, link_code_field_name)
                # Check all combinations of link ID and code provided/not provided
                if link_id is None:
                    # Link ID not provided
                    if link_code is None:
                        # Neither link ID nor code provided
                        if is_null_id:
                            # NULL_ID provided: error since eventual ID may not be NULL_ID
                            success = False
                            child_result.add_error(
                                "b7c2e5f8",
                                f"{linked_model_id_field_name}=NULL_ID could not be resolved",
                            )
                        else:
                            # Nothing provided: optional link assumed, nothing to do
                            pass
                    else:
                        # Link code provided but not link ID
                        if link_code not in code_id_map:
                            # Link code does not exist
                            success = False
                            child_result.add_error(
                                "d2c4b6a8",
                                f"{linked_model_code_field_name}={link_code} does not exist",
                            )
                        else:
                            # Link code exists: fill in link ID
                            if is_frozen:
                                # Need to create a new instance since the class is frozen
                                new_child = child.model_copy(
                                    update={link_id_field_name: code_id_map[link_code]}
                                )
                                children[i] = new_child
                            else:
                                # Not a frozen class, can set attribute directly
                                setattr(
                                    child,
                                    link_id_field_name,
                                    code_id_map[link_code],
                                )
                else:
                    # Link ID provided
                    if link_id not in id_code_map:
                        # Link ID does not exist
                        success = False
                        child_result.add_error(
                            "e3b5c7d9",
                            f"{linked_model_id_field_name}={link_id} does not exist",
                        )
                    elif link_code is None:
                        # Link ID exists and code not given: nothing to do since code is only meant to look up ID
                        pass
                    elif link_code not in code_id_map:
                        # Link code does not exist
                        success = False
                        child_result.add_error(
                            "c7a9b2e4",
                            f"{linked_model_code_field_name}={link_code} does not exist",
                        )
                    elif link_code != id_code_map[link_id]:
                        # Link ID exists but code does not match provided code
                        success = False
                        child_result.add_error(
                            "a4d7b9c3",
                            f"{linked_model_code_field_name}={link_code} with {linked_model_id_field_name}={code_id_map[link_code]} does not match provided {linked_model_id_field_name}={link_id}",
                        )
                    else:
                        # Link ID and code both exist and match: nothing to do
                        pass
        return success

    def create_parents(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create any parents.
        """
        assert isinstance(cmd, command.Command)
        success = True

        # Determine which parents need to be created
        to_create_parent_result_tuples: list[
            tuple[model.ParentForUpload, model.Model, model.UploadResult]
        ] = [  # type:ignore[assignment]
            (x, x.get_parent(), y)
            for x, y in self.parent_result_items(cmd, retval)
            if (x.id is None or x.id == NULL_ID or x.is_new_id)
            and y.status == UploadStatus.PENDING
            and x.get_parent() is not None
        ]
        if not to_create_parent_result_tuples:
            return success
        to_create_parent_result_pairs = [
            (x[1], x[2]) for x in to_create_parent_result_tuples
        ]

        # Create parents
        success &= self.create_objects(
            uow,
            cmd.user.id if cmd.user else None,
            to_create_parent_result_pairs,
        )

        # Update parent IDs in ParentForUpload instances
        for parent_for_upload, parent, _ in to_create_parent_result_tuples:
            parent_for_upload.id = parent.id

        return success

    def update_parents(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Update any parents.
        """
        assert isinstance(cmd, command.Command)
        success = True

        # Determine which parents need to be updated
        to_update_parent_result_tuples: list[
            tuple[model.ParentForUpload, model.Model, model.UploadResult]
        ] = [
            (x, x.get_parent(), y)  # type:ignore[arg-type]
            for x, y in self.parent_result_items(cmd, retval)
            if x.id is not None
            and x.id != NULL_ID
            and not x.is_new_id
            and y.status == UploadStatus.PENDING
            and x.get_parent() is not None
        ]
        if not to_update_parent_result_tuples:
            return success
        to_update_parent_result_pairs = [
            (x[1], x[2]) for x in to_update_parent_result_tuples
        ]

        # Update parents
        success &= self.update_objects(
            uow,
            cmd.user.id if cmd.user else None,
            to_update_parent_result_pairs,
        )

        # Update parent IDs in ParentForUpload instances (should already be set, but just in case)
        for parent_for_upload, parent, parent_result in to_update_parent_result_tuples:
            parent_for_upload.id = parent.id

        return success

    def create_children(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create any child models. Assumes that the parent models already exist.
        """
        assert isinstance(cmd, command.Command)
        user_id = cmd.user.id if cmd.user else None
        success = False

        # Create each child model for each parent
        for model_class, children_field_name in self.children_field_name_map.items():
            parent_id_field_name = self.child_model_parent_id_field_name_map[
                model_class
            ]
            for_upload_model_class = self.child_for_upload_class_map[model_class]
            # Determine which objects need to be created
            to_create_child_result_pairs = []
            for parent, parent_result in self.parent_result_items(cmd, retval):
                children: list[model.Model] | None = getattr(
                    parent, children_field_name
                )
                child_results: list[UploadResult] | None = getattr(
                    parent_result, children_field_name
                )
                for child, child_result in zip(children or [], child_results or []):
                    if (
                        child.id is None or child.id == NULL_ID
                    ) and child_result.status == UploadStatus.PENDING:
                        # Set parent ID link in child, which is known for certain at this point
                        setattr(child, parent_id_field_name, parent.id)
                        # Collect for creation
                        if isinstance(child, for_upload_model_class):
                            actual_child = model_class(**child.model_dump())
                            to_create_child_result_pairs.append(
                                (actual_child, child_result)
                            )
                        else:
                            to_create_child_result_pairs.append((child, child_result))
            if not to_create_child_result_pairs:
                continue

            # Create the objects
            self.create_objects(
                uow,
                user_id,
                to_create_child_result_pairs,
            )

        success = True
        return success

    def update_children(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Update any child models. Assumes that the parent models already exist.
        """
        assert isinstance(cmd, command.Command)
        user_id = cmd.user.id if cmd.user else None
        success = True

        # Update each child model for each parent
        for model_class, children_field_name in self.children_field_name_map.items():
            parent_id_field_name = self.child_model_parent_id_field_name_map[
                model_class
            ]
            # Determine which children need to be updated
            to_update_child_result_pairs = []
            for parent, parent_result in self.parent_result_items(cmd, retval):
                children: list[model.Model] | None = getattr(
                    parent, children_field_name
                )
                child_results: list[UploadResult] | None = getattr(
                    parent_result, children_field_name
                )
                for child, child_result in zip(children or [], child_results or []):
                    if (
                        child.id is not None
                        and child.id != NULL_ID
                        and child_result.status == UploadStatus.PENDING
                    ):
                        # Set parent ID link in child, which is known for certain at this point
                        setattr(child, parent_id_field_name, parent.id)
                        # Collect for update
                        to_update_child_result_pairs.append((child, child_result))
            if not to_update_child_result_pairs:
                continue

            success &= self.update_objects(
                uow,
                user_id,
                to_update_child_result_pairs,
            )
        return success

    def create_external_identifiers(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        assert isinstance(cmd, command.Command)
        success = True

        # Determine which external identifiers need to be created and derive actual model from for upload version
        to_create_external_identifier_result_pairs: list[
            tuple[model.ExternalIdentifier, model.UploadResult]
        ] = []
        for parent, parent_result in self.parent_result_items(cmd, retval):
            external_identifiers_for_upload: list[model.ExternalIdentifierForUpload] = (
                getattr(parent, self.external_identifiers_field_name) or []
            )
            external_identifier_results: list[UploadResult] = (
                getattr(parent_result, self.external_identifiers_field_name) or []
            )
            for external_identifier_for_upload, external_identifier_result in zip(
                external_identifiers_for_upload, external_identifier_results
            ):
                if external_identifier_result.status != UploadStatus.PENDING:
                    # Not pending (likely skipped or failed), no need to create
                    continue
                external_identifier = model.ExternalIdentifier(
                    id=None,
                    internal_id=parent.id,  # type: ignore[arg-type]
                    identifier_type=self.parent_identifier_type,
                    identifier_issuer_id=external_identifier_for_upload.identifier_issuer_id,  # type: ignore[arg-type]
                    external_id=external_identifier_for_upload.external_id,
                )
                to_create_external_identifier_result_pairs.append(
                    (external_identifier, external_identifier_result)
                )
        if not to_create_external_identifier_result_pairs:
            return success

        # Create external identifiers
        external_identifiers = [
            x[0] for x in to_create_external_identifier_result_pairs
        ]
        external_identifier_results = [
            x[1] for x in to_create_external_identifier_result_pairs
        ]
        external_identifier_crud_command_class = (
            self.service.app.domain.get_crud_command_for_model(model.ExternalIdentifier)
        )
        create_cmd = external_identifier_crud_command_class(
            user=cmd.user,
            operation=CrudOperation.CREATE_SOME,
            objs=external_identifiers,  # type: ignore[arg-type]
        )
        created_external_identifiers: list[model.ExternalIdentifier] = (
            self.service.app.handle(create_cmd)
        )

        # Update results
        for created_external_identifier, external_identifier_result in zip(
            created_external_identifiers, external_identifier_results
        ):
            external_identifier_result.id = created_external_identifier.id
            external_identifier_result.status = UploadStatus.CREATED

        return success

    def create_refdata(
        self,
        cmd: command.UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create any new reference data entries as needed. Performs no action and
        returns True.

        Override as needed.
        """
        return True

    def create_objects(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        to_create_obj_result_pairs: list[tuple[model.Model, UploadResult]],
    ) -> bool:
        """
        Create any new objects and update the corresponding UploadResults.
        ️"""
        success = True
        if not to_create_obj_result_pairs:
            return success

        # Determine model class
        model_class = type(to_create_obj_result_pairs[0][0])

        # Create objects, assigning and ID where necessary
        to_create_objs = [x for x, _ in to_create_obj_result_pairs]
        for obj in to_create_objs:
            if obj.id is None or obj.id == NULL_ID:
                # Assign a new ID
                obj.id = self.service.generate_id()  # type: ignore[assignment]
        to_create_obj_results = [x for _, x in to_create_obj_result_pairs]
        created_obj_ids: list[UUID] = (
            self.service.repository.crud(  # type:ignore[assignment]
                uow,
                user_id,
                model_class,
                to_create_objs,
                None,
                operation=CrudOperation.CREATE_SOME,
                return_id=True,  # Avoid returning the whole object list again
            )
        )

        # Assign object ID and status to results
        for created_obj_id, obj_result in zip(created_obj_ids, to_create_obj_results):
            obj_result.id = created_obj_id
            obj_result.status = UploadStatus.CREATED

        return success

    def update_objects(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        to_update_obj_result_pairs: list[tuple[model.Model, UploadResult]],
    ) -> bool:
        """
        Update any existing objects and update the corresponding UploadResults.
        """
        success = True
        if not to_update_obj_result_pairs:
            return success

        # Collect object IDs to update
        obj_ids = [x.id for x, _ in to_update_obj_result_pairs]
        if not obj_ids:
            return success

        # Determine model class and stored model field properties
        model_class = type(to_update_obj_result_pairs[0][0])
        stored_model_field_props = self.stored_model_field_props[model_class]

        # Retrieve existing objects
        existing_objs: list[model.Model] = (
            self.service.repository.crud(  # type:ignore[assignment]
                uow,
                user_id,
                model_class,
                None,
                obj_ids,
                operation=CrudOperation.READ_SOME,
            )
        )

        # Determine which objects actually need to be updated instead of having identical data
        to_update_objs: list[model.Model] = []
        to_update_obj_results: list[model.UploadResult] = []
        for (obj, obj_result), existing_obj in zip(
            to_update_obj_result_pairs, existing_objs
        ):
            # Only check props for updates, other fields are not updatable
            is_updated = False
            for field_name, field_props in stored_model_field_props.items():
                existing_value = getattr(existing_obj, field_name)
                # Field if the field, with its existing value, is (still) mutable
                if not field_props.is_mutable_value(existing_value):
                    success = False
                    obj_result.status = UploadStatus.FAILED
                    obj_result.add_error(
                        "d3c9f6b1",
                        f"Field {field_name} with existing value {existing_value} may not be updated.",
                    )
                    continue
                # Update the existing object's field if the new value is different
                new_value = getattr(obj, field_name)
                if existing_value is None:
                    # Existing value is None: set new value if not None
                    if new_value:
                        is_updated = True
                        setattr(existing_obj, field_name, new_value)
                elif field_props.is_sub_field_dict:
                    # Field content is a dict: update keys individually
                    is_updated |= BatchUploader.update_sub_field_dict(
                        existing_value, new_value
                    )
                else:
                    # Field content is a single value: compare directly
                    if new_value != existing_value:
                        is_updated = True
                        setattr(existing_obj, field_name, new_value)
            # Determine whether to update, i.e. if any values are indeed different, or otherwise skip
            if not is_updated:
                obj_result.status = UploadStatus.SKIPPED
                obj_result.add_info("f7a8b2d4", "Content is identical")
            else:
                to_update_objs.append(obj)
                to_update_obj_results.append(obj_result)

        # Stop if there were errors
        if not success:
            return success

        # Update the objects whose data are different
        if not to_update_objs:
            return success
        _: list[UUID] = self.service.repository.crud(  # type:ignore[assignment]
            uow,
            user_id,
            model_class,
            to_update_objs,
            None,
            operation=CrudOperation.UPDATE_SOME,
            return_id=True,  # Avoid returning the whole object list again
        )

        # Assign status to results
        for obj_result in to_update_obj_results:
            obj_result.status = UploadStatus.UPDATED

        return success

    @staticmethod
    def update_sub_field_dict(content: dict, updates: dict | None) -> bool:
        """
        Update a dictionary in place with new values and return whether any updates were
        made.

        An update is made if:
        - A key from updates does not exist in content and its value is not
            None, add it to content.
        - A key from updates exists in content:
            - If the new value is None: the key is then also removed from content.
            - If the new value is different from the existing value.
        """
        is_updated = False
        if not updates:
            return is_updated
        for key, value in updates.items():
            if key not in content:
                if value is not None:
                    # New key with not None value, update it
                    is_updated = True
                    content[key] = value
            else:
                orig_value = content[key]
                if value is None:
                    # New value is None, remove the key
                    if orig_value is not None:
                        is_updated = True
                    del content[key]
                elif orig_value != value:
                    # New value is different, update it
                    is_updated = True
                    content[key] = value
                else:
                    # New value is the same, do nothing
                    pass
        return is_updated
