from typing import Callable
from uuid import UUID

from gen_epix import fastapp
from gen_epix.commondb.domain.enum import (
    IdentifierType,
    OnExistsUploadAction,
    UploadStatus,
)
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import BaseBatchUploadResult, UploadResult
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_number import EqualsNumberFilter
from gen_epix.filter.string_set import StringSetFilter
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, model


def upload_batch(
    self: BaseService,
    cmd: command.Command,
    verify_user_rights_fn: Callable[[BaseService, command.Command], None],
    init_retval_fn: Callable[[command.Command], BaseBatchUploadResult],
    verify_batch_fn: Callable[
        [BaseService, command.Command, BaseBatchUploadResult, BaseUnitOfWork], bool
    ],
    upsert_batch_fn: Callable[
        [BaseService, command.Command, BaseBatchUploadResult, BaseUnitOfWork], bool
    ],
) -> BaseBatchUploadResult:
    """
    See command.UploadSamplesCommand for details.
    """
    #  Check user rights
    verify_user_rights_fn(self, cmd)

    # Initialize the upload result
    retval = init_retval_fn(cmd)
    retval.add_info(
        code="f1e2d3c4",
        message="Upload started",
    )

    with self.repository.uow() as uow:
        # Verify batch
        retval.add_info(
            code="8b4c2f91",
            message="Verification started",
        )
        success = verify_batch_fn(self, cmd, retval, uow)
        retval.add_info(
            code="a3f7e9d2",
            message="Verification ended",
        )
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
        success = upsert_batch_fn(self, cmd, retval, uow)
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
                code="b2c3d4e5",
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


def verify_external_identifiers(
    self: BaseService,
    cmd: command.Command,
    retval: BaseBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
    parent_model_class: type[model.Model],
    parent_for_upload_model_class: type[model.Model],
    parent_identifier_type: IdentifierType,
    parents: list[model.Model],
    parent_results: list[model.UploadResult],
    external_identifiers_field_name: str = "external_identifiers",
) -> bool:
    """Retrieve and verify identifier issuers in external IDs"""
    success = True

    # Retrieve and verify identifier issuers in external IDs provided by ID
    success &= verify_link_id(
        self,
        cmd,
        uow,
        parent_for_upload_model_class,
        parents,
        parent_results,
        external_identifiers_field_name,
        "identifier_issuer_id",
        "identifier_issuer_code",
        model.IdentifierIssuer,
        is_same_service=False,
        is_frozen=True,
    )

    # Retrieve and verify external IDs
    external_identifier_tuples = list(
        {
            (y.identifier_issuer_id, y.external_id)
            for x in parents
            for y in x.external_identifiers or []  # type: ignore[attr-defined]
        }
    )
    if not external_identifier_tuples:
        return success

    # Get all external identifiers matching the provided external
    # identifiers and identifier issuers, but not their combination
    # This leaves the possibility that the same external identifier for a
    # different identifier issuer is retrieved: this is addressed after
    # retrieval, allowing a straightforward filter here
    existing_external_identifiers: list[model.ExternalIdentifier] = (
        self.app.handle(  # type:ignore[assignment]
            command.ExternalIdentifierCrudCommand(
                user=cmd.user,
                operation=CrudOperation.READ_ALL,
                query_filter=CompositeFilter(
                    operator=LogicalOperator.AND,
                    filters=[
                        EqualsNumberFilter(
                            key="identifier_type",
                            value=parent_identifier_type.value,
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
    for parent, parent_result in zip(parents, parent_results):
        external_identifiers: list[model.ExternalIdentifier] = (
            getattr(parent, external_identifiers_field_name) or []  # type: ignore[attr-defined]
        )
        external_identifier_results: list[UploadResult] = (
            getattr(  # type: ignore[attr-defined]
                parent_result, external_identifiers_field_name
            )
            or []
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
                and not parent.is_new_id  # type: ignore[attr-defined]
            ):
                # Parent already exists
                if existing_external_identifier.internal_id != parent.id:
                    success = False
                    external_identifier_result.add_error(
                        "f8a9b0c1",
                        f"External identifier {external_identifier.external_id} refers to {parent_model_class.NAME}.id={existing_external_identifier.internal_id}, which does not match uploaded {parent_model_class.NAME}.id={parent.id}",
                    )
            else:
                # Parent does not exist yet, fill in parent ID
                parent.id = existing_external_identifier.internal_id
                parent_result.id = parent.id

    return success


def verify_parent_existence(
    self: BaseService,
    cmd: command.Command,
    retval: BaseBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
    parent_model_class: type[model.Model],
    parents: list[model.Model],
    parent_results: list[model.UploadResult],
) -> bool:
    """Check parent model existence when ID is given"""
    user_id = cmd.user.id if cmd.user else None
    success = True

    # Get parent IDs and check existence
    parent_id_is_new_id_pairs = list(
        {(x.id, x.is_new_id) for x in parents if x.id is not None and x.id != NULL_ID}  # type: ignore[attr-defined]
    )
    parent_ids = [x[0] for x in parent_id_is_new_id_pairs]
    new_parent_ids = {x for x, is_new in parent_id_is_new_id_pairs if is_new}
    has_existing_parents = False
    if parent_ids:
        # Some parent IDs are given, check existence
        # Check existence of given parent IDs
        parents_exist: list[bool] = self.repository.crud(  # type:ignore[assignment]
            uow,
            user_id,
            parent_model_class,
            None,
            parent_ids,
            CrudOperation.EXISTS_SOME,
        )
        existing_parent_ids = {x for x, y in zip(parent_ids, parents_exist) if y}
        already_existing_new_parent_ids = new_parent_ids.intersection(
            existing_parent_ids
        )
        for parent, parent_result in zip(parents, parent_results):
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
            if parent.is_new_id:  # type: ignore[attr-defined]
                continue
            # Parent ID given but not as new ID, and exists
            if parent_id in existing_parent_ids:
                has_existing_parents = True
                continue
            # Parent ID given but not as new ID, and does not exist
            success = False
            parent_result.add_error(
                "b2c3d4e5", f"{parent_model_class.NAME}.id={parent.id} does not exist."
            )

    if has_existing_parents and cmd.on_exists == OnExistsUploadAction.ERROR:  # type: ignore[attr-defined]
        success = False
        retval.add_error(
            "d3f5b6a1",
            f"Some {parent_model_class.NAME} already exist and on_exists=ERROR.",
        )
    return success


def verify_child_existence(
    self: BaseService,
    cmd: command.Command,
    retval: BaseBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
    parent_for_upload_model_class: type[model.Model],
    parent_link_id_field_name: str,
    parents: list[model.Model],
    parent_results: list[model.UploadResult],
) -> bool:
    """Check child model existence and consistency"""
    user_id = cmd.user.id if cmd.user else None
    success = True

    # Prepare some data
    rev_map = {
        y: x for x, y in parent_for_upload_model_class.FOR_UPLOAD_CHILD_MODEL_CLASS_MAP.items()  # type: ignore[attr-defined]
    }
    model_field_class_map: dict[str, type[model.Model]] = {
        y: rev_map[x]
        for x, y in parent_for_upload_model_class.CHILD_MODEL_FIELD_NAME_MAP.items()  # type: ignore[attr-defined]
    }

    # Verify each child model for each parent
    has_existing_data = False
    for field_name, model_class in model_field_class_map.items():
        # Collect all IDs for this child model and determine existence
        child_id_is_new_id_pairs: list[tuple[UUID, bool]] = list(
            {
                (y.id, y.is_new_id)
                for x in parents
                for y in getattr(x, field_name) or []
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
                self.repository.crud(  # type:ignore[assignment]
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
                result_iter = self.repository.read_fields(
                    uow,
                    user_id,
                    model_class,
                    ["id", parent_link_id_field_name],
                    filter=UuidSetFilter(
                        key="id", members=frozenset(existing_child_ids)
                    ),
                )
                existing_child_parent_id_map = {x[0]: x[1] for x in result_iter}
        else:
            already_existing_new_child_ids = set()

        # Process all children (both with and without IDs)
        for parent, parent_result in zip(parents, parent_results):
            children: list[model.Model] = getattr(parent, field_name) or []
            child_results: list[UploadResult] = getattr(parent_result, field_name) or []
            for child, child_result in zip(children, child_results):
                child_parent_id = getattr(child, parent_link_id_field_name, None)
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
                                f"{parent_link_id_field_name}={child_parent_id} does not match {parent_for_upload_model_class.NAME}.id={parent.id}",
                            )
                    else:
                        # Child parent ID not given: fill in from parent
                        setattr(child, parent_link_id_field_name, parent.id)
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
                has_existing_data = True

    if has_existing_data and cmd.on_exists == OnExistsUploadAction.ERROR:  # type: ignore[attr-defined]
        success = False
        retval.add_error(
            "c6e7f8a0",
            f"Some child instances already exist and on_exists=ERROR",
        )
    return success


def verify_link_id(
    self: BaseService,
    cmd: command.Command,
    uow: fastapp.BaseUnitOfWork,
    parent_for_upload_model_class: type[model.Model],
    parents: list[model.Model],
    parent_results: list[model.UploadResult],
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
    user_id = cmd.user.id if cmd.user else None
    success = True

    # Get child field name
    if isinstance(child_field_name_or_class, str):
        child_field_name = child_field_name_or_class
    else:
        for_upload_child_model_class = parent_for_upload_model_class.FOR_UPLOAD_CHILD_MODEL_CLASS_MAP[  # type: ignore[attr-defined]
            child_field_name_or_class
        ]
        child_field_name = parent_for_upload_model_class.CHILD_MODEL_FIELD_NAME_MAP[  # type: ignore[attr-defined]
            for_upload_child_model_class
        ]

    # Initialize some data
    id_code_tuples = list(
        {
            (getattr(y, link_id_field_name), getattr(y, link_code_field_name))
            for x in parents
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
        result_iter = self.repository.read_fields(
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
        crud_command_class = self.app.domain.get_crud_command_for_model(
            linked_model_class
        )
        link_objs: list[model.Model] = self.app.handle(
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
    for parent, parent_result in zip(parents, parent_results):
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
    self: BaseService,
    cmd: command.Command,
    uow: BaseUnitOfWork,
    parent_model_class: type[model.Model],
    parents: list[model.Model],
    parent_results: list[model.UploadResult],
) -> bool:
    """
    Create any parents.
    """
    user_id = cmd.user.id if cmd.user else None

    # Determine which parents need to be created
    to_create_parent_result_pairs = [
        (x, y)
        for x, y in zip(parents, parent_results)
        if (x.id is None or x.id == NULL_ID or x.is_new_id)  # type: ignore[attr-defined]
        and y.status == UploadStatus.PENDING
    ]
    if not to_create_parent_result_pairs:
        return True

    # Create samples
    create_objects(
        self,
        uow,
        user_id,
        parent_model_class,
        to_create_parent_result_pairs,  # type:ignore[arg-type]
    )

    return True


def create_external_identifiers(
    self: BaseService,
    cmd: command.Command,
    uow: BaseUnitOfWork,
    external_identifier_class: type[model.Model],
    parents: list[model.Model],
    parent_results: list[model.UploadResult],
    external_identifiers_field_name: str = "external_identifiers",
) -> bool:
    # TODO
    return True


def update_parents(
    self: BaseService,
    cmd: command.Command,
    uow: BaseUnitOfWork,
    stored_model_field_props: dict[str, model.ModelFieldProps],
    parent_model_class: type[model.Model],
    parents: list[model.Model],
    parent_results: list[model.UploadResult],
) -> bool:
    """
    Update any parents.
    """
    user_id = cmd.user.id if cmd.user else None
    success = True

    # Determine which parents need to be updated
    to_update_parent_result_pairs = [
        (x, y)
        for x, y in zip(parents, parent_results)
        if x.id is not None
        and x.id != NULL_ID
        and not x.is_new_id  # type: ignore[attr-defined]
        and y.status == UploadStatus.PENDING
    ]
    if not to_update_parent_result_pairs:
        return success

    return update_objects(
        self,
        uow,
        user_id,
        parent_model_class,
        stored_model_field_props,
        to_update_parent_result_pairs,  # type:ignore[arg-type]
    )

    return success


def create_children(
    self: BaseService,
    cmd: command.Command,
    uow: BaseUnitOfWork,
    parent_for_upload_model_class: type[model.Model],
    parent_link_id_field_name: str,
    parents: list[model.Model],
    parent_results: list[UploadResult],
) -> bool:
    """
    Create any child models. Assumes that the parent models already exist.
    """
    user_id = cmd.user.id if cmd.user else None
    success = False

    # Prepare some data
    rev_map = {
        y: x for x, y in parent_for_upload_model_class.FOR_UPLOAD_CHILD_MODEL_CLASS_MAP.items()  # type: ignore[attr-defined]
    }
    model_class_map: dict[str, type[model.Model]] = {
        y: rev_map[x]
        for x, y in parent_for_upload_model_class.CHILD_MODEL_FIELD_NAME_MAP.items()  # type: ignore[attr-defined]
    }

    # Create each child model for each parent
    for field_name, model_class in model_class_map.items():
        # Determine which objects need to be created
        to_create_child_result_pairs = []
        for parent, parent_result in zip(parents, parent_results):
            children: list[model.Model] | None = getattr(parent, field_name)
            child_results: list[UploadResult] | None = getattr(
                parent_result, field_name
            )
            for child, child_result in zip(children or [], child_results or []):
                if (
                    child.id is None or child.id == NULL_ID
                ) and child_result.status == UploadStatus.PENDING:
                    # Set parent ID link in child, which is known for certain at this point
                    setattr(child, parent_link_id_field_name, parent.id)  # type: ignore[attr-defined]
                    # Collect for creation
                    to_create_child_result_pairs.append((child, child_result))
        if not to_create_child_result_pairs:
            continue

        # Create the objects
        create_objects(
            self,
            uow,
            user_id,
            model_class,
            to_create_child_result_pairs,
        )

    success = True
    return success


def update_children(
    self: BaseService,
    cmd: command.Command,
    uow: BaseUnitOfWork,
    stored_model_field_props: dict[type[model.Model], dict[str, model.ModelFieldProps]],
    parent_for_upload_model_class: type[model.Model],
    parent_link_id_field_name: str,
    parents: list[model.Model],
    parent_results: list[UploadResult],
) -> bool:
    """
    Update any child models. Assumes that the parent models already exist.
    """
    user_id = cmd.user.id if cmd.user else None
    success = True

    # Prepare some data
    rev_map = {
        y: x for x, y in parent_for_upload_model_class.FOR_UPLOAD_CHILD_MODEL_CLASS_MAP.items()  # type: ignore[attr-defined]
    }
    model_class_map: dict[str, type[model.Model]] = {
        y: rev_map[x]
        for x, y in parent_for_upload_model_class.CHILD_MODEL_FIELD_NAME_MAP.items()  # type: ignore[attr-defined]
    }

    # Update each child model for each parent
    for field_name, model_class in model_class_map.items():
        # Determine which children need to be updated
        to_update_child_result_pairs = []
        for parent, parent_result in zip(parents, parent_results):
            children: list[model.Model] | None = getattr(parent, field_name)
            child_results: list[UploadResult] | None = getattr(
                parent_result, field_name
            )
            for child, child_result in zip(children or [], child_results or []):
                if (
                    child.id is not None
                    and child.id != NULL_ID
                    and child_result.status == UploadStatus.PENDING
                ):
                    # Set parent ID link in child, which is known for certain at this point
                    setattr(child, parent_link_id_field_name, parent.id)  # type: ignore[attr-defined]
                    # Collect for update
                    to_update_child_result_pairs.append((child, child_result))
        if not to_update_child_result_pairs:
            continue

        success &= update_objects(
            self,
            uow,
            user_id,
            model_class,
            stored_model_field_props[model_class],
            to_update_child_result_pairs,
        )
    return success


def create_objects(
    self: BaseService,
    uow: BaseUnitOfWork,
    user_id: UUID | None,
    model_class: type[model.Model],
    to_create_obj_result_pairs: list[tuple[model.Model, UploadResult]],
) -> bool:
    """
    Create any new objects and update the corresponding UploadResults.
    ️"""
    success = True
    if not to_create_obj_result_pairs:
        return success

    # Create objects, assigning and ID where necessary
    to_create_objs = [x for x, _ in to_create_obj_result_pairs]
    for obj in to_create_objs:
        if obj.id is None or obj.id == NULL_ID:
            # Assign a new ID
            obj.id = self.generate_id()  # type: ignore[assignment]
    to_create_obj_results = [x for _, x in to_create_obj_result_pairs]
    created_obj_ids: list[UUID] = self.repository.crud(  # type:ignore[assignment]
        uow,
        user_id,
        model_class,
        to_create_objs,
        None,
        operation=CrudOperation.CREATE_SOME,
        return_id=True,  # Avoid returning the whole object list again
    )

    # Assign object ID and status to results
    for created_obj_id, obj_result in zip(created_obj_ids, to_create_obj_results):
        obj_result.id = created_obj_id
        obj_result.status = UploadStatus.CREATED

    return success


def update_objects(
    self: BaseService,
    uow: BaseUnitOfWork,
    user_id: UUID | None,
    model_class: type[model.Model],
    stored_model_field_props: dict[str, model.ModelFieldProps],
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

    # Retrieve existing objects
    existing_objs: list[model.Model] = self.repository.crud(  # type:ignore[assignment]
        uow,
        user_id,
        model_class,
        None,
        obj_ids,
        operation=CrudOperation.READ_SOME,
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
            elif field_props.is_dict:
                # Field content is a dict: update keys individually
                is_updated |= update_dict_value(existing_value, new_value)
            elif field_props.is_list:
                is_updated |= update_list_value(existing_value, new_value)
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
    _: list[UUID] = self.repository.crud(  # type:ignore[assignment]
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


def update_list_value(existing_value: list, new_value: list | None) -> bool:
    """
    Update a list in place with new values and return whether any updates were made.

    An update is made if:
    - The new value is None and the existing list is not empty: clear the existing
      list.
    - The new value is a list and is different from the existing list: replace the
      existing list.
    """
    is_updated = False
    if new_value is None:
        if existing_value:
            # Existing list is not empty, clear it
            is_updated = True
            existing_value.clear()
    else:
        # Replace existing list with new list if different
        if new_value != existing_value:
            is_updated = True
            min_len = min(len(existing_value), len(new_value))
            max_len = max(len(existing_value), len(new_value))
            for i in range(min_len):
                existing_value[i] = new_value[i]
            if len(new_value) > len(existing_value):
                # New value has more items, extend the existing list
                existing_value.extend(new_value[min_len:max_len])
    return is_updated


def update_dict_value(content: dict, updates: dict | None) -> bool:
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
