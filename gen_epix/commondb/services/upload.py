from typing import Generator
from uuid import UUID

from gen_epix import fastapp
from gen_epix.commondb.domain import command, enum, exc, model
from gen_epix.commondb.domain.enum import UploadAction, UploadStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload,
    BaseBatchUploadResult,
    ExternalIdentifiersMixin,
    UploadResult,
    UploadResultWithExternalIdentifiers,
)
from gen_epix.fastapp import BaseService, BaseUnitOfWork, CrudOperation, Model
from gen_epix.filter import (
    CompositeFilter,
    EqualsNumberFilter,
    LogicalOperator,
    StringSetFilter,
    UuidSetFilter,
)


class BatchUploader:
    """
    A class encapsulating batch upload functionality, intended as a singleton.
    """

    def __init__(
        self,
        upload_batch_command_class: type[command.UploadBatchCommandMixin],
        stored_model_field_props: dict[type[Model], dict[str, fastapp.ModelFieldProps]],
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
            self.parent_for_upload_class.EXTERNAL_IDENTIFIER_TYPE
        )
        self.parent_class = self.parent_for_upload_class.PARENT_CLASS
        self.parent_result_class = self.batch_upload_result_class.PARENT_RESULT_CLASS
        self.parent_id_field_name = self.parent_class.ENTITY.get_id_field_name()
        self.child_for_upload_class_map = (
            self.parent_for_upload_class.CHILD_FOR_UPLOAD_CLASS_MAP
        )
        self.children_field_name_map = (
            self.parent_for_upload_class.CHILDREN_FIELD_NAME_MAP
        )
        self.child_model_parent_id_field_name_map = (
            self.parent_for_upload_class.CHILD_PARENT_ID_FIELD_NAME_MAP
        )
        self.child_model_id_field_name_map = {
            x: x.ENTITY.get_id_field_name() for x in self.children_field_name_map.keys()
        }

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
        self, batch_result: BaseBatchUploadResult
    ) -> list[model.ParentUploadResult]:
        """Get parent upload results from the batch upload result."""
        return batch_result.get_parent_results()

    def parent_result_items(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
    ) -> Generator[tuple[model.ParentForUpload, model.ParentUploadResult], None, None]:
        """Get (parent, parent_result) items from the batch upload result."""
        parents = cmd.get_batch_for_upload().get_parents_for_upload()
        parent_results = batch_result.get_parent_results()
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
        batch_result = self.init_batch_upload_result(cmd)
        batch_result.add_info(
            code="f1e2d3c4",
            message="Upload started",
        )

        with self.service.repository.uow() as uow:
            # Verify batch
            batch_result.add_info(
                code="8b4c2f91",
                message="Verification started",
            )
            success = self.verify_batch(cmd, batch_result, uow)
            batch_result.add_info(
                code="a3f7e9d2",
                message="Verification ended",
            )
            if cmd.verify_only:
                # Stop here if only verification was requested
                batch_result.add_info(
                    code="c849b0e2",
                    message="Verification only requested, upload will not proceed",
                )
                return batch_result
            if not success:
                # Do not proceed with upsert due to errors
                batch_result.add_error(
                    code="d6e5c3b4",
                    message="Verification found errors, upload will not proceed",
                )
                return batch_result

            # Upsert the batch data
            batch_result.add_info(
                code="c1a2b3d4",
                message="Upsert started",
            )
            success = self.upsert_batch(cmd, batch_result, uow)
            batch_result.add_info(
                code="e4f5a6b7",
                message="Upsert ended",
            )
            if not success:
                # Rollback due to errors, but do not raise an exception since those will be reported in batch_result
                batch_result.add_error(
                    code="f8e7d6c5",
                    message="Upload had errors",
                )
                uow.rollback()
                batch_result.add_info(
                    code="7729440d",
                    message="Upload had errors, changes have been rolled back",
                )
        batch_result.add_info(
            code="7b9e4a2f",
            message="Upload ended",
        )

        # Assign final status
        if batch_result.status == UploadStatus.PENDING:
            status_count = batch_result.get_status_count(include_self=False)
            n_results = sum(status_count.values())
            if status_count[UploadStatus.SKIPPED] == n_results:
                batch_result.status = UploadStatus.SKIPPED
            elif status_count[UploadStatus.CREATED] == n_results:
                batch_result.status = UploadStatus.CREATED
            elif status_count[UploadStatus.UPDATED] == n_results:
                batch_result.status = UploadStatus.UPDATED
            else:
                # Mixed results, use status processed
                batch_result.status = UploadStatus.PROCESSED

        return batch_result

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
            for (
                child_model_class,
                children_field_name,
            ) in self.children_field_name_map.items():
                child_id_field_name = self.child_model_id_field_name_map[
                    child_model_class
                ]
                children_for_upload: list[Model] | None = getattr(
                    parent_for_upload, children_field_name
                )
                child_results: list[UploadResult] | None = None
                # Special case: no children
                if not children_for_upload:
                    setattr(
                        parent_result,
                        children_field_name,
                        None if children_for_upload is None else [],
                    )
                    continue
                # Determine if child model has external identifiers based on whether the corresponding child for upload class implements ExternalIdentifiersMixin
                has_external_identifiers = isinstance(
                    children_for_upload[0], ExternalIdentifiersMixin
                )
                if has_external_identifiers:
                    # Child class has external identifiers, for which (sub)upload results also need to be initialized
                    child_results = []
                    for child_for_upload in children_for_upload:
                        external_identifiers = child_for_upload.external_identifiers
                        external_identifier_results = (
                            None
                            if external_identifiers is None
                            else [
                                UploadResult(status=UploadStatus.PENDING)
                                for _ in external_identifiers
                            ]
                        )
                        child_results.append(
                            UploadResultWithExternalIdentifiers(
                                status=UploadStatus.PENDING,
                                external_identifiers=external_identifier_results,
                            )
                        )
                else:
                    # Child class does not have external identifiers, only initialize corresponding upload result for the child
                    child_results = [
                        UploadResult(
                            id=getattr(x, child_id_field_name),
                            status=UploadStatus.PENDING,
                        )
                        for x in children_for_upload
                    ]
                setattr(parent_result, children_field_name, child_results)
            # Add parent result to parent results
            parent_results.append(parent_result)

        # Initialize batch result
        kwargs = {self.batch_parents_for_upload_field_name: parent_results}
        batch_result = self.batch_upload_result_class(
            batch_id=cmd.id,
            status=UploadStatus.PENDING,
            **kwargs,  # type: ignore[arg-type]
        )
        return batch_result

    def verify_batch(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Verify parents, children, external identifiers and reference data.
        """
        success = True
        # Verify external identifiers first to fill in any missing parent IDs
        success &= self.verify_parents_external_identifiers(cmd, batch_result, uow)
        # Verify external identifiers for child models to fill in any missing child IDs
        success &= self.verify_children_external_identifiers(cmd, batch_result, uow)
        success &= self.verify_parents(cmd, batch_result, uow)
        success &= self.verify_children(cmd, batch_result, uow)
        # Verify reference data last since it may depend on parent and children verification
        success &= self.verify_refdata(cmd, batch_result, uow)
        return success

    def upsert_batch(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create or update parents, children, external identifiers and reference data.
        """
        success = True
        # Create refdata before parents and children to ensure all references exist
        success &= self.create_refdata(cmd, batch_result, uow)
        # Create and update parents before children to ensure parents exist
        success &= self.create_parents(cmd, batch_result, uow)
        success &= self.update_parents(cmd, batch_result, uow)
        success &= self.create_children(cmd, batch_result, uow)
        success &= self.update_children(cmd, batch_result, uow)
        # Create external identifiers last to preserve atomicity without two-phase
        # commit: if there were any errors after this and a rollback is therefore
        # needed, the external identifiers could otherwise have already been changed
        # in the meantime
        success &= self.create_external_identifiers(cmd, batch_result, uow)
        return success

    def verify_parents_external_identifiers(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """Retrieve and verify identifier issuers in external IDs"""
        assert isinstance(cmd, command.Command)
        success = True

        # Retrieve and verify identifier issuers in external IDs provided by ID
        parent_result_items = list(self.parent_result_items(cmd, batch_result))
        success &= self.verify_link_id(
            parent_result_items,
            uow,
            cmd.user,
            "external_identifiers",
            "identifier_issuer_id",
            "identifier_issuer_code",
            model.IdentifierIssuer,
            is_same_service=False,
            is_frozen=True,
        )

        success &= self.verify_external_identifiers(
            cmd.user,
            self.parent_for_upload_class,
            self.parent_identifier_type,
            parent_result_items,
        )

        # Fill in parent IDs based on external identifiers where possible
        for parent_for_upload, _ in parent_result_items:
            parent = parent_for_upload.get_parent()
            if parent is not None:
                setattr(parent, self.parent_id_field_name, parent_for_upload.id)

        return success

    def verify_children_external_identifiers(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """
        Verify external identifiers in any of the child objects. This includes
        verifying that any provided external identifier IDs exist and are accessible
        by the user, and filling in any missing IDs based on provided codes.
        """
        assert isinstance(cmd, command.Command)
        success = True
        # Get list of (child_for_upload, child_result) tuples for all children across all parents
        parent_result_pairs = list(self.parent_result_items(cmd, batch_result))
        for (
            child_model_class,
            children_field_name,
        ) in self.children_field_name_map.items():
            child_model_for_upload_class = self.child_for_upload_class_map[
                child_model_class
            ]
            has_external_identifiers = issubclass(
                child_model_for_upload_class, ExternalIdentifiersMixin
            )
            if not has_external_identifiers:
                # This child model does not have external identifiers, skip
                continue
            # Get child_for_upload-result pairs
            child_result_pairs = []
            for parent_for_upload, parent_result in parent_result_pairs:
                child_result_pairs.extend(
                    zip(
                        getattr(parent_for_upload, children_field_name) or [],
                        getattr(parent_result, children_field_name) or [],
                    )
                )
            # Verify identifier issuer IDs and codes
            success &= self.verify_link_id(
                child_result_pairs,
                uow,
                cmd.user,
                "external_identifiers",
                "identifier_issuer_id",
                "identifier_issuer_code",
                model.IdentifierIssuer,
                is_same_service=False,
                is_frozen=True,
            )
            # Verify existing external identifiers for all children
            success &= self.verify_external_identifiers(
                cmd.user,
                child_model_class,
                child_model_for_upload_class.EXTERNAL_IDENTIFIER_TYPE,
                child_result_pairs,
            )
        return success

    def verify_parents(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """Check parent model existence when ID is given"""
        assert isinstance(cmd, command.Command)
        user_id = cmd.user.id if cmd.user else None
        success = True
        n_parents = cmd.get_n_parents()
        if n_parents == 0:
            return success

        # Get parent IDs and set status when no parent
        parent_ids: list[UUID | None] = [None] * n_parents
        has_parent_ids = False
        for i, (parent_for_upload, parent_result) in enumerate(
            self.parent_result_items(cmd, batch_result)
        ):
            parent_id = parent_for_upload.id
            parent = parent_for_upload.get_parent()
            if parent is None:
                # Parent not given, set status to SKIPPED
                parent_result.status = UploadStatus.SKIPPED
                continue
            if self.is_null(parent_id):
                # Parent given but ID not given while external identifiers already verified, will need to be created
                parent_result.is_new = True
                continue
            parent_ids[i] = parent_id
            has_parent_ids = True

        if not has_parent_ids:
            # No parent IDs given, nothing left to check
            return success

        # Some parent IDs are given, check existence
        parents_exist = self.objects_exist(uow, user_id, self.parent_class, parent_ids)
        for parent_exists, (parent_for_upload, parent_result) in zip(
            parents_exist, self.parent_result_items(cmd, batch_result)
        ):
            if parent_exists:
                parent_result.id = parent_for_upload.id
                if cmd.on_exists == UploadAction.ERROR:
                    success = False
                    parent_result.add_error(
                        "d3f5b6a1",
                        f"{self.parent_class.NAME} already exists and on_exists={cmd.on_exists.value}.",
                    )
                elif cmd.on_exists == UploadAction.SKIP:
                    # Existing parent and on_exists=SKIP: do not update
                    parent_result.status = UploadStatus.SKIPPED
                    parent_result.add_info(
                        "a7c3f42e",
                        f"{self.parent_class.NAME} already exists and on_exists={cmd.on_exists.value}.",
                    )
            else:
                parent_result.is_new = True
                if cmd.on_new == UploadAction.ERROR:
                    success = False
                    parent_result.add_error(
                        "e5a6c7b2",
                        f"{self.parent_class.NAME} does not exist and on_new={cmd.on_new.value}.",
                    )
                elif cmd.on_new == UploadAction.SKIP:
                    # New parent and on_new=SKIP: do not create
                    parent_result.status = UploadStatus.SKIPPED
                    parent_result.add_info(
                        "b6d7e8f3",
                        f"{self.parent_class.NAME} does not exist and on_new={cmd.on_new.value}.",
                    )
                elif cmd.on_new == UploadAction.CREATE:
                    # New parent and on_new=CREATE: will be created, nothing left to check for this parent
                    if self.is_null(parent_for_upload.id):
                        parent_result.add_info(
                            "c8f9a0b4",
                            f"{self.parent_class.NAME} will be created with generated ID",
                        )
                    else:
                        parent_result.add_info(
                            "9b5d4e32",
                            f"{self.parent_class.NAME} will be created with provided ID",
                        )
        return success

    def verify_children(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """Check child model existence and consistency"""
        assert isinstance(cmd, command.Command)
        user_id = cmd.user.id if cmd.user else None
        success = True

        # Verify each child model for each parent
        parents_for_upload = self.get_parents_for_upload(cmd)
        parent_results = self.get_parent_results(batch_result)
        for (
            child_model_class,
            children_field_name,
        ) in self.children_field_name_map.items():
            child_id_field_name = self.child_model_id_field_name_map[child_model_class]
            child_parent_id_field_name = self.child_model_parent_id_field_name_map[
                child_model_class
            ]
            parent_child_tuples = self._get_parents_and_children(
                parents_for_upload, parent_results, children_field_name
            )

            # Get existing children
            child_ids = [
                getattr(x, child_id_field_name) for _, _, x, _ in parent_child_tuples
            ]
            children_exist = self.objects_exist(
                uow, user_id, child_model_class, child_ids
            )

            # Get (id, parent_id) for all existing ids
            child_parent_id_map: dict[UUID, UUID] = {}
            if any(children_exist):
                result_iter = self.service.repository.read_fields(
                    uow,
                    user_id,
                    child_model_class,
                    [child_id_field_name, child_parent_id_field_name],
                    filter=UuidSetFilter(
                        key=child_id_field_name,
                        members=frozenset(
                            [x for x, y in zip(child_ids, children_exist) if y]
                        ),
                    ),
                )
                child_parent_id_map = {x[0]: x[1] for x in result_iter}

            # Process all children (both with and without IDs)
            for (
                parent_for_upload,
                _,
                child_for_upload,
                child_result,
            ), child_exists in zip(parent_child_tuples, children_exist):
                parent_id = parent_for_upload.id
                has_parent_id = not self.is_null(parent_id)
                child_id = getattr(child_for_upload, child_id_field_name)
                child_parent_id = getattr(
                    child_for_upload, child_parent_id_field_name, None
                )
                has_child_parent_id = not self.is_null(child_parent_id)
                # Set child is new
                child_result.is_new = not child_exists
                # Check consistency of parent ID in child and assign in either direction if possible
                if has_parent_id:
                    # Parent ID given
                    if has_child_parent_id:
                        # Child parent ID given: check if identical
                        if parent_id != child_parent_id:
                            success = False
                            child_result.add_error(
                                "13ba4246",
                                f"{child_parent_id_field_name}={child_parent_id} does not match {self.parent_for_upload_class.NAME}.{self.parent_id_field_name}={parent_id}",
                            )
                        if child_exists:
                            # Child exists: check if parent ID matches existing data
                            assert child_id is not None
                            existing_parent_id = child_parent_id_map.get(child_id)
                            if existing_parent_id != parent_id:
                                success = False
                                child_result.add_error(
                                    "e8f9a0b1",
                                    f"{child_model_class.NAME}.id={child_id} refers to {child_parent_id_field_name}={existing_parent_id}, which does not match existing {self.parent_for_upload_class.NAME}.{self.parent_id_field_name}={parent_id}",
                                )
                    else:
                        # Child parent ID not given: fill in from parent
                        setattr(child_for_upload, child_parent_id_field_name, parent_id)
                else:
                    # Parent ID not given
                    if has_child_parent_id:
                        # Parent ID not given: fill in from child
                        setattr(
                            parent_for_upload,
                            self.parent_id_field_name,
                            child_parent_id,
                        )
                    else:
                        # Neither parent ID nor child parent ID given
                        pass
                # Child ID given
                if child_exists:
                    # Child already exists
                    if cmd.on_exists == UploadAction.ERROR:
                        success = False
                        child_result.add_error(
                            "c6e7f8a0",
                            f"{child_for_upload.__class__.NAME} already exists and on_exists={cmd.on_exists.value}",
                        )
                    elif cmd.on_exists == UploadAction.SKIP:
                        # Existing child and on_exists=SKIP: do not update
                        child_result.status = UploadStatus.SKIPPED
                        child_result.add_info(
                            "7a3f2c81",
                            f"{child_for_upload.__class__.NAME} already exists and on_exists={cmd.on_exists.value}",
                        )
                else:
                    # Child does not exist yet
                    if cmd.on_new == UploadAction.ERROR:
                        success = False
                        child_result.add_error(
                            "d5a6b7c2",
                            f"{child_for_upload.__class__.NAME} does not exist and on_new={cmd.on_new.value}",
                        )
                    elif cmd.on_new == UploadAction.SKIP:
                        # New child and on_new=SKIP: do not create
                        child_result.status = UploadStatus.SKIPPED
                        child_result.add_info(
                            "8b7c6d3f",
                            f"{child_for_upload.__class__.NAME} does not exist and on_new={cmd.on_new.value}",
                        )
                    elif cmd.on_new == UploadAction.CREATE:
                        # New child and on_new=CREATE: will be created
                        if self.is_null(child_id):
                            child_result.add_info(
                                "c8f9a0b4",
                                f"{child_for_upload.__class__.NAME} will be created with generated ID",
                            )
                        else:
                            child_result.add_info(
                                "9b5d4e32",
                                f"{child_for_upload.__class__.NAME} will be created with provided ID",
                            )
        return success

    def verify_refdata(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """
        Verify reference data values. Performs no action and returns True by default.

        Override as needed.
        """
        return True

    def create_parents(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create any parents.
        """
        assert isinstance(cmd, command.Command)
        success = True

        # Determine which parents need to be created
        to_create_parent_result_tuples: list[
            tuple[model.ParentForUpload, Model, model.UploadResult]
        ] = []
        for parent_for_upload, parent_result in self.parent_result_items(
            cmd, batch_result
        ):
            if not parent_result.is_new:
                # Parent already exists, should not be created
                continue
            if parent_result.status != UploadStatus.PENDING:
                # Only PENDING parents can be created
                continue
            # Parent to be created
            parent: Model = parent_for_upload.get_parent()  # type: ignore[assignment]
            to_create_parent_result_tuples.append(
                (parent_for_upload, parent, parent_result)
            )
        if not to_create_parent_result_tuples:
            # Nothing to do
            return success
        to_create_parent_result_pairs = [
            (x[1], x[2]) for x in to_create_parent_result_tuples
        ]

        # Create parents
        success &= self.create_objects(
            uow,
            cmd.user.id if cmd.user else None,
            self.parent_class,
            to_create_parent_result_pairs,
        )

        # Update parent IDs in ParentForUpload instances and in child parent ID fields
        for parent_for_upload, parent, _ in to_create_parent_result_tuples:
            parent_for_upload.id = getattr(parent, self.parent_id_field_name)
            # Update child parent ID fields for this parent
            for (
                child_model_class,
                children_field_name,
            ) in self.children_field_name_map.items():
                child_parent_id_field_name = self.child_model_parent_id_field_name_map[
                    child_model_class
                ]
                children_for_upload: list[Model] | None = getattr(
                    parent_for_upload, children_field_name
                )
                for child_for_upload in children_for_upload or []:
                    setattr(
                        child_for_upload,
                        child_parent_id_field_name,
                        parent_for_upload.id,
                    )

        return success

    def update_parents(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Update any parents.
        """
        assert isinstance(cmd, command.Command)
        success = True

        # Determine which parents need to be updated
        to_update_parent_result_tuples: list[
            tuple[model.ParentForUpload, Model, model.UploadResult]
        ] = []
        for parent_for_upload, parent_result in self.parent_result_items(
            cmd, batch_result
        ):
            if parent_result.is_new:
                # Parent did not exist, should not be updated
                continue
            if parent_result.status != UploadStatus.PENDING:
                # Only PENDING parents can be updated
                continue
            parent = parent_for_upload.get_parent()
            if parent is None:
                # No parent provided, cannot be updated
                continue
            # Parent to be updated
            to_update_parent_result_tuples.append(
                (parent_for_upload, parent, parent_result)
            )
        if not to_update_parent_result_tuples:
            # Nothing to do
            return success
        to_update_parent_result_pairs = [
            (x[1], x[2]) for x in to_update_parent_result_tuples
        ]

        # Update parents
        success &= self.update_objects(
            uow,
            cmd.user.id if cmd.user else None,
            self.parent_class,
            to_update_parent_result_pairs,
        )

        # Update parent IDs in ParentForUpload instances (should already be set, but just in case)
        for parent_for_upload, parent, parent_result in to_update_parent_result_tuples:
            parent_for_upload.id = getattr(parent, self.parent_id_field_name)

        return success

    def create_children(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create any child models. Assumes that the parent models already exist.
        """
        assert isinstance(cmd, command.Command)
        user_id = cmd.user.id if cmd.user else None
        success = True

        # Create each child model for each parent
        parents_for_upload = self.get_parents_for_upload(cmd)
        parent_results = self.get_parent_results(batch_result)
        for (
            child_model_class,
            children_field_name,
        ) in self.children_field_name_map.items():
            child_parent_id_field_name = self.child_model_parent_id_field_name_map[
                child_model_class
            ]
            child_model_for_upload_class = self.child_for_upload_class_map[
                child_model_class
            ]
            parent_child_tuples = self._get_parents_and_children(
                parents_for_upload, parent_results, children_field_name
            )

            # Determine which objects need to be created
            to_create_child_result_pairs: list[tuple[Model, UploadResult]] = []
            for (
                parent_for_upload,
                _,
                child_for_upload,
                child_result,
            ) in parent_child_tuples:
                if not child_result.is_new:
                    # Child already exists, should not be created
                    continue
                if child_result.status != UploadStatus.PENDING:
                    # Only PENDING children can be created
                    continue
                parent_id = parent_for_upload.id
                # Set parent ID link in child, which is known for certain at this point
                setattr(child_for_upload, child_parent_id_field_name, parent_id)
                # Collect for creation
                if isinstance(child_for_upload, child_model_for_upload_class):
                    actual_child = child_model_class(**child_for_upload.model_dump())
                    to_create_child_result_pairs.append((actual_child, child_result))
                else:
                    to_create_child_result_pairs.append(
                        (child_for_upload, child_result)
                    )

            if to_create_child_result_pairs:
                success &= self.create_objects(
                    uow,
                    user_id,
                    child_model_class,
                    to_create_child_result_pairs,
                )

        return success

    def update_children(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Update any child models. Assumes that the parent models already exist.
        """
        assert isinstance(cmd, command.Command)
        user_id = cmd.user.id if cmd.user else None
        success = True

        # Update each child model for each parent
        parents_for_upload = self.get_parents_for_upload(cmd)
        parent_results = self.get_parent_results(batch_result)
        for (
            child_model_class,
            children_field_name,
        ) in self.children_field_name_map.items():
            child_model_for_upload_class = self.child_for_upload_class_map[
                child_model_class
            ]
            child_parent_id_field_name = self.child_model_parent_id_field_name_map[
                child_model_class
            ]
            # Determine which children need to be updated
            to_update_child_result_pairs = []
            parent_child_tuples = self._get_parents_and_children(
                parents_for_upload, parent_results, children_field_name
            )
            for (
                parent_for_upload,
                _,
                child_for_upload,
                child_result,
            ) in parent_child_tuples:
                if child_result.is_new:
                    # Child did not exist, should not be updated
                    continue
                if child_result.status != UploadStatus.PENDING:
                    # Only PENDING children can be updated
                    continue
                parent_id = parent_for_upload.id
                # Set parent ID link in child, which is known for certain at this point
                setattr(child_for_upload, child_parent_id_field_name, parent_id)
                # Collect for update
                if isinstance(child_for_upload, child_model_for_upload_class):
                    actual_child = child_model_class(**child_for_upload.model_dump())
                    to_update_child_result_pairs.append((actual_child, child_result))
                else:
                    to_update_child_result_pairs.append(
                        (child_for_upload, child_result)
                    )
            if not to_update_child_result_pairs:
                continue

            success &= self.update_objects(
                uow,
                user_id,
                child_model_class,
                to_update_child_result_pairs,
            )
        return success

    def verify_external_identifiers(
        self,
        user: model.User | None,
        model_class: type[Model],
        identifier_type: enum.IdentifierType,
        obj_result_pairs: list[
            tuple[
                model.ExternalIdentifiersMixin,
                model.UploadResultWithExternalIdentifiers,
            ]
        ],
    ) -> bool:
        success = True
        # Retrieve and verify external IDs
        external_identifier_tuples: list[tuple[UUID, str]] = (
            list(  # type: ignore[assignment]
                {
                    (y.identifier_issuer_id, y.external_id)
                    for x, _ in obj_result_pairs
                    for y in x.external_identifiers or []
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
                    user=user,
                    operation=CrudOperation.READ_ALL,
                    query_filter=CompositeFilter(
                        operator=LogicalOperator.AND,
                        filters=[
                            EqualsNumberFilter(
                                key="identifier_type",
                                value=identifier_type.value,
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

        # Verify external IDs for each object
        obj_id_field_name = model_class.ENTITY.get_id_field_name()
        for obj_for_upload, obj_result in obj_result_pairs:
            obj_id = getattr(obj_for_upload, obj_id_field_name)
            for external_identifier, external_identifier_result in zip(
                obj_for_upload.external_identifiers or [],
                obj_result.external_identifiers or [],
            ):
                if external_identifier_result.status != UploadStatus.PENDING:
                    # Not pending (likely skipped or failed), no need to check existence
                    continue
                assert external_identifier.identifier_issuer_id is not None
                key: tuple[UUID, str] = (
                    external_identifier.identifier_issuer_id,
                    external_identifier.external_id,
                )
                if key not in existing_external_identifier_map:
                    # External ID does not exist
                    external_identifier_result.is_new = True
                    continue
                # External ID already exists
                existing_external_identifier = existing_external_identifier_map[key]
                external_identifier_result.id = existing_external_identifier.id
                external_identifier_result.status = UploadStatus.SKIPPED
                # Cross-validate with object ID if given
                if self.is_null(obj_id):
                    # Object does not exist yet, fill in object ID
                    setattr(
                        obj_for_upload,
                        obj_id_field_name,
                        existing_external_identifier.internal_id,
                    )
                    obj_result.id = existing_external_identifier.internal_id
                else:
                    # Object already exists
                    obj_result.id = obj_id
                    if existing_external_identifier.internal_id != obj_id:
                        success = False
                        external_identifier_result.add_error(
                            "f8a9b0c1",
                            f"External identifier {external_identifier.external_id} refers to internal_id={existing_external_identifier.internal_id}, which does not match {model_class.NAME}.{obj_id_field_name}={obj_id}",
                        )

        return success

    def create_external_identifiers(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        assert isinstance(cmd, command.Command)
        success = True

        # Gather the external identifiers to create for the parent objects
        parents_for_upload = self.get_parents_for_upload(cmd)
        parent_results = self.get_parent_results(batch_result)
        to_create_external_identifier_result_pairs: list[
            tuple[model.ExternalIdentifier, model.UploadResult]
        ] = []
        for parent_for_upload, parent_result in zip(parents_for_upload, parent_results):
            parent_id = parent_for_upload.id
            for external_identifier_for_upload, external_identifier_result in zip(
                parent_for_upload.external_identifiers or [],
                parent_result.external_identifiers or [],
            ):
                if external_identifier_result.status != UploadStatus.PENDING:
                    # Not pending (likely skipped or failed), no need to create
                    continue
                if not external_identifier_result.is_new:
                    # Not new: unexpected since updating existing external identifiers is not supported
                    external_identifier_result.add_error(
                        "f8a9b0c2",
                        f"External identifier {external_identifier_for_upload.external_id} already exists and cannot be updated",
                    )
                    continue
                external_identifier = model.ExternalIdentifier(
                    id=None,
                    internal_id=parent_id,  # type: ignore[arg-type]
                    identifier_type=self.parent_identifier_type,
                    identifier_issuer_id=external_identifier_for_upload.identifier_issuer_id,  # type: ignore[arg-type]
                    external_id=external_identifier_for_upload.external_id,
                )
                to_create_external_identifier_result_pairs.append(
                    (external_identifier, external_identifier_result)
                )

        # Gather the external identifiers to create for the child objects
        for (
            child_model_class,
            children_field_name,
        ) in self.children_field_name_map.items():
            child_model_for_upload_class = self.child_for_upload_class_map[
                child_model_class
            ]
            has_external_identifiers = issubclass(
                child_model_for_upload_class, ExternalIdentifiersMixin
            )
            if not has_external_identifiers:
                continue
            child_parent_id_field_name = self.child_model_parent_id_field_name_map[
                child_model_class
            ]

            for (
                parent_for_upload,
                parent_result,
                child_for_upload,
                child_result,
            ) in self._get_parents_and_children(
                parents_for_upload, parent_results, children_field_name
            ):
                child_id = getattr(child_for_upload, child_parent_id_field_name)
                assert isinstance(child_for_upload, model.ExternalIdentifiersMixin)
                assert isinstance(
                    child_result, model.UploadResultWithExternalIdentifiers
                )
                if self.is_null(child_id):
                    # Child ID not available: unexpected since children should have been created already
                    child_result.add_error(
                        "f8a9b0c3",
                        f"Child {child_model_class.NAME} does not have a valid ID and cannot be assigned external identifiers",
                    )
                    continue
                for external_identifier, external_identifier_result in zip(
                    child_for_upload.external_identifiers or [],
                    child_result.external_identifiers or [],
                ):
                    if external_identifier_result.status != UploadStatus.PENDING:
                        # Not pending (likely skipped or failed), no need to create
                        continue
                    to_create_external_identifier_result_pairs.append(
                        (
                            model.ExternalIdentifier(
                                internal_id=child_id,
                                identifier_type=child_model_for_upload_class.EXTERNAL_IDENTIFIER_TYPE,
                                **external_identifier.model_dump(),
                            ),
                            external_identifier_result,
                        )
                    )
        if not to_create_external_identifier_result_pairs:
            return success

        # Create external identifiers
        success &= self.create_objects(
            uow,
            cmd.user.id if cmd.user else None,
            model.ExternalIdentifier,
            to_create_external_identifier_result_pairs,
            is_same_service=False,
            user=cmd.user,
        )

        return success

    def create_refdata(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create any new reference data entries as needed. Performs no action and
        returns True.

        Override as needed.
        """
        return True

    def verify_link_id(
        self,
        parent_result_pairs: list[tuple[Model, model.UploadResult]],
        uow: fastapp.BaseUnitOfWork,
        user: model.User | None,
        child_field_name: str,
        link_id_field_name: str,
        link_code_field_name: str,
        linked_model_class: type[Model],
        linked_model_id_field_name: str = "id",
        linked_model_code_field_name: str = "code",
        is_same_service: bool = True,
        is_frozen: bool = False,
    ) -> bool:
        """Set and verify entities provided by ID and/or code, filling in IDs and verifying consistency"""
        success = True
        if not parent_result_pairs:
            return success

        # Initialize some data
        id_code_tuples = list(
            {
                (getattr(y, link_id_field_name), getattr(y, link_code_field_name))
                for x, _ in parent_result_pairs
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
                user.id,
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
            link_objs: list[Model] = self.service.app.handle(
                crud_command_class(
                    user=user,
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
        for parent, parent_result in parent_result_pairs:
            children_for_upload: list[Model] = getattr(parent, child_field_name) or []
            child_results: list[UploadResult] = (
                getattr(parent_result, child_field_name) or []
            )
            for i, (child_for_upload, child_result) in enumerate(
                zip(children_for_upload, child_results)
            ):
                # Get link ID and code
                link_id = getattr(child_for_upload, link_id_field_name)
                is_null_id = link_id == NULL_ID
                if is_null_id:
                    link_id = None
                link_code = getattr(child_for_upload, link_code_field_name)
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
                                new_child = child_for_upload.model_copy(
                                    update={link_id_field_name: code_id_map[link_code]}
                                )
                                children_for_upload[i] = new_child
                            else:
                                # Not a frozen class, can set attribute directly
                                setattr(
                                    child_for_upload,
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

    def objects_exist(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        model_class: type[Model],
        obj_ids: list[UUID | None],
    ) -> list[bool]:
        # Initialise output
        objs_exist = [False] * len(obj_ids)
        # Determine which indices are actually IDs
        is_id_indices = [
            i for i, x in enumerate(obj_ids) if x is not None and x != NULL_ID
        ]
        if len(is_id_indices) == 0:
            return objs_exist
        # Retrieve which of the actual IDs also exists
        is_id_obj_ids: list[UUID] = [obj_ids[i] for i in is_id_indices]
        is_id_objs_exist: list[bool] = (
            self.service.repository.crud(  # type: ignore[assignment]
                uow,
                user_id,
                model_class,
                None,
                is_id_obj_ids,
                CrudOperation.EXISTS_SOME,
            )
        )
        # Finalise output
        for i, obj_exists in zip(is_id_indices, is_id_objs_exist):
            objs_exist[i] = obj_exists
        return objs_exist

    def create_objects(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        model_class: type[Model],
        to_create_obj_result_pairs: list[tuple[Model, UploadResult]],
        is_same_service: bool = True,
        user: model.User | None = None,
    ) -> bool:
        """
        Create any new objects and update the corresponding UploadResults.
        """
        success = True
        if not to_create_obj_result_pairs:
            return success

        # Create objects, assigning and ID where necessary
        to_create_objs = [x for x, _ in to_create_obj_result_pairs]
        obj_id_field_name = model_class.ENTITY.get_id_field_name()
        for obj in to_create_objs:
            obj_id = getattr(obj, obj_id_field_name)
            if self.is_null(obj_id):
                # Assign a new ID
                obj_id = self.service.generate_id()
                setattr(obj, obj_id_field_name, obj_id)  # type: ignore[assignment]
        if is_same_service:
            created_obj_ids: list[UUID] = (
                self.service.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id,
                    model_class,
                    to_create_objs,
                    None,
                    operation=CrudOperation.CREATE_SOME,
                    return_id=True,  # Avoid returning the whole object list again
                )
            )
        else:
            crud_command_class = self.service.app.domain.get_crud_command_for_model(
                model_class
            )
            created_obj_ids = self.service.app.handle(
                crud_command_class(
                    user=user,
                    operation=CrudOperation.CREATE_SOME,
                    objs=to_create_objs,
                    props={
                        "return_id": True
                    },  # Avoid returning the whole object list again
                )
            )

        # Assign object ID and status to results
        for created_obj_id, (_, obj_result) in zip(
            created_obj_ids, to_create_obj_result_pairs
        ):
            obj_result.id = created_obj_id
            obj_result.status = UploadStatus.CREATED

        return success

    def update_objects(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        model_class: type[Model],
        to_update_obj_result_pairs: list[tuple[Model, UploadResult]],
    ) -> bool:
        """
        Update any existing objects and update the corresponding UploadResults.
        """
        success = True
        if not to_update_obj_result_pairs:
            return success

        # Collect object IDs to update
        obj_ids: list[UUID] = []
        obj_id_field_name = model_class.ENTITY.get_id_field_name()
        for obj, obj_result in to_update_obj_result_pairs:
            obj_id = getattr(obj, obj_id_field_name)
            if self.is_null(obj_id):
                success = False
                obj_result.status = UploadStatus.FAILED
                obj_result.add_error(
                    "e9c1b3d5",
                    f"Cannot update object without valid ID: {obj}",
                )
            else:
                obj_ids.append(obj_id)

        # Determine model class and stored model field properties
        stored_model_field_props = self.stored_model_field_props[model_class]

        # Retrieve existing objects
        existing_objs: list[Model] = (
            self.service.repository.crud(  # type: ignore[assignment]
                uow,
                user_id,
                model_class,
                None,
                obj_ids,
                operation=CrudOperation.READ_SOME,
            )
        )

        # Determine which objects actually need to be updated instead of having identical data
        to_update_objs: list[Model] = []
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
        _: list[UUID] = self.service.repository.crud(  # type: ignore[assignment]
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

    def _get_parents_and_children(
        self,
        parents_for_upload: list[model.ParentForUpload],
        parent_results: list[model.ParentUploadResult],
        children_field_name: str,
    ) -> list[
        tuple[model.ParentForUpload, model.ParentUploadResult, Model, UploadResult]
    ]:
        """
        Get a list of tuples of (parent_for_upload, parent_result, child_for_upload,
        child_result) for all children across all parents based on the given children
        field name.
        """
        result = []
        for parent_for_upload, parent_result in zip(parents_for_upload, parent_results):
            children_for_upload: list[Model] = (
                getattr(parent_for_upload, children_field_name) or []
            )
            child_results: list[UploadResult] = (
                getattr(parent_result, children_field_name) or []
            )
            for child_for_upload, child_result in zip(
                children_for_upload, child_results
            ):
                result.append(
                    (parent_for_upload, parent_result, child_for_upload, child_result)
                )
        return result

    def _get_obj_id_field_name(self, obj: Model) -> str:
        obj_class = obj.__class__
        if obj_class is self.parent_for_upload_class:
            return self.parent_id_field_name
        else:
            return self.child_model_parent_id_field_name_map[obj_class]

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

    @staticmethod
    def is_null(obj_id: UUID | None) -> bool:
        return obj_id is None or obj_id == NULL_ID
