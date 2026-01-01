from collections import defaultdict
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
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_number import EqualsNumberFilter
from gen_epix.filter.string_set import StringSetFilter
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService
from gen_epix.seqdb.services.seq.upload_verify_batch_refdata import (
    _verify_batch_refdata_allele_profiles,
)


def _verify_batch_sample_existence(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Check sample existence when ID is given"""
    return _verify_batch_parent_existence(
        self,
        cmd,
        retval,
        uow,
        model.Sample,
        cmd.sample_batch.samples,  # type: ignore[arg-type]
        retval.samples,  # type: ignore[arg-type]
    )


def _verify_batch_sample_external_ids(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Retrieve and verify identifier issuers in external IDs"""
    return _verify_batch_parent_external_ids(
        self,
        cmd,
        retval,
        uow,
        model.Sample,
        model.SampleForUpload,
        IdentifierType.SAMPLE,
        cmd.sample_batch.samples,  # type: ignore[arg-type]
        retval.samples,  # type: ignore[arg-type]
    )


def _verify_batch_sample_children(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Check child model existence and consistency"""
    # Generic child model verifications
    success = _verify_batch_parent_children(
        self,
        cmd,
        retval,
        uow,
        model.SampleForUpload,
        "sample_id",
        cmd.sample_batch.samples,  # type: ignore[arg-type]
        retval.samples,  # type: ignore[arg-type]
    )

    # Child model specific verifications
    success &= _verify_batch_seqs(self, cmd, retval, uow)
    success &= _verify_batch_allele_profiles(self, cmd, retval, uow)

    return success


def _verify_batch_seqs(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify seq specific rules"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Retrieve and verify assembly protocols provided by ID and/or code
    success &= _verify_batch_set_and_verify_id_by_code(
        self,
        cmd,
        uow,
        model.SampleForUpload,
        samples,  # type: ignore[arg-type]
        sample_results,  # type: ignore[arg-type]
        model.Seq,
        "assembly_protocol_id",
        "assembly_protocol_code",
        model.AssemblyProtocol,
    )

    # Get dict[(sample_id, seq_hash), [(read_set_id, read_set2_id, assembly_protocol_id, id)]
    sample_ids = list({sample.id for sample in samples if sample.id is not None})
    if not sample_ids:
        # No samples with ID, nothing to verify
        return success
    result_iter = self.repository.read_fields(
        uow,
        user_id,
        model.Seq,
        [
            "sample_id",
            "seq_hash",
            "read_set_id",
            "read_set2_id",
            "assembly_protocol_id",
            "id",
        ],
        filter=UuidSetFilter(key="sample_id", members=frozenset(sample_ids)),
    )
    key_map: defaultdict[tuple[UUID, UUID], list[tuple]] = defaultdict(list)
    for x in result_iter:
        key_map[(x[0], x[1])].append((x[2], x[3], x[4], x[5]))

    # Verify each seq
    has_existing_seqs = False
    for sample, sample_result in zip(samples, sample_results):
        if sample.id is None or sample.id == NULL_ID:
            # Sample does not exist
            continue
        for seq, seq_result in zip(sample.seqs or [], sample_result.seqs or []):
            existing_seq_data = key_map.get((sample.id, seq.seq_hash))
            if existing_seq_data is None:
                # No existing seq with this hash for this sample
                continue
            # Compare existing seqs with this hash
            for (
                read_set_id,
                read_set2_id,
                assembly_protocol_id,
                seq_id,
            ) in existing_seq_data:
                if seq.assembly_protocol_id != assembly_protocol_id:
                    # Different assembly protocol, cannot give rise to an issue
                    continue
                if seq.read_set_id == read_set_id and seq.read_set2_id == read_set2_id:
                    # Same read sets -> skip since the seq is identical and there are
                    # no immutable parts
                    seq.id = seq_id
                    seq_result.add_warning(
                        "a2b3c4d5",
                        f"Seq with same hash ({seq.seq_hash}), read sets and assembly protocol already exists",
                    )
                    seq_result.status = UploadStatus.SKIPPED
                    has_existing_seqs = True
                    break
                if seq.read_set_id is None and seq.read_set2_id is None:
                    # New seq with same hash but unknown read sets -> error since
                    # cannot verify if indeed it was derived from the same reads sets
                    success = False
                    seq_result.add_error(
                        "f1e2d3c4",
                        f"Seq with same hash ({seq.seq_hash}) and assembly protocol already exists with ID {seq_id}, but new seq has no read sets no read sets are provided for the new seq to compare",
                    )
                    break

    # Finalise checks
    if has_existing_seqs and cmd.on_exists == OnExistsUploadAction.ERROR:
        success = False
        retval.add_error(
            "b4c5d6e7",
            "One or more seqs already exist and on_exists=ERROR",
        )
    return success


def _verify_batch_allele_profiles(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify allele profile specific rules"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Get sample IDs
    sample_ids = list({sample.id for sample in samples if sample.id is not None})
    if not sample_ids:
        # No existing samples, nothing to verify
        return success

    # Retrieve and verify locus detection protocols provided by ID and/or code
    success &= _verify_batch_set_and_verify_id_by_code(
        self,
        cmd,
        uow,
        model.SampleForUpload,
        samples,  # type: ignore[arg-type]
        sample_results,  # type: ignore[arg-type]
        model.AlleleProfile,
        "locus_detection_protocol_id",
        "locus_detection_protocol_code",
        model.LocusDetectionProtocol,
    )

    # Retrieve and verify locus sets provided by ID and/or code
    success &= _verify_batch_set_and_verify_id_by_code(
        self,
        cmd,
        uow,
        model.SampleForUpload,
        samples,  # type: ignore[arg-type]
        sample_results,  # type: ignore[arg-type]
        model.AlleleProfile,
        "locus_set_id",
        "locus_set_code",
        model.LocusSet,
    )

    # Retrieve and verify locus code maps provided by ID and/or code
    success &= _verify_batch_set_and_verify_id_by_code(
        self,
        cmd,
        uow,
        model.SampleForUpload,
        samples,  # type: ignore[arg-type]
        sample_results,  # type: ignore[arg-type]
        model.AlleleProfile,
        "locus_code_map_id",
        "locus_code_map_code",
        model.LocusCodeMap,
    )

    # Get dict[(sample_id, allele_profile_hash), [(locus_detection_protocol_id, locus_set_id, seq_id,id)]
    result_iter = self.repository.read_fields(
        uow,
        user_id,
        model.AlleleProfile,
        [
            "sample_id",
            "allele_profile_hash",
            "locus_detection_protocol_id",
            "locus_set_id",
            "seq_id",
            "id",
        ],
        filter=UuidSetFilter(key="sample_id", members=frozenset(sample_ids)),
    )
    key_map: defaultdict[tuple[UUID, UUID], list[tuple]] = defaultdict(list)
    for x in result_iter:
        key_map[(x[0], x[1])].append((x[2], x[3], x[4], x[5]))

    # Verify each allele profile
    has_existing_allele_profiles = False
    for sample, sample_result in zip(samples, sample_results):
        if sample.id is None or sample.id == NULL_ID:
            # Sample does not exist
            continue
        for allele_profile, allele_profile_result in zip(
            sample.allele_profiles or [], sample_result.allele_profiles or []
        ):
            existing_allele_profile_data = key_map.get(
                (sample.id, allele_profile.allele_profile_hash)
            )
            if existing_allele_profile_data is None:
                # No existing allele profile with this hash for this sample
                continue
            # Compare existing allele profiles with this hash
            for (
                locus_detection_protocol_id,
                locus_set_id,
                seq_id,
                allele_profile_id,
            ) in existing_allele_profile_data:
                if (
                    allele_profile.locus_detection_protocol_id
                    != locus_detection_protocol_id
                ):
                    # Different locus detection protocol, cannot give rise to an issue
                    continue
                if allele_profile.locus_set_id != locus_set_id:
                    # Different locus set, cannot give rise to an issue
                    continue
                if allele_profile.seq_id == seq_id:
                    # Same seq -> skip since the allele profile is identical and there are
                    # no immutable parts
                    allele_profile.id = allele_profile_id
                    allele_profile_result.add_warning(
                        "c7d8e9f0",
                        f"Allele profile with same hash ({allele_profile.allele_profile_hash}), seq and assembly protocol already exists",
                    )
                    allele_profile_result.status = UploadStatus.SKIPPED
                    has_existing_allele_profiles = True
                    break
                if allele_profile.seq_id is None:
                    # New allele profile with same hash but unknown read sets -> error since
                    # cannot verify if indeed it was derived from the same seq
                    success = False
                    allele_profile_result.add_error(
                        "a8f3e7b2",
                        f"Allele profile with same hash ({allele_profile.allele_profile_hash}) and assembly protocol already exists with ID {allele_profile_id}, but new allele profile has no seq ID provided for the new allele profile to compare",
                    )
                    break

    # Finalise checks
    if has_existing_allele_profiles and cmd.on_exists == OnExistsUploadAction.ERROR:
        success = False
        retval.add_error(
            "d8a3b7f4",
            "One or more allele profiles already exist and on_exists=ERROR",
        )
    return success


def _verify_batch_sample_refdata(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """
    Verify and complete reference data.
    """
    success = True
    # Read sets: nothing to do
    # Sequences: nothing to do
    # Allele profiles
    success &= _verify_batch_refdata_allele_profiles(self, cmd, retval, uow)

    return success


def _verify_batch_parent_existence(
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


def _verify_batch_parent_external_ids(
    self: BaseService,
    cmd: command.Command,
    retval: BaseBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
    parent_model_class: type[model.Model],
    parent_for_upload_model_class: type[model.Model],
    parent_identifier_type: IdentifierType,
    parents: list[model.Model],
    parent_results: list[model.UploadResult],
) -> bool:
    """Retrieve and verify identifier issuers in external IDs"""
    user_id = cmd.user.id if cmd.user else None
    success = True

    # Retrieve and verify identifier issuers in external IDs provided by ID
    success &= _verify_batch_set_and_verify_id_by_code(
        self,
        cmd,
        uow,
        parent_for_upload_model_class,
        parents,
        parent_results,
        "external_ids",
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
            for y in x.external_ids or []  # type: ignore[attr-defined]
        }
    )
    if external_identifier_tuples:
        # Get all external identifiers matching the provided external
        # identifiers and identifier issuers, but not their combination
        # This leaves the possibility that the same external identifier for a
        # different identifier issuer is retrieved: this is addressed after
        # retrieval, allowing a straightforward filter here
        existing_external_ids: list[model.ExternalIdentifier] = (
            self.crud(  # type:ignore[assignment]
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
        existing_external_id_map: dict[tuple[UUID, str], model.ExternalIdentifier] = {
            (x.identifier_issuer_id, x.external_id): x for x in existing_external_ids
        }
        has_existing_parents = False
        for parent, parent_result in zip(parents, parent_results):
            for external_id, external_id_result in zip(
                parent.external_ids or [], parent_result.external_ids or []  # type: ignore[attr-defined]
            ):
                if external_id_result.status != UploadStatus.PENDING:
                    # Not pending (likely skipped or failed), no need to check existence
                    continue
                key: tuple[UUID, str] = (
                    external_id.identifier_issuer_id,
                    external_id.external_id,
                )
                if key in existing_external_id_map:
                    has_existing_parents = True
                    existing_external_id = existing_external_id_map[key]
                    # Cross-validate with parent ID if given and not new ID
                    if (
                        parent.id is not None
                        and parent.id != NULL_ID
                        and not parent.is_new_id  # type: ignore[attr-defined]
                    ):
                        # Parent already exists
                        if existing_external_id.internal_id != parent.id:
                            success = False
                            external_id_result.add_error(
                                "f8a9b0c1",
                                f"External identifier {external_id.external_id} refers to {parent_model_class.NAME}.id={existing_external_id.internal_id}, which does not match uploaded {parent_model_class.NAME}.id={parent.id}",
                            )
                        # External ID already exists, nothing to upload
                        external_id_result.id = existing_external_id.id
                        external_id_result.status = UploadStatus.SKIPPED
                    else:
                        # Parent does not exist yet, fill in parent ID
                        parent.id = existing_external_id.internal_id
        if has_existing_parents and cmd.on_exists == OnExistsUploadAction.ERROR:  # type: ignore[attr-defined]
            success = False
            retval.add_error(
                "a1c7d9f3",
                f"Some {parent_model_class.NAME} already exist and on_exists=ERROR",
            )

    return success


def _verify_batch_parent_children(
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
    model_class_map: dict[str, type[model.Model]] = {
        y: rev_map[x]
        for x, y in parent_for_upload_model_class.CHILD_MODEL_FIELD_NAME_MAP.items()  # type: ignore[attr-defined]
    }

    # Verify each child model for each parent
    has_existing_data = False
    for field_name, model_class in model_class_map.items():
        # Collect all IDs for this child model and determine existence
        child_id_is_new_id_pairs: list[tuple[UUID, bool]] = list(
            {
                (y.id, y.is_new_id)
                for x in parents
                for y in getattr(x, field_name) or []
                if y.id is not None
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
        for i, (parent, parent_result) in enumerate(zip(parents, parent_results)):
            children: list[model.Model] = getattr(parent, field_name) or []
            child_results: list[UploadResult] = getattr(parent_result, field_name) or []
            for child, child_result in zip(children, child_results):
                parent_id = getattr(child, parent_link_id_field_name, None)
                if parent_id == NULL_ID:
                    parent_id = None
                child_id = child.id
                if child_id == NULL_ID:
                    child_id = None
                # Child does not exist yet, assign parent ID if existing
                if child_id is None:
                    setattr(child, parent_link_id_field_name, parent.id)
                    continue
                # Child ID given as new ID and already exists
                if child_id in already_existing_new_child_ids:
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
                if child_id not in existing_child_ids:
                    success = False
                    child_result.add_error(
                        "d4f5e6a7",
                        f"ID does not exist",
                    )
                    continue  # Skip to next child since this one doesn't exist
                # Child ID given but not as new ID, and exists
                has_existing_data = True
                existing_parent_id = existing_child_parent_id_map[child_id]
                if parent.id is None or parent.id == NULL_ID:
                    # Parent ID not given: fill in from parent
                    parent.id = existing_parent_id
                else:
                    # Parent ID given
                    if parent.id != existing_parent_id:
                        # Parent ID different from actually existing one
                        success = False
                        child_result.add_error(
                            "e5f6a7b8",
                            f"{parent_link_id_field_name}={existing_parent_id} does not match {parent_for_upload_model_class.NAME}.id={parent.id}",
                        )
    if has_existing_data and cmd.on_exists == OnExistsUploadAction.ERROR:  # type: ignore[attr-defined]
        success = False
        retval.add_error(
            "c6e7f8a0",
            f"Some child instances already exist and on_exists=ERROR",
        )
    return success


def _verify_batch_set_and_verify_id_by_code(
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
    if isinstance(child_field_name_or_class, str):
        child_field_name = child_field_name_or_class
    else:
        for_upload_child_model_class = parent_for_upload_model_class.FOR_UPLOAD_CHILD_MODEL_CLASS_MAP[  # type: ignore[attr-defined]
            child_field_name_or_class
        ]
        child_field_name = parent_for_upload_model_class.CHILD_MODEL_FIELD_NAME_MAP[  # type: ignore[attr-defined]
            for_upload_child_model_class
        ]
    # Retrieve and verify links from child model provided by ID and/or code
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
    if ids or codes:
        # Retrieve existing ID-code pairs
        if is_same_service:
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
                if link_id == NULL_ID:
                    link_id = None
                link_code = getattr(child, link_code_field_name)
                # Link ID provided but does not exist
                if link_id and link_id not in id_code_map:
                    success = False
                    child_result.add_error(
                        "b9e4f7c2",
                        f"{linked_model_id_field_name}={link_id} does not exist",
                    )
                # Link code provided
                if link_code:
                    if link_code not in code_id_map:
                        # Link code does not exist
                        success = False
                        child_result.add_error(
                            "c7a9b2e4",
                            f"{linked_model_code_field_name}={link_code} does not exist",
                        )
                    elif link_id and code_id_map[link_code] != link_id:
                        # Link code exists but does not match provided ID
                        success = False
                        child_result.add_error(
                            "a4d7b9c3",
                            f"{linked_model_code_field_name}={link_code} with {linked_model_id_field_name}={code_id_map[link_code]} does not match provided {linked_model_id_field_name}={link_id}",
                        )
                    elif not link_id:
                        # Link code exists and link ID is not provided: fill in link ID
                        if is_frozen:
                            # Need to create a new instance since the class is frozen
                            new_child = child.model_copy(
                                update={link_id_field_name: code_id_map[link_code]}
                            )
                            children[i] = new_child
                        else:
                            # Not a frozen class, can set attribute directly
                            setattr(child, link_id_field_name, code_id_map[link_code])
    return success
