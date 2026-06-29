from collections import defaultdict
from typing import Generator, cast
from uuid import UUID

from gen_epix import fastapp
from gen_epix.commondb.domain import command, exc, model
from gen_epix.commondb.domain.enum import EtlStatus, UploadAction
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import BaseIdentifier
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload,
    BaseBatchUploadResult,
    IdentifiersMixin,
    UploadResult,
    UploadResultWithIdentifiers,
)
from gen_epix.fastapp import BaseService, BaseUnitOfWork, CrudOperation, Model
from gen_epix.fastapp.exc import DuplicateIdsError
from gen_epix.filter import (
    CompositeFilter,
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
        self.parent_identifier_class: type[BaseIdentifier] = self.parent_for_upload_class.IDENTIFIER_CLASS  # type: ignore[assignment]
        self.parent_class = self.parent_for_upload_class.PARENT_CLASS
        self.parent_result_class = self.batch_upload_result_class.PARENT_RESULT_CLASS
        self.parent_id_field_name = self.parent_class.ENTITY.get_id_field_name()  # type: ignore[union-attr]
        self.child_for_upload_class_map = (
            self.parent_for_upload_class.CHILD_FOR_UPLOAD_CLASS_MAP
        )
        self.child_children_field_name_map = (
            self.parent_for_upload_class.CHILDREN_FIELD_NAME_MAP
        )
        self.child_parent_id_field_name_map = (
            self.parent_for_upload_class.CHILD_PARENT_ID_FIELD_NAME_MAP
        )
        self.child_id_field_name_map = {
            x: x.ENTITY.get_id_field_name() for x in self.child_children_field_name_map  # type: ignore[union-attr]
        }
        self.child_identifier_class_map: dict[type[Model], type[BaseIdentifier]] = {  # type: ignore[assignment]
            x: y.IDENTIFIER_CLASS
            for x, y in self.child_for_upload_class_map.items()
            if issubclass(y, IdentifiersMixin)
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
            raise exc.InvalidArgumentsError("d47e1515", "cmd.id must be set")

        #  Check user rights
        self.verify_user_rights(cmd)

        # Initialize the upload result
        batch_result = self.init_batch_upload_result(cmd)
        batch_result.add_info(
            code="4f9046fe",
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
                # Stop here if only verification was requested; mark all
                # still-PENDING individual results as SKIPPED (nothing was stored)
                batch_result.add_info(
                    code="c849b0e2",
                    message="Verification only requested, upload will not proceed",
                )
                for parent_result in batch_result.get_parent_results():
                    parent_result.convert_status(EtlStatus.PENDING, EtlStatus.SKIPPED)

                batch_result.add_info(
                    code="ff9e4a2f",
                    message="Upload ended",
                )
                batch_result.resolve_status()
                return batch_result

            if not success:
                # Do not proceed with upsert due to errors
                batch_result.add_error(
                    code="02095f22",
                    message="Verification found errors, upload will not proceed",
                )
                return batch_result

            # Upsert the batch data
            batch_result.add_info(
                code="add3eb54",
                message="Upsert started",
            )
            success = self.upsert_batch(cmd, batch_result, uow)
            batch_result.add_info(
                code="f8b12027",
                message="Upsert ended",
            )
            if not success:
                # Rollback due to errors, but do not raise an exception since those will be reported in batch_result
                batch_result.add_error(
                    code="05358e8a",
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
        batch_result.resolve_status()

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
            parent_result = self.parent_result_class(status=EtlStatus.PENDING)
            # Initialise Identifier results
            identifiers = parent_for_upload.identifiers
            identifier_results = (
                None
                if identifiers is None
                else [
                    UploadResultWithIdentifiers(status=EtlStatus.PENDING)
                    for _ in identifiers
                ]
            )
            parent_result.identifiers = identifier_results
            # Initialize child results
            for (
                child_model_class,
                children_field_name,
            ) in self.child_children_field_name_map.items():
                child_id_field_name = self.child_id_field_name_map[child_model_class]
                children_for_upload: list[Model] | None = getattr(
                    parent_for_upload, children_field_name
                )
                # Special case: no children
                if not children_for_upload:
                    setattr(
                        parent_result,
                        children_field_name,
                        None if children_for_upload is None else [],
                    )
                    continue
                # Determine if child model has identifiers
                has_identifiers = child_model_class in self.child_identifier_class_map
                child_results: list[UploadResult] = []
                if has_identifiers:
                    # Child class has identifiers, for which (sub)upload results also need to be initialized
                    for child_for_upload in children_for_upload:
                        assert isinstance(child_for_upload, IdentifiersMixin)
                        identifiers = child_for_upload.identifiers
                        identifier_results = (
                            None
                            if identifiers is None
                            else [
                                UploadResult(status=EtlStatus.PENDING)
                                for _ in identifiers
                            ]
                        )
                        child_results.append(
                            UploadResultWithIdentifiers(
                                status=EtlStatus.PENDING,
                                identifiers=identifier_results,
                            )
                        )
                else:
                    # Child class does not have identifiers, only initialize corresponding upload result for the child
                    child_results = [
                        UploadResult(
                            id=getattr(x, child_id_field_name),
                            status=EtlStatus.PENDING,
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
            status=EtlStatus.PENDING,
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
        Verify parents, children, identifiers and reference data.
        """
        success = True
        # Verify Identifiers first to fill in any missing parent IDs
        success &= self.verify_parents_identifiers(cmd, batch_result, uow)
        # Verify Identifiers for child models to fill in any missing child IDs
        success &= self.verify_children_identifiers(cmd, batch_result, uow)
        # Verify children before parents. Child parent links may resolve missing
        # parent IDs, so parent existence/newness must be evaluated afterwards.
        success &= self.verify_children(cmd, batch_result, uow)
        success &= self.verify_parents(cmd, batch_result, uow)
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
        Create or update parents, children, identifiers and reference data.
        """
        success = True
        # Create refdata before parents and children to ensure all references exist
        success &= self.create_refdata(cmd, batch_result, uow)
        # Create and update parents before children to ensure parents already exist
        success &= self.create_parents(cmd, batch_result, uow)
        success &= self.update_parents(cmd, batch_result, uow)
        success &= self.create_children(cmd, batch_result, uow)
        success &= self.update_children(cmd, batch_result, uow)
        # Create parent and child Identifiers last since all parents and children with
        # identifiers first have to exist before a link can be created to them
        success &= self.create_parent_identifiers(cmd, batch_result, uow)
        success &= self.create_child_identifiers(cmd, batch_result, uow)
        return success

    def verify_parents_identifiers(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """Retrieve and verify parent Identifiers"""
        assert isinstance(cmd, command.Command)
        success = True

        # Retrieve and verify identifier issuers provided by ID or code
        parent_result_pairs = list(self.parent_result_items(cmd, batch_result))
        success &= self.verify_link_id(
            parent_result_pairs,  # type: ignore[arg-type]
            uow,
            cmd.user,
            "identifiers",
            "identifier_issuer_id",
            "identifier_issuer_code",
            model.IdentifierIssuer,
            is_same_service=False,
            is_frozen=True,
        )

        success &= self.verify_identifiers(
            cmd.user,
            self.parent_for_upload_class,
            self.parent_identifier_class,
            parent_result_pairs,  # type: ignore[arg-type]
        )

        # Fill in parent IDs based on Identifiers where possible
        for parent_for_upload, _ in parent_result_pairs:
            parent = parent_for_upload.get_parent()
            if parent is not None:
                setattr(parent, self.parent_id_field_name, parent_for_upload.id)

        return success

    def verify_children_identifiers(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: fastapp.BaseUnitOfWork,
    ) -> bool:
        """
        Verify Identifiers in any of the child objects. This includes
        verifying that any provided identifier IDs exist and are accessible
        by the user, and filling in any missing IDs based on provided codes.
        """
        assert isinstance(cmd, command.Command)
        success = True
        # Get list of (child_for_upload, child_result) tuples for all children across all parents
        parent_result_pairs = list(self.parent_result_items(cmd, batch_result))
        for (
            child_model_class,
            children_field_name,
        ) in self.child_children_field_name_map.items():
            child_identifier_class = self.child_identifier_class_map.get(
                child_model_class
            )
            if not child_identifier_class:
                # This child model does not have identifiers, skip
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
                "identifiers",
                "identifier_issuer_id",
                "identifier_issuer_code",
                model.IdentifierIssuer,
                is_same_service=False,
                is_frozen=True,
            )
            # Verify existing Identifiers for all children
            success &= self.verify_identifiers(
                cmd.user,
                child_model_class,
                child_identifier_class,
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
            if parent_result.status == EtlStatus.FAILED:
                continue
            # TODO: parents resolved in verify_children (child-inferred parent ID)
            # also land here and get existence-checked + on_exists/on_new applied a
            # second time. Detected cases: SKIPPED (guard above misses it), and
            # PENDING parents where verify_children set parent_result.id or
            # parent_result.is_new. Consequence is redundant DB calls and duplicate
            # info log messages; final state is identical so no correctness bug.
            parent_id = parent_for_upload.id
            parent = parent_for_upload.get_parent()
            if parent is None:
                # Parent not given: skip writing the parent record (children may still
                # be processed if the parent ID is resolved via identifier lookup).
                parent_result.status = EtlStatus.SKIPPED
                parent_result.add_info(
                    "a740e288",
                    f"{self.parent_class.NAME} model not provided; parent record will not be written",
                )
                continue
            if self.is_null(parent_id):
                # Parent given but no ID: always a new entity.
                parent_result.is_new = True
                if cmd.on_new == UploadAction.ERROR:
                    success = False
                    parent_result.add_error(
                        "eacd67d4",
                        f"{self.parent_class.NAME} has no ID and on_new={cmd.on_new.value}.",
                    )
                elif cmd.on_new == UploadAction.SKIP:
                    parent_result.status = EtlStatus.SKIPPED
                    parent_result.add_info(
                        "f457324b",
                        f"{self.parent_class.NAME} has no ID and on_new={cmd.on_new.value}.",
                    )
                continue
            parent_ids[i] = parent_id
            has_parent_ids = True

        if not has_parent_ids:
            # No parent IDs given, nothing left to check
            return success

        # Detect duplicate parent IDs. Mark every occurrence of a duplicated UUID as
        # FAILED (including the first — a duplicate UUID is always ambiguous) and
        # remove them from the existence-check list so the repository never sees it.
        parent_id_to_indices: dict[UUID, list[int]] = {}
        for i, parent_id in enumerate(parent_ids):
            if parent_id is None:
                continue
            parent_id_to_indices.setdefault(parent_id, []).append(i)
        parent_result_list = list(self.parent_result_items(cmd, batch_result))
        for parent_id, indices in parent_id_to_indices.items():
            if len(indices) <= 1:
                continue
            for i in indices:
                _, parent_result = parent_result_list[i]
                parent_result.add_error(
                    "a1b2c3d4",
                    f"{self.parent_class.NAME} id={parent_id} appears "
                    f"{len(indices)} times in the batch.",
                )
                parent_ids[i] = None  # exclude from objects_exist()

        # Some parent IDs are given, check existence
        parents_exist = self.objects_exist(uow, user_id, self.parent_class, parent_ids)
        for parent_exists, (parent_for_upload, parent_result) in zip(
            parents_exist, self.parent_result_items(cmd, batch_result)
        ):
            if parent_result.status == EtlStatus.FAILED:
                continue  # already marked by duplicate detection above
            if parent_exists:
                parent_result.id = parent_for_upload.id
                if cmd.on_exists == UploadAction.ERROR:
                    success = False
                    parent_result.add_error(
                        "1e5e22b3",
                        f"{self.parent_class.NAME} already exists and on_exists={cmd.on_exists.value}.",
                    )
                elif cmd.on_exists == UploadAction.SKIP:
                    # Existing parent and on_exists=SKIP: do not update
                    parent_result.status = EtlStatus.SKIPPED
                    parent_result.add_info(
                        "a7c3f42e",
                        f"{self.parent_class.NAME} already exists and on_exists={cmd.on_exists.value}.",
                    )
            else:
                parent_result.is_new = True
                if cmd.on_new == UploadAction.ERROR:
                    success = False
                    parent_result.add_error(
                        "c544eba4",
                        f"{self.parent_class.NAME} does not exist and on_new={cmd.on_new.value}.",
                    )
                elif cmd.on_new == UploadAction.SKIP:
                    # New parent and on_new=SKIP: do not create
                    parent_result.status = EtlStatus.SKIPPED
                    parent_result.add_info(
                        "cd349a43",
                        f"{self.parent_class.NAME} does not exist and on_new={cmd.on_new.value}.",
                    )
                elif cmd.on_new == UploadAction.CREATE:
                    # New parent and on_new=CREATE: will be created, nothing left to check for this parent
                    if self.is_null(parent_for_upload.id):
                        parent_result.add_info(
                            "8f289ecb",
                            f"{self.parent_class.NAME} will be created with generated ID",
                        )
                    else:
                        parent_result.add_info(
                            "46b0bce4",
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
        ) in self.child_children_field_name_map.items():
            child_id_field_name = self.child_id_field_name_map[child_model_class]
            child_parent_id_field_name = self.child_parent_id_field_name_map[
                child_model_class
            ]
            parent_child_tuples = self._get_parents_and_children(
                parents_for_upload, parent_results, children_field_name
            )

            # Get existing children
            child_ids = [
                getattr(x, child_id_field_name) for _, _, x, _ in parent_child_tuples
            ]

            # Detect duplicate child IDs (within a parent or across parents).
            # For every duplicated child UUID, mark all parent results that contain
            # it as FAILED and remove those child slots from the existence-check list.
            child_id_to_entries: defaultdict[
                UUID,
                list[tuple[int, model.ParentForUpload, model.ParentUploadResult]],
            ] = defaultdict(list)
            for idx, (parent_for_upload, parent_result, _, _) in enumerate(
                parent_child_tuples
            ):
                child_id = child_ids[idx]
                if self.is_null(child_id):
                    continue
                child_id_to_entries[child_id].append(
                    (idx, parent_for_upload, parent_result)
                )
            for child_id, entries in child_id_to_entries.items():
                if len(entries) <= 1:
                    continue
                seen_parent_results: set[int] = set()
                parent_ids_str = ", ".join(
                    str(e[1].id) for e in entries if e[1].id is not None
                )
                for idx, parent_for_upload, parent_result in entries:
                    child_ids[idx] = None  # exclude from objects_exist()
                    if id(parent_result) not in seen_parent_results:
                        seen_parent_results.add(id(parent_result))
                        parent_result.add_error(
                            "e5f6a7b8",
                            f"{child_model_class.NAME} id={child_id} appears in multiple "
                            f"entries in the batch (parents: {parent_ids_str}).",
                        )

            # Single read_fields replaces the old EXISTS_SOME + read_fields pair.
            # Presence in the result means the child exists; absence means new.
            # Duplicate-nulled entries (None) are excluded from the query and
            # correctly map to children_exist=False via the `in` check below.
            actual_child_ids = frozenset(x for x in child_ids if not self.is_null(x))
            child_parent_id_map: dict[UUID, UUID] = {}
            if actual_child_ids:
                result_iter = self.service.repository.read_fields(
                    uow,
                    user_id,
                    child_model_class,
                    [child_id_field_name, child_parent_id_field_name],
                    filter=UuidSetFilter(
                        key=child_id_field_name,
                        members=actual_child_ids,
                    ),
                )
                child_parent_id_map = {x[0]: x[1] for x in result_iter}
            children_exist = [x in child_parent_id_map for x in child_ids]

            # Process all children (both with and without IDs)
            for (
                parent_for_upload,
                parent_result,
                child_for_upload,
                child_result,
            ), child_exists in zip(parent_child_tuples, children_exist):
                if parent_result.status == EtlStatus.FAILED:
                    continue  # parent already marked FAILED by duplicate detection above
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
                                    "cfc3da21",
                                    f"{child_model_class.NAME}.id={child_id} refers to {child_parent_id_field_name}={existing_parent_id}, which does not match existing {self.parent_for_upload_class.NAME}.{self.parent_id_field_name}={parent_id}",
                                )
                    else:
                        # Child parent ID not given: fill in from parent
                        setattr(child_for_upload, child_parent_id_field_name, parent_id)
                else:
                    # Parent ID not given
                    if has_child_parent_id:
                        # Parent ID not given: infer from child and re-apply
                        # on_exists/on_new semantics for the resolved parent ID.
                        parent_for_upload.id = child_parent_id
                        parent = parent_for_upload.get_parent()
                        if parent is not None:
                            setattr(parent, self.parent_id_field_name, child_parent_id)
                        parent_exists = self.objects_exist(
                            uow,
                            user_id,
                            self.parent_class,
                            [child_parent_id],
                        )[0]
                        if parent_exists:
                            parent_result.id = child_parent_id
                            parent_result.is_new = False
                            if cmd.on_exists == UploadAction.ERROR:
                                success = False
                                parent_result.add_error(
                                    "f2a13b7c",
                                    f"{self.parent_class.NAME} already exists and on_exists={cmd.on_exists.value}.",
                                )
                            elif cmd.on_exists == UploadAction.SKIP:
                                parent_result.status = EtlStatus.SKIPPED
                                parent_result.add_info(
                                    "9f43d602",
                                    f"{self.parent_class.NAME} already exists and on_exists={cmd.on_exists.value}.",
                                )
                        else:
                            parent_result.is_new = True
                            if cmd.on_new == UploadAction.ERROR:
                                success = False
                                parent_result.add_error(
                                    "1ca29f8e",
                                    f"{self.parent_class.NAME} does not exist and on_new={cmd.on_new.value}.",
                                )
                            elif cmd.on_new == UploadAction.SKIP:
                                parent_result.status = EtlStatus.SKIPPED
                                parent_result.add_info(
                                    "6e8ab14d",
                                    f"{self.parent_class.NAME} does not exist and on_new={cmd.on_new.value}.",
                                )
                            elif cmd.on_new == UploadAction.CREATE:
                                parent_result.add_info(
                                    "3b9d87f4",
                                    f"{self.parent_class.NAME} will be created with provided ID",
                                )
                    else:
                        # Neither parent ID nor child parent ID given
                        pass
                # Child ID given
                # Apply on_exists/on_new based on existence determined from storage,
                # not just on whether a child ID value is present in the payload.
                if child_exists:
                    # Child already exists
                    if cmd.on_exists == UploadAction.ERROR:
                        success = False
                        child_result.add_error(
                            "c351c931",
                            f"{child_for_upload.__class__.NAME} already exists and on_exists={cmd.on_exists.value}",
                        )
                    elif cmd.on_exists == UploadAction.SKIP:
                        # Existing child and on_exists=SKIP: do not update
                        child_result.status = EtlStatus.SKIPPED
                        child_result.add_info(
                            "7a3f2c81",
                            f"{child_for_upload.__class__.NAME} already exists and on_exists={cmd.on_exists.value}",
                        )
                else:
                    # Child does not exist yet
                    if cmd.on_new == UploadAction.ERROR:
                        success = False
                        child_result.add_error(
                            "2824fa39",
                            f"{child_for_upload.__class__.NAME} does not exist and on_new={cmd.on_new.value}",
                        )
                    elif cmd.on_new == UploadAction.SKIP:
                        # New child and on_new=SKIP: do not create
                        child_result.status = EtlStatus.SKIPPED
                        child_result.add_info(
                            "cfd622df",
                            f"{child_for_upload.__class__.NAME} does not exist and on_new={cmd.on_new.value}",
                        )
                    elif cmd.on_new == UploadAction.CREATE:
                        # New child and on_new=CREATE: will be created
                        if self.is_null(child_id):
                            child_result.add_info(
                                "85401e0e",
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
            if parent_result.status != EtlStatus.PENDING:
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
            ) in self.child_children_field_name_map.items():
                child_parent_id_field_name = self.child_parent_id_field_name_map[
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
            tuple[model.ParentForUpload, Model, model.ParentUploadResult]
        ] = []
        for parent_for_upload, parent_result in self.parent_result_items(
            cmd, batch_result
        ):
            if parent_result.is_new:
                # Parent did not exist, should not be updated
                continue
            if parent_result.status != EtlStatus.PENDING:
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
        ) in self.child_children_field_name_map.items():
            child_parent_id_field_name = self.child_parent_id_field_name_map[
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
            to_create_child_for_uploads: list[Model] = []
            for (
                parent_for_upload,
                parent_result,
                child_for_upload,
                child_result,
            ) in parent_child_tuples:
                if not child_result.is_new:
                    # Child already exists, should not be created
                    continue
                if child_result.status != EtlStatus.PENDING:
                    # Only PENDING children can be created
                    continue
                parent_id = parent_for_upload.id
                if self.is_null(parent_id):
                    child_result.add_error(
                        "f701df83",
                        f"Child cannot be created: parent has no resolved ID "
                        f"(parent status={parent_result.status.value})",
                    )
                    continue
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
                to_create_child_for_uploads.append(child_for_upload)

            if to_create_child_result_pairs:
                success &= self.create_objects(
                    uow,
                    user_id,
                    child_model_class,
                    to_create_child_result_pairs,
                )
                # write back assigned IDs to original for-upload objects
                child_id_field_name = self.child_id_field_name_map[child_model_class]
                for (created_obj, _), child_for_upload in zip(
                    to_create_child_result_pairs, to_create_child_for_uploads
                ):
                    setattr(
                        child_for_upload,
                        child_id_field_name,
                        getattr(created_obj, child_id_field_name),
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
        ) in self.child_children_field_name_map.items():
            child_model_for_upload_class = self.child_for_upload_class_map[
                child_model_class
            ]
            child_parent_id_field_name = self.child_parent_id_field_name_map[
                child_model_class
            ]
            # Determine which children need to be updated
            to_update_child_result_pairs = []
            parent_child_tuples = self._get_parents_and_children(
                parents_for_upload, parent_results, children_field_name
            )
            for (
                parent_for_upload,
                parent_result,
                child_for_upload,
                child_result,
            ) in parent_child_tuples:
                if child_result.is_new:
                    # Child did not exist, should not be updated
                    continue
                if child_result.status != EtlStatus.PENDING:
                    # Only PENDING children can be updated
                    continue
                parent_id = parent_for_upload.id
                if self.is_null(parent_id):
                    child_result.add_error(
                        "1417de99",
                        f"Child cannot be updated: parent has no resolved ID "
                        f"(parent status={parent_result.status.value})",
                    )
                    continue
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

    def verify_identifiers(
        self,
        user: model.User | None,
        model_class: type[Model],
        identifier_model_class: type[BaseIdentifier],
        obj_result_pairs: list[
            tuple[
                model.IdentifiersMixin,
                model.UploadResultWithIdentifiers,
            ]
        ],
    ) -> bool:
        """
        Verify that any provided Identifiers exist and are consistent with provided
        object IDs, and fill in any missing object IDs based on provided Identifiers.
        """
        success = True
        # Retrieve and verify Identifiers
        identifier_tuples: list[tuple[UUID, str]] = list(
            {
                (cast(UUID, y.identifier_issuer_id), y.external_id)
                for x, _ in obj_result_pairs
                for y in x.identifiers or []
            }
        )
        if not identifier_tuples:
            return success

        # Get all Identifiers matching the provided Identifiers and identifier issuers, but not their combination
        # This leaves the possibility that the same Identifier for a different identifier issuer is retrieved: this is addressed after retrieval, allowing a straightforward filter here
        command_class = self.service.app.domain.get_crud_command_for_model(
            identifier_model_class
        )
        existing_identifiers: list[model.BaseIdentifier] = self.service.app.handle(
            command_class(
                user=user,
                operation=CrudOperation.READ_ALL,
                query_filter=CompositeFilter(
                    operator=LogicalOperator.AND,
                    filters=[
                        UuidSetFilter(
                            key="identifier_issuer_id",
                            members=frozenset({x[0] for x in identifier_tuples}),
                        ),
                        StringSetFilter(
                            key="external_id",
                            members=frozenset({x[1] for x in identifier_tuples}),
                        ),
                    ],
                ),
            )
        )
        existing_identifier_map: dict[tuple[UUID, str], model.BaseIdentifier] = {
            (x.identifier_issuer_id, x.external_id): x for x in existing_identifiers
        }

        # Verify Identifiers for each object
        obj_id_field_name = model_class.ENTITY.get_id_field_name()
        for obj_for_upload, obj_result in obj_result_pairs:
            for identifier_for_upload, identifier_result in zip(
                obj_for_upload.identifiers or [],
                obj_result.identifiers or [],
            ):
                obj_id = getattr(obj_for_upload, obj_id_field_name)
                if identifier_result.status != EtlStatus.PENDING:
                    # Not pending (likely skipped or failed), no need to check existence
                    continue
                assert identifier_for_upload.identifier_issuer_id is not None
                key: tuple[UUID, str] = (
                    identifier_for_upload.identifier_issuer_id,
                    identifier_for_upload.external_id,
                )
                if key not in existing_identifier_map:
                    # Identifier does not exist
                    identifier_result.is_new = True
                    continue
                # Identifier already exists
                existing_identifier = existing_identifier_map[key]
                identifier_result.id = existing_identifier.id
                identifier_result.status = EtlStatus.SKIPPED
                # Cross-validate with object ID if given
                if self.is_null(obj_id):
                    # Object does not exist yet, fill in object ID
                    setattr(
                        obj_for_upload,
                        obj_id_field_name,
                        existing_identifier.internal_id,
                    )
                    obj_result.id = existing_identifier.internal_id
                else:
                    # Object already exists
                    obj_result.id = obj_id
                    if existing_identifier.internal_id != obj_id:
                        success = False
                        identifier_result.add_error(
                            "0561ecd7",
                            f"{model_class.NAME} Identifier ({identifier_for_upload.identifier_issuer_id}, {identifier_for_upload.external_id}) refers to internal_id={existing_identifier.internal_id}, which does not match {obj_id_field_name}={obj_id}",
                        )

        return success

    def create_parent_identifiers(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create any new Identifiers for parent objects. Assumes that all parent objects
        already exist and have IDs, and that any provided Identifiers have already
        been verified.
        """
        assert isinstance(cmd, command.Command)
        parents_for_upload = self.get_parents_for_upload(cmd)
        parent_results = self.get_parent_results(batch_result)
        identifier_tuples: list[
            tuple[
                UUID,
                list[model.IdentifierForUpload] | None,
                list[model.UploadResult] | None,
            ]
        ] = [
            (
                cast(UUID, parent_for_upload.id),
                parent_for_upload.identifiers,
                parent_result.identifiers,
            )
            for parent_for_upload, parent_result in zip(
                parents_for_upload, parent_results
            )
        ]
        return self.create_identifiers(
            uow,
            cmd.user,
            self.parent_identifier_class,
            identifier_tuples,
        )

    def create_child_identifiers(
        self,
        cmd: command.UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create any new Identifiers for child objects. Assumes that all child objects
        already exist and have IDs, and that any provided Identifiers have already
        been verified.
        """
        assert isinstance(cmd, command.Command)
        success = True
        parents_for_upload = self.get_parents_for_upload(cmd)
        parent_results = self.get_parent_results(batch_result)

        for (
            child_model_class,
            children_field_name,
        ) in self.child_children_field_name_map.items():
            child_identifier_class = self.child_identifier_class_map.get(
                child_model_class
            )
            if not child_identifier_class:
                # This child model does not have identifiers, skip
                continue
            identifier_tuples: list[
                tuple[
                    UUID,
                    list[model.IdentifierForUpload] | None,
                    list[model.UploadResult] | None,
                ]
            ] = []
            for _, _, child_for_upload, child_result in self._get_parents_and_children(
                parents_for_upload, parent_results, children_field_name
            ):
                assert isinstance(child_for_upload, model.IdentifiersMixin)
                assert isinstance(child_result, model.UploadResultWithIdentifiers)
                child_id = getattr(
                    child_for_upload,
                    self.child_id_field_name_map[child_model_class],
                )
                if self.is_null(child_id):
                    # TODO: investigate this case
                    # raise AssertionError(
                    #     f"Parent ID should not be null for child to be created, but got null for parent_for_upload={parent_for_upload}"
                    # )
                    # Child was skipped (e.g. parent model was null); skip identifiers
                    continue
                identifier_tuples.append(
                    (child_id, child_for_upload.identifiers, child_result.identifiers)
                )
            success &= self.create_identifiers(
                uow,
                cmd.user,
                child_identifier_class,
                identifier_tuples,
            )

        return success

    def create_identifiers(
        self,
        uow: BaseUnitOfWork,
        user: model.User | None,
        identifier_class: type[model.BaseIdentifier],
        identifier_tuples: list[
            tuple[
                UUID,
                list[model.IdentifierForUpload] | None,
                list[model.UploadResult] | None,
            ]
        ],
    ) -> bool:
        """
        Create new Identifiers for objects that already exist and have IDs. Assumes
        that any provided Identifiers have already been verified.
        """
        success = True
        to_create_identifier_result_pairs: list[
            tuple[model.BaseIdentifier, model.UploadResult]
        ] = []
        for (
            internal_id,
            identifiers_for_upload,
            identifier_results,
        ) in identifier_tuples:
            if self.is_null(internal_id):
                # Parent was skipped or failed and was never assigned a real ID;
                # no identifiers can be created for it.
                continue
            for identifier_for_upload, identifier_result in zip(
                identifiers_for_upload or [],
                identifier_results or [],
            ):
                if identifier_result.status != EtlStatus.PENDING:
                    # Not pending (likely skipped or failed), no need to create
                    continue
                if not identifier_result.is_new:
                    # Not new: unexpected since updating existing Identifiers is not supported
                    identifier_result.add_error(
                        "d3ac4368",
                        f"{identifier_class.NAME} ({identifier_for_upload.identifier_issuer_id}, {identifier_for_upload.external_id}) already exists and cannot be updated",
                    )
                    continue
                assert identifier_for_upload.identifier_issuer_id is not None
                # Create Identifier object and add to list
                identifier = identifier_class(
                    id=None,
                    internal_id=internal_id,
                    identifier_issuer_id=identifier_for_upload.identifier_issuer_id,
                    external_id=identifier_for_upload.external_id,
                )
                to_create_identifier_result_pairs.append(
                    (identifier, identifier_result)
                )
        if not to_create_identifier_result_pairs:
            return success

        # Create Identifiers
        success &= self.create_objects(
            uow,
            user.id if user else None,
            identifier_class,
            to_create_identifier_result_pairs,  # type: ignore[arg-type]
            is_same_service=False,
            user=user,
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
        ids = {x[0] for x in id_code_tuples if not self.is_null(x[0])}
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
                user.id if user else None,
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
        link_msg_part = (
            f"link to {linked_model_class.NAME}.{linked_model_id_field_name}"
        )
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
                                "1e496cee",
                                f"{child_for_upload.__class__.NAME}.{link_id_field_name}=NULL_ID {link_msg_part} could not be resolved",
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
                                "ff4ff6db",
                                f"{child_for_upload.__class__.NAME}.{link_code_field_name}={link_code} link to {linked_model_class.NAME}.{linked_model_code_field_name} does not exist",
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
                            "dec840ca",
                            f"{child_for_upload.__class__.NAME}.{link_id_field_name}={link_id} link to {linked_model_class.NAME}.{linked_model_id_field_name} does not exist",
                        )
                    elif link_code is None:
                        # Link ID exists and code not given: nothing to do since code is only meant to look up ID
                        pass
                    elif link_code not in code_id_map:
                        # Link code does not exist
                        success = False
                        child_result.add_error(
                            "95558de7",
                            f"{child_for_upload.__class__.NAME}.{link_code_field_name}={link_code} link to {linked_model_class.NAME}.{linked_model_code_field_name} does not exist",
                        )
                    elif link_code != id_code_map[link_id]:
                        # Link ID exists but code does not match provided code
                        success = False
                        child_result.add_error(
                            "79de83f2",
                            f"{child_for_upload.__class__.NAME}.{linked_model_code_field_name}={link_code} with {linked_model_class.NAME}.{linked_model_id_field_name}={code_id_map[link_code]} does not match provided {child_for_upload.__class__.NAME}.{link_id_field_name}={link_id}",
                        )
                    else:
                        # Link ID and code both exist and match: nothing to do
                        pass
        return success

    def retrieve_parent_id_by_intra_parent_linked_child_id(
        self,
        uow: BaseUnitOfWork,
        cmd: command.UploadBatchCommandMixin,
        from_child_class: type[Model],
        from_child_link_id_field_name: str,
        to_child_class: type[Model],
    ) -> dict[UUID, UUID]:
        """
        Retrieve a dict[to_child_id, parent_id] containing all existing (to_child_id,
        parent_id) pairs for children referred to by the from_child_link_id_field_name
        field on from_child_class instances in the upload, where parent_id is the ID of
        the parent of the child with ID to_child_id
        """
        # Get all to_child_ids referred to by from_child_link_id_field_name fields on from_child_class instances in the upload
        to_child_ids: list[UUID] = []
        for parent_for_upload in self.get_parents_for_upload(cmd):
            children_for_upload: list[Model] = (
                getattr(
                    parent_for_upload,
                    self.child_children_field_name_map[from_child_class],
                )
                or []
            )
            for child_for_upload in children_for_upload:
                child_link_id = getattr(child_for_upload, from_child_link_id_field_name)
                if not self.is_null(child_link_id):
                    to_child_ids.append(cast(UUID, child_link_id))

        # Retrieve parent IDs for these child IDs
        existing_parent_id_by_child_id: dict[UUID, UUID] = {}
        if to_child_ids:
            to_child_id_field_name = self.child_id_field_name_map[to_child_class]
            to_child_parent_id_field_name = self.child_parent_id_field_name_map[
                to_child_class
            ]
            user: model.User | None = getattr(cmd, "user")
            result_iter = self.service.repository.read_fields(
                uow,
                user.id if user else None,
                to_child_class,
                [
                    to_child_id_field_name,
                    to_child_parent_id_field_name,
                ],
                filter=UuidSetFilter(
                    key=to_child_id_field_name, members=frozenset(to_child_ids)
                ),
            )
            for x in result_iter:
                existing_parent_id_by_child_id[x[0]] = x[1]
        return existing_parent_id_by_child_id

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
        is_id_indices = [i for i, x in enumerate(obj_ids) if not self.is_null(x)]
        if len(is_id_indices) == 0:
            return objs_exist
        # Retrieve which of the actual IDs also exists
        is_id_obj_ids: list[UUID] = [obj_ids[i] for i in is_id_indices]
        is_id_objs_exist: list[bool] = self.service.repository.crud(
            uow,
            user_id,
            model_class,
            CrudOperation.EXISTS_SOME,
            obj_ids=is_id_obj_ids,
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
        try:
            if is_same_service:
                created_obj_ids: list[UUID] = self.service.repository.crud(
                    uow,
                    user_id,
                    model_class,
                    CrudOperation.CREATE_SOME,
                    objs=to_create_objs,
                    return_id=True,  # Avoid returning the whole object list again
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
                        return_id=True,  # Avoid returning the whole object list again
                    )
                )
        except DuplicateIdsError as exc_:
            # TODO [LSP-3357] check how it is possible that these errors occur here
            duplicate_ids = set(exc_.ids) if exc_.ids else set()
            obj_id_field_name_local = model_class.ENTITY.get_id_field_name()
            for obj, obj_result in to_create_obj_result_pairs:
                if getattr(obj, obj_id_field_name_local) in duplicate_ids:
                    obj_result.add_error(
                        "c9d0e1f2",
                        f"{model_class.NAME} id={getattr(obj, obj_id_field_name_local)} "
                        "is a duplicate and could not be created.",
                    )
            return False

        # Assign object ID and status to results
        for created_obj_id, (_, obj_result) in zip(
            created_obj_ids, to_create_obj_result_pairs
        ):
            obj_result.id = created_obj_id
            obj_result.status = EtlStatus.CREATED

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
        Per-object errors (missing ID, immutable field) are logged to the individual
        UploadResult and that object is skipped; they do not abort the remaining batch.
        """
        success = True
        if not to_update_obj_result_pairs:
            return success

        obj_id_field_name = model_class.ENTITY.get_id_field_name()
        stored_model_field_props = self.stored_model_field_props[model_class]

        # Separate pairs with valid IDs from those without, to keep zip alignment correct
        valid_pairs: list[tuple[Model, UploadResult]] = []
        obj_ids: list[UUID] = []
        for obj, obj_result in to_update_obj_result_pairs:
            obj_id = getattr(obj, obj_id_field_name)
            if self.is_null(obj_id):
                obj_result.add_error(
                    "8b7824f4",
                    f"Cannot update object without valid ID: {obj}",
                )
            else:
                valid_pairs.append((obj, obj_result))
                obj_ids.append(obj_id)

        if not obj_ids:
            return success

        # Retrieve existing objects (aligned with valid_pairs / obj_ids)
        existing_objs: list[Model] = self.service.repository.crud(
            uow,
            user_id,
            model_class,
            CrudOperation.READ_SOME,
            obj_ids=obj_ids,
        )

        # Determine which objects actually need to be updated instead of having identical data
        to_update_objs: list[Model] = []
        to_update_obj_results: list[model.UploadResult] = []
        for (obj, obj_result), existing_obj in zip(valid_pairs, existing_objs):
            # Only check props for updates, other fields are not updatable
            is_updated = False
            for field_name, field_props in stored_model_field_props.items():
                if field_name == obj_id_field_name:
                    continue  # ID field is the lookup key; never part of updates
                existing_value = getattr(existing_obj, field_name)
                new_value = getattr(obj, field_name)
                if not field_props.is_mutable_value(existing_value):
                    # Immutable field: only an error if the value is actually changing.
                    # Re-uploading the same value (e.g. a full record with one extra
                    # field added) is fine and requires no action for this field.
                    # None or NULL_ID means "not specified" — treat as a no-op for
                    # immutable fields so that partial-update payloads don't fail.
                    if not self.is_null(new_value) and new_value != existing_value:
                        obj_result.add_error(
                            "f5e09001",
                            f"Field {field_name} with existing value {existing_value} may not be updated to {new_value}.",
                        )
                        break
                    continue
                # Mutable field: apply update if value differs
                if existing_value is None:
                    # Existing value is None: set new value if not None
                    if new_value:
                        is_updated = True
                        setattr(existing_obj, field_name, new_value)
                elif field_props.is_sub_field_dict:
                    # Field content is a dict: update keys individually
                    if existing_value != new_value:
                        is_updated |= BatchUploader.update_sub_field_dict(
                            existing_value, new_value
                        )
                else:
                    # Field content is a single value: compare directly
                    if new_value != existing_value:
                        is_updated = True
                        setattr(existing_obj, field_name, new_value)
            if obj_result.status == EtlStatus.FAILED:
                # Per-object error logged above; skip without aborting the batch
                continue
            # Determine whether to update or skip (identical content)
            if not is_updated:
                obj_result.status = EtlStatus.SKIPPED
                obj_result.add_info("64eef8a5", "Content is identical")
            else:
                # Persist the merged existing object because mutable sub-dict fields
                # are updated in place on existing_obj.
                to_update_objs.append(existing_obj)
                to_update_obj_results.append(obj_result)

        # Update the objects whose data are different
        if not to_update_objs:
            return success
        _: list[UUID] = self.service.repository.crud(
            uow,
            user_id,
            model_class,
            operation=CrudOperation.UPDATE_SOME,
            objs=to_update_objs,
            return_id=True,  # Avoid returning the whole object list again
        )

        # Assign status to results
        for obj_result in to_update_obj_results:
            obj_result.status = EtlStatus.UPDATED

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
        if obj_class in self.child_id_field_name_map:
            return self.child_id_field_name_map[obj_class]
        for (
            child_model_class,
            child_for_upload_class,
        ) in self.child_for_upload_class_map.items():
            if obj_class is child_for_upload_class:
                return self.child_id_field_name_map[child_model_class]
        raise KeyError(f"Could not determine ID field for {obj_class.__name__}")

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
