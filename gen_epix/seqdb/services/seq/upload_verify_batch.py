from collections import defaultdict
from uuid import UUID

from gen_epix import fastapp
from gen_epix.commondb.domain.enum import (
    IdentifierType,
    OnExistsUploadAction,
    UploadStatus,
)
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_number import EqualsNumberFilter
from gen_epix.filter.string_set import StringSetFilter
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def _verify_batch_sample_existence(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Check sample existence when ID is given"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True
    sample_ids = list({x.id for x in samples if x.id is not None and x.id != NULL_ID})
    has_existing_samples = False
    if sample_ids:
        # Some sample IDs are given, check existence
        # Check existence of given sample IDs
        samples_exist: list[bool] = self.repository.crud(  # type:ignore[assignment]
            uow,
            user_id,
            model.Sample,
            None,
            sample_ids,
            CrudOperation.EXISTS_SOME,
        )
        existing_sample_ids = {x for x, y in zip(sample_ids, samples_exist) if y}
        for sample, sample_result in zip(samples, sample_results):
            sample_id = sample.id
            if sample_id == NULL_ID:
                sample_id = None
            if sample_id is None:
                # Sample ID not given, cannot exist
                continue
            if sample_id in existing_sample_ids:
                # Sample exists
                has_existing_samples = True
                continue
            # Sample ID given but does not exist
            # TODO: handle case where sample ID is given for a new sample to be explicitly created with this ID
            success = False
            sample_result.add_error(
                "b2c3d4e5", f"Sample with ID {sample.id} does not exist."
            )

    if has_existing_samples and cmd.on_exists == OnExistsUploadAction.ERROR:
        success = False
        retval.add_error(
            "d3f5b6a1", "One or more samples already exist and on_exists=ERROR."
        )
    return success


def _verify_batch_external_ids(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Retrieve and verify identifier issuers in external IDs"""
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Retrieve and verify identifier issuers in external IDs provided by ID
    success &= _set_and_verify_id_by_code(
        self,
        cmd,
        retval,
        uow,
        "external_ids",
        "identifier_issuer_id",
        "identifier_issuer_code",
        model.IdentifierIssuer,
        is_same_service=False,
        is_frozen=True,
    )
    # identifier_issuer_ids = list(
    #     {
    #         y.identifier_issuer_id
    #         for x in samples
    #         for y in x.external_ids or []
    #         if y.identifier_issuer_id is not None
    #     }
    # )
    # identifier_issuer_by_id_map: dict[UUID, model.IdentifierIssuer] = {}
    # identifier_issuers: list[model.IdentifierIssuer] = []
    # if identifier_issuer_ids:
    #     identifier_issuers = self.crud(  # type:ignore[assignment]
    #         command.IdentifierIssuerCrudCommand(
    #             user=cmd.user,
    #             obj_ids=list(identifier_issuer_ids),
    #             operation=CrudOperation.READ_SOME,
    #         )
    #     )
    #     identifier_issuer_by_id_map = {  # type: ignore[misc]
    #         x.id: x for x in identifier_issuers if x.id is not None
    #     }
    #     for sample, sample_result in zip(samples, sample_results):
    #         for external_id, external_id_result in zip(
    #             sample.external_ids or [], sample_result.external_ids or []
    #         ):
    #             identifier_issuer_id = external_id.identifier_issuer_id
    #             if identifier_issuer_id is None:
    #                 continue
    #             if identifier_issuer_id not in identifier_issuer_by_id_map:
    #                 success = False
    #                 external_id_result.add_error(
    #                     "c4d5e6f7",
    #                     f"Identifier issuer with ID {identifier_issuer_id} does not exist",
    #                 )

    # # Retrieve and verify identifier issuers in external IDs provided by code
    # identifier_issuer_codes = list(
    #     {
    #         y.identifier_issuer_code
    #         for x in samples
    #         for y in x.external_ids or []
    #         if y.identifier_issuer_code is not None
    #     }
    # )
    # identifier_issuer_by_code_map: dict[str, model.IdentifierIssuer] = {}
    # if identifier_issuer_codes:
    #     identifier_issuers = self.crud(  # type:ignore[assignment]
    #         command.IdentifierIssuerCrudCommand(
    #             user=cmd.user,
    #             operation=CrudOperation.READ_ALL,
    #             query_filter=StringSetFilter(
    #                 key="code", members=frozenset(identifier_issuer_codes)
    #             ),
    #         )
    #     )
    #     identifier_issuer_by_code_map = {x.code: x for x in identifier_issuers}
    #     for sample, sample_result in zip(samples, sample_results):
    #         for i, (external_id, external_id_result) in enumerate(
    #             zip(
    #                 sample.external_ids or [],
    #                 sample_result.external_ids or [],
    #             )
    #         ):
    #             identifier_issuer_code = external_id.identifier_issuer_code
    #             if identifier_issuer_code is None:
    #                 continue
    #             if identifier_issuer_code not in identifier_issuer_by_code_map:
    #                 success = False
    #                 external_id_result.add_error(
    #                     "d6e7f8a9",
    #                     f"Identifier issuer with code {identifier_issuer_code} does not exist",
    #                 )
    #                 continue
    #             identifier_issuer = identifier_issuer_by_code_map[
    #                 identifier_issuer_code
    #             ]
    #             if external_id.identifier_issuer_id is not None:
    #                 if external_id.identifier_issuer_id != identifier_issuer.id:
    #                     success = False
    #                     external_id_result.add_error(
    #                         "e7f8a9b0",
    #                         f"Identifier issuer code {identifier_issuer_code} with ID {identifier_issuer.id} does not match provided ID {external_id.identifier_issuer_id}",
    #                     )
    #             else:
    #                 # Add identifier issuer ID, must be as a new instance since external_ids are frozen
    #                 if sample.external_ids is not None:
    #                     sample.external_ids[i] = external_id.model_copy(
    #                         update={"identifier_issuer_id": identifier_issuer.id}
    #                     )
    #             # Add to ID map as well
    #             if identifier_issuer.id is not None:
    #                 identifier_issuer_by_id_map[identifier_issuer.id] = identifier_issuer  # type: ignore[misc]

    # Retrieve and verify external IDs
    external_identifier_tuples = list(
        {
            (y.identifier_issuer_id, y.external_id)
            for x in samples
            for y in x.external_ids or []
        }
    )
    if external_identifier_tuples:
        # Get all SAMPLE external identifiers matching the provided external
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
                                value=IdentifierType.SAMPLE.value,
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
        has_existing_samples = False
        for sample, sample_result in zip(samples, sample_results):
            for external_id, external_id_result in zip(
                sample.external_ids or [], sample_result.external_ids or []
            ):
                if external_id_result.status in [
                    UploadStatus.SKIPPED,
                    UploadStatus.FAILED,
                ]:
                    # Already skipped or failed, no need to check existence
                    continue
                key: tuple[UUID, str] = (external_id.identifier_issuer_id, external_id.external_id)  # type: ignore[assignment]
                if key in existing_external_id_map:
                    has_existing_samples = True
                    existing_external_id = existing_external_id_map[key]
                    # Cross-validate with sample ID if given
                    if sample.id is not None:
                        if existing_external_id.internal_id != sample.id:
                            success = False
                            external_id_result.add_error(
                                "f8a9b0c1",
                                f"External identifier {external_id.external_id} refers to sample ID {existing_external_id.internal_id}, which does not match provided sample ID {sample.id}",
                            )
                        # External ID already exists, nothing to upload
                        external_id_result.id = existing_external_id.id
                        external_id_result.status = UploadStatus.SKIPPED
                    else:
                        # Fill in sample ID
                        sample.id = existing_external_id.internal_id
        if has_existing_samples and cmd.on_exists == OnExistsUploadAction.ERROR:
            success = False
            retval.add_error(
                "a1c7d9f3",
                "One or more samples already exist and on_exists=ERROR",
            )

    return success


def _verify_batch_associated_data(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Check associated data existence and consistency"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Prepare some data
    rev_map = {
        y: x for x, y in model.SampleForUpload.FOR_UPLOAD_MODEL_CLASS_MAP.items()
    }
    model_class_map: dict[str, type[model.Model]] = {
        y: rev_map[x]
        for x, y in model.SampleForUpload.MODEL_DATA_FIELD_NAME_MAP.items()
    }

    # Verify each associated data type for each sample
    has_existing_data = False
    for field_name, model_class in model_class_map.items():
        print(f"DEBUG: Processing field_name={field_name}, model_class={model_class}")
        # Collect all IDs for this associated data type and determine existence
        obj_ids: list[UUID] = list(
            {
                y.id
                for x in samples
                for y in getattr(x, field_name) or []
                if y.id is not None
            }
        )
        print(f"DEBUG: obj_ids for {field_name} = {obj_ids}")

        # Get existing object data if there are IDs to check
        existing_obj_ids = set()
        existing_obj_sample_id_map: dict[UUID, UUID] = {}
        if obj_ids:
            # Some object IDs are given, check existence
            objs_exist: list[bool] = self.repository.crud(  # type:ignore[assignment]
                uow,
                user_id,
                model_class,
                None,
                obj_ids,
                CrudOperation.EXISTS_SOME,
            )
            existing_obj_ids = {x for x, y in zip(obj_ids, objs_exist) if y}
            # Get (id, sample_id) for all existing ids
            if existing_obj_ids:
                result_iter = self.repository.read_fields(
                    uow,
                    user_id,
                    model_class,
                    ["id", "sample_id"],
                    filter=UuidSetFilter(key="id", members=frozenset(existing_obj_ids)),
                )
                existing_obj_sample_id_map = {x[0]: x[1] for x in result_iter}

        # Process all objects (both with and without IDs)
        for i, (sample, sample_result) in enumerate(zip(samples, sample_results)):
            print(f"DEBUG: Processing sample {i}, field_name={field_name}")
            sample_data = getattr(sample, field_name) or []
            sample_result_data = getattr(sample_result, field_name) or []
            print(
                f"DEBUG: sample_data length = {len(sample_data)}, sample_result_data length = {len(sample_result_data)}"
            )
            for obj, obj_result in zip(sample_data, sample_result_data):
                print(f"DEBUG: Processing obj.id = {obj.id}")
                sample_id = obj.sample_id
                if sample_id == NULL_ID:
                    sample_id = None
                obj_id = obj.id
                if obj_id == NULL_ID:
                    obj_id = None
                if obj_id is None:
                    # Instance does not exist yet, assign sample ID if existing
                    print(
                        f"DEBUG: Setting obj.sample_id from {obj.sample_id} to {sample.id}"
                    )
                    obj.sample_id = sample.id
                    print(f"DEBUG: After assignment, obj.sample_id = {obj.sample_id}")
                    continue
                if obj_id not in existing_obj_ids:
                    success = False
                    obj_result.add_error(
                        "d4f5e6a7",
                        f"ID does not exist",
                    )
                    continue  # Skip to next object since this one doesn't exist
                # Existing instance
                has_existing_data = True
                existing_sample_id = existing_obj_sample_id_map[obj_id]
                if sample.id is None or sample.id == NULL_ID:
                    # Fill in sample ID
                    sample.id = existing_sample_id
                else:
                    if sample.id != existing_sample_id:
                        success = False
                        obj_result.add_error(
                            "e5f6a7b8",
                            f"Associated data ID {obj.id} refers to sample ID {existing_sample_id}, which does not match provided sample ID {sample.id}",
                        )
    if has_existing_data and cmd.on_exists == OnExistsUploadAction.ERROR:
        success = False
        retval.add_error(
            "c6e7f8a0",
            f"One or more {model_class.NAME} instances already exist and on_exists=ERROR",
        )

    # Associated data class specific verifications
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
    success &= _set_and_verify_id_by_code(
        self,
        cmd,
        retval,
        uow,
        model.Seq,
        "assembly_protocol_id",
        "assembly_protocol_code",
        model.AssemblyProtocol,
    )

    # Get dict[(sample_id, seq_hash), [(read_set_id, read_set2_id, assembly_protocol_id, id)]
    sample_ids = list({sample.id for sample in samples if sample.id is not None})
    if not sample_ids:
        return success  # No samples with ID, nothing to verify
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
    success &= _set_and_verify_id_by_code(
        self,
        cmd,
        retval,
        uow,
        model.AlleleProfile,
        "locus_detection_protocol_id",
        "locus_detection_protocol_code",
        model.LocusDetectionProtocol,
    )

    # Retrieve and verify locus sets provided by ID and/or code
    success &= _set_and_verify_id_by_code(
        self,
        cmd,
        retval,
        uow,
        model.AlleleProfile,
        "locus_set_id",
        "locus_set_code",
        model.LocusSet,
    )

    # Retrieve and verify locus code maps provided by ID and/or code
    success &= _set_and_verify_id_by_code(
        self,
        cmd,
        retval,
        uow,
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

    # Finalise checks
    if has_existing_allele_profiles and cmd.on_exists == OnExistsUploadAction.ERROR:
        success = False
        retval.add_error(
            "d8a3b7f4",
            "One or more allele profiles already exist and on_exists=ERROR",
        )
    return success


def _set_and_verify_id_by_code(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
    data_field_name_or_class: str | type[model.Model],
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
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True
    if isinstance(data_field_name_or_class, str):
        data_field_name = data_field_name_or_class
    else:
        for_upload_model_class = model.SampleForUpload.FOR_UPLOAD_MODEL_CLASS_MAP[
            data_field_name_or_class
        ]
        data_field_name = model.SampleForUpload.MODEL_DATA_FIELD_NAME_MAP[
            for_upload_model_class
        ]
    # Retrieve and verify locus detection protocols provided by ID and/or code
    id_code_tuples = list(
        {
            (getattr(y, link_id_field_name), getattr(y, link_code_field_name))
            for x in samples
            for y in getattr(x, data_field_name) or []
        }
    )
    ids = {x[0] for x in id_code_tuples if x[0] is not None and x[0] != NULL_ID}
    codes = {x[1] for x in id_code_tuples if x[1] is not None}
    id_code_map: dict[UUID, str] = {}
    code_id_map: dict[str, UUID] = {}
    if ids or codes:
        # Retrieve existing ID-code pairs
        if is_same_service:
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
            # Different service, need to issue a command
            crud_command_class = self.app.domain.get_crud_command_for_model(
                linked_model_class
            )
            link_objs: list[model.Model] = self.app.handle(  # type:ignore[assignment]
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
        # Verify locus detection protocols in allele profiles
        for sample, sample_result in zip(samples, sample_results):
            link_objs = getattr(sample, data_field_name) or []
            obj_results = getattr(sample_result, data_field_name) or []
            for i, (obj, obj_result) in enumerate(zip(link_objs, obj_results)):
                link_id = getattr(obj, link_id_field_name)
                if link_id == NULL_ID:
                    link_id = None
                link_code = getattr(obj, link_code_field_name)
                if link_id and link_id not in id_code_map:
                    success = False
                    obj_result.add_error(
                        "b9e4f7c2",
                        f"{linked_model_class.NAME}.{linked_model_id_field_name}={link_id} does not exist",
                    )
                if link_code:
                    if link_code not in code_id_map:
                        success = False
                        obj_result.add_error(
                            "c7a9b2e4",
                            f"{linked_model_class.NAME}.{linked_model_code_field_name}={link_code} does not exist",
                        )
                    elif link_id and code_id_map[link_code] != link_id:
                        success = False
                        obj_result.add_error(
                            "a4d7b9c3",
                            f"{linked_model_class.NAME}.{linked_model_code_field_name}={link_code} with {linked_model_class.NAME}.{linked_model_id_field_name}={code_id_map[link_code]} does not match provided {linked_model_class.NAME}.{linked_model_id_field_name}={link_id}",
                        )
                    elif not link_id:
                        # Add ID
                        if is_frozen:
                            # Need to create a new instance since the class is frozen
                            new_obj = obj.model_copy(
                                update={link_id_field_name: code_id_map[link_code]}
                            )
                            link_objs[i] = new_obj
                        else:
                            setattr(obj, link_id_field_name, code_id_map[link_code])
    return success
